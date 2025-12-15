import streamlit as st
import pandas as pd
import json
import data_manager as dm
from datetime import datetime

# 1. الإعدادات
st.set_page_config(page_title="نظام التقييم الشامل", layout="wide", page_icon="🎓")

def load_css():
    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""<style>html, body, [class*="css"] { direction: rtl; text-align: right; }</style>""", unsafe_allow_html=True)
load_css()

if 'students' not in st.session_state:
    st.session_state.students = dm.load_data()

# 2. القائمة
with st.sidebar:
    st.title("🎓 نظام التقييم")
    menu = st.radio("القائمة:", ["سجل التلاميذ", "التقييم الأكاديمي", "التقييم السلوكي", "التقرير التشخيصي", "لوحة التحكم"], index=3)

# 3. سجل التلاميذ
if menu == "سجل التلاميذ":
    st.header("📂 إدارة الملفات")
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.form("new_stud"):
            name = st.text_input("الاسم:")
            dob = st.date_input("الميلاد:")
            gender = st.selectbox("الجنس:", ["ذكر", "أنثى"])
            level = st.selectbox("المستوى:", ["تحضيري", "روضة", "سنة أولى"])
            if st.form_submit_button("حفظ"):
                dm.save_student_info(name, {"dob": str(dob), "gender": gender, "class_level": level})
                st.session_state.students = dm.load_data()
                st.success("تم الحفظ")
    with c2:
        if st.session_state.students:
            st.dataframe(pd.DataFrame.from_dict(st.session_state.students, orient='index')['info'].apply(pd.Series))

# 4. الأكاديمي
elif menu == "التقييم الأكاديمي":
    st.header("📚 التقييم الأكاديمي")
    if st.session_state.students:
        s = st.selectbox("الطالب:", list(st.session_state.students.keys()))
        curr = st.session_state.students[s].get("evaluations", {}).get("academic", {})
        with st.form("ac_form"):
            new_d = {}
            tabs = st.tabs(list(dm.ACADEMIC_SUBJECTS.keys()))
            for i, (subj, skills) in enumerate(dm.ACADEMIC_SUBJECTS.items()):
                with tabs[i]:
                    sd = {}
                    for sk in skills:
                        val = st.radio(sk, dm.RATING_OPTIONS, index=curr.get(subj, {}).get(sk, 1), key=f"a_{s}_{sk}", horizontal=True)
                        sd[sk] = dm.RATING_MAP[val]
                    new_d[subj] = sd
            if st.form_submit_button("حفظ"):
                d = st.session_state.students; d[s].setdefault("evaluations", {})["academic"] = new_d
                d[s]["evaluations"]["last_update"] = datetime.now().strftime("%Y-%m-%d")
                dm.save_data(d); st.toast("تم الحفظ")

# 5. السلوكي
elif menu == "التقييم السلوكي":
    st.header("🧠 التقييم السلوكي")
    if st.session_state.students:
        s = st.selectbox("الطالب:", list(st.session_state.students.keys()))
        curr = st.session_state.students[s].get("evaluations", {}).get("behavioral", {})
        with st.form("beh_form"):
            new_d = {}
            tabs = st.tabs(list(dm.BEHAVIORAL_SKILLS.keys()))
            for i, (main, subs) in enumerate(dm.BEHAVIORAL_SKILLS.items()):
                with tabs[i]:
                    md = {}
                    for sub, skills in subs.items():
                        st.markdown(f"**{sub}**")
                        sd = {}
                        for sk in skills:
                            val = st.radio(sk, dm.RATING_OPTIONS, index=curr.get(main, {}).get(sub, {}).get(sk, 1), key=f"b_{s}_{sk}", horizontal=True)
                            sd[sk] = dm.RATING_MAP[val]
                        md[sub] = sd
                    new_d[main] = md
            if st.form_submit_button("حفظ"):
                d = st.session_state.students; d[s].setdefault("evaluations", {})["behavioral"] = new_d
                d[s]["evaluations"]["last_update"] = datetime.now().strftime("%Y-%m-%d")
                dm.save_data(d); st.toast("تم الحفظ")

# 6. التقرير
elif menu == "التقرير التشخيصي":
    st.header("📈 التقرير الشامل")
    if st.session_state.students:
        s = st.selectbox("الطالب:", list(st.session_state.students.keys()))
        data = st.session_state.students[s].get("evaluations", {})
        info = st.session_state.students[s]["info"]
        
        narrative, plan = dm.analyze_student_performance(s, data, info.get("gender", "ذكر"))
        scores = dm.calculate_scores(data)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("أكاديمي", f"{scores['academic_percentage']:.0f}%")
        c2.metric("سلوكي", f"{scores['behavioral_percentage']:.0f}%")
        c3.metric("عام", f"{scores['overall_percentage']:.0f}%")
        
        st.divider()
        c_txt, c_plan = st.columns([2, 1])
        with c_txt:
            st.subheader("📝 التحليل")
            st.info(narrative)
        with c_plan:
            st.subheader("💡 الخطة")
            if plan:
                for k, v in plan:
                    with st.expander(k): st.write(v)
            else: st.success("ممتاز!")
            
        st.divider()
        if st.button("📄 إنشاء PDF"):
            try:
                import pdf_generator
                pdf_bytes, err = pdf_generator.create_pdf(s, info, data, narrative, plan)
                if pdf_bytes:
                    st.download_button("📥 تحميل PDF", pdf_bytes, f"Report_{s}.pdf", "application/pdf")
                else: st.error(err)
            except ImportError: st.error("مكتبات PDF مفقودة")

# 7. لوحة التحكم
elif menu == "لوحة التحكم":
    st.header("📊 الإحصائيات")
    if st.session_state.students:
        if st.button("حذف البيانات"):
            st.session_state.students = {}; dm.save_data({}); st.rerun()

