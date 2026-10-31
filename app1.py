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
        st.markdown("""
        <style>
            html, body, [class*="css"] { direction: rtl; text-align: right; }
            .stButton button { width: 100%; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

load_css()

# تهيئة البيانات
if 'students' not in st.session_state:
    st.session_state.students = dm.load_data()

# ==========================================
# 2. القائمة الجانبية
# ==========================================
with st.sidebar:
    st.title("🎓 نظام التقييم")
    st.markdown("---")
    menu = st.radio("القائمة الرئيسية:", [
        "سجل التلاميذ", 
        "تقييم المواد الدراسية", 
        "تقييم المهارات السلوكية", 
        "التقرير التشخيصي",
        "لوحة التحكم"
    ], index=3) 
    
    st.markdown("---")
    
    if st.session_state.students:
        st.caption(f"عدد التلاميذ: {len(st.session_state.students)}")

# ==========================================
# 3. سجل التلاميذ
# ==========================================
if menu == "سجل التلاميذ":
    st.header("📂 إدارة ملفات التلاميذ")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        with st.form("add_student", clear_on_submit=True):
            st.subheader("تسجيل تلميذ جديد")
            name = st.text_input("الاسم الثلاثي:")
            col_a, col_b = st.columns(2)
            with col_a: dob = st.date_input("تاريخ الميلاد:", value=None)
            with col_b: gender = st.selectbox("الجنس:", ["ذكر", "أنثى"])
            level = st.selectbox("المستوى:", ["تحضيري", "روضة", "سنة أولى"])
            
            if st.form_submit_button("حفظ البيانات", type="primary"):
                if name:
                    info = {"dob": str(dob), "gender": gender, "class_level": level}
                    dm.save_student_info(name, info)
                    st.session_state.students = dm.load_data()
                    st.success(f"تم حفظ {name}")
                else:
                    st.error("الاسم مطلوب")

    with c2:
        st.subheader("القائمة")
        if st.session_state.students:
            for n, d in st.session_state.students.items():
                with st.expander(n):
                    st.write(f"المستوى: {d['info'].get('class_level')}")
                    st.write(f"الجنس: {d['info'].get('gender')}")

# ==========================================
# 4. التقييم الأكاديمي
# ==========================================
elif menu == "تقييم المواد الدراسية":
    st.header("📚 التقييم الأكاديمي")
    if not st.session_state.students:
        st.warning("الرجاء إضافة تلاميذ.")
    else:
        student = st.selectbox("اختر التلميذ:", list(st.session_state.students.keys()))
        info = st.session_state.students[student]["info"]
        st.caption(f"البيانات: {info.get('class_level')} | {info.get('gender')}")
        
        with st.form("academic_form"):
            current = st.session_state.students[student].get("evaluations", {}).get("academic", {})
            new_data = {}
            
            tabs = st.tabs(list(dm.ACADEMIC_SUBJECTS.keys()))
            for i, (subj, skills) in enumerate(dm.ACADEMIC_SUBJECTS.items()):
                with tabs[i]:
                    subj_data = {}
                    for skill in skills:
                        prev = current.get(subj, {}).get(skill, 1) 
                        # تم إضافة subj للمفتاح لمنع التكرار
                        val = st.radio(skill, dm.RATING_OPTIONS, index=prev, key=f"ac_{student}_{subj}_{skill}", horizontal=True)
                        subj_data[skill] = dm.RATING_MAP[val]
                    new_data[subj] = subj_data
            
            if st.form_submit_button("حفظ التقييم الأكاديمي"):
                data = st.session_state.students
                if "evaluations" not in data[student]: data[student]["evaluations"] = {}
                data[student]["evaluations"]["academic"] = new_data
                data[student]["evaluations"]["last_update"] = datetime.now().strftime("%Y-%m-%d")
                dm.save_data(data)
                st.session_state.students = dm.load_data()
                st.toast("تم الحفظ!", icon="✅")

# ==========================================
# 5. التقييم السلوكي
# ==========================================
elif menu == "تقييم المهارات السلوكية":
    st.header("🧠 التقييم السلوكي")
    if st.session_state.students:
        student = st.selectbox("اختر التلميذ:", list(st.session_state.students.keys()))
        
        with st.form("behavioral_form"):
            current = st.session_state.students[student].get("evaluations", {}).get("behavioral", {})
            new_data = {}
            
            tabs = st.tabs(list(dm.BEHAVIORAL_SKILLS.keys()))
            for i, (main, subs) in enumerate(dm.BEHAVIORAL_SKILLS.items()):
                with tabs[i]:
                    main_data = {}
                    for sub, skills in subs.items():
                        st.markdown(f"**{sub}**")
                        sub_data = {}
                        for skill in skills:
                            prev = current.get(main, {}).get(sub, {}).get(skill, 1)
                            # تم إضافة main و sub للمفتاح لمنع التكرار نهائياً
                            val = st.radio(skill, dm.RATING_OPTIONS, index=prev, key=f"beh_{student}_{main}_{sub}_{skill}", horizontal=True)
                            sub_data[skill] = dm.RATING_MAP[val]
                        main_data[sub] = sub_data
                        st.markdown("---")
                    new_data[main] = main_data
            
            if st.form_submit_button("حفظ التقييم السلوكي"):
                data = st.session_state.students
                if "evaluations" not in data[student]: data[student]["evaluations"] = {}
                data[student]["evaluations"]["behavioral"] = new_data
                data[student]["evaluations"]["last_update"] = datetime.now().strftime("%Y-%m-%d")
                dm.save_data(data)
                st.session_state.students = dm.load_data()
                st.toast("تم الحفظ!", icon="✅")

# ==========================================
# 6. التقرير التشخيصي (النسخة النهائية)
# ==========================================
elif menu == "التقرير التشخيصي":
    st.header("📈 التقرير التشخيصي الشامل")
    
    if not st.session_state.students:
        st.warning("لا توجد بيانات.")
    else:
        student = st.selectbox("اختر التلميذ:", list(st.session_state.students.keys()))
        
        student_data = st.session_state.students[student]
        info = student_data["info"]
        evals = student_data.get("evaluations", {})
        gender = info.get("gender", "ذكر")
        
        # عرض النتائج بالأرقام
        scores = dm.calculate_scores(evals)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("التحصيل الدراسي", f"{scores['academic_percentage']:.0f}%")
        c2.metric("السلوك والمواظبة", f"{scores['behavioral_percentage']:.0f}%")
        c3.metric("النسبة العامة", f"{scores['overall_percentage']:.0f}%")
        st.progress(scores['overall_percentage'] / 100)
        
        st.divider()

        # إدارة استدعاء الذكاء الاصطناعي لمنع استهلاك الحد المسموح (Rate Limit)
        ai_state_key = f"ai_report_{student}"
        if ai_state_key not in st.session_state:
            st.session_state[ai_state_key] = {"narrative": "", "action_plan": []}

        if st.button("🤖 توليد / تحديث التحليل التربوي الذكي", type="secondary"):
            with st.spinner("يتصل بالذكاء الاصطناعي لتحليل البيانات..."):
                narr, plan = dm.analyze_student_performance(student, evals, gender)
                st.session_state[ai_state_key] = {"narrative": narr, "action_plan": plan}

        narrative = st.session_state[ai_state_key]["narrative"]
        action_plan = st.session_state[ai_state_key]["action_plan"]
        
        # عرض التحليل والخطة
        col_text, col_plan = st.columns([2, 1])
        
        with col_text:
            st.subheader("📝 التحليل التربوي")
            if narrative:
                st.markdown(
                    f"""
                    <div style="background-color:#f8f9fa; padding:20px; border-radius:10px; border-right: 5px solid #2e86de; font-size:16px; line-height:1.8; color:#2c3e50;">
                    {narrative.replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True
                )
            else:
                st.info("اضغط على الزر أعلاه لتوليد التحليل باستخدام الذكاء الاصطناعي.")

        with col_plan:
            st.subheader("💡 الخطة المقترحة")
            if action_plan:
                for item, rec in action_plan:
                    with st.expander(f"📌 {item}"):
                        st.info(rec)
            elif narrative and ("خطأ" in narrative or "Error" in narrative):
                st.warning("تعذر جلب الخطة المقترحة بسبب مشكلة في الاتصال. حاول لاحقاً.")
            elif narrative:
                st.success("الأداء ممتاز، استمر في التشجيع!")
            else:
                st.caption("في انتظار التوليد...")

        st.divider()
        
        # قسم PDF
        st.subheader("📄 إصدار التقرير الرسمي")
        
        pdf_key = f"pdf_{student}_{evals.get('last_update', 'new')}"
        
        if pdf_key not in st.session_state:
            if st.button("🔄 إنشاء ملف PDF (جاهز للطباعة)", type="primary"):
                try:
                    import pdf_generator
                    with st.spinner("جاري صياغة التقرير، رسم الجداول، وضبط التنسيق..."):
                        pdf_bytes, error = pdf_generator.create_pdf(
                            student, info, evals, narrative, action_plan
                        )
                        
                        if pdf_bytes:
                            st.session_state[pdf_key] = pdf_bytes
                            st.rerun()
                        else:
                            st.error(f"خطأ: {error}")
                except ImportError:
                    st.error("المكتبات مفقودة (fpdf2, arabic-reshaper, python-bidi)")
        
        if pdf_key in st.session_state:
            c_d1, c_d2 = st.columns([1, 4])
            with c_d1:
                st.download_button(
                    label="📥 تحميل PDF",
                    data=st.session_state[pdf_key],
                    file_name=f"Report_{student}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
            with c_d2:
                if st.button("إعادة إنشاء"):
                    del st.session_state[pdf_key]
                    st.rerun()

# ==========================================
# 7. لوحة التحكم
# ==========================================
elif menu == "لوحة التحكم":
    st.header("📊 إحصائيات عامة")
    if st.session_state.students:
        df = []
        for name, data in st.session_state.students.items():
            scores = dm.calculate_scores(data.get("evaluations", {}))
            df.append({
                "الاسم": name,
                "المستوى": data["info"].get("class_level"),
                "الأداء العام": f"{scores['overall_percentage']:.1f}%"
            })
        st.dataframe(pd.DataFrame(df), use_container_width=True)
        
        if st.button("🗑️ حذف جميع البيانات"):
            st.session_state.students = {}
            dm.save_data({})
            st.rerun()
    else:
        st.info("لا توجد بيانات.")

