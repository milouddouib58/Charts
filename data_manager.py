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

