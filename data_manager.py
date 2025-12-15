import json
import os
import random

DATA_FILE = "students_data.json"

# ==============================================================================
# 1. الثوابت والبيانات (Constants & Data) - هذا هو الجزء الذي كان ناقصاً
# ==============================================================================

RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]
RATING_MAP = {"غير مكتسب": 0, "في طريق الاكتساب": 1, "مكتسب": 2}

# --- قائمة المواد الدراسية ---
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

# --- قائمة المهارات السلوكية ---
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

# --- بنك العبارات التربوية (للتحليل الذكي) ---
ANALYSIS_TEMPLATES = {
    "opening": {
        "excellent": [
            "أبان {student_type} {name} عن قدرات استثنائية وجاهزية عالية للتعلم، مما يعكس نضجاً مبكراً في مهارات التفكير والتحليل.",
            "يتميز {student_type} {name} بحضور ذهني متوقد وشغف واضح للاكتشاف، وهو ما ظهر جلياً في سرعة استيعابه للمفاهيم المقدمة.",
            "أظهر {student_type} {name} مستوى متميزاً من الكفاءة، حيث يجمع بين الذكاء المعرفي والانضباط السلوكي بشكل مثير للإعجاب."
        ],
        "good": [
            "يسير {student_type} {name} بخطى ثابتة ومطمئنة في رحلته التعليمية، مبدياً تجاوباً إيجابياً مع معظم الأنشطة المقترحة.",
            "أظهر {student_type} {name} تطوراً ملحوظاً في اكتساب المهارات الأساسية، مع وجود بعض التفاوت الطبيعي بين الجوانب الأكاديمية والسلوكية.",
            "يتمتع {student_type} {name} بإمكانيات طيبة وقابلية عالية للتعلم، وهو يبذل جهداً مشكوراً لمواكبة متطلبات القسم."
        ],
        "needs_support": [
            "يواجه {student_type} {name} بعض التحديات في التكيف مع البيئة المدرسية، وهو ما يتطلب منا تفهماً وصبراً لاحتواء احتياجاته الخاصة.",
            "يمر {student_type} {name} بمرحلة انتقالية دقيقة، حيث تظهر النتائج حاجته الماسة لدعم فردي مكثف لتعزيز ثقته بنفسه.",
            "تشير الملاحظات إلى أن {student_type} {name} يمتلك طاقة كامنة لم يتم توظيفها بعد بالشكل الصحيح، مما يستدعي تدخلاً تربويًا موجهاً."
        ]
    },
    "cognitive_style": { 
        "analytical": "من الناحية المعرفية، يميل {pronoun} إلى التفكير المنطقي والمنظم، ويظهر شغفاً بالأنشطة التي تتطلب دقة وتركيزاً، مثل التعامل مع الأرقام والأشكال.",
        "verbal": "يتميز {pronoun} بطلاقة لغوية وقدرة تعبيرية لافتة، حيث يعتمد في تعلمه بشكل كبير على التواصل اللفظي وسرد القصص والتفاعل الحي.",
        "balanced": "يظهر {pronoun} مرونة ذهنية رائعة، حيث يتنقل بسلاسة بين المهام اللغوية والمنطقية، مما يعكس توازناً في نمو نصفي الدماغ.",
        "struggling": "يجد {pronoun} بعض الصعوبة في معالجة المعلومات المجردة والمتسلسلة، ويفضل الاعتماد على الوسائل الحسية والملموسة لفهم المطلوب."
    },
    "social_emotional": {
        "leader": "اجتماعياً، يتمتع بشخصية قيادية محبوبة، ويجيد إدارة المواقف مع أقرانه بذكاء عاطفي، مما يجعله عنصراً فعالاً في العمل الجماعي.",
        "introvert": "يميل {pronoun} إلى الهدوء والتأمل، ويفضل العمل الفردي أو ضمن مجموعات صغيرة، وهو ما يعكس شخصية حساسة ودقيقة الملاحظة.",
        "impulsive": "يتسم سلوكه ببعض الاندفاع والحماس الزائد، مما يتطلب توجيه هذه الطاقة الحركية نحو أنشطة بناءة لتعزيز التركيز.",
        "dependent": "يحتاج {pronoun} إلى تشجيع مستمر ودعم عاطفي للشعور بالأمان، حيث يتردد أحياناً في المبادرة خوفاً من الخطأ."
    },
    "work_habits": {
        "focused": "يتميز بجلد وصبر في إنجاز المهام، ولديه قدرة عالية على التركيز لفترات طويلة دون تشتت.",
        "distracted": "يتأثر انتباهه بسهولة بالمشوشات الخارجية، مما يستدعي تقسيم المهام الطويلة إلى مراحل قصيرة للحفاظ على تفاعله.",
        "creative": "يظهر لمسات إبداعية في إنجاز أعماله، وغالباً ما يبحث عن حلول غير تقليدية للمشكلات التي تواجهه."
    }
}

# ==============================================================================
# 2. الدوال المساعدة (Helper Functions)
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
    academic_total = 0
    academic_max = 0
    behavioral_total = 0
    behavioral_max = 0
    weaknesses = []
    strengths = []
    
    # حساب الأكاديمي
    if "academic" in evaluations:
        for subj, skills in evaluations["academic"].items():
            for skill, score in skills.items():
                if isinstance(score, int):
                    academic_total += score
                    academic_max += 2
                    if score == 0: weaknesses.append(f"{subj}: {skill}")
                    elif score == 2: strengths.append(skill)
    
    # حساب السلوكي
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

# ==============================================================================
# 3. المحرك الذكي للتحليل (Smart Analysis Logic)
# ==============================================================================
def analyze_student_performance(name, data, gender="ذكر"):
    stats = calculate_scores(data)
    ac_score = stats['academic_percentage']
    beh_score = stats['behavioral_percentage']
    
    # تجهيز المتغيرات للاستبدال
    tags = {
        "{name}": name,
        "{student_type}": "المتعلم" if gender == "ذكر" else "المتعلمة",
        "{pronoun}": "هو" if gender == "ذكر" else "هي"
    }

    narrative_parts = []

    # --- 1. الافتتاحية ---
    if stats['overall_percentage'] >= 85:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["excellent"])
    elif stats['overall_percentage'] >= 60:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["good"])
    else:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["needs_support"])
    narrative_parts.append(opening)

    # --- 2. التحليل المعرفي ---
    if ac_score < 50:
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["struggling"]
    elif ac_score >= 85:
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["analytical"]
    else:
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["balanced"]
    narrative_parts.append(cog_text)

    # --- 3. التحليل السلوكي ---
    if beh_score >= 85:
        soc_text = ANALYSIS_TEMPLATES["social_emotional"]["leader"]
    elif beh_score < 50:
         soc_text = ANALYSIS_TEMPLATES["social_emotional"]["dependent"]
    else:
         soc_text = "يظهر تفاعلاً اجتماعياً متزناً، ويبدي احتراماً للقواعد الصفية مع رغبة في المشاركة."
    narrative_parts.append(soc_text)

    # --- 4. عادات العمل ---
    weakness_str = " ".join(stats['weaknesses'])
    if "تشتت" in weakness_str or "تركيز" in weakness_str:
        work_text = ANALYSIS_TEMPLATES["work_habits"]["distracted"]
    else:
        work_text = ANALYSIS_TEMPLATES["work_habits"]["focused"] if ac_score > 70 else "يحتاج إلى مزيد من المثابرة لإتمام المهام."
    narrative_parts.append(work_text)

    # --- 5. الخاتمة ---
    closing = random.choice([
        "ختاماً، نحن متفائلون جداً بمستقبل {student_type}، ونؤكد أن التعاون المثمر هو المفتاح.",
        "إن المسار التعليمي لـ{student_type} يبشر بالخير مع استمرار الدعم.",
        "نوصي بالتركيز على الجانب النفسي وتعزيز الشعور بالإنجاز."
    ])
    narrative_parts.append(closing)

    # تجميع النص وتطبيق الاستبدالات
    full_text = "\n\n".join(narrative_parts)
    for k, v in tags.items():
        full_text = full_text.replace(k, v)
        
    # --- الخطة العلاجية (Action Plan) ---
    action_plan = []
    RECOMMENDATIONS_MAP = {
         "يسمي الحروف الهجائية المدروسة": "استخدام بطاقات الصنفرة والتشكيل بالعجين.",
         "يمسك القلم بطريقة صحيحة": "تمارين تقوية عضلات اليد الدقيقة (لقط الحبوب).",
         "يعد شفوياً إلى 20": "ربط العد بالحركة (القفز مع العد).",
         "التركيز على نشاط لمدة 15 دقيقة": "زيادة وقت المهام تدريجياً (دقيقة كل يوم).",
         "احترام الدور والقوانين": "استخدام ألعاب الأدوار والقصص الاجتماعية.",
         "التحكم في الانفعالات": "تدريبه على تقنيات التنفس عند الغضب.",
         "الاعتماد على النفس": "تشجيعه على أداء مهام بسيطة بمفرده ومكافأته.",
         "تذكر تعليمات من 3 خطوات": "لعبة 'أحضر لي' بطلبات متزايدة.",
         "استخدام المقص بدقة": "قص العجين أو خطوط عريضة مستقيمة أولاً."
    }
    
    # اختيار أهم 4 نقاط ضعف
    for w in stats['weaknesses'][:4]:
        clean_name = w.split(": ")[-1] if ":" in w else w
        if clean_name in RECOMMENDATIONS_MAP:
            action_plan.append((clean_name, RECOMMENDATIONS_MAP[clean_name]))
        else:
            action_plan.append((clean_name, "التدريب المكثف والمتابعة المستمرة."))

    return full_text, action_plan

def generate_text_report(student_name, student_info, evaluation_data, stats, narrative, action_plan):
    report = []
    report.append(f"تقرير التقييم الشامل - {student_name}")
    report.append("="*40)
    report.append(f"المستوى: {student_info.get('class_level')}")
    report.append(f"النتيجة العامة: {stats['overall_percentage']:.1f}%")
    report.append("-" * 40)
    report.append(narrative)
    report.append("-" * 40)
    report.append("الخطة المقترحة:")
    for k, v in action_plan:
        report.append(f"* {k}: {v}")
    
    return "\n".join(report)

