import json
import os
import random

DATA_FILE = "students_data.json"

# ==============================================================================
# 1. الثوابت والبيانات
# ==============================================================================

RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]
RATING_MAP = {"غير مكتسب": 0, "في طريق الاكتساب": 1, "مكتسب": 2}

ACADEMIC_SUBJECTS = {
    "المجال اللغوي": [
        "يتعرف على الصفات والألوان وظروف المكان ويعبر بها",
        "يعبر باستخدام جمل فعلية مركبة والزمن الماضي",
        "يستخرج ويربط بين الأصوات والحروف المدروسة",
        "يرسم الحروف المدروسة (ف، د، ز، ج، ت، ح، س، ش، خ، م) بشكل صحيح"
    ],
    "الرياضيات": [
        "يعد ويتعرف على الأعداد من 1 إلى 8 والأعداد الرتبية",
        "يميز الاتجاهات (يمين/يسار) ومفهومي الانطلاق والوصول",
        "يتعرف على الأشكال الهندسية المدروسة",
        "يقارن بين الكميات (أكثر من/أقل من، بقدر) والأطوال",
        "يصنف العناصر ضمن تجمعات"
    ],
    "التربية الإسلامية والمدنية": [
        "يحفظ سورتي الفلق والنصر وحديث الإتقان ودعاء طلب العلم",
        "يتحلى بآداب النظافة والصدق والعطف والاحترام والتسامح والأمانة",
        "يتعرف على قواعد التغذية السليمة وفوائد الماء",
        "يتعرف على محيطه (الحي، المدينة، المهن، وسائل الاتصال)",
        "يحافظ على البيئة (زراعة النباتات، تصنيف النفايات)"
    ],
    "التربية العلمية والتكنولوجية": [
        "يميز بين مصادر الغذاء (نباتي وحيواني)",
        "يتعرف على الكائنات الحية وخصائصها (تنفس وتغذية النبات)",
        "يدرك وجود وأهمية الماء في الطبيعة",
        "يتعرف على المادة ومشتقاتها والأدوات التكنولوجية الحديثة"
    ],
    "التربية الفنية": [
        "يشتق الألوان ويلون الفضاءات والأشكال",
        "يشكل المسطحات والمجسمات (هرم، مكعب، أسطوانة)",
        "يميز أصوات الطبيعة ويؤدي إيقاعات بالأطراف والآلات",
        "يؤدي أدواراً مسرحية وتعبيرات جسدية وصوتية"
    ],
    "التربية البدنية الإيقاعية": [
        "يشارك بفعالية في الألعاب الرياضية الجماعية (ككرة القدم والتتابع)",
        "يؤدي وضعيات رياضية متنوعة (المشي، الجري، القفز، التسلق، الرمي)",
        "يستعمل الأدوات الرياضية كالحلقات ويؤدي رقصات رياضية"
    ]
}

BEHAVIORAL_SKILLS = {
    "الوظائف التنفيذية": {
        "الانتباه والذاكرة": ["التركيز على نشاط لمدة 15 دقيقة", "إكمال المهمة للنهاية دون تشتت", "تذكر تعليمات من 3 خطوات", "تذكر أحداث قصة قصيرة", "ينتبه للتفاصيل المهمة"],
        "المرونة والتفكير": ["الانتقال بين الأنشطة بسلاسة", "تقبل التغيير في الروتين", "إدراك التسلسل المنطقي للأحداث", "حل المشكلات البسيطة", "يطرح أسئلة ذكية"]
    },
    "الكفاءة الاجتماعية": {
        "التطور الشخصي": ["التعبير عن المشاعر بدقة", "الثقة بالنفس والمبادرة", "المشاركة في اللعب الجماعي", "احترام الدور والقوانين", "التحكم في الانفعالات", "تقدير الذات والإيجابية"],
        "المهارات العاطفية": ["التعاطف مع الآخرين", "التعبير عن الحاجة للمساعدة", "تحمل المسؤولية", "التكيف مع المواقف الجديدة"]
    },
    "المهارات الحركية": {
        "النمو الحركي": ["استخدام المقص بدقة", "تلوين داخل الحدود", "التوازن (الوقوف على قدم واحدة)", "التقاط الكرة ورميها", "القفز على قدمين معاً"],
        "الاستقلالية": ["الاعتماد على النفس (لبس، حمام، ترتيب)", "تناول الطعام بنفسه", "ترتيب الأدوات المدرسية", "العناية بالنظافة الشخصية"]
    }
}

# --- بنك العبارات التربوية (المصحح لغوياً والبيداغوجي 100%) ---
# المفاتيح المستخدمة:
# {vs} = بداية الفعل (يـ / تـ)
# {s} = ضمير متصل (ه / ها)
# {adj} = تاء التأنيث للصفات (ة / "")
# {student} = المتعلم / المتعلمة
# {name} = اسم التلميذ
# {dem} = هذا / هذه

ANALYSIS_TEMPLATES = {
    "opening": {
        "excellent": [
            "أبان{adj} {student} {name} عن كفاءة عالية في استيعاب الكفاءات القاعدية المقررة، محققاً تقدماً نوعياً وشاملاً في مختلف المجالات التعلمية.",
            "{vs}تميز {student} {name} بجاهزية ذهنية ممتازة، حيث {vs}ظهر تحكماً دقيقاً في توظيف المكتسبات اللغوية والرياضية التي تم تناولها خلال هذه المرحلة.",
            "أظهر{adj} {student} {name} مستوى أكاديمياً متميزاً، حيث {vs}جمع ببراعة بين الفهم السريع للمفاهيم العلمية والتطبيق المتقن للمهارات الأساسية."
        ],
        "good": [
            "{vs}سير {student} {name} بخطى ثابتة نحو تحقيق الأهداف التعلمية المسطرة، حيث {vs}ظهر تجاوباً إيجابياً وملحوظاً مع التعلمات اللغوية والعلمية المقررة.",
            "أظهر{adj} {student} {name} تطوراً مستمراً في اكتساب المعارف الأساسية، مع نمو تدريجي وواضح في مهارات{s} المعرفية والتواصلية داخل القسم.",
            "{vs}متلك {student} {name} إرادة طيبة للتعلم، و{vs}بذل جهداً مقدراً لمواكبة وتيرة بناء التعلمات في مختلف الأنشطة المبرمجة."
        ],
        "needs_support": [
            "{vs}واجه {student} {name} بعض التحديات في مسايرة وتيرة بناء التعلمات، مما يتطلب تكييفاً للمفاهيم الرياضية واللغوية لدعم استيعاب{s} التدريجي.",
            "تشير الملاحظات إلى أن {student} {name} {vs}مر بمرحلة بناء أساسيات تتطلب دعماً فردياً مكثفاً لترسيخ المكتسبات وتجاوز صعوبات الاستيعاب.",
            "{vs}حتاج {student} {name} إلى مرافقة بيداغوجية مستمرة لتوظيف طاقات{s} الكامنة، وتحفيز{s} على التفاعل الإيجابي مع الأنشطة الصفية."
        ]
    },
    "cognitive_style": { 
        "analytical": "من الناحية المعرفية، {vs}ظهر تفوقاً ملموساً في المجالين الرياضي والعلمي، حيث {vs}تحكم في بناء المفاهيم العددية والتنظيم الفضائي، مع قدرة واضحة على تصنيف واستنتاج خصائص الأشياء.",
        "verbal": "{vs}تميز بتقدم لافت في المجال اللغوي، حيث {vs}جيد التعبير الشفوي وتوظيف الصفات، مع قدرة ممتازة على التمييز السمعي للأصوات وتجريد ورسم الحروف المدروسة.",
        "balanced": "{vs}عكس مسار{s} التعلمي توازناً ممتازاً؛ حيث {vs}جمع بين التمكن من أنشطة القراءة والتخطيط لغوياً، وبين الاستيعاب السليم للعمليات المنطقية والأعداد رياضياً.",
        "struggling": "{vs}جد صعوبة نسبية في تجريد المفاهيم اللغوية والرياضية، و{vs}حتاج إلى توظيف مكثف للوسائل الحسية والملموسة لترسيخ الأعداد والحروف وتجاوز هذه العقبة."
    },
    "social_emotional": {
        "leader": "اجتماعياً، {vs}جسد القيم المدروسة في التربية الإسلامية والمدنية بامتياز، حيث {vs}ظهر روحاً قيادية وتفاعلاً إيجابياً في تطبيق قواعد النظافة، التعاون، واحترام الآخرين.",
        "introvert": "{vs}ميل إلى الهدوء في القسم، إلا أن{s} {vs}ستوعب جيداً قواعد الحياة الجماعية والسلوكيات المدنية المدروسة، حيث {vs}فضل تطبيقها بصمت وتأمل بعيداً عن الصخب.",
        "impulsive": "{vs}تسم سلوك{s} بالحركية والاندفاع، مما {vs}جعل{s} يتألق في أنشطة المجال البدني والألعاب الجماعية، مع الحاجة لتهذيب هذه الطاقة في مواقف التعلم التي تتطلب هدوءاً.",
        "dependent": "{vs}ظهر تردداً في المبادرات الاجتماعية، و{vs}حتاج إلى تعزيز ثقت{s} بنفس{s} لترجمة ما تعلم{s} في مجالي التربية الإسلامية والمدنية إلى ممارسات وسلوكيات يومية واثقة."
    },
    "work_habits": {
        "focused": "{vs}تميز بتركيز عالٍ ودقة في إنجاز المهام، وهو ما ينعكس جلياً في جودة أعمال{s} في المجال الفني من تلوين وتشكيل، والتزام{s} الصارم بتعليمات العمل.",
        "distracted": "{vs}تأثر انتباه{s} بسرعة بالمحيط، مما يستوجب دمج الألعاب الإيقاعية والأنشطة الحركية ضمن مسار{s} التعلمي لتجديد نشاط{s} وضمان استمرارية تركيز{s}.",
        "creative": "{vs}متلك حساً فنياً وإبداعياً عالياً، يتجلى بوضوح في أنشطة التربية التشكيلية والمسرح، حيث {vs}ضفي لمسة شخصية ومميزة على أداء الأدوار واستعمال الألوان."
    }
}

# ==============================================================================
# 2. الدوال المساعدة
# ==============================================================================

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def save_student_info(name, info):
    data = load_data()
    if name not in data: data[name] = {"info": info, "evaluations": {}, "history": []}
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
                    academic_total += score; academic_max += 2
                    if score == 0: weaknesses.append(f"{subj}: {skill}")
                    elif score == 2: strengths.append(skill)
    
    if "behavioral" in evaluations:
        for main, subs in evaluations["behavioral"].items():
            for sub, skills in subs.items():
                for skill, score in skills.items():
                    if isinstance(score, int):
                        behavioral_total += score; behavioral_max += 2
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
# 3. المحرك الذكي للتحليل (المصحح)
# ==============================================================================
def analyze_student_performance(name, data, gender="ذكر"):
    stats = calculate_scores(data)
    ac_score = stats['academic_percentage']
    beh_score = stats['behavioral_percentage']
    
    # --- إعداد متغيرات اللغة بدقة ---
    is_female = (gender == "أنثى")
    
    T = {
        "{name}": name,
        "{student}": "المتعلمة" if is_female else "المتعلم",
        "{dem}": "هذه" if is_female else "هذا",
        "{vs}": "ت" if is_female else "ي",      
        "{s}": "ها" if is_female else "ه",      
        "{adj}": "ت" if is_female else "",      
        "{adj_p}": "ها" if is_female else "ه",  
    }

    narrative_parts = []

    # 1. الافتتاحية
    if stats['overall_percentage'] >= 85:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["excellent"])
    elif stats['overall_percentage'] >= 60:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["good"])
    else:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["needs_support"])
    narrative_parts.append(opening)

    # 2. المعرفي
    if ac_score < 50:
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["struggling"]
    elif ac_score >= 85:
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["analytical"]
    else:
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["balanced"]
    narrative_parts.append(cog_text)

    # 3. السلوكي
    if beh_score >= 85:
        soc_text = ANALYSIS_TEMPLATES["social_emotional"]["leader"]
    elif beh_score < 50:
         soc_text = ANALYSIS_TEMPLATES["social_emotional"]["dependent"]
    else:
         soc_text = "{vs}ظهر تفاعلاً اجتماعياً متزناً، و{vs}بدي احتراماً للقواعد الصفية مع رغبة في المشاركة."
    narrative_parts.append(soc_text)

    # 4. عادات العمل
    weakness_str = " ".join(stats['weaknesses'])
    if "تشتت" in weakness_str or "تركيز" in weakness_str:
        work_text = ANALYSIS_TEMPLATES["work_habits"]["distracted"]
    else:
        work_text = ANALYSIS_TEMPLATES["work_habits"]["focused"] if ac_score > 70 else "{vs}حتاج إلى مزيد من المثابرة لإتمام المهام."
    narrative_parts.append(work_text)

    # 5. الخاتمة
    closing = "ختاماً، نوصي بالتركيز على الجانب النفسي وتعزيز الشعور بالإنجاز."
    narrative_parts.append(closing)

    # --- تجميع النص وتطبيق الاستبدال ---
    full_text = "\n\n".join(narrative_parts)
    for k, v in T.items():
        full_text = full_text.replace(k, v)
    
    if is_female:
        full_text = full_text.replace("متميز ", "متميزة ")
        full_text = full_text.replace("مبدع ", "مبدعة ")
    
    # --- الخطة العلاجية ---
    action_plan = []
    # تم تحديث مفاتيح الخطة العلاجية لتتناسب مع الكفاءات الجديدة في التحضيري
    REC_MAP = {
         "يستخرج ويربط بين الأصوات والحروف المدروسة": "استخدام بطاقات الصنفرة والتشكيل بالعجين للحروف.",
         "يرسم الحروف المدروسة (ف، د، ز، ج، ت، ح، س، ش، خ، م) بشكل صحيح": "تمارين تقوية عضلات اليد الدقيقة والتخطيط على الرمل.",
         "يعد ويتعرف على الأعداد من 1 إلى 8 والأعداد الرتبية": "ربط العد بالحركة (القفز مع العد) واستخدام الخشيبات.",
         "التركيز على نشاط لمدة 15 دقيقة": "زيادة وقت المهام تدريجياً (دقيقة كل يوم).",
         "احترام الدور والقوانين": "استخدام ألعاب الأدوار والقصص الاجتماعية.",
         "التحكم في الانفعالات": "تدريبه على تقنيات التنفس عند الغضب.",
         "الاعتماد على النفس (لبس، حمام، ترتيب)": "تشجيعه على أداء مهام بسيطة بمفرده ومكافأته.",
         "تذكر تعليمات من 3 خطوات": "لعبة 'أحضر لي' بطلبات متزايدة.",
         "استخدام المقص بدقة": "قص العجين أو خطوط عريضة مستقيمة أولاً."
    }
    
    for w in stats['weaknesses'][:4]:
        clean = w.split(": ")[-1] if ":" in w else w
        action_plan.append((clean, REC_MAP.get(clean, "التدريب المكثف والمتابعة المستمرة.")))

    return full_text, action_plan

def generate_text_report(student_name, student_info, evaluation_data, stats, narrative, action_plan):
    report = [f"تقرير: {student_name}", "="*20, narrative, "-"*20]
    for k, v in action_plan: report.append(f"* {k}: {v}")
    return "\n".join(report)
