import json
import os
import streamlit as st
from openai import OpenAI

# ==========================================
# 1. إعدادات مسار تخزين البيانات
# ==========================================
DATA_FILE = "students_data.json"

# ==========================================
# 2. الثوابت والقوائم (Constants)
# ==========================================
ACADEMIC_SUBJECTS = {
    "اللغة العربية": ["القراءة", "الكتابة", "التواصل الشفهي", "الفهم والاستيعاب"],
    "الرياضيات": ["الأعداد والحساب", "الهندسة والفضاء", "القياس", "حل المسائل"],
    "التربية الإسلامية": ["حفظ القرآن", "الفهم والاستيعاب", "السيرة والآداب"],
    "التربية العلمية": ["اكتشاف المحيط", "البيئة والطبيعة"]
}

BEHAVIORAL_SKILLS = {
    "المهارات الاجتماعية والشخصية": {
        "التفاعل والاندماج": ["المشاركة مع الأقران", "العمل الجماعي", "احترام القواعد"],
        "الاستقلالية": ["الاعتماد على النفس", "إدارة الأدوات المدرسية", "المبادرة"]
    },
    "المهارات المعرفية والحركية": {
        "التركيز والانتباه": ["الانتباه أثناء الدرس", "إنجاز المهمة المطلوبة"],
        "التناسق الحركي": ["التحكم في القلم", "الأنشطة اليدوية"]
    }
}

RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]
RATING_MAP = {"غير مكتسب": 0, "في طريق الاكتساب": 1, "مكتسب": 2}

# ==========================================
# 3. دوال إدارة الملفات (Input/Output)
# ==========================================
def load_data():
    """تحميل بيانات الطلاب من ملف JSON"""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}

def save_data(data):
    """حفظ قاموس البيانات بالكامل في ملف JSON"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")

def save_student_info(name, info):
    """حفظ أو تحديث بيانات تلميذ معين"""
    data = load_data()
    if name not in data:
        data[name] = {"info": info, "evaluations": {}}
    else:
        data[name]["info"] = info
    save_data(data)

# ==========================================
# 4. حساب الدرجات والنسب
# ==========================================
def calculate_scores(evals):
    """حساب النسبة المئوية للتقييم الأكاديمي والسلوكي"""
    result = {
        "academic_percentage": 0.0,
        "behavioral_percentage": 0.0,
        "overall_percentage": 0.0
    }
    
    # حساب الأكاديمي
    academic_data = evals.get("academic", {})
    ac_total_score = 0
    ac_max_score = 0
    for subj, skills in academic_data.items():
        for skill, score in skills.items():
            ac_total_score += score
            ac_max_score += 2  # أقصى درجة هي 2 (مكتسب)

    if ac_max_score > 0:
        result["academic_percentage"] = (ac_total_score / ac_max_score) * 100

    # حساب السلوكي
    behavioral_data = evals.get("behavioral", {})
    bh_total_score = 0
    bh_max_score = 0
    for main_cat, sub_cats in behavioral_data.items():
        for sub_cat, skills in sub_cats.items():
            for skill, score in skills.items():
                bh_total_score += score
                bh_max_score += 2

    if bh_max_score > 0:
        result["behavioral_percentage"] = (bh_total_score / bh_max_score) * 100

    # الأداء العام (متوسط الاثنين)
    if ac_max_score > 0 and bh_max_score > 0:
        result["overall_percentage"] = (result["academic_percentage"] + result["behavioral_percentage"]) / 2
    elif ac_max_score > 0:
        result["overall_percentage"] = result["academic_percentage"]
    elif bh_max_score > 0:
        result["overall_percentage"] = result["behavioral_percentage"]

    return result

# ==========================================
# 5. التحليل الذكي عبر Cerebras
# ==========================================
def analyze_student_performance(student_name, evals, gender):
    """
    تحليل بيانات التلميذ باستخدام ذكاء Cerebras 
    لإرجاع تقرير سردي وخطة عمل مقترحة.
    """
    # التحقق من وجود مفتاح API
    try:
        api_key = st.secrets["CEREBRAS_API_KEY"]
    except KeyError:
        return "⚠️ تنبيه: لم يتم العثور على مفتاح Cerebras في إعدادات الأمان (Secrets).", []

    # إعداد عميل الاتصال
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.cerebras.ai/v1",
    )

    # حساب الدرجات لتزويد الذكاء الاصطناعي بها
    scores = calculate_scores(evals)
    
    # تجهيز النص المساعد
    evals_text = json.dumps(evals, ensure_ascii=False)
    pronoun = "التلميذ" if gender == "ذكر" else "التلميذة"

    # صياغة الأوامر (Prompt)
    prompt = f"""
    أنت خبير تربوي ومستشار تعليمي متمرس.
    قم بتحليل نتائج {pronoun} "{student_name}".
    
    النسبة الأكاديمية: {scores['academic_percentage']:.1f}%
    النسبة السلوكية: {scores['behavioral_percentage']:.1f}%
    
    تفاصيل التقييمات (0=غير مكتسب، 1=في طريق الاكتساب، 2=مكتسب):
    {evals_text}

    المطلوب إرجاع الرد بصيغة JSON حصرياً يحتوي على مفتاحين فقط:
    1. "narrative": فقرة واحدة (حوالي 4-6 أسطر) مكتوبة بلغة عربية سليمة، احترافية، ومهنية تلخص مستوى {pronoun} الأكاديمي والسلوكي بشكل مشجع ودقيق، مع ذكر نقاط القوة والنقاط التي تحتاج إلى تحسين.
    2. "action_plan": قائمة (List) تحتوي على 3 نصائح أو خطوات عملية مقترحة لولي الأمر لتحسين أداء {pronoun}. كل خطوة عبارة عن قائمة فرعية من عنصرين ["عنوان الخطوة", "التفاصيل الدقيقة"].

    ملاحظة هامة: يجب أن يكون الرد عبارة عن كود JSON فقط ولا تضف أي نص قبله أو بعده.
    """

    try:
        # استدعاء نموذج llama3.1-70b من Cerebras
        response = client.chat.completions.create(
            model="qwen-3-235b-a22b-instruct-2507", 
            messages=[
                {"role": "system", "content": "أنت خبير تربوي دقيق. استجابتك يجب أن تكون بصيغة JSON صحيحة 100% فقط."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        result_text = response.choices[0].message.content.strip()
        
        # إزالة علامات Markdown إذا أضافها النموذج
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "", 1)
        if result_text.endswith("```"):
            result_text = result_text.rpartition("```")[0]
            
        # استخراج JSON بذكاء وتجاهل أي نص إضافي
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
            clean_json_str = result_text[start_idx:end_idx+1]
        else:
            clean_json_str = result_text # محاولة قراءة النص كاملاً كخطة بديلة
            
        # تحويل النص إلى قاموس بايثون
        parsed_data = json.loads(clean_json_str)
        
        narrative = parsed_data.get("narrative", "تعذر توليد التحليل التربوي بشكل صحيح.")
        action_plan = parsed_data.get("action_plan", [])
        
        return narrative, action_plan

    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e} \nResponse was: {result_text}")
        return "عذراً، قام الذكاء الاصطناعي بتوليد نص غير متوافق مع الهيكل المطلوب. يرجى المحاولة مرة أخرى.", []
    except Exception as e:
        print(f"API Error: {e}")
        return f"حدث خطأ أثناء الاتصال بمزود الذكاء الاصطناعي: {str(e)}", []

# ==========================================
# 6. توليد التقارير النصية 
# ==========================================
def generate_text_report(name, info, data, stats, narrative, action_plan):
    """توليد تقرير نصي شامل كبديل للـ PDF"""
    report = f"=== تقرير التقييم الشامل ===\n"
    report += f"الاسم: {name}\n"
    report += f"المستوى: {info.get('class_level', 'غير محدد')}\n"
    report += f"الأداء العام: {stats.get('overall_percentage', 0):.1f}%\n"
    report += "-" * 30 + "\n"
    
    report += "التحليل التربوي:\n"
    report += f"{narrative}\n"
    report += "-" * 30 + "\n"
    
    report += "خطة العمل:\n"
    for title, detail in action_plan:
         report += f"- {title}: {detail}\n"
         
    return report

