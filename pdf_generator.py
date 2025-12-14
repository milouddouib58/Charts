from fpdf import FPDF
import os


class PDFReport(FPDF):
    def __init__(self, student_name):
        super().__init__()
        self.student_name = student_name
        self.font_family = 'Helvetica'

        base_path = os.path.dirname(os.path.abspath(__file__))
        path_reg = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Regular.ttf')
        path_bold = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Bold.ttf')

        if not os.path.exists(path_reg) or not os.path.exists(path_bold):
            raise ValueError("ملفات الخط Amiri غير موجودة")

        self.add_font('Amiri', '', path_reg)
        self.add_font('Amiri', 'B', path_bold)
        self.font_family = 'Amiri'

    def process_text(self, text):
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(text))
        except Exception:
            return text

    def header(self):
        self.set_font(self.font_family, 'B', 14)
        self.cell(0, 8, self.process_text("تقرير التقييم الشامل"), ln=True, align='C')
        self.set_font(self.font_family, '', 10)
        self.cell(0, 6, self.process_text("نظام التقييم التربوي - الإصدار 4.0"),
                  ln=True, align='C')
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font(self.font_family, '', 8)
        self.cell(0, 8, f"Page {self.page_no()}", align='C')

    # ==================================================

    def generate(self, data, stats, narrative, action_plan):
        self.add_page()

        TABLE_X = 10
        TABLE_W = 190
        ROW_H = 6

        # ---------- بيانات التلميذ ----------
        self.set_font(self.font_family, 'B', 11)
        self.cell(0, 7, self.process_text(f"اسم التلميذ: {self.student_name}"),
                  ln=True, align='R')

        self.set_font(self.font_family, '', 9)
        summary = f"النسبة العامة: {stats['score']:.1f}% | نقاط الضعف: {stats['weaknesses_count']}"
        self.cell(0, 6, self.process_text(summary), ln=True, align='R')

        # ---------- التحليل (مختصر) ----------
        self.set_font(self.font_family, 'B', 9)
        self.cell(0, 6, self.process_text("التحليل النوعي:"), ln=True, align='R')
        self.set_font(self.font_family, '', 8)
        self.multi_cell(TABLE_W, 4, self.process_text(narrative[:180] + "..."),
                        align='R')

        # ==================================================
        # =============== جدول التقييم (صفحة واحدة) =========
        # ==================================================

        self.ln(2)
        self.set_x(TABLE_X)
        self.set_font(self.font_family, 'B', 9)
        self.set_fill_color(230, 230, 230)
        self.cell(TABLE_W, ROW_H,
                  self.process_text("التقييم حسب المهارات"),
                  border=1, fill=True, align='C')
        self.ln()

        self.set_font(self.font_family, '', 7)

        # ---- تجميع كل المهارات ----
        all_skills = []

        for subject, skills in data.get("academic", {}).items():
            for skill, score in skills.items():
                status = "مكتسب" if score == 2 else "بالمسار" if score == 1 else "غير مكتسب"
                all_skills.append((skill, status))

        for main_cat, sub_cats in data.get("behavioral", {}).items():
            for sub_cat, skills in sub_cats.items():
                for skill, score in skills.items():
                    status = "مكتسب" if score == 2 else "بالمسار" if score == 1 else "غير مكتسب"
                    all_skills.append((skill, status))

        # ---- 4 مهارات في السطر = 8 أعمدة ----
        COL_W = TABLE_W / 8

        for i in range(0, len(all_skills), 4):
            self.set_x(TABLE_X)
            row = all_skills[i:i + 4]

            while len(row) < 4:
                row.append(("", ""))

            for skill, status in reversed(row):
                self.cell(COL_W, ROW_H, self.process_text(status),
                          border=1, align='C')
                self.cell(COL_W, ROW_H, self.process_text(skill),
                          border=1, align='R')

            self.ln()

        # ---------- خطة العمل (مختصرة) ----------
        if action_plan:
            self.ln(2)
            self.set_font(self.font_family, 'B', 9)
            self.cell(0, 6, self.process_text("خطة العمل المقترحة"), ln=True, align='R')

            self.set_font(self.font_family, '', 7)
            text = "\n".join(
                self.process_text(f"- {s}: {a}") for s, a in action_plan[:6]
            )
            self.multi_cell(TABLE_W, 4, text, align='R')

        return bytes(self.output())


# ==================================================
# =============== الدالة الرئيسية ====================
# ==================================================

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
