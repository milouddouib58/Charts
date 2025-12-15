import streamlit as st
import pandas as pd
import json
import data_manager as dm
from datetime import datetime

# ==========================================
# 1. إعدادات الصفحة والتهيئة
# ==========================================
st.set_page_config(page_title="نظام التقييم الشامل المطور", layout="wide", page_icon="🎓")

# تحميل التنسيقات (CSS)
def load_css():
    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # تنسيق احتياطي في حال عدم وجود الملف
        st.markdown("""
        <style>
            html, body, [class*="css"] { direction: rtl; text-align: right; }
            .stButton button { width: 100%; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

load_css()

# تهيئة مخزن البيانات في الجلسة
if 'students' not in st.session_state:
    st.session_state.students = dm.load_data()

# ==========================================
# 2. القائمة الجانبية (Sidebar)
# ==========================================
with st.sidebar:
    st.title("🎓 نظام التقييم المتكامل")
    st.markdown("---")
    menu = st.radio("القائمة الرئيسية:", [
        "سجل التلاميذ", 
        "تقييم المواد الدراسية", 
        "تقييم المهارات السلوكية", 
        "التقرير التشخيصي",
        "لوحة التحكم"
    ], index=1)
    
    st.markdown("---")
    
    with st.expander("ℹ️ معلومات النظام"):
        st.info("""
        **المميزات الجديدة:**
        1. تقارير PDF احترافية مع رموز (✔ / ✖).
        2. تحليل ذكي لنقاط الضعف وعرض الحلول.
        3. حساب نسب التحكم لكل مادة.
        4. إمكانية توقيع الولي والإدارة.
        """)
    
    # إحصائيات سريعة في القائمة
    if st.session_state.students:
        st.markdown("**📊 حالة القسم:**")
        st.caption(f"عدد التلاميذ: {len(st.session_state.students)}")
        evaluated_count = sum(1 for s in st.session_state.students.values() if s.get("evaluations"))
        st.caption(f"تم تقييمهم: {evaluated_count}")

# ==========================================
# 3. القسم الأول: سجل التلاميذ
# ==========================================
if menu == "سجل التلاميذ":
    st.header("📂 إدارة ملفات التلاميذ")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("add_student", clear_on_submit=True):
            st.subheader("إضافة تلميذ جديد")
            name = st.text_input("اسم التلميذ بالكامل:")
            
            col_a, col_b = st.columns(2)
            with col_a:
                birth_date = st.date_input("تاريخ الميلاد:", value=None)
            with col_b:
                gender = st.selectbox("الجنس:", ["ذكر", "أنثى"])
            
            class_level = st.selectbox("المستوى الدراسي:", 
                                      ["القسم التحضيري", "تمهيدي", "روضة أولى", "روضة ثانية", "صف أول ابتدائي"])
            
            notes = st.text_area("ملاحظات أولية (صحيّة/عائلية/أخرى):", height=100)
            
            if st.form_submit_button("📥 حفظ بيانات التلميذ", type="primary"):
                if not name or name.strip() == "":
                    st.error("الرجاء إدخال اسم التلميذ")
                elif name in st.session_state.students:
                    st.warning(f"التلميذ '{name}' مسجل مسبقاً")
                else:
                    new_info = {
                        "dob": str(birth_date),
                        "gender": gender,
                        "class_level": class_level,
                        "notes": notes,
                        "registration_date": datetime.now().strftime("%Y-%m-%d")
                    }
                    dm.save_student_info(name, new_info)
                    st.session_state.students = dm.load_data() # تحديث البيانات
                    st.success(f"✅ تم تسجيل التلميذ: {name}")
    
    with col2:
        st.subheader("قائمة التلاميذ")
        if st.session_state.students:
            for student_name in st.session_state.students.keys():
                with st.expander(f"👤 {student_name}"):
                    info = st.session_state.students[student_name]["info"]
                    st.write(f"**المستوى:** {info.get('class_level', '-')}")
                    st.write(f"**تاريخ الميلاد:** {info.get('dob', '-')}")
        else:
            st.info("لا يوجد تلاميذ مسجلين بعد.")

# ==========================================
# 4. القسم الثاني: تقييم المواد الدراسية
# ==========================================
elif menu == "تقييم المواد الدراسية":
    st.header("📚 تقييم المواد الدراسية الأساسية")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("⚠️ الرجاء تسجيل تلاميذ أولاً من قسم 'سجل التلاميذ'.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", student_names)
        
        # عرض معلومات مختصرة
        if selected_student:
            student_info = st.session_state.students[selected_student]["info"]
            c1, c2, c3 = st.columns(3)
            c1.metric("المستوى", student_info.get("class_level", "-"))
            c2.metric("الجنس", student_info.get("gender", "-"))
            c3.metric("تاريخ الميلاد", student_info.get("dob", "-"))
        
        st.markdown("---")
        
        with st.form("academic_evaluation"):
            st.subheader("📋 تقييم المواد الدراسية")
            
            current_evals = st.session_state.students[selected_student].get("evaluations", {})
            academic_evals = current_evals.get("academic", {})
            new_academic_data = {}
            
            # إنشاء تبويبات للمواد
            academic_tabs = st.tabs(list(dm.ACADEMIC_SUBJECTS.keys()))
            
            for i, (subject, skills) in enumerate(dm.ACADEMIC_SUBJECTS.items()):
                with academic_tabs[i]:
                    st.markdown(f"### {subject}")
                    subject_data = {}
                    for skill in skills:
                        # استرجاع القيمة السابقة أو الافتراضي (1: في طريق الاكتساب)
                        prev_val_idx = 1
                        if subject in academic_evals:
                            prev_val_idx = academic_evals[subject].get(skill, 1)
                        
                        col_label, col_radio = st.columns([3, 2])
                        with col_label: st.markdown(f"**{skill}**")
                        with col_radio:
                            choice = st.radio(
                                f"label_{skill}", dm.RATING_OPTIONS, index=prev_val_idx,
                                key=f"ac_{selected_student}_{subject}_{skill}",
                                horizontal=True, label_visibility="collapsed"
                            )
                        subject_data[skill] = dm.RATING_MAP[choice]
                    new_academic_data[subject] = subject_data
                    st.markdown("---")
            
            academic_notes = st.text_area("ملاحظات الأستاذ (أكاديمي):", value=current_evals.get("academic_notes", ""))
            
            if st.form_submit_button("💾 حفظ تقييم المواد الدراسية", type="primary"):
                # تحديث الهيكل
                data = st.session_state.students
                if "evaluations" not in data[selected_student]:
                    data[selected_student]["evaluations"] = {}
                
                data[selected_student]["evaluations"]["academic"] = new_academic_data
                data[selected_student]["evaluations"]["academic_notes"] = academic_notes
                data[selected_student]["evaluations"]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                dm.save_data(data)
                st.session_state.students = dm.load_data()
                st.toast("تم الحفظ بنجاح!", icon="✅")

# ==========================================
# 5. القسم الثالث: تقييم المهارات السلوكية
# ==========================================
elif menu == "تقييم المهارات السلوكية":
    st.header("🧠 تقييم المهارات السلوكية والتنموية")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("⚠️ الرجاء تسجيل تلاميذ أولاً.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", student_names)
        st.markdown("---")
        
        with st.form("behavioral_evaluation"):
            st.subheader("📊 تقييم المهارات السلوكية")
            
            current_evals = st.session_state.students[selected_student].get("evaluations", {})
            behavioral_evals = current_evals.get("behavioral", {})
            new_behavioral_data = {}
            
            behavioral_tabs = st.tabs(list(dm.BEHAVIORAL_SKILLS.keys()))
            
            for i, (main_cat, sub_cats) in enumerate(dm.BEHAVIORAL_SKILLS.items()):
                with behavioral_tabs[i]:
                    st.markdown(f"### {main_cat}")
                    cat_data = {}
                    for sub_cat, skills in sub_cats.items():
                        st.markdown(f"#### {sub_cat}")
                        sub_data = {}
                        for skill in skills:
                            prev_val_idx = 1
                            if main_cat in behavioral_evals and sub_cat in behavioral_evals[main_cat]:
                                prev_val_idx = behavioral_evals[main_cat][sub_cat].get(skill, 1)
                            
                            col_l, col_r = st.columns([3, 2])
                            with col_l: st.markdown(f"**{skill}**")
                            with col_r:
                                choice = st.radio(
                                    f"label_{skill}", dm.RATING_OPTIONS, index=prev_val_idx,
                                    key=f"beh_{selected_student}_{main_cat}_{sub_cat}_{skill}",
                                    horizontal=True, label_visibility="collapsed"
                                )
                            sub_data[skill] = dm.RATING_MAP[choice]
                        cat_data[sub_cat] = sub_data
                        st.markdown("---")
                    new_behavioral_data[main_cat] = cat_data
            
            behav_notes = st.text_area("ملاحظات السلوك:", value=current_evals.get("behavioral_notes", ""))
            
            if st.form_submit_button("💾 حفظ تقييم المهارات السلوكية", type="primary"):
                data = st.session_state.students
                if "evaluations" not in data[selected_student]:
                    data[selected_student]["evaluations"] = {}
                    
                data[selected_student]["evaluations"]["behavioral"] = new_behavioral_data
                data[selected_student]["evaluations"]["behavioral_notes"] = behav_notes
                data[selected_student]["evaluations"]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                dm.save_data(data)
                st.session_state.students = dm.load_data()
                st.toast("تم الحفظ بنجاح!", icon="✅")

# ==========================================
# 6. القسم الرابع: التقرير التشخيصي (تم استعادة عرض التحليل والحلول)
# ==========================================
elif menu == "التقرير التشخيصي":
    st.header("📈 التقرير التشخيصي الشامل")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("لا يوجد بيانات لعرض التقارير.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", student_names)
        
        # جلب البيانات
        data = st.session_state.students[selected_student].get("evaluations", {})
        student_info = st.session_state.students[selected_student]["info"]
        
        # حساب الدرجات
        scores = dm.calculate_scores(data)
        
        # 1. بطاقة النتائج المرئية
        st.subheader("🎯 مؤشرات الأداء")
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.metric("المواد الدراسية", f"{scores['academic_percentage']:.1f}%")
            st.progress(scores['academic_percentage'] / 100)
        with c2: 
            st.metric("المهارات السلوكية", f"{scores['behavioral_percentage']:.1f}%")
            st.progress(scores['behavioral_percentage'] / 100)
        with c3: 
            st.metric("المجموع الكلي", f"{scores['overall_percentage']:.1f}%")
            st.progress(scores['overall_percentage'] / 100)

        st.divider()

        # ---------------------------------------------------------
        # عرض التحليل والحلول على الشاشة
        # ---------------------------------------------------------
        
        # جلب التحليل والخطة من Logic
        narrative, action_plan = dm.analyze_student_performance(selected_student, data)

        col_analysis, col_solutions = st.columns(2)
        
        # عرض التحليل (أسباب الصعوبات ونقاط القوة)
        with col_analysis:
            st.subheader("📝 التحليل النوعي")
            st.info(narrative, icon="ℹ️")
            
            # عرض نقاط الضعف المحددة
            if scores['weaknesses']:
                st.markdown("##### ⚠️ صعوبات تم رصدها:")
                for w in scores['weaknesses']:
                    st.error(w)
            else:
                st.success("لم يتم رصد صعوبات جوهرية.")

        # عرض الحلول المقترحة (الخطة العلاجية)
        with col_solutions:
            st.subheader("💡 الحلول المقترحة (الخطة العلاجية)")
            if action_plan:
                for skill, recommendation in action_plan:
                    with st.expander(f"لتحسين: {skill}", expanded=True):
                        st.markdown(f"**✅ الإجراء المقترح:**")
                        st.write(recommendation)
            else:
                st.success("🎉 مستوى التلميذ ممتاز، يوصى بالاستمرار في التعزيز الإيجابي.", icon="🌟")

        st.divider()
        # ---------------------------------------------------------

        # 3. أزرار التحميل (Text & PDF)
        
        # --- تحميل التقرير النصي ---
        report_text = dm.generate_text_report(
            selected_student, student_info, data, scores, narrative, action_plan
        )
        st.download_button("📄 تحميل مسودة نصية (TXT)", report_text, f"report_{selected_student}.txt")

        # --- قسم تحميل PDF ---
        st.write("")
        st.markdown("### 📄 التقرير الرسمي (PDF)")
        st.caption("يتضمن التقرير الرموز (✔/✖)، النسب المئوية، وخانات التوقيع.")
        
        last_update = data.get("last_update", datetime.now().strftime("%Y%m%d%H%M"))
        pdf_key = f"pdf_cache_{selected_student}_{last_update}"
        
        if pdf_key not in st.session_state:
            if st.button("🔄 إنشاء وتجهيز ملف PDF", type="secondary"):
                try:
                    import pdf_generator
                    with st.spinner("جاري الرسم ومعالجة الخطوط العربية..."):
                        pdf_bytes, error_msg = pdf_generator.create_pdf(
                            selected_student, 
                            student_info, 
                            data, 
                            narrative, 
                            action_plan
                        )
                        
                        if pdf_bytes:
                            st.session_state[pdf_key] = pdf_bytes
                            st.rerun()
                        else:
                            st.error(f"حدث خطأ أثناء الإنشاء: {error_msg}")
                except ImportError:
                    st.error("مكتبات PDF مفقودة (fpdf2, arabic-reshaper, python-bidi).")
        
        if pdf_key in st.session_state:
            st.success("التقرير جاهز للطباعة!")
            col_d1, col_d2 = st.columns([1, 2])
            with col_d1:
                st.download_button(
                    label="📥 تحميل التقرير (PDF)",
                    data=st.session_state[pdf_key],
                    file_name=f"Report_{selected_student}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
            with col_d2:
                if st.button("إعادة الإنشاء"):
                    del st.session_state[pdf_key]
                    st.rerun()

# ==========================================
# 7. القسم الخامس: لوحة التحكم
# ==========================================
elif menu == "لوحة التحكم":
    st.header("📊 لوحة التحكم والإحصاءات")
    
    if st.session_state.students:
        total = len(st.session_state.students)
        evaluated = sum(1 for s in st.session_state.students.values() if s.get("evaluations"))
        
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي التلاميذ", total)
        c2.metric("تم تقييمهم", evaluated)
        c3.metric("نسبة الإنجاز", f"{(evaluated/total*100):.1f}%" if total else "0%")
        
        st.divider()
        
        # جدول البيانات
        st.subheader("سجل المتابعة")
        data_list = []
        for name, info in st.session_state.students.items():
            last_up = info.get("evaluations", {}).get("last_update", "غير مقيم")
            data_list.append({
                "الاسم": name,
                "المستوى": info["info"].get("class_level", ""),
                "آخر تحديث": last_up
            })
        st.dataframe(pd.DataFrame(data_list), use_container_width=True)
        
        st.divider()
        st.subheader("⚙️ النسخ الاحتياطي")
        
        json_data = json.dumps(st.session_state.students, ensure_ascii=False, indent=2)
        st.download_button("💾 تحميل قاعدة البيانات (JSON)", json_data, "students_backup.json", "application/json")
        
        with st.expander("منطقة الخطر"):
            if st.button("🗑️ حذف جميع البيانات (لا يمكن التراجع)", type="primary"):
                st.session_state.students = {}
                dm.save_data({})
                st.rerun()
    else:
        st.info("لا توجد بيانات حالياً.")

