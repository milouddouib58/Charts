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
# 5. التحليل الذكي عبر SambaNova Cloud
# ==========================================
def _read_dotenv_setting(name):
    """قراءة قيمة اختيارية من ملف .env بجوار التطبيق دون الحاجة إلى python-dotenv."""
    env_path = os.path.join(BASE_DIR, ".env")
    try:
        with open(env_path, "r", encoding="utf-8-sig") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() != name:
                    continue
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ("\"", "'"):
                    value = value[1:-1]
                return value.strip()
    except (OSError, UnicodeError):
        pass
    return None


def _normalize_sambanova_key(value):
    """تنظيف أخطاء النسخ الشائعة دون تغيير قيمة المفتاح نفسها."""
    if value is None:
        return None
    value = str(value).strip().lstrip("\ufeff")
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("\"", "'"):
        value = value[1:-1].strip()
    # حقل API key يحتاج المفتاح فقط، لا بادئة ترويسة HTTP.
    if value.lower().startswith("bearer "):
        value = value[7:].strip()
    return value or None


def _get_sambanova_setting(name, default=None):
    """الأولوية: Streamlit Secrets ثم environment ثم ملف .env."""
    try:
        value = st.secrets.get(name)
        if value:
            return _normalize_sambanova_key(value) if name == "SAMBANOVA_API_KEY" else str(value).strip()
    except Exception:
        pass
    value = os.environ.get(name)
    if not value:
        value = _read_dotenv_setting(name)
    if not value:
        value = default
    if name == "SAMBANOVA_API_KEY":
        return _normalize_sambanova_key(value)
    return str(value).strip() if value else default


def analyze_student_performance(student_name, evals, gender):
    """تحليل تربوي عبر SambaNova وإرجاع (التحليل، خطة العمل).

    لا يُرسل اسم الطفل إلى المزوّد. يلزم إعداد SAMBANOVA_API_KEY في Secrets
    أو متغيرات البيئة. النموذج الافتراضي قابل للتغيير عبر SAMBANOVA_MODEL.
    """
    api_key = _get_sambanova_setting("SAMBANOVA_API_KEY")
    if not api_key:
        return (
            "⚠️ لم يُضبط مفتاح SambaNova. أضف SAMBANOVA_API_KEY إلى "
            "إعدادات Secrets أو متغيرات البيئة ثم أعد تشغيل التطبيق.", []
        )

    model = _get_sambanova_setting("SAMBANOVA_MODEL", "gpt-oss-120b")
    client = OpenAI(api_key=api_key, base_url="https://api.sambanova.ai/v1", timeout=45.0, max_retries=1)

    scores = calculate_scores(evals)
    evals_text = json.dumps(evals, ensure_ascii=False)
    pronoun = "التلميذ" if gender == "ذكر" else "التلميذة"
    prompt = f"""
أنت خبير تربوي ومستشار تعليمي متمرس في مرحلة ما قبل التمدرس.
حلّل نتائج {pronoun} دون استخدام اسم الطفل أو أي بيانات تعريفية.

النسبة الأكاديمية: {scores.get('academic_percentage', 0):.1f}%
النسبة السلوكية: {scores.get('behavioral_percentage', 0):.1f}%

تفاصيل التقييمات (0=غير مكتسب، 1=في طريق الاكتساب، 2=مكتسب):
{evals_text}

أعد JSON صالحًا فقط يحتوي على مفتاحين:
1. narrative: فقرة عربية مهنية ومشجعة، دقيقة وغير تشخيصية، تذكر نقاط القوة وما يحتاج إلى دعم.
2. action_plan: قائمة من 3 خطوات عملية لولي الأمر، وكل خطوة قائمة من عنصرين: [عنوان الخطوة، التفاصيل].
لا تخترع نتائج غير موجودة، ولا تعتبر المهارات غير المقيمة ضعفًا.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "أنت خبير تربوي دقيق. أعد JSON صالحًا فقط دون Markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )
        result_text = (response.choices[0].message.content or "").strip()
        parsed_data = json.loads(result_text)
        narrative = parsed_data.get("narrative")
        action_plan = parsed_data.get("action_plan")
        if not isinstance(narrative, str) or not narrative.strip():
            raise ValueError("حقل narrative مفقود أو غير صالح")
        if not isinstance(action_plan, list):
            raise ValueError("حقل action_plan ليس قائمة")
        cleaned_plan = []
        for item in action_plan[:3]:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                cleaned_plan.append([str(item[0]), str(item[1])])
            elif isinstance(item, dict):
                title = item.get("title") or item.get("عنوان")
                detail = item.get("details") or item.get("التفاصيل")
                if title and detail:
                    cleaned_plan.append([str(title), str(detail)])
        return narrative.strip(), cleaned_plan

    except Exception as e:
        # رسالة مناسبة للمستخدم مع الاحتفاظ بالتفاصيل في سجل الخادم فقط.
        error_text = str(e)
        print(f"SambaNova API error ({type(e).__name__}): {error_text}")
        status_code = getattr(e, "status_code", None)
        if status_code == 402 or "402" in error_text or "Payment required" in error_text:
            return (
                "تعذر إنشاء التحليل لأن SambaNova رفض الطلب بسبب الفوترة أو عدم توفر رصيد/صلاحية مجانية لهذا الحساب. "
                "تغيير اسم النموذج وحده لا يضمن المجانية؛ تحقق من خطة حسابك قبل إعادة المحاولة.", []
            )
        if status_code == 401 or "401" in error_text or "invalid_api_key" in error_text.lower() or "invalid api key" in error_text.lower():
            return (
                "رفضت SambaNova مفتاح API (401). تأكد أن المفتاح من لوحة SambaCloud الخاصة بـ API Keys، "
                "وليس مفتاح OpenAI أو مفتاح SambaStudio؛ انسخه كاملًا دون مسافات أو بادئة Bearer، "
                "ثم حدّث SAMBANOVA_API_KEY في Secrets أو متغيرات البيئة أو ملف .env وأعد تشغيل التطبيق.", []
            )
        if status_code == 429 or "429" in error_text:
            return "تعذر إنشاء التحليل مؤقتًا بسبب بلوغ حد الطلبات. انتظر قليلًا ثم أعد المحاولة.", []
        if isinstance(e, (json.JSONDecodeError, ValueError)):
            return "وصل رد من مزوّد الذكاء الاصطناعي لكن بنيته غير صالحة. أعد المحاولة لاحقًا.", []
        return "تعذر الاتصال بـ SambaNova أو إكمال التحليل. تحقق من الإنترنت وإعدادات المزوّد ثم أعد المحاولة.", []

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
