from fpdf import FPDF
import os


class PDFReport(FPDF):
    def __init__(self, student_name):
        super().__init__()
        self.student_name = student_name
        self.custom_font_loaded = False
        self.font_family = 'Helvetica'

        # مسارات الخطوط (مرفقة داخل المشروع)
        base_path = os.path.dirname(os.path.abspath(__file__))
        path_reg = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Regular.ttf')
        path_bold = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Bold.ttf')

        if os.path.exists(path_reg) and os.path.exists(path_bold):
            self.add_font('Amiri', '', path_reg, uni=True)
            self.add_font('Amiri', 'B', path_bold, uni=True)
            self.font_family = 'Amiri'
            self.custom_font_loaded = True
        else:
            raise ValueError("ملفات الخط غير موجودة داخل assets/fonts")

    def process_text(self, text):
        if not self.custom_font_loaded:
            return text
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(text))
        except Exception:
            return text

    # ================== HEADER / FOOTER ==================

    def header(self):
        self.set_font(self.font_family, 'B', 15)
        self.cell(0, 10, self.process_text('تقرير التقييم الشامل'), ln=True, align='C')
        self.set_font(self.font_family, '', 10)
        self.cell(0, 8, self.process_text('نظام التقييم التربوي - الإصدار 4.0'),
                  ln=True, align='C')
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family, '', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    # ================== GENERATE ==================

    def generate(self, evaluation_data, summary_stats, narrative, action_plan):
        self.add_page()

        # ثوابت الجداول
        TABLE_X = 10
        TABLE_WIDTH = 190
        ROW_H = 6

        # ---------- بيانات التلميذ ----------
        self.set_font(self.font_family, 'B', 11)
        self.cell(0, 8,
                  self.process_text(f'اسم التلميذ: {self.student_name}'),
                  ln=True, align='R')

        self.set_font(self.font_family, '', 9)
        stats_text = f"النسبة العامة: {summary_stats['score']:.1f}% | نقاط الضعف: {summary_stats['weaknesses_count']}"
        self.cell(0, 6, self.process_text(stats_text), ln=True, align='R')

        # ---------- التحليل ----------
        self.set_font(self.font_family, 'B', 9)
        self.cell(0, 6, self.process_text("التحليل النوعي وخطة العمل:"), ln=True, align='R')

        self.set_font(self.font_family, '', 8)
        short_narrative = narrative[:150] + "..."
        self.multi_cell(TABLE_WIDTH, 4, self.process_text(short_narrative), align='R')

        # ================== جدول المواد الدراسية ==================

        self.ln(2)
        self.set_x(TABLE_X)
        self.set_fill_color(230, 230, 230)
        self.set_font(self.font_family, 'B', 9)
        self.cell(TABLE_WIDTH, ROW_H,
                  self.process_text("المواد الدراسية"),
                  border=1, fill=True, align='C')
        self.ln()

        self.set_font(self.font_family, '', 7)
        col_w = TABLE_WIDTH / 8

        academic_list = []
        for subject, skills in evaluation_data.get("academic", {}).items():
            for skill, score in skills.items():
                status = "مكتسب" if score == 2 else "بالمسار" if score == 1 else "غير مكتسب"
                academic_list.append((skill, status))

        for i in range(0, len(academic_list), 4):
            self.set_x(TABLE_X)
            row_items = academic_list[i:i + 4]

            while len(row_items) < 4:
                row_items.append(("", ""))

            for skill, status in reversed(row_items):
                self.cell(col_w, ROW_H, self.process_text(status), border=1, align='C')
                self.cell(col_w, ROW_H, self.process_text(skill), border=1, align='R')

            self.ln()

        # ================== جدول المهارات السلوكية ==================

        self.ln(2)
        self.set_x(TABLE_X)
        self.set_fill_color(230, 230, 230)
        self.set_font(self.font_family, 'B', 9)
        self.cell(TABLE_WIDTH, ROW_H,
                  self.process_text("المهارات السلوكية والوظائف الذهنية"),
                  border=1, fill=True, align='C')
        self.ln()

        self.set_font(self.font_family, '', 7)
        col_w = TABLE_WIDTH / 6

        behavioral_list = []
        for main_cat, sub_cats in evaluation_data.get("behavioral", {}).items():
            for sub_cat, skills in sub_cats.items():
                for skill, score in skills.items():
                    status = "مكتسب" if score == 2 else "بالمسار" if score == 1 else "غير مكتسب"
                    behavioral_list.append((skill, status))

        for i in range(0, len(behavioral_list), 3):
            self.set_x(TABLE_X)
            row_items = behavioral_list[i:i + 3]

            while len(row_items) < 3:
                row_items.append(("", ""))

            for skill, status in reversed(row_items):
                self.cell(col_w, ROW_H, self.process_text(status), border=1, align='C')
                self.cell(col_w, ROW_H, self.process_text(skill), border=1, align='R')

            self.ln()

        # ================== خطة العمل ==================

        if action_plan:
            self.ln(2)
            self.set_font(self.font_family, 'B', 9)
            self.cell(0, 6, self.process_text("خطة العمل المقترحة"), ln=True, align='R')

            self.set_font(self.font_family, '', 7)
            plan_text = "\n".join(
                [self.process_text(f"- {skill}: {activity}") for skill, activity in action_plan]
            )
            self.multi_cell(TABLE_WIDTH, 4, plan_text, align='R')

        return bytes(self.output())


# ================== الدالة الرئيسية ==================

def create_pdf(student_name, data, narrative, action_plan):
    try:
        pdf = PDFReport(student_name)

        total = max_score = weaknesses = 0

        for section in ["academic", "behavioral"]:
            for block in data.get(section, {}).values():
                if isinstance(block, dict):
                    for sub in block.values() if section == "behavioral" else [block]:
                        if isinstance(sub, dict):
                            for score in sub.values():
                                total += score
                                max_score += 2
                                if score == 0:
                                    weaknesses += 1

        score = (total / max_score * 100) if max_score else 0
        stats = {"score": score, "weaknesses_count": weaknesses}

        return pdf.generate(data, stats, narrative, action_plan), None

    except Exception as e:
        return None, str(e)
