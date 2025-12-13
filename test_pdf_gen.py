from pdf_generator import create_pdf

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

narrative = "This is a test narrative."
action_plan = [("Plan A", "Do this")]

pdf_bytes, error = create_pdf("Test Student", data, narrative, action_plan)

if error:
    print(f"FAILED: {error}")
    exit(1)
else:
    print(f"SUCCESS: Generated {len(pdf_bytes)} bytes")
