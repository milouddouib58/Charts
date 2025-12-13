import json
import os
import streamlit as st
from datetime import datetime

DATA_FILE = "students_data.json"

# --- Constants ---
RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]
RATING_MAP = {"غير مكتسب": 0, "في طريق الاكتساب": 1, "مكتسب": 2}
RATING_COLORS = {"غير مكتسب": "#FF4B4B", "في طريق الاكتساب": "#FFA500", "مكتسب": "#4CAF50"}

# --- Assessment Criteria ---
# 1. Academic Subjects
ACADEMIC_SUBJECTS = {
    "اللغة العربية": [
        "يسمي الحروف الهجائية المدروسة",
        "يميز صواتياً بين الحروف",
        "يمسك القلم بطريقة صحيحة",
    ],
    "الرياضيات": [
        "يعد شفوياً إلى 20",
        "يربط العدد بالمعدود",
        "يميز الأشكال الهندسية",
        "يصنف الأشياء حسب خاصية معينة",
        "يتعرف على الأعداد حتى 10"
    ],
    "التربية الإسلامية والمدنية": [
        "يحفظ قصار السور المقررة",
        "يلقي التحية ويردها",
        "يحافظ على نظافة مكانه",
        "يتعاون مع زملائه",
        "يحترم المعلم والزملاء"
    ],
    "التربية العلمية": [
        "يسمي أعضاء جسم الإنسان",
        "يميز بين الحواس الخمس",
        "يعرف الحيوانات الأليفة والمتوحشة",
    ],

}

# 2. Behavioral Skills
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

# --- Helper Functions ---

def load_data():
    """Load student data from the JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return {}
    return {}

def save_data(data):
    """Save the entire data dictionary to file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def save_student_info(name, info):
    """Save or update basic student info."""
    data = load_data()
    if name not in data:
        data[name] = {"info": info, "evaluations": {}, "history": []}
    else:
        # Update info but keep existing structure
        if "info" not in data[name]:
            data[name]["info"] = {}
        data[name]["info"].update(info)
        
    save_data(data)

def calculate_scores(evaluations):
    """Calculate scores and percentages for assessments."""
    if not evaluations:
        return {
            "academic_total": 0, "academic_max": 0, "academic_percentage": 0,
            "behavioral_total": 0, "behavioral_max": 0, "behavioral_percentage": 0,
            "overall_total": 0, "overall_max": 0, "overall_percentage": 0,
            "weaknesses": [], "strengths": []
        }
    
    academic_total = 0
    academic_max = 0
    behavioral_total = 0
    behavioral_max = 0
    weaknesses = []
    strengths = []
    
    # Calculate Academic
    if "academic" in evaluations:
        for subject, skills in evaluations["academic"].items():
            for skill, score in skills.items():
                academic_total += score
                academic_max += 2
                if score == 0:
                    weaknesses.append(f"[المواد الدراسية - {subject}] {skill}")
                elif score == 2:
                    strengths.append(f"[المواد الدراسية - {subject}] {skill}")
    
    # Calculate Behavioral
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


# --- Smart Analysis & Recommendations (v4.1) ---
RECOMMENDATIONS_MAP = {
    "تمييز الأحرف الأبجدية": "استخدام بطاقات الصنفرة (Sandpaper Letters) لتعزيز الذاكرة الحسية.",
    "مطابقة الصورة بالكلمة": "ألعاب الذاكرة البصرية (Memory Match) مع صور وكلمات.",
    "تتبع النص من اليمين لليسار": "أنشطة القراءة المشتركة مع الإشارة بالإصبع أثناء القراءة.",
    "مسك القلم بالطريقة الصحيحة": "استخدام مقابض الأقلام (Pencil Grips) والتدريب على التقاط الأشياء الصغيرة.",
    "نسخ أشكال وأحرف بسيطة": "التدرب على الرسم في الرمل أو المعجون قبل الورق.",
    "كتابة الاسم الأول": "كتابة الاسم بخط منقط ليقوم التلميذ بتتبعه.",
    "العد حتى 20": "استخدام المحسوسات (الخرز، المكعبات) للعد الملموس.",
    "المقارنة الكمية (أكثر/أقل)": "توزيع الحلوى أو الألعاب على مجموعتين والمقارنة بينهما.",
    "تصنيف الأشياء حسب اللون/الشكل": "لعبة 'فرز الأزرار' أو المكعبات في أوعية ملونة.",
    "سرد قصة متسلسلة": "استخدام بطاقات القصة المصورة لترتيب الأحداث.",
    "استخدام جمل كاملة": "تشجيع التلميذ على وصف ما يراه في الصور بجمل تامة.",
    "فهم التعليمات المركبة": "لعبة 'قال القائد' بتعليمات مزدوجة (صفق ثم قف).",
    "التركيز على نشاط لمدة 15 دقيقة": "استخدام المؤقت الرملي لزيادة وقت التركيز تدريجياً.",
    "إكمال المهمة للنهاية": "تقسيم المهام الكبيرة إلى خطوات صغيرة ومكافأة كل خطوة.",
    "تذكر تعليمات من 3 خطوات": "لعبة 'أحضر لي' بطلبات متزايدة الصعوبة.",
    "تذكر أحداث قصة قصيرة": "طرح أسئلة (ماذا، أين، من) بعد قراءة القصة مباشرة.",
    "الانتقال بين الأنشطة بسلاسة": "استخدام جدول بصري (Visual Schedule) وتنبيه قبل الانتقال.",
    "تقبل التغيير في الروتين": "إدخال تغييرات بسيطة ومفاجئة في اللعب كتدريب.",
    "التعبير عن المشاعر بدقة": "استخدام 'عجلة المشاعر' للمساعدة في تسمية الشعور.",
    "الثقة بالنفس": "تكليف التلميذ بمهام قيادية بسيطة (موزع الأوراق).",
    "المشاركة في اللعب الجماعي": "تنظيم ألعاب تعاونية تتطلب عمل الفريق.",
    "احترام الدور": "استخدام 'عصا التحدث' أو الكرة لتنظيم الأدوار.",
    "حل النزاعات ودياً": "تمثيل الأدوار (Role-playing) لحل المشكلات.",
    "اتباع قواعد القسم": "لوحة التعزيز الإيجابي للنجمات.",
    "التحكم في الانفعالات": "ركن الهدوء (Calm Down Corner) وتمارين التنفس.",
    "استخدام المقص": "قص العجين أو خطوط عريضة ومستقيمة أولاً.",
    "تلوين داخل الحدود": "استخدام حدود بارزة (الغراء الجاف) للمساعدة.",
    "تركيب المكعبات": "تقليد نماذج بسيطة ثلاثية الأبعاد.",
    "التوازن (الوقوف على قدم واحدة)": "لعبة 'الثبات كالصنم' أو المشي على خط مرسوم.",
    "التقاط الكرة ورميها": "استخدام كرة كبيرة وخفيفة وتقليل المسافة.",
    "ارتداء الملابس/الحذاء": "التدريب على ملابس العرايس أو سترة بأزرار كبيرة.",
    "استخدام الحمام بمفرده": "جدول روتيني مصور داخل الحمام.",
    "ترتيب الأغراض الشخصية": "تخصيص علامات صورية لمكان كل غرض."
}

import random

def analyze_student_performance(name, evaluation_data):
    """
    Generates a creative narrative analysis and actionable recommendations.
    Uses randomized templates to avoid robotic repetition.
    """
    narrative = []
    strengths = []
    weaknesses_list = []
    
    # Analyze Scores
    total_score = 0
    max_score = 0
    
    # Calculate Academic
    if "academic" in evaluation_data:
        for subject, skills in evaluation_data["academic"].items():
            for skill, score in skills.items():
                total_score += score
                max_score += 2
                if score == 2:
                    strengths.append(skill)
                elif score == 0:
                    weaknesses_list.append(skill)
    
    # Calculate Behavioral
    if "behavioral" in evaluation_data:
        for category, domains in evaluation_data["behavioral"].items():
            for domain, skills in domains.items():
                for skill, score in skills.items():
                    total_score += score
                    max_score += 2
                    if score == 2:
                        strengths.append(skill)
                    elif score == 0:
                        weaknesses_list.append(skill)
    
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    # 1. Creative Opening (Randomized)
    # Using 'المتعلم' (The Learner) is often more neutral/professional in reports than 'التلميذ'
    openings_excellent = [
        f"أظهر المتعلم **{name}** مستوى متميزاً من الاستعداد المدرسي بنسبة **{percentage:.1f}%**، مما يعكس امتلاكه لمهارات تأسيسية متينة.",
        f"يسرنا تسجيل تقدم ملحوظ للمتعلم **{name}**، حيث حقق نسبة جاهزية بلغت **{percentage:.1f}%**، وهو مؤشر إيجابي جداً.",
    ]
    openings_good = [
        f"يحرز المتعلم **{name}** تقدماً طيباً في اكتساب المهارات الأساسية بنسبة **{percentage:.1f}%**، مع وجود هامش جيد للتطوير.",
        f"أظهر التقييم مستوى جيداً للمتعلم **{name}** بنسبة **{percentage:.1f}%**، مما يعني أنه يسير في الطريق الصحيح مع الحاجة لبعض التدعيم.",
    ]
    openings_needs_support = [
        f"تشير النتائج إلى حاجة المتعلم **{name}** لدعم مكثف في بعض الجوانب، حيث بلغت نسبة الاستعداد **{percentage:.1f}%**.",
        f"نوصي بوضع خطة علاجية مخصصة للمتعلم **{name}** لتعزيز المكتسبات، بناءً على نتيجة التقييم الحالية ({percentage:.1f}%).",
    ]
    
    if percentage >= 85: intro = random.choice(openings_excellent)
    elif percentage >= 65: intro = random.choice(openings_good)
    else: intro = random.choice(openings_needs_support)
    
    narrative.append(intro)
    
    # helper for arabic list join
    def arabic_join(items):
        if not items: return ""
        if len(items) == 1: return items[0]
        return "، ".join(items[:-1]) + " و" + items[-1]

    # 2. Strengths (Dynamic Phrasing)
    if strengths:
        s_phrases = ["تبرز نقاط القوة بوضوح في: ", "أظهر تمكناً ملحوظاً في: ", "من الجوانب المشرقة في أدائه: "]
        s_text = random.choice(s_phrases)
        s_sample = strengths[:5] # Take up to 5
        s_text += f"{arabic_join(s_sample)}."
        if len(strengths) > 5: s_text += " وغيرها."
        narrative.append(s_text)
        
    # 3. Weaknesses (Soft & Constructive Language)
    if weaknesses_list:
        w_phrases = ["لتحقيق توازن في الأداء، ينصح بالتركيز على: ", "تستدعي المهارات التالية بعض الانتباه: ", "سنعمل على تعزيز الجوانب التالية: "]
        w_text = random.choice(w_phrases)
        w_text += f"{arabic_join(weaknesses_list[:5])}."
        narrative.append(w_text)
    else:
        narrative.append("✅ وبفضل الله، لم يتم رصد صعوبات جوهرية، ونوصي بالاستمرار في تعزيز التحديات المعرفية.")
    
    # Closing
    closing = "إن المتابعة المستمرة والتشجيع هما المفتاح لتطوير قدرات المتعلم والوصول به إلى أقصى إمكاناته."
    narrative.append(closing)
        
    # Recommendations
    action_plan = []
    for w in weaknesses_list:
        if w in RECOMMENDATIONS_MAP:
            action_plan.append((w, RECOMMENDATIONS_MAP[w]))
            
    full_narrative = "\n\n".join(narrative) # Separated by double newlines for readable paragraphs
    
    return full_narrative, action_plan
