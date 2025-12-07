import streamlit as st
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام التقييم الشامل المطور", layout="wide", page_icon="🎓")

# تنسيق CSS احترافي
st.markdown("""
<style>
    .main {direction: rtl; text-align: right;}
    .stRadio, .stSelectbox, .stTextInput, .stNumberInput {direction: rtl; text-align: right;}
    div[role="radiogroup"] {flex-direction: row-reverse; justify-content: flex-end;}
    h1, h2, h3, h4, p, div, label, li {text-align: right;}
    .stProgress > div > div > div > div {background-color: #4CAF50;}
</style>
""", unsafe_allow_html=True)

# --- ثوابت التقييم ---
RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]
RATING_MAP = {"غير مكتسب": 0, "في طريق الاكتساب": 1, "مكتسب": 2}

# --- قاعدة بيانات المهارات (الشاملة من النسخة الأولى) ---
ASSESSMENT_CRITERIA = {
    "1. المهارات الأكاديمية واللغوية": {
        "القراءة": ["تمييز الأحرف الأبجدية", "مطابقة الصورة بالكلمة", "تتبع النص من اليمين لليسار"],
        "الكتابة": ["مسك القلم بالطريقة الصحيحة", "نسخ أشكال وأحرف بسيطة", "كتابة الاسم الأول"],
        "الرياضيات": ["العد حتى 20", "المقارنة الكمية (أكثر/أقل)", "تصنيف الأشياء حسب اللون/الشكل"],
        "اللغة والتواصل": ["سرد قصة متسلسلة", "استخدام جمل كاملة", "فهم التعليمات المركبة"]
    },
    "2. الوظائف التنفيذية (الذهنية)": {
        "الانتباه والتركيز": ["التركيز على نشاط لمدة 15 دقيقة", "إكمال المهمة للنهاية"],
        "الذاكرة": ["تذكر تعليمات من 3 خطوات", "تذكر أحداث قصة قصيرة"],
        "المرونة": ["الانتقال بين الأنشطة بسلاسة", "تقبل التغيير في الروتين"]
    },
    "3. الكفاءة الاجتماعية والعاطفية": {
        "الوعي الذاتي": ["التعبير عن المشاعر بدقة", "الثقة بالنفس"],
        "التفاعل الاجتماعي": ["المشاركة في اللعب الجماعي", "احترام الدور", "حل النزاعات ودياً"],
        "السلوك": ["اتباع قواعد القسم", "التحكم في الانفعالات"]
    },
    "4. المهارات الحركية والاستقلالية": {
        "حركية دقيقة": ["استخدام المقص", "تلوين داخل الحدود", "تركيب المكعبات"],
        "حركية كبرى": ["التوازن (الوقوف على قدم واحدة)", "التقاط الكرة ورميها"],
        "الاستقلالية": ["ارتداء الملابس/الحذاء", "استخدام الحمام بمفرده", "ترتيب الأغراض الشخصية"]
    }
}

# --- إدارة البيانات ---
if 'students' not in st.session_state:
    st.session_state.students = {}

# --- القائمة الجانبية ---
with st.sidebar:
    st.title("نظام التقييم الشامل 3.0")
    menu = st.radio("القائمة:", ["سجل التلاميذ", "التقييم المفصل", "التقرير التشخيصي"], index=1)
    st.info("نظام هجين: دقة المحتوى + سهولة الاستخدام")

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
    st.header("📝 تقييم المهارات والقدرات")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("الرجاء تسجيل تلاميذ أولاً.")
    else:
        selected_student = st.selectbox("ملف التلميذ:", student_names)
        current_evals = st.session_state.students[selected_student]["evaluations"]
        
        st.markdown("---")
        
        with st.form("comprehensive_eval"):
            # إنشاء تبويبات للمحاور الرئيسية لتقليل الازدحام
            main_tabs = st.tabs(list(ASSESSMENT_CRITERIA.keys()))
            
            new_evals_data = {}
            
            for i, (main_domain, sub_domains) in enumerate(ASSESSMENT_CRITERIA.items()):
                with main_tabs[i]:
                    domain_data = {}
                    for sub_domain, skills in sub_domains.items():
                        st.subheader(f"🔹 {sub_domain}")
                        sub_domain_data = {}
                        for skill in skills:
                            # استرجاع القيمة السابقة
                            prev_val_idx = 1
                            if main_domain in current_evals:
                                if sub_domain in current_evals[main_domain]:
                                    val_score = current_evals[main_domain][sub_domain].get(skill, 1)
                                    # تحويل السكور (0,1,2) إلى اندكس (0,1,2)
                                    prev_val_idx = val_score 
                            
                            # زر الاختيار الثلاثي
                            choice = st.radio(
                                skill, 
                                RATING_OPTIONS, 
                                index=prev_val_idx, 
                                key=f"{selected_student}_{skill}", 
                                horizontal=True
                            )
                            sub_domain_data[skill] = RATING_MAP[choice]
                        
                        domain_data[sub_domain] = sub_domain_data
                        st.markdown("---")
                    new_evals_data[main_domain] = domain_data
            
            save = st.form_submit_button("حفظ التقييم الشامل", type="primary")
            if save:
                st.session_state.students[selected_student]["evaluations"] = new_evals_data
                st.toast("تم الحفظ بنجاح!", icon="✅")

# ==========================================
# 3. التقرير التشخيصي (التحليل العميق)
# ==========================================
elif menu == "التقرير التشخيصي":
    st.header("📊 التقرير التربوي الشامل")
    
    student_names = list(st.session_state.students.keys())
    if not student_names:
        st.warning("لا يوجد بيانات.")
    else:
        selected_student = st.selectbox("اختر التلميذ:", student_names)
        data = st.session_state.students[selected_student]["evaluations"]
        
        if not data:
            st.error("لم يتم إجراء تقييم لهذا التلميذ بعد.")
        else:
            # --- 1. ملخص الاستعداد المدرسي ---
            total_points = 0
            max_possible = 0
            
            # تجميع البيانات للتحليل
            weaknesses = []
            strengths = []
            
            for main_domain, sub_domains in data.items():
                for sub, skills in sub_domains.items():
                    for skill, score in skills.items():
                        total_points += score
                        max_possible += 2
                        if score == 0:
                            weaknesses.append(f"{main_domain} -> {skill}")
                        elif score == 2:
                            strengths.append(skill)

            readiness_score = (total_points / max_possible) * 100 if max_possible > 0 else 0
            
            st.subheader("مؤشر الاستعداد للمدرسة الابتدائية")
            st.progress(readiness_score / 100)
            st.caption(f"النسبة العامة: {readiness_score:.1f}%")
            
            # --- 2. تفاصيل المحاور (شريط تقدم لكل محور) ---
            st.subheader("تحليل المجالات الرئيسية")
            col1, col2 = st.columns(2)
            
            chart_data = {}
            
            for i, (main_domain, sub_domains) in enumerate(data.items()):
                domain_points = 0
                domain_max = 0
                for sub, skills in sub_domains.items():
                    domain_points += sum(skills.values())
                    domain_max += len(skills) * 2
                
                perc = (domain_points / domain_max) * 100 if domain_max > 0 else 0
                chart_data[main_domain] = perc
                
                # توزيع العرض على عمودين
                target_col = col1 if i % 2 == 0 else col2
                with target_col:
                    st.write(f"**{main_domain}**")
                    st.progress(perc / 100)
                    st.write(f"{perc:.0f}% مكتسب")

            # --- 3. نظام الإنذار وتوصيات التدخل ---
            st.markdown("---")
            st.subheader("🚨 أولويات التدخل (المهارات غير المكتسبة)")
            
            if weaknesses:
                st.error(f"تم رصد {len(weaknesses)} مهارات تحتاج لتدخل عاجل:")
                for w in weaknesses:
                    st.write(f"- ⭕ {w}")
            else:
                st.success("سجل نظيف: التلميذ يظهر تحكماً في جميع المهارات المقيمة.")

            # --- 4. التوصية التربوية الآلية ---
            st.subheader("💡 التوصية التربوية")
            note_container = st.container(border=True)
            if readiness_score > 85:
                note_container.markdown("**مستوى متقدم:** الطفل جاهز تماماً. يُنصح بالتركيز على مهارات القيادة والإثراء اللغوي المتقدم.")
            elif readiness_score > 60:
                note_container.markdown("**مستوى متوسط:** الطفل يتقدم بشكل طبيعي، لكن يجب مراجعة القائمة الحمراء أعلاه وتكثيف الأنشطة المنزلية في تلك النقاط.")
            else:
                note_container.markdown("**يحتاج لدعم مكثف:** يُنصح بعقد اجتماع مع الولي ووضع خطة فردية تركز أولاً على المهارات الاستقلالية والانتباه.")

            # --- زر الطباعة ---
            # نقوم بإنشاء نص بسيط يمكن نسخه ولصقه في الوورد
            report_text = f"""
            تقرير تقييم التلميذ: {selected_student}
            نسبة الاستعداد: {readiness_score:.1f}%
            
            المهارات غير المكتسبة:
            {chr(10).join(['- ' + w for w in weaknesses])}
            
            التوصية: تم الاطلاع على التقرير الرقمي
            """
            st.download_button("تحميل ملخص التقرير (TXT)", report_text, file_name=f"Report_{selected_student}.txt")
