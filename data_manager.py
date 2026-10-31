import json
import os
import streamlit as st
from openai import OpenAI

# ==========================================
# 1. إعدادات مسار تخزين البيانات
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "students_data.json")

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
    """حفظ البيانات بصورة ذرية لتقليل خطر تلف الملف عند انقطاع التشغيل."""
    temp_file = DATA_FILE + ".tmp"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(DATA_FILE)), exist_ok=True)
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, DATA_FILE)
        return True
    except Exception as e:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except OSError:
            pass
        print(f"Error saving data: {e}")
        return False


def save_student_info(name, info):
    """حفظ أو تحديث بيانات تلميذ معين"""
    data = load_data()
    if name not in data:
        data[name] = {"info": info, "evaluations": {}}
    else:
        data[name]["info"] = info
    save_data(data)



def apply_group_ratings(students, student_names, rating_path, ratings_by_student):
    """تطبيق تقييم مهارة/مجموعة مهارات على عدة أطفال دفعة واحدة.

    rating_path: tuple مثل ("academic", "اللغة العربية") أو
    ("behavioral", "المهارات الاجتماعية والشخصية", "الاستقلالية").
    القيم المقبولة 0 و1 و2، أما None أو "" فتعني إزالة التقييم السابق
    وترك المهارة بحالة «لم يقيّم بعد».
    يعيد عدد السجلات التي تغيرت.
    """
    from datetime import datetime
    changed = 0
    if not rating_path or rating_path[0] not in ("academic", "behavioral"):
        raise ValueError("مسار التقييم غير صالح")
    for name in student_names:
        if name not in students:
            continue
        record = students[name]
        evaluations = record.setdefault("evaluations", {})
        node = evaluations
        for part in rating_path:
            node = node.setdefault(part, {})
        row = ratings_by_student.get(name, {})
        for skill, value in row.items():
            if value in (None, "", "لم يقيّم بعد"):
                node.pop(skill, None)
            else:
                try:
                    numeric = int(value)
                except (TypeError, ValueError):
                    raise ValueError(f"قيمة تقييم غير صالحة للمهارة: {skill}")
                if numeric not in (0, 1, 2):
                    raise ValueError(f"قيمة تقييم خارج النطاق للمهارة: {skill}")
                node[skill] = numeric
        # تنظيف الحاويات الفارغة الناتجة عن إزالة تقييمات قديمة
        if rating_path[0] == "academic":
            if len(node) == 0:
                evaluations[rating_path[0]].pop(rating_path[1], None)
        else:
            main, sub = rating_path[1], rating_path[2]
            if len(node) == 0:
                evaluations["behavioral"].get(main, {}).pop(sub, None)
            if not evaluations.get("behavioral", {}).get(main):
                evaluations.get("behavioral", {}).pop(main, None)
        evaluations["last_update"] = datetime.now().strftime("%Y-%m-%d")
        changed += 1
    return changed



# ==========================================
# 4. سجل التقييمات الدورية ومتابعة التطور
# ==========================================
def save_assessment_snapshot(student_record, period, school_year, snapshot_date=None):
    """يحفظ لقطة مستقلة للتقييم الحالي داخل سجل الطفل، دون تغيير التقييمات الحالية."""
    from datetime import date
    import copy

    if not isinstance(student_record, dict):
        raise ValueError("سجل الطفل غير صالح")
    period = str(period or "").strip()
    school_year = str(school_year or "").strip()
    if not period or not school_year:
        raise ValueError("يجب تحديد فترة التقييم والسنة الدراسية")

    evaluations = student_record.get("evaluations", {})
    scores = calculate_scores(evaluations)
    if snapshot_date is None:
        snapshot_date = date.today().isoformat()

    history = student_record.setdefault("assessment_history", [])
    if not isinstance(history, list):
        history = []
        student_record["assessment_history"] = history

    # الفترة نفسها في السنة نفسها تمثل لقطة واحدة؛ حفظها مجددًا يحدّثها صراحةً.
    existing_index = next(
        (i for i, item in enumerate(history)
         if item.get("period") == period and item.get("school_year") == school_year),
        None
    )
    snapshot = {
        "period": period,
        "school_year": school_year,
        "date": str(snapshot_date),
        "scores": copy.deepcopy(scores),
        "evaluations": copy.deepcopy({
            "academic": evaluations.get("academic", {}),
            "behavioral": evaluations.get("behavioral", {}),
        }),
    }
    if existing_index is None:
        history.append(snapshot)
        action = "added"
    else:
        history[existing_index] = snapshot
        action = "updated"
    history.sort(key=lambda item: (item.get("school_year", ""), item.get("date", "")))
    return action, snapshot


def compare_assessment_snapshots(first, second):
    """مقارنة النسب بين لقطتين وإرجاع فروق النقاط المئوية."""
    first_scores = first.get("scores", {})
    second_scores = second.get("scores", {})
    keys = ("academic_percentage", "behavioral_percentage", "overall_percentage")
    return {
        key: round(float(second_scores.get(key, 0)) - float(first_scores.get(key, 0)), 1)
        for key in keys
    }


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
    قم بتحليل نتائج {pronoun} دون استخدام اسم الطفل أو أي بيانات تعريفية.
    
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
            model="gpt-oss-120b", 
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



# ==========================================
# 7. استيراد قوائم الأطفال دفعة واحدة
# ==========================================
def _clean_cell(value):
    if value is None:
        return ""
    try:
        # التعامل مع NaN القادمة من pandas دون الاعتماد عليها
        if value != value:
            return ""
    except Exception:
        pass
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    return text


def import_students_rows(rows, existing_data=None):
    """يستورد صفوفاً على شكل قواميس. يعيد البيانات وعدد المضافين والمتجاوزين والأخطاء.

    أسماء الأعمدة المقبولة: الاسم/الاسم واللقب/name/nom؛ تاريخ الميلاد؛ الجنس؛ المستوى؛ رقم التعريف.
    لا يستبدل تقييمات الطفل الموجود عند تكرار اسمه.
    """
    data = dict(existing_data if existing_data is not None else load_data())
    aliases = {
        "name": {"الاسم", "اسم الطفل", "الاسم واللقب", "الاسم الكامل", "الاسم الثلاثي", "name", "full name", "nom", "nom et prénom", "eleve", "élève"},
        "dob": {"تاريخ الميلاد", "الميلاد", "dob", "birth date", "date of birth", "date naissance", "date de naissance"},
        "gender": {"الجنس", "ذكر/أنثى", "gender", "sexe"},
        "level": {"المستوى", "القسم", "المستوى الدراسي", "class", "class level", "niveau", "classe"},
        "id": {"رقم التعريف", "رقم التسجيل", "الرقم", "id", "identifier", "matricule", "رقم الطفل"},
    }
    def norm(value):
        return " ".join(_clean_cell(value).lower().replace("ـ", "").split())
    added = skipped = updated = 0
    errors = []
    seen_in_file = set()
    for row_num, row in enumerate(rows, start=2):
        if not hasattr(row, "items"):
            errors.append(f"السطر {row_num}: صيغة السطر غير صحيحة.")
            continue
        mapped = {}
        for key, value in row.items():
            key_n = norm(key).replace("_", " ")
            for target, names in aliases.items():
                if key_n in {norm(a) for a in names}:
                    mapped[target] = _clean_cell(value)
                    break
        # يدعم أيضاً الترتيب الافتراضي عندما تكون الأعمدة غير معنونة
        name = mapped.get("name", "").strip()
        if not name:
            # قد تكون الأعمدة المرسلة من لصق مباشر ذات أسماء 0,1,2...
            vals = [_clean_cell(v) for v in row.values()]
            if vals and vals[0] and norm(vals[0]) not in {norm(x) for x in aliases["name"]}:
                name = vals[0]
                if len(vals) > 1: mapped.setdefault("dob", vals[1])
                if len(vals) > 2: mapped.setdefault("gender", vals[2])
                if len(vals) > 3: mapped.setdefault("level", vals[3])
                if len(vals) > 4: mapped.setdefault("id", vals[4])
        if not name:
            # تجاهل الصفوف الفارغة أو صف العناوين
            if any(_clean_cell(v) for v in row.values()):
                errors.append(f"السطر {row_num}: الاسم مفقود.")
            else:
                skipped += 1
            continue
        key = name.strip()
        name_key = norm(key)
        if name_key in seen_in_file:
            skipped += 1
            errors.append(f"السطر {row_num}: الاسم مكرر داخل الملف ({key})، تم تجاوز التكرار.")
            continue
        seen_in_file.add(name_key)
        gender = mapped.get("gender", "").strip()
        if gender not in {"ذكر", "أنثى"}:
            g = norm(gender)
            gender = "ذكر" if g in {"m", "male", "garçon", "garcon", "ذكر"} else ("أنثى" if g in {"f", "female", "fille", "انثى", "أنثى"} else "غير محدد")
        level = mapped.get("level", "").strip() or "تحضيري"
        info = {"dob": mapped.get("dob", ""), "gender": gender, "class_level": level}
        if mapped.get("id"):
            info["id"] = mapped["id"]
        # مطابقة غير حساسة لحالة الحروف والمسافات، مع المحافظة على تقييمات السجل الموجود
        existing_name = next((old for old in data if norm(old) == name_key), None)
        if existing_name:
            old_info = data[existing_name].setdefault("info", {})
            for k, v in info.items():
                if v != "" and (k not in old_info or not old_info.get(k)):
                    old_info[k] = v
            updated += 1
        else:
            data[key] = {"info": info, "evaluations": {}}
            added += 1
    return data, {"added": added, "updated": updated, "skipped": skipped, "errors": errors}
