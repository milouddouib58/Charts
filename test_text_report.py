import data_manager as dm
from datetime import datetime

# Mock Data
name = "Test Student"
info = {"class_level": "Grade 1", "dob": "2018-01-01"}
data = {
    "academic": {
        "Math": {"Counting": 2}
    },
    "behavioral": {
        "Social": {"General": {"Sharing": 1}}
    }
}
stats = {
    "overall_percentage": 75.0,
    "academic_percentage": 100.0,
    "behavioral_percentage": 50.0,
    "weaknesses": ["Sharing"]
}
narrative = "Good student."
action_plan = [("Sharing", "Practice sharing")]

# Generate Report
report = dm.generate_text_report(name, info, data, stats, narrative, action_plan)

with open("test_output.txt", "w", encoding="utf-8") as f:
    f.write(report)
print("Report generated successfully.")

# Validations
assert "تقرير التقييم الشامل" in report
assert "Test Student" in report
assert "75.0%" in report
assert "Good student." in report
assert "Sharing" in report
assert "Math" in report
