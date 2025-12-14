from fpdf import FPDF
import os


class PDFReport(FPDF):
    def __init__(self, student_name):
        super().__init__()
        self.student_name = student_name
        self.font_family = 'Helvetica'

        base_path = os.path.dirname(os.path.abspath(__file__))
        reg = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Regular.ttf')
        bold = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Bold.ttf')

        if not os.path.exists(reg) or not os.path.exists(bold):
            raise ValueError("خط Amiri غير موجود داخل assets/fonts")

        self.add_font('Amiri', '', reg)
        self.add_font('Amiri', 'B', bold)
        self.font_family = 'Amiri'

    # ---------------- RTL ----------------
    def process_text(self, text):
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(text))
        except Exception:
            return text

    # ---------------- Header / Footer ----------------
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

    # ---------------- عمود مادة واحد ----------------
    def draw_domain_column(self, x, y, width, title, items):
        self.set_xy(x, y)
        self.set_font(self.font_family, 'B', 9)
        self.multi_cell(width, 7, self.process_text(title), border=1, align='C')

        self.set_font(self.font_family, '', 7)
        for skill, score in items:
            status = "مكتسب" if score == 2 else "بالمسار" if score == 1 else "غير مكتسب"
            text = f"{skill}\n({status})"
            self.multi_cell(width, 7, self.process_text(text), border=1, align='R')

    # ---------------- Generate ----------------
    def generate(self, data, stats, narrative, action_plan):
        self.add_page()

        # معلومات التلميذ
        self.set_font(self.font_family, 'B', 11)
        self.cell(0, 7, self.process_text(f"اسم التلميذ: {self.student_name}"),
                  ln=True, align='R')

        self.set_font(self.font_family, '', 9)
        summary = f"النسبة العامة: {stats['score']:.1f}% | نقاط الضعف: {stats['weaknesses_count']}"
        self.cell(0, 6, self.process_text(summary), ln=True, align='R')

        # تحليل مختصر
        self.set_font(self.font_family, 'B', 9)
        self.cell(0, 6, self.process_text("التحليل النوعي:"), ln=True, align='R')
        self.set_font(self.font_family, '', 8)
        self.multi_cell(190, 4, self.process_text(narrative[:180] + "..."), align='R')

        # =====================================================
        #                تقييم المواد الدراسية
        # =====================================================
        self.ln(4)
        self.set_font(self.font_family, 'B', 11)
        self.cell(0, 8, self.process_text("تقييم المواد الدراسية"), ln=True, align='C')

        start_x = 10
        start_y = self.get_y()
        col_w = 190 / 4

        subjects = [
            "اللغة العربية",
            "الرياضيات",
            "التربية الإسلامية والمدنية",
            "التربية العلمية"
        ]

        academic = data.get("academic", {})

        for i, subject in enumerate(subjects):
            skills = academic.get(subject, {})
            items = [(k, v) for k, v in skills.items()]
            self.draw_domain_column(start_x + i * col_w, start_y, col_w, subject, items)

        self.set_y(start_y + 85)

        # =====================================================
        #                تقييم المهارات السلوكية
        # =====================================================
        self.ln(6)
        self.set_font(self.font_family, 'B', 11)
        self.cell(0, 8, self.process_text("تقييم المهارات السلوكية"), ln=True, align='C')

        start_y = self.get_y()
        col_w = 190 / 3

        behavioral = data.get("behavioral", {})

        domains = [
            "الوظائف التنفيذية",
            "الكفاءة الاجتماعية والعاطفية",
            "المهارات الحركية والاستقلالية"
        ]

        for i, domain in enumerate(domains):
            items = []
            for sub in behavioral.get(domain, {}).values():
                for skill, score in sub.items():
                    items.append((skill, score))

            self.draw_domain_column(start_x + i * col_w, start_y, col_w, domain, items)

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
