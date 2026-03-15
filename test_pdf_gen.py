from pdf_generator import create_pdf

# تمت إضافة بيانات الطالب لتجنب الخطأ
student_info = {
    "class_level": "القسم التحضيري",
    "dob": "2020-01-01",
    "gender": "ذكر"
}

data = {
    "academic": {
        "الرياضيات": {"العد": 2, "الجمع": 1}
    },
    "behavioral": {
        "الوظائف الذهنية": {
            "الانتباه": {"التركيز": 2}
        }
    },
    "academic_notes": "Good progress",
    "last_update": "2023-10-27"
}

narrative = "هذا نص تجريبي للتحليل التربوي."
action_plan = [("الخطة الأولى", "تفاصيل الخطة الأولى هنا")]

# تم تمرير student_info كمعامل ثاني
pdf_bytes, error = create_pdf("Test Student", student_info, data, narrative, action_plan)

if error:
    print(f"FAILED: {error}")
    exit(1)
else:
    print(f"SUCCESS: Generated {len(pdf_bytes)} bytes")

