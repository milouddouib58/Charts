import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام التقييم التحضيري", layout="wide", page_icon="🎓")

# تفعيل دعم اللغة العربية وتنسيق الاتجاه من اليمين لليسار
st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    .stTextInput, .stSelectbox, .stNumberInput, .stSlider {direction: rtl; text-align: right;}
    h1, h2, h3, p, div {text-align: right;}
</style>
""", unsafe_allow_html=True)

# --- هيكل البيانات (المحاور والمؤشرات) ---
# تم استخراج هذه البيانات من النص الذي قدمته
ASSESSMENT_CRITERIA = {
    "المهارات الأكاديمية": [
        "القراءة المبكرة (تمييز الأحرف)",
        "الكتابة التحضيرية (مسك القلم)",
        "المفاهيم الرياضية (العد والمقارنة)",
        "المنطق والتصنيف"
    ],
    "المهارات التنفيذية": [
        "الانتباه والتركيز",
        "الذاكرة العاملة",
        "التحكم في الاندفاع",
        "المرونة والتنظيم"
    ],
    "الكفاءة الاجتماعية": [
        "الوعي الذاتي",
        "التنظيم الذاتي للمشاعر",
        "التفاعل مع الأقران",
        "حل النزاعات"
    ],
    "الكفاءة اللغوية": [
        "الوعي الصوتي",
        "ثراء المفردات",
        "تركيب الجمل",
        "القدرة السردية"
    ],
    "الاستقلالية": [
        "العناية الذاتية",
        "تحمل المسؤولية",
        "التنظيم وترتيب الأغراض"
    ]
}

# --- إدارة البيانات (Session State) ---
if 'students' not in st.session_state:
    st.session_state.students = {} # قاموس لتخزين بيانات الطلاب

# --- الواجهة الجانبية (القائمة) ---
with st.sidebar:
    st.title("لوحة التحكم ⚙️")
    menu = st.radio("اختر الإجراء:", ["إضافة تلميذ", "تقييم تلميذ", "التقرير والتحليل"])
    
    st.markdown("---")
    st.info("نظام تقييم المرحلة التحضيرية (5-6 سنوات)")

# --- الصفحة 1: إضافة تلميذ ---
if menu == "إضافة تلميذ":
    st.title("📂 إضافة تلميذ جديد")
    with st.form("add_student_form"):
        name = st.text_input("اسم التلميذ الرباعي:")
        age = st.number_input("العمر (سنوات):", min_value=4, max_value=7, value=5)
        class_name = st.text_input("الفوج/القسم:")
        submitted = st.form_submit_button("حفظ البيانات")
        
        if submitted and name:
            if name not in st.session_state.students:
                # إنشاء سجل فارغ للطالب
                st.session_state.students[name] = {
                    "info": {"age": age, "class": class_name},
                    "scores": {}
                }
                st.success(f"تمت إضافة التلميذ: {name} بنجاح!")
            else:
                st.warning("هذا الاسم مسجل مسبقاً!")

# --- الصفحة 2: تقييم تلميذ ---
elif menu == "تقييم تلميذ":
    st.title("📝 تقييم المهارات")
    
    student_names = list(st.session_state.students.keys())
    
    if not student_names:
        st.warning("الرجاء إضافة تلاميذ أولاً من القائمة الجانبية.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", student_names)
        
        st.write(f"### تقييم الطالب: {selected_student}")
        st.info("مقياس التقييم: 1 (ضعيف جداً) - 5 (متقن/مستقل)")
        
        # نموذج التقييم
        with st.form("assessment_form"):
            scores = {}
            
            # إنشاء تبويبات لكل محور لترتيب الصفحة
            tabs = st.tabs(list(ASSESSMENT_CRITERIA.keys()))
            
            for i, (domain, skills) in enumerate(ASSESSMENT_CRITERIA.items()):
                with tabs[i]:
                    st.subheader(domain)
                    domain_scores = {}
                    for skill in skills:
                        # محاولة استرجاع تقييم سابق إن وجد
                        current_val = st.session_state.students[selected_student]["scores"].get(domain, {}).get(skill, 3)
                        val = st.slider(f"{skill}", 1, 5, current_val, key=f"{selected_student}_{skill}")
                        domain_scores[skill] = val
                    scores[domain] = domain_scores
            
            save_assessment = st.form_submit_button("حفظ التقييم")
            
            if save_assessment:
                st.session_state.students[selected_student]["scores"] = scores
                st.success("تم حفظ التقييم بنجاح! انتقل لقسم التقارير لرؤية النتائج.")

# --- الصفحة 3: التقرير والتحليل ---
elif menu == "التقرير والتحليل":
    st.title("📊 التقرير التحليلي الشامل")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("لا يوجد بيانات لعرضها.")
    else:
        selected_student = st.selectbox("اختر التلميذ لعرض تقريره:", student_names)
        student_data = st.session_state.students[selected_student]
        
        if not student_data["scores"]:
            st.warning("لم يتم تقييم هذا التلميذ بعد.")
        else:
            # --- 1. حساب المتوسطات ---
            scores_data = student_data["scores"]
            domain_averages = {}
            
            for domain, skills in scores_data.items():
                avg = sum(skills.values()) / len(skills)
                domain_averages[domain] = avg

            # --- 2. الرسم البياني (الرادار) ---
            st.subheader("🕸️ خريطة الكفاءات (Spider Chart)")
            
            categories = list(domain_averages.keys())
            values = list(domain_averages.values())
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=selected_student
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 5])
                ),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # --- 3. التحليل النصي التفصيلي ---
            st.subheader("📑 التحليل التفصيلي ونقاط القوة/الضعف")
            
            col1, col2 = st.columns(2)
            
            strengths = []
            improvements = []
            
            for domain, skills in scores_data.items():
                for skill, score in skills.items():
                    if score >= 4:
                        strengths.append(f"{domain}: {skill}")
                    elif score <= 2:
                        improvements.append(f"{domain}: {skill}")
            
            with col1:
                st.success("**🌟 نقاط القوة والتميز:**")
                if strengths:
                    for s in strengths: st.write(f"- {s}")
                else:
                    st.write("لا توجد نقاط قوة بارزة جداً حالياً.")
                    
            with col2:
                st.error("**🔧 مجالات تحتاج إلى دعم وتطوير:**")
                if improvements:
                    for imp in improvements: st.write(f"- {imp}")
                else:
                    st.write("مستوى الطالب متوازن وجيد بشكل عام.")

            # --- 4. التوصيات الآلية ---
            st.markdown("---")
            st.subheader("💡 التوصيات المقترحة")
            
            general_avg = sum(values) / len(values)
            if general_avg >= 4:
                st.info("الطفل يظهر استعداداً ممتازاً للمدرسة. يُنصح بإدراج أنشطة إثرائية متقدمة.")
            elif general_avg >= 3:
                st.warning("الطفل في المسار الصحيح، لكنه يحتاج لتعزيز المهارات التي حصل فيها على تقييم أقل من 3.")
            else:
                st.error("يحتاج الطفل إلى خطة تدخل فردية مكثفة، يرجى مراجعة الأخصائي أو تكثيف التمارين المنزلية.")

            # زر محاكاة الطباعة
            st.download_button("تحميل التقرير (PDF - محاكاة)", data="Report Data", file_name=f"report_{selected_student}.txt")
