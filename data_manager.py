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
    "اللغة العربية": ["يسمي الحروف الهجائية المدروسة", "يميز صواتياً بين الحروف", "يمسك القلم بطريقة صحيحة", "يكتب اسمه بدقة"],
    "الرياضيات": ["يعد شفوياً إلى 20", "يربط العدد بالمعدود", "يميز الأشكال الهندسية", "يصنف الأشياء حسب خاصية معينة", "يتعرف على الأعداد حتى 10"],
    "التربية الإسلامية والمدنية": ["يحفظ قصار السور المقررة", "يلقي التحية ويردها", "يحافظ على نظافة مكانه", "يتعاون مع زملائه", "يحترم المعلم والزملاء"],
    "التربية العلمية": ["يسمي أعضاء جسم الإنسان", "يميز بين الحواس الخمس", "يعرف الحيوانات الأليفة والمتوحشة"],
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

# --- بنك العبارات التربوية (المصحح لغوياً 100%) ---
# المفاتيح المستخدمة:
# {vs} = بداية الفعل (يـ / تـ)
# {s} = ضمير متصل (ه / ها)
# {adj} = تاء التأنيث للصفات (ة / "")
# {student} = المتعلم / المتعلمة
# {dem} = هذا / هذه

ANALYSIS_TEMPLATES = {
    "opening": {
        "excellent": [
            "أبان{adj} {student} {name} عن قدرات استثنائية وجاهزية عالية للتعلم، مما يعكس نضجاً مبكراً في مهارات التفكير والتحليل.",
            "{vs}تميز {student} {name} بحضور ذهني متوقد وشغف واضح للاكتشاف، وهو ما ظهر جلياً في سرعة استيعاب{s} للمفاهيم المقدمة.",
            "أظهر{adj} {student} {name} مستوى متميزاً من الكفاءة، حيث {vs}جمع بين الذكاء المعرفي والانضباط السلوكي بشكل مثير للإعجاب."
        ],
        "good": [
            "{vs}سير {student} {name} بخطى ثابتة ومطمئنة في الرحلة التعليمية، {vs}بدي تجاوباً إيجابياً مع معظم الأنشطة المقترحة.",
            "أظهر{adj} {student} {name} تطوراً ملحوظاً في اكتساب المهارات الأساسية، مع وجود بعض التفاوت الطبيعي بين الجوانب الأكاديمية والسلوكية.",
            "{vs}تمتع {student} {name} بإمكانيات طيبة وقابلية عالية للتعلم، و{vs}بذل جهداً مشكوراً لمواكبة متطلبات القسم."
        ],
        "needs_support": [
            "{vs}واجه {student} {name} بعض التحديات في التكيف مع البيئة المدرسية، مما يتطلب منا تفهماً وصبراً لاحتواء احتياجات{s} الخاصة.",
            "{vs}مر {student} {name} بمرحلة انتقالية دقيقة، حيث تظهر النتائج حاجت{s} الماسة لدعم فردي مكثف لتعزيز ثقت{s} بنفس{s}.",
            "تشير الملاحظات إلى أن {student} {name} {vs}متلك طاقة كامنة لم يتم توظيفها بعد بالشكل الصحيح، مما يستدعي تدخلاً تربويًا موجهاً."
        ]
    },
    "cognitive_style": { 
        "analytical": "من الناحية المعرفية، {vs}ميل إلى التفكير المنطقي والمنظم، و{vs}ظهر شغفاً بالأنشطة التي تتطلب دقة وتركيزاً، مثل التعامل مع الأرقام والأشكال.",
        "verbal": "{vs}تميز بطلاقة لغوية وقدرة تعبيرية لافتة، حيث {vs}عتمد في تعلم{s} بشكل كبير على التواصل اللفظي وسرد القصص والتفاعل الحي.",
        "balanced": "{vs}ظهر مرونة ذهنية رائعة، حيث {vs}تنقل بسلاسة بين المهام اللغوية والمنطقية، مما يعكس توازناً في نمو نصفي الدماغ.",
        "struggling": "{vs}جد بعض الصعوبة في معالجة المعلومات المجردة والمتسلسلة، و{vs}فضل الاعتماد على الوسائل الحسية والملموسة لفهم المطلوب."
    },
    "social_emotional": {
        "leader": "اجتماعياً، {vs}تمتع بشخصية قيادية محبوبة، و{vs}جيد إدارة المواقف مع الأقران بذكاء عاطفي، مما {vs}جعل{s} عنصراً فعالاً في العمل الجماعي.",
        "introvert": "{vs}ميل إلى الهدوء والتأمل، و{vs}فضل العمل الفردي أو ضمن مجموعات صغيرة، وهو ما يعكس شخصية حساسة ودقيقة الملاحظة.",
        "impulsive": "{vs}تسم سلوك{s} ببعض الاندفاع والحماس الزائد، مما يتطلب توجيه هذه الطاقة الحركية نحو أنشطة بناءة لتعزيز التركيز.",
        "dependent": "{vs}حتاج إلى تشجيع مستمر ودعم عاطفي للشعور بالأمان، حيث {vs}تردد أحياناً في المبادرة خوفاً من الخطأ."
    },
    "work_habits": {
        "focused": "{vs}تميز بجلد وصبر في إنجاز المهام، ولديه{adj_p} قدرة عالية على التركيز لفترات طويلة دون تشتت.",
        "distracted": "{vs}تأثر انتباه{s} بسهولة بالمشوشات الخارجية، مما يستدعي تقسيم المهام الطويلة إلى مراحل قصيرة للحفاظ على تفاعل{s}.",
        "creative": "{vs}ظهر لمسات إبداعية في إنجاز أعمال{s}، وغالباً ما {vs}بحث عن حلول غير تقليدية للمشكلات التي {vs}واجهها."
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
        "{vs}": "ت" if is_female else "ي",      # بداية الفعل المضارع (تكتب/يكتب)
        "{s}": "ها" if is_female else "ه",      # ضمير متصل (كتبها/كتبه)
        "{adj}": "ت" if is_female else "",      # ماضي (أظهرت/أظهر) أو صفة (متميزة) - هنا نستخدم تاء التأنيث للفعل الماضي
        "{adj_p}": "ها" if is_female else "ه",  # لديه/لديها
    }
    # تصحيح خاص لتاء التأنيث في الصفات
    # سنقوم بدمجها في النص مباشرة باستخدام {adj} للفعل الماضي
    # وللصفات سنكتبها يدوياً في القوالب إذا لزم الأمر، أو نستخدم منطقاً بسيطاً

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
    
    # تصحيح إضافي للتاء المربوطة في الصفات إذا كان النص يحتوي على "{adj}" متبقية للصفات
    # في القاموس أعلاه استخدمنا {adj} للفعل الماضي (أظهر/أظهرت).
    # للصفات مثل "متميز/متميزة"، سنضيف قاعدة بسيطة:
    if is_female:
        # استبدال يدوي لبعض الكلمات الشائعة لضمان سلامتها
        full_text = full_text.replace("متميز ", "متميزة ")
        full_text = full_text.replace("مبدع ", "مبدعة ")
    
    # --- الخطة العلاجية ---
    action_plan = []
    REC_MAP = {
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
    
    for w in stats['weaknesses'][:4]:
        clean = w.split(": ")[-1] if ":" in w else w
        action_plan.append((clean, REC_MAP.get(clean, "التدريب المكثف والمتابعة المستمرة.")))

    return full_text, action_plan

def generate_text_report(student_name, student_info, evaluation_data, stats, narrative, action_plan):
    report = [f"تقرير: {student_name}", "="*20, narrative, "-"*20]
    for k, v in action_plan: report.append(f"* {k}: {v}")
    return "\n".join(report)

