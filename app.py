import streamlit as st
import pandas as pd
import json
import plotly.express as px
import data_manager as dm
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام التقييم الشامل المطور", layout="wide", page_icon="🎓")

# --- تحميل التنسيقات ---
def load_css():
    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("ملف التنسيق غير موجود (assets/style.css)")

load_css()

# --- تهيئة البيانات ---
if 'students' not in st.session_state:
    st.session_state.students = dm.load_data()

# --- القائمة الجانبية ---
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
    
    # معلومات حول النظام
    with st.expander("ℹ️ معلومات النظام"):
        st.info("""
        **مميزات النظام:**
        1. تقييم منفصل للمواد الدراسية
        2. تقييم منفصل للمهارات السلوكية
        3. تقارير تحليلية مفصلة
        4. تخزين بيانات آمن
        """)
    
    # عرض إحصاءات سريعة
    if st.session_state.students:
        st.markdown("**📊 إحصاءات سريعة:**")
        st.caption(f"عدد التلاميذ: {len(st.session_state.students)}")
        
        # حساب التلاميذ الذين لديهم تقييم
        evaluated = sum(1 for s in st.session_state.students.values() if s.get("evaluations"))
        st.caption(f"تم تقييمهم: {evaluated}")

# ==========================================
# 1. سجل التلاميذ
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
            
            submitted = st.form_submit_button("📥 حفظ بيانات التلميذ", type="primary")
            
            if submitted and name:
                if name.strip() == "":
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
                    st.session_state.students = dm.load_data() # Reload
                    st.success(f"✅ تم تسجيل التلميذ: {name}")
    
    with col2:
        st.subheader("قائمة التلاميذ المسجلين")
        if st.session_state.students:
            for student_name in st.session_state.students.keys():
                with st.expander(f"👤 {student_name}"):
                    info = st.session_state.students[student_name]["info"]
                    st.caption(f"**المستوى:** {info.get('class_level', 'غير محدد')}")
                    st.caption(f"**تاريخ الميلاد:** {info.get('dob', 'غير محدد')}")
                    st.caption(f"**الجنس:** {info.get('gender', 'غير محدد')}")
        else:
            st.info("لا يوجد تلاميذ مسجلين بعد")

# ==========================================
# 2. تقييم المواد الدراسية
# ==========================================
elif menu == "تقييم المواد الدراسية":
    st.header("📚 تقييم المواد الدراسية الأساسية")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("⚠️ الرجاء تسجيل تلاميذ أولاً من قسم 'سجل التلاميذ'.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", student_names)
        
        # معلومات التلميذ
        if selected_student:
            student_info = st.session_state.students[selected_student]["info"]
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1: st.metric("المستوى", student_info.get("class_level", "غير محدد"))
            with col_info2: st.metric("الجنس", student_info.get("gender", "غير محدد"))
            with col_info3: st.metric("تاريخ الميلاد", student_info.get("dob", "غير محدد"))
        
        st.markdown("---")
        
        with st.form("academic_evaluation"):
            st.subheader("📋 تقييم المواد الدراسية")
            
            # الحصول على التقييمات السابقة
            current_evals = st.session_state.students[selected_student].get("evaluations", {})
            academic_evals = current_evals.get("academic", {})
            
            new_academic_data = {}
            
            # إنشاء تبويبات للمواد الدراسية
            academic_tabs = st.tabs(list(dm.ACADEMIC_SUBJECTS.keys()))
            
            for i, (subject, skills) in enumerate(dm.ACADEMIC_SUBJECTS.items()):
                with academic_tabs[i]:
                    st.markdown(f"### {subject}")
                    subject_data = {}
                    
                    for skill in skills:
                        # استرجاع القيمة السابقة
                        prev_val_idx = 1
                        if subject in academic_evals:
                            prev_val_idx = academic_evals[subject].get(skill, 1)
                        
                        col_label, col_radio = st.columns([3, 2])
                        with col_label: st.markdown(f"**{skill}**")
                        with col_radio:
                            choice = st.radio(
                                "", dm.RATING_OPTIONS, index=prev_val_idx,
                                key=f"ac_{selected_student}_{subject}_{skill}",
                                horizontal=True, label_visibility="collapsed"
                            )
                        subject_data[skill] = dm.RATING_MAP[choice]
                    new_academic_data[subject] = subject_data
                    st.markdown("---")
            
            academic_notes = st.text_area("ملاحظات إضافية:", value=current_evals.get("academic_notes", ""))
            
            if st.form_submit_button("💾 حفظ تقييم المواد الدراسية", type="primary"):
                # Update logic
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
# 3. تقييم المهارات السلوكية
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
                                    "", dm.RATING_OPTIONS, index=prev_val_idx,
                                    key=f"beh_{selected_student}_{main_cat}_{sub_cat}_{skill}",
                                    horizontal=True, label_visibility="collapsed"
                                )
                            sub_data[skill] = dm.RATING_MAP[choice]
                        cat_data[sub_cat] = sub_data
                        st.markdown("---")
                    new_behavioral_data[main_cat] = cat_data
            
            behav_notes = st.text_area("ملاحظات:", value=current_evals.get("behavioral_notes", ""))
            
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
# 4. التقرير التشخيصي
# ==========================================
elif menu == "التقرير التشخيصي":
    st.header("📈 التقرير التشخيصي الشامل")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("لا يوجد بيانات.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", student_names)
        data = st.session_state.students[selected_student].get("evaluations", {})
        
        scores = dm.calculate_scores(data)
        
        # --- 1. بطاقة النتائج ---
        st.subheader("🎯 النتائج العامة")
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

        st.markdown("---")
        
        # --- 2. التحليل التفصيلي ---
        with st.expander("📚 تحليل المواد الدراسية", expanded=True):
             if "academic" in data:
                for subject, skills in data["academic"].items():
                    s_total = sum(skills.values())
                    s_max = len(skills) * 2
                    s_perc = (s_total/s_max*100) if s_max else 0
                    st.write(f"**{subject}**: {s_perc:.1f}%")
                    st.progress(s_perc/100)

        # --- 3. نقاط القوة والضعف ---
        c_weak, c_strong = st.columns(2)
        with c_weak:
            st.subheader("🚨 يحتاج لتحسين")
            for w in scores['weaknesses']: st.error(w)
        with c_strong:
            st.subheader("✅ نقاط القوة")
            for s in scores['strengths'][:10]: st.success(s)

        # --- Report Export ---
        st.divider()
        report_text = f"تقرير التلميذ: {selected_student}\nالمجموع: {scores['overall_percentage']:.1f}%"
        st.download_button("📄 تحميل تقرير نصي", report_text, f"report_{selected_student}.txt")

# ==========================================
# 5. Dashboard
# ==========================================
elif menu == "لوحة التحكم":
    st.header("📊 لوحة التحكم والإحصاءات")
    if st.session_state.students:
        total = len(st.session_state.students)
        evaluated = sum(1 for s in st.session_state.students.values() if s.get("evaluations"))
        
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي التلاميذ", total)
        c2.metric("تم تقييمهم", evaluated)
        c3.metric("النسبة", f"{(evaluated/total*100):.1f}%" if total else "0%")
        
        st.divider()
        
        # Table
        data_list = []
        for name, info in st.session_state.students.items():
            data_list.append({
                "الاسم": name,
                "المستوى": info["info"].get("class_level", ""),
                "تم التقييم": "نعم" if info.get("evaluations") else "لا"
            })
        st.dataframe(pd.DataFrame(data_list), use_container_width=True)
        
        # Backup
        st.divider()
        st.subheader("⚙️ إدارة البيانات")
        json_data = json.dumps(st.session_state.students, ensure_ascii=False, indent=2)
        st.download_button("💾 تحميل نسخة احتياطية (JSON)", json_data, "backup.json", "application/json")
        
        if st.button("🗑️ مسح كافة البيانات (حذر!)"):
            st.session_state.students = {}
            dm.save_data({})
            st.rerun()


