import json
import os
import random

DATA_FILE = "students_data.json"

# --- ثوابت التقييم ---
RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]
RATING_MAP = {"غير مكتسب": 0, "في طريق الاكتساب": 1, "مكتسب": 2}

# --- الدوال المساعدة لإدارة البيانات ---
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
    # (نفس منطق الحساب السابق دون تغيير)
    academic_total, academic_max = 0, 0
    behavioral_total, behavioral_max = 0, 0
    weaknesses, strengths = [], []
    
    if "academic" in evaluations:
        for subj, skills in evaluations["academic"].items():
            for skill, score in skills.items():
                academic_total += score; academic_max += 2
                if score == 0: weaknesses.append(skill)
                elif score == 2: strengths.append(skill)
    
    if "behavioral" in evaluations:
        for main, subs in evaluations["behavioral"].items():
            for sub, skills in subs.items():
                for skill, score in skills.items():
                    behavioral_total += score; behavioral_max += 2
                    if score == 0: weaknesses.append(skill)
                    elif score == 2: strengths.append(skill)

    return {
        "academic_percentage": (academic_total / academic_max * 100) if academic_max else 0,
        "behavioral_percentage": (behavioral_total / behavioral_max * 100) if behavioral_max else 0,
        "overall_percentage": ((academic_total+behavioral_total)/(academic_max+behavioral_max)*100) if (academic_max+behavioral_max) else 0,
        "weaknesses": weaknesses,
        "strengths": strengths
    }

# ==============================================================================
# المحرك الذكي للتحليل (تم التعديل لدعم الجنس بدقة)
# ==============================================================================
def analyze_student_performance(name, data, gender="ذكر"):
    stats = calculate_scores(data)
    ac_score = stats['academic_percentage']
    beh_score = stats['behavioral_percentage']
    overall = stats['overall_percentage']

    # 1. ضبط المتغيرات اللغوية
    is_female = (gender == "أنثى")
    
    T = {
        "student": "المتعلمة" if is_female else "المتعلم",
        "demonstrative": "هذه" if is_female else "هذا",
        "pronoun": "هي" if is_female else "هو",
        "verb_start": "ت" if is_female else "ي",  # تـتميز / يـتميز
        "suffix": "ها" if is_female else "ه",     # أداؤها / أداؤه
        "adj_suffix": "ة" if is_female else ""    # متميز/ة
    }

    narrative_parts = []

    # --- الجزء 1: الافتتاحية (حسب الأداء العام) ---
    if overall >= 85:
        texts = [
            f"أبان{T['adj_suffix']} {T['student']} **{name}** عن قدرات استثنائية وجاهزية عالية للتعلم، مما يعكس نضجاً مبكراً في المهارات.",
            f"{T['verb_start']}تميز {T['student']} **{name}** بحضور ذهني متوقد، وقد أظهر{T['adj_suffix']} استيعاباً سريعاً للمفاهيم."
        ]
    elif overall >= 60:
        texts = [
            f"{T['verb_start']}سير {T['student']} **{name}** بخطى ثابتة في المسار التعليمي، {T['verb_start']}بدي تجاوباً إيجابياً مع الأنشطة.",
            f"أظهر{T['adj_suffix']} {T['student']} **{name}** تطوراً ملحوظاً في اكتساب المهارات الأساسية مع وجود فرص للتحسين."
        ]
    else:
        texts = [
            f"{T['verb_start']}واجه {T['student']} **{name}** بعض التحديات في التكيف، مما يتطلب دعماً خاصاً لتجاوز الصعوبات.",
            f"تشير النتائج إلى حاجة {T['student']} **{name}** لبرنامج دعم مكثف لتعزيز المكتسبات الأساسية."
        ]
    narrative_parts.append(random.choice(texts))

    # --- الجزء 2: التحليل المعرفي (بناءً على الأكاديمي) ---
    if ac_score >= 80:
        narrative_parts.append(f"من الناحية المعرفية، {T['verb_start']}متلك قدرة ممتازة على التحليل والربط، و{T['verb_start']}ظهر شغفاً بالتعلم الذاتي.")
    elif ac_score >= 50:
        narrative_parts.append(f"{T['verb_start']}ستجيب جيداً للمحفزات التعليمية، لكن{T['suffix']} بحاجة للتكرار لترسيخ المعلومات.")
    else:
        narrative_parts.append(f"{T['verb_start']}جد بعض الصعوبة في التعامل مع المفاهيم المجردة، و{T['verb_start']}فضل الاعتماد على الوسائل المحسوسة.")

    # --- الجزء 3: التحليل السلوكي ---
    if beh_score >= 80:
        narrative_parts.append(f"اجتماعياً، {T['pronoun']} شخصية محبوبة و{T['verb_start']}حترم القواعد الصفية، و{T['verb_start']}شارك بفاعلية مع الزملاء.")
    elif beh_score >= 50:
        narrative_parts.append(f"سلوكياً، {T['verb_start']}حتاج إلى بعض التوجيه لزيادة التركيز والانضباط أثناء الأنشطة الجماعية.")
    else:
        narrative_parts.append(f"يلاحظ تشتت انتباه{T['suffix']} بسرعة، مما يستدعي تدخلاً لتعزيز مهارات الانضباط والهدوء.")

    # --- الجزء 4: الخاتمة ---
    closing = f"ختاماً، نؤكد أن تشجيع {T['student']} ومتابعة {T['demonstrative']} المكتسبات سيحدث فرقاً كبيراً في مستوا{T['suffix']}."
    narrative_parts.append(closing)

    full_text = "\n\n".join(narrative_parts)

    # --- الخطة العلاجية ---
    # (نفس المنطق السابق - اختيار أهم نقاط الضعف)
    action_plan = []
    RECOMMENDATIONS_MAP = {
         "يسمي الحروف الهجائية المدروسة": "استخدام بطاقات الصنفرة والتشكيل بالعجين.",
         "يمسك القلم بطريقة صحيحة": "تمارين تقوية عضلات اليد الدقيقة.",
         "يعد شفوياً إلى 20": "ربط العد بالحركة والأنشطة الإيقاعية.",
         "التركيز على نشاط لمدة 15 دقيقة": "زيادة وقت المهام تدريجياً وتقليل المشتتات.",
         "التحكم في الانفعالات": "التدريب على مهارات التنفس والتعبير اللفظي."
    }
    
    for w in stats['weaknesses'][:4]: 
        clean_name = w # تبسيط الاسم إذا لزم الأمر
        rec = RECOMMENDATIONS_MAP.get(clean_name, "تكثيف التدريب المنزلي والمتابعة المستمرة.")
        action_plan.append((clean_name, rec))

    return full_text, action_plan

def generate_text_report(student_name, student_info, evaluation_data, stats, narrative, action_plan):
    # دالة بسيطة لإنشاء النص (لزر التحميل TXT)
    lines = [f"تقرير: {student_name}", "="*20, narrative, "-"*20, "الخطة:"]
    for k, v in action_plan: lines.append(f"- {k}: {v}")
    return "\n".join(lines)

