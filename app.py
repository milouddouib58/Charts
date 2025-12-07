import streamlit as st
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام التقييم الثلاثي", layout="wide", page_icon="📝")

# تنسيق CSS للكتابة من اليمين لليسار وتحسين شكل الأزرار
st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    .stRadio, .stSelectbox, .stTextInput, .stNumberInput {direction: rtl; text-align: right;}
    div[role="radiogroup"] {flex-direction: row-reverse; justify-content: flex-end;}
    h1, h2, h3, p, div, label {text-align: right;}
    /* تلوين خيارات التقييم لسهولة التمييز */
    div[data-testid="stMarkdownContainer"] p {font-size: 16px;}
</style>
""", unsafe_allow_html=True)

# --- ثوابت التقييم ---
# خيارات التقييم الثلاثة
RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]

# تحويل الخيارات اللفظية إلى أرقام للتحليل (0، 1، 2)
RATING_MAP = {
    "غير مكتسب": 0,
    "في طريق الاكتساب": 1,
    "مكتسب": 2
}

# عكس القاموس للتقارير
REVERSE_MAP = {v: k for k, v in RATING_MAP.items()}

# معايير التقييم
ASSESSMENT_CRITERIA = {
    "اللغة العربية": [
        "يسمي الحروف الهجائية المدروسة",
        "يميز صواتياً بين الحروف",
        "يمسك القلم بطريقة صحيحة",
        "ينسخ كلمات وجمل بسيطة"
    ],
    "الرياضيات": [
        "يعد شفوياً إلى 20",
        "يربط العدد بالمعدود",
        "يميز الأشكال الهندسية",
        "يصنف الأشياء حسب خاصية معينة"
    ],
    "التربية الإسلامية والمدنية": [
        "يحفظ قصار السور المقررة",
        "يلقي التحية ويردها",
        "يحافظ على نظافة مكانه",
        "يتعاون مع زملائه"
    ],
    "التربية العلمية": [
        "يسمي أعضاء جسم الإنسان",
        "يميز بين الحواس الخمس",
        "يعرف الحيوانات الأليفة والمتوحشة",
        "يدرك تعاقب الليل والنهار"
    ]
}

# --- إدارة البيانات (Session State) ---
if 'students' not in st.session_state:
    st.session_state.students = {}

# --- القائمة الجانبية ---
with st.sidebar:
    st.title("القائمة الرئيسية")
    menu = st.radio("العمليات:", ["تسجيل تلميذ جديد", "دفتر التقييم", "عرض النتائج"], index=1)
    st.markdown("---")
    st.caption("نظام التقييم بمقياس: مكتسب / في طريق الاكتساب / غير مكتسب")

# ==========================================
# 1. صفحة تسجيل تلميذ
# ==========================================
if menu == "تسجيل تلميذ جديد":
    st.header("➕ إضافة تلميذ جديد")
    with st.form("new_student"):
        name = st.text_input("اسم التلميذ الثلاثي:")
        group = st.selectbox("الفوج:", ["التحضيري 1", "التحضيري 2"])
        submit = st.form_submit_button("حفظ")
        
        if submit and name:
            if name not in st.session_state.students:
                st.session_state.students[name] = {"group": group, "evaluations": {}}
                st.success(f"تم تسجيل التلميذ: {name}")
            else:
                st.warning("هذا الاسم موجود مسبقاً")

# ==========================================
# 2. صفحة التقييم (الواجهة الجديدة)
# ==========================================
elif menu == "دفتر التقييم":
    st.header("📝 تقييم المهارات")
    
    students_list = list(st.session_state.students.keys())
    
    if not students_list:
        st.info("قم بإضافة تلاميذ أولاً.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", students_list)
        st.divider()
        
        # استرجاع التقييمات السابقة إن وجدت
        student_evals = st.session_state.students[selected_student]["evaluations"]
        
        with st.form("evaluation_form"):
            # عرض المواد في تبويبات
            tabs = st.tabs(list(ASSESSMENT_CRITERIA.keys()))
            
            new_evals = {}
            
            for i, (subject, skills) in enumerate(ASSESSMENT_CRITERIA.items()):
                with tabs[i]:
                    st.subheader(f"ميدان: {subject}")
                    subject_scores = {}
                    for skill in skills:
                        # تحديد القيمة الافتراضية (إذا كان مقيماً سابقاً نضع تقييمه، وإلا نبدأ بـ "في طريق الاكتساب")
                        default_val_index = 1 # الافتراضي: في طريق الاكتساب
                        if subject in student_evals and skill in student_evals[subject]:
                            prev_score = student_evals[subject][skill]
                            # البحث عن الاندكس بناء على القيمة المخزنة
                            if prev_score == 0: default_val_index = 0
                            elif prev_score == 2: default_val_index = 2
                        
                        # --- هنا التغيير الجوهري: استخدام Radio Buttons ---
                        val = st.radio(
                            label=skill,
                            options=RATING_OPTIONS,
                            index=default_val_index,
                            key=f"{selected_student}_{skill}",
                            horizontal=True # جعل الخيارات أفقية بجانب بعضها
                        )
                        subject_scores[skill] = RATING_MAP[val]
                        st.markdown("---") # خط فاصل خفيف بين كل مهارة
                    
                    new_evals[subject] = subject_scores
            
            save_btn = st.form_submit_button("حفظ التقييم في الدفتر", type="primary")
            
            if save_btn:
                st.session_state.students[selected_student]["evaluations"] = new_evals
                st.success(f"تم تحديث تقييم التلميذ {selected_student} بنجاح ✅")

# ==========================================
# 3. صفحة عرض النتائج والتحليل
# ==========================================
elif menu == "عرض النتائج":
    st.header("📊 تحليل مستوى التلميذ")
    
    students_list = list(st.session_state.students.keys())
    if not students_list:
        st.warning("لا توجد بيانات.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", students_list)
        data = st.session_state.students[selected_student]["evaluations"]
        
        if not data:
            st.warning("لم يتم تقييم هذا التلميذ بعد.")
        else:
            # 1. إحصائيات عامة
            total_skills = 0
            acquired = 0
            in_progress = 0
            not_acquired = 0
            
            for subject, skills in data.items():
                for skill, score in skills.items():
                    total_skills += 1
                    if score == 2: acquired += 1
                    elif score == 1: in_progress += 1
                    else: not_acquired += 1
            
            # عرض بطاقات ملخصة بالأعلى
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ مكتسب", f"{acquired}", f"{(acquired/total_skills)*100:.1f}%")
            col2.metric("⚠️ في طريق الاكتساب", f"{in_progress}", delta_color="off")
            col3.metric("❌ غير مكتسب", f"{not_acquired}", delta_color="inverse")
            
            st.divider()

            # 2. الرسم البياني (بسيط وبدون مكتبات خارجية معقدة)
            st.subheader("توزيع الكفاءات حسب المواد")
            
            chart_data = []
            for subject, skills in data.items():
                # نحسب نسبة الاكتساب في كل مادة (مجموع النقاط / المجموع الكلي المحتمل)
                # مكتسب=2 نقطة، المجموع المحتمل = عدد المهارات * 2
                points = sum(skills.values())
                max_points = len(skills) * 2
                percentage = (points / max_points) * 100 if max_points > 0 else 0
                chart_data.append({"المادة": subject, "نسبة التحكم (%)": percentage})
            
            df_chart = pd.DataFrame(chart_data)
            st.bar_chart(df_chart, x="المادة", y="نسبة التحكم (%)")

            # 3. جدول التفاصيل (ماذا ينقص التلميذ؟)
            st.subheader("🔍 تفاصيل المهارات غير المكتسبة")
            found_issues = False
            for subject, skills in data.items():
                weak_skills = [k for k, v in skills.items() if v == 0] # 0 يعني غير مكتسب
                if weak_skills:
                    found_issues = True
                    with st.expander(f"تنبيهات في مادة: {subject}", expanded=True):
                        for ws in weak_skills:
                            st.error(f"- {ws}")
            
            if not found_issues:
                st.success("ما شاء الله! التلميذ لا يعاني من تعثرات 'غير مكتسبة' في المهارات المرصودة.")

