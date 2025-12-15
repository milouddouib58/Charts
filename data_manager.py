import json
import os
import random
from datetime import datetime

DATA_FILE = "students_data.json"

# --- ثوابت التقييم ---
RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]
RATING_MAP = {"غير مكتسب": 0, "في طريق الاكتساب": 1, "مكتسب": 2}

# --- بنك العبارات التربوية (The Enrichment Bank) ---
# يحتوي على جمل متنوعة لتجنب التكرار ولإعطاء صبغة إنسانية
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
    "cognitive_style": { # تحليل نمط التفكير
        "analytical": "من الناحية المعرفية، يميل {pronoun} إلى التفكير المنطقي والمنظم، ويظهر شغفاً بالأنشطة التي تتطلب دقة وتركيزاً، مثل التعامل مع الأرقام والأشكال.",
        "verbal": "يتميز {pronoun} بطلاقة لغوية وقدرة تعبيرية لافتة، حيث يعتمد في تعلمه بشكل كبير على التواصل اللفظي وسرد القصص والتفاعل الحي.",
        "balanced": "يظهر {pronoun} مرونة ذهنية رائعة، حيث يتنقل بسلاسة بين المهام اللغوية والمنطقية، مما يعكس توازناً في نمو نصفي الدماغ.",
        "struggling": "يجد {pronoun} بعض الصعوبة في معالجة المعلومات المجردة والمتسلسلة، ويفضل الاعتماد على الوسائل الحسية والملموسة لفهم المطلوب."
    },
    "social_emotional": { # التحليل النفسي والاجتماعي
        "leader": "اجتماعياً، يتمتع بشخصية قيادية محبوبة، ويجيد إدارة المواقف مع أقرانه بذكاء عاطفي، مما يجعله عنصراً فعالاً في العمل الجماعي.",
        "introvert": "يميل {pronoun} إلى الهدوء والتأمل، ويفضل العمل الفردي أو ضمن مجموعات صغيرة، وهو ما يعكس شخصية حساسة ودقيقة الملاحظة.",
        "impulsive": "يتسم سلوكه ببعض الاندفاع والحماس الزائد، مما يتطلب توجيه هذه الطاقة الحركية نحو أنشطة بناءة لتعزيز التركيز.",
        "dependent": "يحتاج {pronoun} إلى تشجيع مستمر ودعم عاطفي للشعور بالأمان، حيث يتردد أحياناً في المبادرة خوفاً من الخطأ."
    },
    "work_habits": { # عادات العمل
        "focused": "يتميز بجلد وصبر في إنجاز المهام، ولديه قدرة عالية على التركيز لفترات طويلة دون تشتت.",
        "distracted": "يتأثر انتباهه بسهولة بالمشوشات الخارجية، مما يستدعي تقسيم المهام الطويلة إلى مراحل قصيرة للحفاظ على تفاعله.",
        "creative": "يظهر لمسات إبداعية في إنجاز أعماله، وغالباً ما يبحث عن حلول غير تقليدية للمشكلات التي تواجهه."
    },
    "closing": [
        "ختاماً، نحن متفائلون جداً بمستقبل {student_type}، ونؤكد أن التعاون المثمر بين البيت والمدرسة هو المفتاح لصقل هذه الجوهرة.",
        "إن المسار التعليمي لـ{student_type} يبشر بالخير، ومع استمرار الدعم والتحفيز، نتوقع أن يحقق قفزات نوعية في الفصل القادم.",
        "نوصي بالتركيز على الجانب النفسي وتعزيز الشعور بالإنجاز، فالراحة النفسية هي البوابة الأولى للتعلم."
    ]
}

# --- الدوال المساعدة ---

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
                academic_total += score
                academic_max += 2
                if score == 0: weaknesses.append(f"{subj}: {skill}")
                elif score == 2: strengths.append(skill)
    
    # حساب السلوكي
    if "behavioral" in evaluations:
        for main, subs in evaluations["behavioral"].items():
            for sub, skills in subs.items():
                for skill, score in skills.items():
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
        "strengths": strengths,
        "academic_raw": (academic_total, academic_max), # نحتاجها للتحليل التفصيلي
        "behavioral_raw": (behavioral_total, behavioral_max)
    }

# ==============================================================================
# المحرك الذكي للتحليل (The Smart Analysis Engine)
# ==============================================================================
def analyze_student_performance(name, data):
    # 1. استخراج المعلومات الأساسية
    stats = calculate_scores(data)
    ac_score = stats['academic_percentage']
    beh_score = stats['behavioral_percentage']
    
    # تحديد الجنس (يفترض أن يكون مخزناً، وإلا نفترض ذكر افتراضياً)
    # ملاحظة: data هنا هي evaluations، نحتاج info من الجلسة في app.py
    # للتبسيط، سنعتمد على دالة مساعدة تمرر الجنس أو نكشفه من الاسم (غير دقيق)
    # سنقوم بصياغة جمل محايدة أو استخدام متغيرات استبدال في app.py
    # الحل الأفضل: افترض أنك ستمرر info للدالة مستقبلاً، هنا سنستخدم placeholder
    
    # سنستخدم متغيرات للاستبدال لاحقاً
    tags = {
        "{name}": name,
        "{student_type}": "المتعلم", # يمكن تغييرها لـ المتعلمة في app.py
        "{pronoun}": "هو" # أو هي
    }

    narrative_parts = []

    # --- الخطوة 1: اختيار المقدمة بناءً على الأداء العام ---
    if stats['overall_percentage'] >= 85:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["excellent"])
    elif stats['overall_percentage'] >= 60:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["good"])
    else:
        opening = random.choice(ANALYSIS_TEMPLATES["opening"]["needs_support"])
    
    narrative_parts.append(opening)

    # --- الخطوة 2: تحليل النمط المعرفي (Cognitive) ---
    # نقارن بين درجات اللغة والرياضيات (إذا توفرت)
    # هذا يتطلب البحث في تفاصيل data
    math_score = 0
    lang_score = 0
    
    if "academic" in data:
        # محاولة تقديرية بسيطة
        for subj, skills in data["academic"].items():
            if "رياضيات" in subj:
                math_score = sum(skills.values())
            elif "لغة" in subj:
                lang_score = sum(skills.values())
    
    if ac_score < 50:
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["struggling"]
    elif math_score > lang_score + 2: # متفوق في الرياضيات
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["analytical"]
    elif lang_score > math_score + 2: # متفوق في اللغة
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["verbal"]
    else:
        cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["balanced"]
        
    narrative_parts.append(cog_text)

    # --- الخطوة 3: تحليل الشخصية والسلوك (Psycho-Social) ---
    # نعتمد على نسبة السلوك وبعض الكلمات المفتاحية في نقاط القوة/الضعف
    
    weakness_str = " ".join(stats['weaknesses'])
    strength_str = " ".join(stats['strengths'])
    
    if beh_score >= 85:
        soc_text = ANALYSIS_TEMPLATES["social_emotional"]["leader"]
    elif "خجل" in weakness_str or "مشاركة" in weakness_str:
        soc_text = ANALYSIS_TEMPLATES["social_emotional"]["introvert"]
    elif "اندفاع" in weakness_str or "تركيز" in weakness_str or "حركة" in weakness_str:
        soc_text = ANALYSIS_TEMPLATES["social_emotional"]["impulsive"]
    elif beh_score < 50:
         soc_text = ANALYSIS_TEMPLATES["social_emotional"]["dependent"]
    else:
         # حالة افتراضية جيدة
         soc_text = "يظهر تفاعلاً اجتماعياً متزناً، ويبدي احتراماً للقواعد الصفية مع رغبة في المشاركة."

    narrative_parts.append(soc_text)

    # --- الخطوة 4: عادات العمل ---
    if "تركيز" in strength_str or "إكمال" in strength_str:
        work_text = ANALYSIS_TEMPLATES["work_habits"]["focused"]
    elif "تشتت" in weakness_str:
        work_text = ANALYSIS_TEMPLATES["work_habits"]["distracted"]
    else:
        work_text = "يمتلك عادات عمل جيدة وقابلة للتطور، ويحتاج فقط إلى التذكير المستمر بالوقت."
    
    narrative_parts.append(work_text)

    # --- الخطوة 5: الخاتمة ---
    closing = random.choice(ANALYSIS_TEMPLATES["closing"])
    narrative_parts.append(closing)

    # تجميع النص
    full_text = "\n\n".join(narrative_parts)
    
    # تطبيق الاستبدالات (يمكن تحسين هذا الجزء بتمرير الجنس للدالة)
    for k, v in tags.items():
        full_text = full_text.replace(k, v)
        
    # --- الخطة العلاجية (مبسطة ونظيفة) ---
    # نأخذ أهم 3 نقاط ضعف فقط
    action_plan = []
    # قاموس التوصيات (نسخة مختصرة للأمثلة)
    RECOMMENDATIONS_MAP = {
         "يسمي الحروف الهجائية المدروسة": "استخدام بطاقات الصنفرة والتشكيل بالعجين.",
         "يمسك القلم بطريقة صحيحة": "تمارين تقوية عضلات اليد (لقط الحبوب، العصر).",
         "يعد شفوياً إلى 20": "ربط العد بالحركة (القفز مع العد).",
         "التركيز على نشاط لمدة 15 دقيقة": "زيادة وقت المهام تدريجياً (دقيقة كل يوم).",
         "احترام الدور والقوانين": "استخدام ألعاب الأدوار والقصص الاجتماعية.",
         "التحكم في الانفعالات": "تدريبه على تقنيات التنفس عند الغضب.",
         "الاعتماد على النفس": "تشجيعه على أداء مهام بسيطة بمفرده ومكافأته."
    }
    
    for w in stats['weaknesses'][:4]: # نأخذ أول 4 فقط
        # تنظيف الاسم (قد يحتوي على اسم المادة)
        clean_name = w.split(": ")[-1] if ":" in w else w
        if clean_name in RECOMMENDATIONS_MAP:
            action_plan.append((clean_name, RECOMMENDATIONS_MAP[clean_name]))
        else:
            # توصية عامة إذا لم توجد في القاموس
            action_plan.append((clean_name, "تكثيف التدريب المنزلي والمتابعة المستمرة."))

    return full_text, action_plan

def generate_text_report(student_name, student_info, evaluation_data, stats, narrative, action_plan):
    # (نفس الدالة السابقة، لا تحتاج تعديل كبير، فقط لتوليد ملف TXT)
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

