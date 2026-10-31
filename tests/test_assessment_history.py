import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import data_manager as dm


class TestAssessmentHistory(unittest.TestCase):
    def setUp(self):
        self.record = {
            "info": {"class_level": "تحضيري"},
            "evaluations": {
                "academic": {"اللغة العربية": {"القراءة": 2}},
                "behavioral": {"المهارات الاجتماعية والشخصية": {"الاستقلالية": {"المبادرة": 1}}},
            },
        }

    def test_snapshots_preserve_previous_evaluation(self):
        dm.save_assessment_snapshot(self.record, "تقييم تشخيصي", "2026/2027", "2026-09-15")
        self.record["evaluations"]["academic"]["اللغة العربية"]["القراءة"] = 1
        dm.save_assessment_snapshot(self.record, "الفصل الأول", "2026/2027", "2026-12-15")
        history = self.record["assessment_history"]
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["evaluations"]["academic"]["اللغة العربية"]["القراءة"], 2)
        self.assertEqual(history[1]["evaluations"]["academic"]["اللغة العربية"]["القراءة"], 1)

    def test_saving_same_period_updates_that_snapshot(self):
        dm.save_assessment_snapshot(self.record, "الفصل الأول", "2026/2027", "2026-10-01")
        self.record["evaluations"]["academic"]["اللغة العربية"]["القراءة"] = 0
        action, _ = dm.save_assessment_snapshot(self.record, "الفصل الأول", "2026/2027", "2026-10-03")
        self.assertEqual(action, "updated")
        self.assertEqual(len(self.record["assessment_history"]), 1)
        self.assertEqual(self.record["assessment_history"][0]["evaluations"]["academic"]["اللغة العربية"]["القراءة"], 0)

    def test_compare_returns_percentage_point_difference(self):
        first = {"scores": {"academic_percentage": 20, "behavioral_percentage": 40, "overall_percentage": 30}}
        second = {"scores": {"academic_percentage": 55, "behavioral_percentage": 35, "overall_percentage": 45}}
        self.assertEqual(dm.compare_assessment_snapshots(first, second), {
            "academic_percentage": 35.0, "behavioral_percentage": -5.0, "overall_percentage": 15.0
        })

    def test_requires_period_and_school_year(self):
        with self.assertRaises(ValueError):
            dm.save_assessment_snapshot(self.record, "", "2026/2027", "2026-10-01")


if __name__ == "__main__":
    unittest.main()
