import streamlit as st
import pandas as pd
from datetime import datetime

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
    .stTabs [data-baseweb="tab-list"] {justify-content: center;}
    .stTabs [data-baseweb="tab"] {height: 50px;}
</style>
""", unsafe_allow_html=True)

# --- ثوابت التقييم ---
RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]
RATING_MAP = {"غير مكتسب": 0, "في طريق الاكتساب": 1, "مكتسب": 2}
RATING_COLORS = {"غير مكتسب": "#FF4B4B", "في طريق الاكتساب": "#FFA500", "مكتسب": "#4CAF50"}

# --- قاعدة بيانات المهارات (مقسمة إلى قسمين) ---
# 1. المواد الدراسية الأساسية
ACADEMIC_SUBJECTS = {
    "اللغة العربية": [
        "يسمي الحروف الهجائية المدروسة",
        "يميز صواتياً بين الحروف",
        "يمسك القلم بطريقة صحيحة",
        "ينسخ كلمات وجمل بسيطة",
        "يقرأ كلمات بسيطة",
        "يكتب اسمه بشكل صحيح"
    ],
    "الرياضيات": [
        "يعد شفوياً إلى 20",
        "يربط العدد بالمعدود",
        "يميز الأشكال الهندسية",
        "يصنف الأشياء حسب خاصية معينة",
        "يحل مسائل جمع بسيطة",
        "يتعرف على الأعداد حتى 10"
    ],
    "التربية الإسلامية والمدنية": [
        "يحفظ قصار السور المقررة",
        "يلقي التحية ويردها",
        "يحافظ على نظافة مكانه",
        "يتعاون مع زملائه",
        "يعرف أركان الإسلام",
        "يحترم المعلم والزملاء"
    ],
    "التربية العلمية": [
        "يسمي أعضاء جسم الإنسان",
        "يميز بين الحواس الخمس",
        "يعرف الحيوانات الأليفة والمتوحشة",
        "يدرك تعاقب الليل والنهار",
        "يتعرف على الفصول الأربعة",
        "يميز بين النباتات والحيوانات"
    ],
    "اللغة الفرنسية": [
        "يتعرف على الحروف الفرنسية",
        "ينطق كلمات بسيطة",
        "يحيي بالفرنسية",
        "يعد حتى 10 بالفرنسية"
    ]
}

# 2. المهارات السلوكية والتنموية
BEHAVIORAL_SKILLS = {
    "الوظائف التنفيذية (الذهنية)": {
        "الانتباه والذاكرة": [
            "التركيز على نشاط لمدة 15 دقيقة",
            "إكمال المهمة للنهاية دون تشتت",
            "تذكر تعليمات من 3 خطوات",
            "تذكر أحداث قصة قصيرة",
            "ينتبه للتفاصيل المهمة"
        ],
        "المرونة والتفكير": [
            "الانتقال بين الأنشطة بسلاسة",
            "تقبل التغيير في الروتين",
            "إدراك التسلسل المنطقي للأحداث",
            "حل المشكلات البسيطة",
            "يطرح أسئلة ذكية"
        ]
    },
    "الكفاءة الاجتماعية والعاطفية": {
        "التطور الشخصي والاجتماعي": [
            "التعبير عن المشاعر بدقة",
            "الثقة بالنفس والمبادرة",
            "المشاركة في اللعب الجماعي",
            "احترام الدور والقوانين",
            "التحكم في الانفعالات",
            "تقدير الذات والإيجابية"
        ],
        "المهارات العاطفية": [
            "التعاطف مع الآخرين",
            "التعبير عن الحاجة للمساعدة",
            "تحمل المسؤولية",
            "التكيف مع المواقف الجديدة"
        ]
    },
    "المهارات الحركية والاستقلالية": {
        "النمو الحركي": [
            "استخدام المقص بدقة",
            "تلوين داخل الحدود",
            "التوازن (الوقوف على قدم واحدة)",
            "التقاط الكرة ورميها",
            "القفز على قدمين معاً"
        ],
        "الاستقلالية": [
            "الاعتماد على النفس (لبس، حمام، ترتيب)",
            "تناول الطعام بنفسه",
            "ترتيب الأدوات المدرسية",
            "العناية بالنظافة الشخصية"
        ]
    }
}

# --- إدارة البيانات (تخزين مؤقت) ---
if 'students' not in st.session_state:
    st.session_state.students = {}

# --- الدوال المساعدة ---
def calculate_scores(evaluations):
    """حساب النقاط والتقييمات"""
    if not evaluations:
        return {
            "academic_total": 0,
            "academic_max": 0,
            "academic_percentage": 0,
            "behavioral_total": 0,
            "behavioral_max": 0,
            "behavioral_percentage": 0,
            "overall_total": 0,
            "overall_max": 0,
            "overall_percentage": 0,
            "weaknesses": [],
            "strengths": []
        }
    
    academic_total = 0
    academic_max = 0
    behavioral_total = 0
    behavioral_max = 0
    weaknesses = []
    strengths = []
    
    # حساب المواد الدراسية
    if "academic" in evaluations:
        for subject, skills in evaluations["academic"].items():
            for skill, score in skills.items():
                academic_total += score
                academic_max += 2
                if score == 0:
                    weaknesses.append(f"[المواد الدراسية - {subject}] {skill}")
                elif score == 2:
                    strengths.append(f"[المواد الدراسية - {subject}] {skill}")
    
    # حساب المهارات السلوكية
    if "behavioral" in evaluations:
        for category, domains in evaluations["behavioral"].items():
            for domain, skills in domains.items():
                for skill, score in skills.items():
                    behavioral_total += score
                    behavioral_max += 2
                    if score == 0:
                        weaknesses.append(f"[المهارات - {category}/{domain}] {skill}")
                    elif score == 2:
                        strengths.append(f"[المهارات - {category}/{domain}] {skill}")
    
    overall_total = academic_total + behavioral_total
    overall_max = academic_max + behavioral_max
    
    academic_percentage = (academic_total / academic_max * 100) if academic_max > 0 else 0
    behavioral_percentage = (behavioral_total / behavioral_max * 100) if behavioral_max > 0 else 0
    overall_percentage = (overall_total / overall_max * 100) if overall_max > 0 else 0
    
    return {
        "academic_total": academic_total,
        "academic_max": academic_max,
        "academic_percentage": academic_percentage,
        "behavioral_total": behavioral_total,
        "behavioral_max": behavioral_max,
        "behavioral_percentage": behavioral_percentage,
        "overall_total": overall_total,
        "overall_max": overall_max,
        "overall_percentage": overall_percentage,
        "weaknesses": weaknesses,
        "strengths": strengths
    }

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
                                      ["تمهيدي", "روضة أولى", "روضة ثانية", "صف أول ابتدائي"])
            
            notes = st.text_area("ملاحظات أولية (صحيّة/عائلية/أخرى):", height=100)
            
            submitted = st.form_submit_button("📥 حفظ بيانات التلميذ", type="primary")
            
            if submitted and name:
                if name.strip() == "":
                    st.error("الرجاء إدخال اسم التلميذ")
                elif name in st.session_state.students:
                    st.warning(f"التلميذ '{name}' مسجل مسبقاً")
                else:
                    st.session_state.students[name] = {
                        "info": {
                            "dob": str(birth_date),
                            "gender": gender,
                            "class_level": class_level,
                            "notes": notes,
                            "registration_date": datetime.now().strftime("%Y-%m-%d")
                        },
                        "evaluations": {}
                    }
                    st.success(f"✅ تم تسجيل التلميذ: {name}")
                    st.balloons()
    
    with col2:
        st.subheader("قائمة التلاميذ المسجلين")
        if st.session_state.students:
            for student_name in st.session_state.students.keys():
                with st.expander(f"👤 {student_name}"):
                    info = st.session_state.students[student_name]["info"]
                    st.caption(f"**المستوى:** {info.get('class_level', 'غير محدد')}")
                    st.caption(f"**تاريخ الميلاد:** {info.get('dob', 'غير محدد')}")
                    st.caption(f"**الجنس:** {info.get('gender', 'غير محدد')}")
                    
                    # زر حذف التلميذ
                    if st.button(f"حذف", key=f"del_{student_name}"):
                        del st.session_state.students[student_name]
                        st.rerun()
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
        st.info("انتقل إلى القائمة الجانبية ← 'سجل التلاميذ' لإضافة تلاميذ جدد.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", student_names)
        
        # معلومات التلميذ
        if selected_student:
            student_info = st.session_state.students[selected_student]["info"]
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("المستوى", student_info.get("class_level", "غير محدد"))
            with col_info2:
                st.metric("الجنس", student_info.get("gender", "غير محدد"))
            with col_info3:
                st.metric("تاريخ الميلاد", student_info.get("dob", "غير محدد"))
        
        st.markdown("---")
        
        with st.form("academic_evaluation"):
            st.subheader("📋 تقييم المواد الدراسية")
            
            # الحصول على التقييمات السابقة إن وجدت
            current_evals = st.session_state.students[selected_student].get("evaluations", {})
            academic_evals = current_evals.get("academic", {})
            
            new_academic_data = {}
            
            # إنشاء تبويبات للمواد الدراسية
            academic_tabs = st.tabs(list(ACADEMIC_SUBJECTS.keys()))
            
            for i, (subject, skills) in enumerate(ACADEMIC_SUBJECTS.items()):
                with academic_tabs[i]:
                    st.markdown(f"### {subject}")
                    subject_data = {}
                    
                    for skill in skills:
                        # استرجاع القيمة السابقة أو البدء بـ "في طريق الاكتساب" (1)
                        prev_val_idx = 1
                        if subject in academic_evals:
                            prev_val_idx = academic_evals[subject].get(skill, 1)
                        
                        # واجهة الاختيار (Radio Buttons)
                        col_label, col_radio = st.columns([3, 2])
                        with col_label:
                            st.markdown(f"**{skill}**")
                        with col_radio:
                            choice = st.radio(
                                "",
                                RATING_OPTIONS,
                                index=prev_val_idx,
                                key=f"academic_{selected_student}_{subject}_{skill}",
                                horizontal=True,
                                label_visibility="collapsed"
                            )
                        
                        subject_data[skill] = RATING_MAP[choice]
                    
                    new_academic_data[subject] = subject_data
                    st.markdown("---")
            
            # قسم الملاحظات
            st.subheader("ملاحظات إضافية على المواد الدراسية")
            academic_notes = st.text_area("اكتب ملاحظاتك حول أداء التلميذ في المواد الدراسية:", 
                                         height=100,
                                         value=current_evals.get("academic_notes", ""))
            
            col_save, col_clear = st.columns([3, 1])
            with col_save:
                save_academic = st.form_submit_button("💾 حفظ تقييم المواد الدراسية", type="primary")
            with col_clear:
                if st.form_submit_button("مسح النموذج"):
                    st.rerun()
            
            if save_academic:
                # تحديث البيانات
                if "evaluations" not in st.session_state.students[selected_student]:
                    st.session_state.students[selected_student]["evaluations"] = {}
                
                st.session_state.students[selected_student]["evaluations"]["academic"] = new_academic_data
                st.session_state.students[selected_student]["evaluations"]["academic_notes"] = academic_notes
                st.session_state.students[selected_student]["evaluations"]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                st.success(f"✅ تم حفظ تقييم المواد الدراسية للتلميذ: {selected_student}")
                st.toast("تم الحفظ بنجاح!", icon="✅")

# ==========================================
# 3. تقييم المهارات السلوكية
# ==========================================
elif menu == "تقييم المهارات السلوكية":
    st.header("🧠 تقييم المهارات السلوكية والتنموية")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("⚠️ الرجاء تسجيل تلاميذ أولاً من قسم 'سجل التلاميذ'.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", student_names)
        
        st.markdown("---")
        
        with st.form("behavioral_evaluation"):
            st.subheader("📊 تقييم المهارات السلوكية والتنموية")
            
            # الحصول على التقييمات السابقة إن وجدت
            current_evals = st.session_state.students[selected_student].get("evaluations", {})
            behavioral_evals = current_evals.get("behavioral", {})
            
            new_behavioral_data = {}
            
            # إنشاء تبويبات للمجالات السلوكية
            behavioral_tabs = st.tabs(list(BEHAVIORAL_SKILLS.keys()))
            
            for i, (main_category, sub_categories) in enumerate(BEHAVIORAL_SKILLS.items()):
                with behavioral_tabs[i]:
                    st.markdown(f"### {main_category}")
                    category_data = {}
                    
                    for sub_category, skills in sub_categories.items():
                        st.markdown(f"#### {sub_category}")
                        sub_category_data = {}
                        
                        for skill in skills:
                            # استرجاع القيمة السابقة أو البدء بـ "في طريق الاكتساب" (1)
                            prev_val_idx = 1
                            if (main_category in behavioral_evals and 
                                sub_category in behavioral_evals[main_category]):
                                prev_val_idx = behavioral_evals[main_category][sub_category].get(skill, 1)
                            
                            # واجهة الاختيار (Radio Buttons)
                            col_label, col_radio = st.columns([3, 2])
                            with col_label:
                                st.markdown(f"**{skill}**")
                            with col_radio:
                                choice = st.radio(
                                    "",
                                    RATING_OPTIONS,
                                    index=prev_val_idx,
                                    key=f"behavioral_{selected_student}_{main_category}_{sub_category}_{skill}",
                                    horizontal=True,
                                    label_visibility="collapsed"
                                )
                            
                            sub_category_data[skill] = RATING_MAP[choice]
                        
                        category_data[sub_category] = sub_category_data
                        st.markdown("---")
                    
                    new_behavioral_data[main_category] = category_data
            
            # قسم الملاحظات
            st.subheader("ملاحظات إضافية على المهارات السلوكية")
            behavioral_notes = st.text_area("اكتب ملاحظاتك حول أداء التلميذ في المهارات السلوكية:", 
                                           height=100,
                                           value=current_evals.get("behavioral_notes", ""))
            
            col_save, col_clear = st.columns([3, 1])
            with col_save:
                save_behavioral = st.form_submit_button("💾 حفظ تقييم المهارات السلوكية", type="primary")
            with col_clear:
                if st.form_submit_button("مسح النموذج"):
                    st.rerun()
            
            if save_behavioral:
                # تحديث البيانات
                if "evaluations" not in st.session_state.students[selected_student]:
                    st.session_state.students[selected_student]["evaluations"] = {}
                
                st.session_state.students[selected_student]["evaluations"]["behavioral"] = new_behavioral_data
                st.session_state.students[selected_student]["evaluations"]["behavioral_notes"] = behavioral_notes
                st.session_state.students[selected_student]["evaluations"]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                st.success(f"✅ تم حفظ تقييم المهارات السلوكية للتلميذ: {selected_student}")
                st.toast("تم الحفظ بنجاح!", icon="✅")

# ==========================================
# 4. التقرير التشخيصي
# ==========================================
elif menu == "التقرير التشخيصي":
    st.header("📈 التقرير التشخيصي الشامل")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("لا يوجد بيانات لعرضها.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", student_names)
        data = st.session_state.students[selected_student].get("evaluations", {})
        
        if not data or ("academic" not in data and "behavioral" not in data):
            st.error("لم يتم إجراء تقييم لهذا التلميذ بعد.")
            st.info("الرجاء الذهاب إلى قسم 'تقييم المواد الدراسية' أو 'تقييم المهارات السلوكية'")
        else:
            # حساب النتائج
            scores = calculate_scores(data)
            
            # --- 1. بطاقة النتائج العامة ---
            st.subheader("🎯 النتائج العامة")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("المواد الدراسية", f"{scores['academic_percentage']:.1f}%")
                st.progress(scores['academic_percentage'] / 100)
            with col2:
                st.metric("المهارات السلوكية", f"{scores['behavioral_percentage']:.1f}%")
                st.progress(scores['behavioral_percentage'] / 100)
            with col3:
                st.metric("المجموع الكلي", f"{scores['overall_percentage']:.1f}%")
                st.progress(scores['overall_percentage'] / 100)
            
            # تقييم عام
            st.markdown("### 📝 التقييم العام")
            overall_score = scores['overall_percentage']
            
            if overall_score >= 85:
                st.success("""
                **ممتاز!** التلميذ يظهر استعداداً ممتازاً للمرحلة الابتدائية في جميع المجالات.
                - المواد الدراسية: متقدم
                - المهارات السلوكية: ممتازة
                """)
            elif overall_score >= 70:
                st.info("""
                **جيد جداً!** التلميذ يظهر استعداداً جيداً مع بعض المجالات التي تحتاج دعم.
                - المواد الدراسية: جيد
                - المهارات السلوكية: جيدة
                """)
            elif overall_score >= 50:
                st.warning("""
                **مقبول!** التلميذ يحتاج إلى دعم إضافي في بعض المجالات.
                - المواد الدراسية: يحتاج تحسين
                - المهارات السلوكية: تحتاج متابعة
                """)
            else:
                st.error("""
                **يحتاج دعم!** التلميذ يحتاج إلى برنامج دعم مكثف.
                - المواد الدراسية: ضعيف
                - المهارات السلوكية: تحتاج تدخل
                """)
            
            st.markdown("---")
            
            # --- 2. تحليل المواد الدراسية ---
            if "academic" in data:
                st.subheader("📚 تحليل المواد الدراسية")
                
                academic_cols = st.columns(len(ACADEMIC_SUBJECTS))
                
                for idx, (subject, skills) in enumerate(ACADEMIC_SUBJECTS.items()):
                    with academic_cols[idx]:
                        st.markdown(f"**{subject}**")
                        
                        if subject in data.get("academic", {}):
                            subject_data = data["academic"][subject]
                            total_score = sum(subject_data.values())
                            max_score = len(skills) * 2
                            percentage = (total_score / max_score) * 100 if max_score > 0 else 0
                            
                            st.progress(percentage / 100)
                            st.caption(f"{percentage:.0f}%")
                            
                            # عرض تفاصيل المهارات
                            with st.expander("تفاصيل المهارات"):
                                for skill, score in subject_data.items():
                                    color = RATING_COLORS[RATING_OPTIONS[score]]
                                    st.markdown(f"<span style='color:{color}'>●</span> {skill}", unsafe_allow_html=True)
                
                # ملاحظات المواد الدراسية
                if "academic_notes" in data and data["academic_notes"]:
                    with st.expander("📝 ملاحظات المواد الدراسية"):
                        st.write(data["academic_notes"])
            
            st.markdown("---")
            
            # --- 3. تحليل المهارات السلوكية ---
            if "behavioral" in data:
                st.subheader("🧠 تحليل المهارات السلوكية")
                
                for main_category, sub_categories in BEHAVIORAL_SKILLS.items():
                    with st.expander(f"**{main_category}**", expanded=True):
                        for sub_category, skills in sub_categories.items():
                            col_a, col_b = st.columns([3, 1])
                            
                            with col_a:
                                st.markdown(f"**{sub_category}**")
                                
                                if (main_category in data.get("behavioral", {}) and 
                                    sub_category in data["behavioral"][main_category]):
                                    
                                    sub_data = data["behavioral"][main_category][sub_category]
                                    total_score = sum(sub_data.values())
                                    max_score = len(skills) * 2
                                    percentage = (total_score / max_score) * 100 if max_score > 0 else 0
                                    
                                    st.progress(percentage / 100)
                            
                            with col_b:
                                if (main_category in data.get("behavioral", {}) and 
                                    sub_category in data["behavioral"][main_category]):
                                    st.metric("", f"{percentage:.0f}%")
                
                # ملاحظات المهارات السلوكية
                if "behavioral_notes" in data and data["behavioral_notes"]:
                    with st.expander("📝 ملاحظات المهارات السلوكية"):
                        st.write(data["behavioral_notes"])
            
            st.markdown("---")
            
            # --- 4. نقاط القوة والضعف ---
            col_weak, col_strong = st.columns(2)
            
            with col_weak:
                st.subheader("🚨 المجالات التي تحتاج تحسين")
                if scores['weaknesses']:
                    for weakness in scores['weaknesses']:
                        st.error(f"❌ {weakness}")
                else:
                    st.success("🎉 لا توجد مهارات تحتاج تحسين")
            
            with col_strong:
                st.subheader("✅ نقاط القوة")
                if scores['strengths']:
                    for strength in scores['strengths'][:10]:  # عرض أول 10 فقط
                        st.success(f"✓ {strength}")
                    if len(scores['strengths']) > 10:
                        st.info(f"... و {len(scores['strengths']) - 10} مهارة أخرى")
                else:
                    st.info("لم يتم تحديد نقاط قوة بعد")
            
            # --- 5. التوصيات ---
            st.markdown("---")
            st.subheader("💡 التوصيات التربوية")
            
            recommendations = []
            
            if scores['academic_percentage'] < 60:
                recommendations.append("تكثيف الدروس الخصوصية في المواد الدراسية الضعيفة")
            
            if scores['behavioral_percentage'] < 60:
                recommendations.append("برنامج تدريب على المهارات الاجتماعية والعاطفية")
            
            if len(scores['weaknesses']) > 10:
                recommendations.append("تطبيق خطة تعليمية فردية (IEP)")
            
            if scores['overall_percentage'] > 80:
                recommendations.append("توفير أنشطة إثرائية للموهوبين")
            
            if not recommendations:
                recommendations.append("المتابعة العادية حسب المنهج الدراسي")
            
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
            
            # --- 6. زر التصدير ---
            st.markdown("---")
            st.subheader("📥 تصدير التقرير")
            
            # إنشاء التقرير النصي
            report_text = f"""
            ======================================
            تقرير التقييم التشخيصي
            ======================================
            
            التلميذ: {selected_student}
            تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d')}
            
            ======================================
            ١. النتائج العامة:
            - المواد الدراسية: {scores['academic_percentage']:.1f}%
            - المهارات السلوكية: {scores['behavioral_percentage']:.1f}%
            - المجموع الكلي: {scores['overall_percentage']:.1f}%
            
            ======================================
            ٢. نقاط الضعف ({len(scores['weaknesses'])}):
            {chr(10).join(['- ' + w for w in scores['weaknesses']])}
            
            ======================================
            ٣. نقاط القوة ({len(scores['strengths'])}):
            {chr(10).join(['- ' + s for s in scores['strengths'][:20]])}
            
            ======================================
            ٤. التوصيات:
            {chr(10).join(['- ' + r for r in recommendations])}
            
            ======================================
            تم إعداد التقرير بواسطة نظام التقييم الشامل
            """
            
            col_download, col_print = st.columns(2)
            with col_download:
                st.download_button(
                    "📄 تحميل التقرير النصي",
                    report_text,
                    file_name=f"تقرير_{selected_student}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
            with col_print:
                if st.button("🖨️ طباعة التقرير"):
                    st.success("جاري إعداد التقرير للطباعة...")

# ==========================================
# 5. لوحة التحكم
# ==========================================
elif menu == "لوحة التحكم":
    st.header("📊 لوحة التحكم والإحصاءات")
    
    if not st.session_state.students:
        st.warning("لا يوجد بيانات لعرضها.")
    else:
        # إحصاءات عامة
        total_students = len(st.session_state.students)
        evaluated_students = sum(1 for s in st.session_state.students.values() if s.get("evaluations"))
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("إجمالي التلاميذ", total_students)
        with col_stat2:
            st.metric("تم تقييمهم", evaluated_students)
        with col_stat3:
            st.metric("النسبة المئوية", f"{(evaluated_students/total_students*100):.1f}%" if total_students > 0 else "0%")
        
        st.markdown("---")
        
        # جدول بيانات التلاميذ
        st.subheader("📋 جدول بيانات التلاميذ")
        
        student_data = []
        for name, info in st.session_state.students.items():
            student_data.append({
                "اسم التلميذ": name,
                "المستوى": info["info"].get("class_level", ""),
                "الجنس": info["info"].get("gender", ""),
                "تم التقييم": "✅" if info.get("evaluations") else "❌",
                "آخر تحديث": info.get("evaluations", {}).get("last_update", "لم يتم")
            })
        
        if student_data:
            df = pd.DataFrame(student_data)
            st.dataframe(df, use_container_width=True, height=300)
            
            # تصدير البيانات
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 تحميل البيانات (CSV)",
                csv,
                "بيانات_التلاميذ.csv",
                "text/csv"
            )
        
        st.markdown("---")
        
        # تحليل النتائج الإجمالية
        st.subheader("📈 تحليل النتائج الإجمالية")
        
        if evaluated_students > 0:
            all_scores = []
            for name, data in st.session_state.students.items():
                if data.get("evaluations"):
                    scores = calculate_scores(data["evaluations"])
                    all_scores.append({
                        "اسم التلميذ": name,
                        "المواد الدراسية": scores["academic_percentage"],
                        "المهارات السلوكية": scores["behavioral_percentage"],
                        "المجموع": scores["overall_percentage"]
                    })
            
            if all_scores:
                scores_df = pd.DataFrame(all_scores)
                
                # عرض المتوسطات
                col_avg1, col_avg2, col_avg3 = st.columns(3)
                with col_avg1:
                    st.metric("متوسط المواد الدراسية", f"{scores_df['المواد الدراسية'].mean():.1f}%")
                with col_avg2:
                    st.metric("متوسط المهارات السلوكية", f"{scores_df['المهارات السلوكية'].mean():.1f}%")
                with col_avg3:
                    st.metric("المتوسط العام", f"{scores_df['المجموع'].mean():.1f}%")
                
                # عرض التوزيع
                st.bar_chart(scores_df.set_index("اسم التلميذ")[["المواد الدراسية", "المهارات السلوكية"]])
        
        # إدارة البيانات
        st.markdown("---")
        st.subheader("⚙️ إدارة النظام")
        
        col_backup, col_reset = st.columns(2)
        
        with col_backup:
            if st.button("💾 إنشاء نسخة احتياطية"):
                import json
                backup_data = json.dumps(st.session_state.students, ensure_ascii=False, indent=2)
                st.download_button(
                    "📥 تحميل النسخة الاحتياطية",
                    backup_data,
                    f"backup_التقييم_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    "application/json"
                )
        
        with col_reset:
            if st.button("🗑️ مسح جميع البيانات", type="secondary"):
                if st.checkbox("تأكيد حذف جميع البيانات (لا يمكن التراجع عن هذا الإجراء)"):
                    st.session_state.students = {}
                    st.success("تم مسح جميع البيانات")
                    st.rerun()

# --- تذييل الصفحة ---
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col2:
    st.caption("© 2024 نظام التقييم الشامل المطور - الإصدار 2.0")
