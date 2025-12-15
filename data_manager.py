import json
import os
import random

DATA_FILE = "students_data.json"

# ==============================================================================
# 1. الثوابت والبيانات (هذا الجزء كان مفقوداً ويسبب الخطأ)
# ==============================================================================

RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]
RATING_MAP = {"غير مكتسب": 0, "في طريق الاكتساب": 1, "مكتسب": 2}

# قائمة المواد الدراسية
ACADEMIC_SUBJECTS = {
    "اللغة العربية": [
        "يسمي الحروف الهجائية المدروسة",
        "يميز صواتياً بين الحروف",
        "يمسك القلم بطريقة صحيحة",
        "يكتب اسمه بدقة"
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

# قائمة المهارات السلوكية
BEHAVIORAL_SKILLS = {
    "الوظائف التنفيذية": {
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
    "الكفاءة الاجتماعية": {
        "التطور الشخصي": [
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
    "المهارات الحركية": {
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

# بنك العبارات التربوية
ANALYSIS_TEMPLATES = {
    "opening": {
        "excellent": [
            "أبان {student_type} {name} عن قدرات استثنائية وجاهزية عالية للتعلم.",
            "يتميز {student_type} {name} بحضور ذهني متوقد وشغف واضح للاكتشاف."
        ],
        "good": [
            "يسير {student_type} {name} بخطى ثابتة ومطمئنة في رحلته التعليمية.",
            "أظهر {student_type} {name} تطوراً ملحوظاً في اكتساب المهارات الأساسية."
        ],
        "needs_support": [
            "يواجه {student_type} {name} بعض التحديات في التكيف مع البيئة المدرسية.",
            "يمر {student_type} {name} بمرحلة انتقالية دقيقة تتطلب دعماً."
        ]
    },
    "cognitive_style": { 
        "analytical": "من الناحية المعرفية، يميل {pronoun} إلى التفكير المنطقي والمنظم.",
        "verbal": "يتميز {pronoun} بطلاقة لغوية وقدرة تعبيرية لافتة.",
        "balanced": "يظهر {pronoun} مرونة ذهنية رائعة بين المهام اللغوية والمنطقية.",
        "struggling": "يجد {pronoun} بعض الصعوبة في معالجة المعلومات المجردة."
    },
    "social_emotional": {
        "leader": "اجتماعياً، يتمتع بشخصية قيادية محبوبة بين أقرانه.",
        "introvert": "يميل {pronoun} إلى الهدوء والتأمل ويفضل العمل ضمن مجموعات صغيرة.",
        "impulsive": "يتسم سلوكه ببعض الحماس الزائد الذي يحتاج لتوجيه.",
        "dependent": "يحتاج {pronoun} إلى تشجيع مستمر لتعزيز ثقته بنفسه."
    },
    "work_habits": {
        "focused": "يتميز بجلد وصبر في إنجاز المهام.",
        "distracted": "يتأثر انتباهه بالمشوشات الخارجية بسهولة.",
        "creative": "يظهر لمسات إبداعية في إنجاز أعماله."
    }
}

# ==============================================================================
# 2. الدوال (Functions)
# ==============================================================================

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_student_info(name, info):
    data = load_data()
    if name not in data:
        data[name] = {"info": info, "evaluations": {}, "history": []}
    else:
        if "info" not in data[name]: data[name]["info"] = {}
        data[name]["info"].update(info)
    save_data(data)

def calculate_scores(evaluations):
    academic_total, academic_max = 0, 0
    behavioral_total, behavioral_max = 0, 0
    weaknesses, strengths = [], []
    
    if "academic" in evaluations:
        for subj, skills in evaluations["academic"].items():
            for skill, score in skills.items():
                if isinstance(score, int):
                    academic_total += score
                    academic_max += 2
                    if score == 0: weaknesses.append(f"{subj}: {skill}")
                    elif score == 2: strengths.append(skill)
    
    if "behavioral" in evaluations:
        for main, subs in evaluations["behavioral"].items():
            for sub, skills in subs.items():
                for skill, score in skills.items():
                    if isinstance(score, int):
                        behavioral_total += score
                        behavioral_max += 2
                        if score == 0: weaknesses.append(f"{main}: {skill}")
                        elif score == 2: strengths.append(skill)

    ac_pct = (academic_total / academic_max * 100) if academic_max > 0 else 0
    beh_pct = (behavioral_total / behavioral_max * 100) if behavioral_max > 0 else 0
    ov_pct = ((academic_total+behavioral_total)/(academic_max+behavioral_max)*100) if (academic_max+behavioral_max) > 0 else 0
    
    return {
        "academic_percentage": ac_pct,
        "behavioral_percentage": beh_pct,
        "overall_percentage": ov_pct,
        "weaknesses": weaknesses,
        "strengths": strengths
    }

def analyze_student_performance(name, data, gender="ذكر"):
    stats = calculate_scores(data)
    ac_score = stats['academic_percentage']
    beh_score = stats['behavioral_percentage']
    
    tags = {
        "{name}": name,
        "{student_type}": "المتعلم" if gender == "ذكر" else "المتعلمة",
        "{pronoun}": "هو" if gender == "ذكر" else "هي"
    }

    narrative_parts = []

    # الافتتاحية
    if stats['overall_percentage'] >= 85:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["excellent"])
    elif stats['overall_percentage'] >= 60:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["good"])
    else:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["needs_support"])
    narrative_parts.append(opening)

    # المعرفي
    if ac_score < 50:
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["struggling"]
    elif ac_score >= 85:
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["analytical"]
    else:
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["balanced"]
    narrative_parts.append(cog_text)

    # السلوكي
    if beh_score >= 85:
        soc_text = ANALYSIS_TEMPLATES["social_emotional"]["leader"]
    elif beh_score < 50:
         soc_text = ANALYSIS_TEMPLATES["social_emotional"]["dependent"]
    else:
         soc_text = "يظهر تفاعلاً اجتماعياً متزناً، ويبدي احتراماً للقواعد الصفية."
    narrative_parts.append(soc_text)

    # عادات العمل
    work_text = ANALYSIS_TEMPLATES["work_habits"]["focused"] if ac_score > 70 else "يحتاج إلى مزيد من المثابرة لإتمام المهام."
    narrative_parts.append(work_text)

    # الخاتمة
    closing = "نوصي بالتركيز على الجانب النفسي وتعزيز الشعور بالإنجاز."
    narrative_parts.append(closing)

    full_text = "\n\n".join(narrative_parts)
    for k, v in tags.items():
        full_text = full_text.replace(k, v)
        
    action_plan = []
    for w in stats['weaknesses'][:4]:
        clean_name = w.split(": ")[-1] if ":" in w else w
        action_plan.append((clean_name, "التدريب المكثف والمتابعة المستمرة."))

    return full_text, action_plan

def generate_text_report(student_name, student_info, evaluation_data, stats, narrative, action_plan):
    report = [f"تقرير: {student_name}", "="*20, narrative, "-"*20]
    for k, v in action_plan: report.append(f"* {k}: {v}")
    return "\n".join(report)

