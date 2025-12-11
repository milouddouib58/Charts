import streamlit as st
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام التقييم الشامل المطور", layout="wide", page_icon="🎓")

# تنسيق CSS احترافي (لدعم اللغة العربية وتجميل الواجهة)
st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    .stRadio, .stSelectbox, .stTextInput, .stNumberInput, .stDateInput, .stTextArea {direction: rtl; text-align: right;}
    div[role="radiogroup"] {flex-direction: row-reverse; justify-content: flex-end;}
    h1, h2, h3, h4, p, div, label, li {text-align: right;}
    .stProgress > div > div > div > div {background-color: #4CAF50;}
</style>
""", unsafe_allow_html=True)

# --- ثوابت التقييم ---
RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]
RATING_MAP = {"غير مكتسب": 0, "في طريق الاكتساب": 1, "مكتسب": 2}

# --- قاعدة بيانات المهارات (دمج المعايير من الصورة + المهارات الإضافية) ---
ASSESSMENT_CRITERIA = {
    "1. المناهج الدراسية الأساسية": {
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
    },
    "2. الوظائف التنفيذية (الذهنية)": {
        "الانتباه والذاكرة": [
            "التركيز على نشاط لمدة 15 دقيقة",
            "إكمال المهمة للنهاية دون تشتت",
            "تذكر تعليمات من 3 خطوات",
            "تذكر أحداث قصة قصيرة"
        ],
        "المرونة والتفكير": [
            "الانتقال بين الأنشطة بسلاسة",
            "تقبل التغيير في الروتين",
            "إدراك التسلسل المنطقي للأحداث"
        ]
    },
    "3. الكفاءة الاجتماعية والعاطفية": {
        "التطور الشخصي والاجتماعي": [
            "التعبير عن المشاعر بدقة",
            "الثقة بالنفس والمبادرة",
            "المشاركة في اللعب الجماعي",
            "احترام الدور والقوانين",
            "التحكم في الانفعالات"
        ]
    },
    "4. المهارات الحركية والاستقلالية": {
        "النمو الحركي والاستقلالية": [
            "استخدام المقص بدقة",
            "تلوين داخل الحدود",
            "التوازن (الوقوف على قدم واحدة)",
            "التقاط الكرة ورميها",
            "الاعتماد على النفس (لبس، حمام، ترتيب)"
        ]
    }
}

# --- إدارة البيانات (تخزين مؤقت) ---
if 'students' not in st.session_state:
    st.session_state.students = {}

# --- القائمة الجانبية ---
with st.sidebar:
    st.title("نظام التقييم المتكامل")
    menu = st.radio("القائمة:", ["سجل التلاميذ", "التقييم المفصل", "التقرير التشخيصي"], index=1)
    st.divider()
    st.info("💡 نصيحة: استخدم التبويبات في صفحة التقييم للتنقل بين المواد الدراسية والمهارات السلوكية.")

# ==========================================
# 1. سجل التلاميذ
# ==========================================
if menu == "سجل التلاميذ":
    st.header("📂 إدارة ملفات التلاميذ")
    with st.form("add_student"):
        name = st.text_input("اسم التلميذ:")
        birth_date = st.date_input("تاريخ الميلاد:")
        notes = st.text_area("ملاحظات أولية (صحيّة/عائلية):")
        submitted = st.form_submit_button("فتح ملف جديد")
        
        if submitted and name:
            if name not in st.session_state.students:
                st.session_state.students[name] = {
                    "info": {"dob": str(birth_date), "notes": notes},
                    "evaluations": {}
                }
                st.success(f"تم فتح ملف للتلميذ: {name}")
            else:
                st.warning("الملف موجود مسبقاً")

# ==========================================
# 2. التقييم المفصل (الواجهة السهلة للمحتوى العميق)
# ==========================================
elif menu == "التقييم المفصل":
    st.header("📝 التقييم المستمر")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("الرجاء تسجيل تلاميذ أولاً من القائمة الجانبية.")
    else:
        selected_student = st.selectbox("ملف التلميذ:", student_names)
        current_evals = st.session_state.students[selected_student]["evaluations"]
        
        st.markdown("---")
        
        with st.form("comprehensive_eval"):
            # إنشاء تبويبات للمحاور الرئيسية (المناهج، الوظائف الذهنية، إلخ)
            main_tabs = st.tabs([k.split(". ")[1] for k in ASSESSMENT_CRITERIA.keys()])
            
            new_evals_data = {}
            
            for i, (main_domain, sub_domains) in enumerate(ASSESSMENT_CRITERIA.items()):
                with main_tabs[i]:
                    domain_data = {}
                    for sub_domain, skills in sub_domains.items():
                        st.subheader(f"🔹 {sub_domain}")
                        sub_domain_data = {}
                        for skill in skills:
                            # استرجاع القيمة السابقة أو البدء بـ "في طريق الاكتساب" (1)
                            prev_val_idx = 1
                            if main_domain in current_evals:
                                if sub_domain in current_evals[main_domain]:
                                    val_score = current_evals[main_domain][sub_domain].get(skill, 1)
                                    prev_val_idx = val_score 
                            
                            # واجهة الاختيار (Radio Buttons)
                            choice = st.radio(
                                skill, 
                                RATING_OPTIONS, 
                                index=prev_val_idx, 
                                key=f"{selected_student}_{skill}", 
                                horizontal=True
                            )
                            sub_domain_data[skill] = RATING_MAP[choice]
                            st.write("") # مسافة صغيرة
                        
                        domain_data[sub_domain] = sub_domain_data
                        st.divider()
                    new_evals_data[main_domain] = domain_data
            
            save = st.form_submit_button("حفظ التقييم الشامل", type="primary")
            if save:
                st.session_state.students[selected_student]["evaluations"] = new_evals_data
                st.toast("تم حفظ التقييم بنجاح!", icon="✅")

# ==========================================
# 3. التقرير التشخيصي (التحليل العميق)
# ==========================================
elif menu == "التقرير التشخيصي":
    st.header("📊 بطاقة التقييم التحليلي")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("لا يوجد بيانات لعرضها.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", student_names)
        data = st.session_state.students[selected_student]["evaluations"]
        
        if not data:
            st.error("لم يتم إجراء تقييم لهذا التلميذ بعد.")
        else:
            # --- 1. الحسابات العامة ---
            total_points = 0
            max_possible = 0
            weaknesses = []
            
            for main_domain, sub_domains in data.items():
                for sub, skills in sub_domains.items():
                    for skill, score in skills.items():
                        total_points += score
                        max_possible += 2
                        if score == 0: # 0 = غير مكتسب
                            weaknesses.append(f"[{sub}] {skill}")

            readiness_score = (total_points / max_possible) * 100 if max_possible > 0 else 0
            
            # --- 2. العرض البياني العام ---
            col_score, col_text = st.columns([1, 3])
            with col_score:
                st.metric("نسبة التحكم العامة", f"{readiness_score:.1f}%")
            with col_text:
                st.progress(readiness_score / 100)
                if readiness_score > 75:
                    st.success("مستوى ممتاز: التلميذ مستعد للمرحلة الابتدائية.")
                elif readiness_score > 50:
                    st.warning("مستوى متوسط: يحتاج لبعض الدعم في النقاط غير المكتسبة.")
                else:
                    st.error("مستوى يحتاج لدعم: يجب تكثيف الجهود التربوية.")
            
            st.divider()

            # --- 3. تفاصيل المحاور (المواد الدراسية vs المهارات) ---
            st.subheader("تحليل المواد والمهارات")
            
            for main_domain, sub_domains in data.items():
                with st.expander(main_domain, expanded=True):
                    for sub, skills in sub_domains.items():
                        pts = sum(skills.values())
                        mx = len(skills) * 2
                        pc = (pts / mx) * 100 if mx > 0 else 0
                        
                        # شريط تقدم صغير لكل مادة/مجال فرعي
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.write(f"**{sub}**")
                            st.progress(pc / 100)
                        with c2:
                            st.write(f"{pc:.0f}%")

            # --- 4. التنبيهات (النقاط غير المكتسبة) ---
            st.divider()
            st.subheader("🚨 المهارات التي تتطلب معالجة (غير مكتسبة)")
            
            if weaknesses:
                for w in weaknesses:
                    st.error(f"❌ {w}")
            else:
                st.success("🎉 لا توجد مهارات غير مكتسبة. أداء ممتاز!")

            # --- 5. زر التصدير ---
            report_text = f"""
            تقرير التقييم للتلميذ: {selected_student}
            ----------------------------------------
            نسبة التحكم العامة: {readiness_score:.1f}%
            
            المهارات غير المكتسبة (تتطلب معالجة):
            {chr(10).join(['- ' + w for w in weaknesses])}
            
            تم التقييم عبر النظام الرقمي
            """
            st.download_button("تحميل التقرير النصي", report_text, file_name=f"Report_{selected_student}.txt")
