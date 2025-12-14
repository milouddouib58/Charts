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

    # ---------- RTL ----------
    def process_text(self, text):
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(text))
        except Exception:
            return text

    # ---------- Header / Footer ----------
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

    # ---------- Generate ----------
    def generate(self, evaluation_data, summary_stats, narrative, action_plan):
        self.add_page()

        # ===== معلومات التلميذ =====
        self.set_font(self.font_family, 'B', 11)
        self.cell(0, 7,
                  self.process_text(f"اسم التلميذ: {self.student_name}"),
                  ln=True, align='R')

        self.set_font(self.font_family, '', 9)
        summary = f"النسبة العامة: {summary_stats['score']:.1f}% | نقاط الضعف: {summary_stats['weaknesses_count']}"
        self.cell(0, 6, self.process_text(summary), ln=True, align='R')

        # ===== التحليل النوعي =====
        self.set_font(self.font_family, 'B', 10)
        self.cell(0, 7, self.process_text("التحليل النوعي"), ln=True, align='R')
        self.set_font(self.font_family, '', 9)
        self.multi_cell(190, 5, self.process_text(narrative), align='R')

        # =====================================================
        #              جدول تقييم المواد الدراسية
        # =====================================================
        self.ln(4)
        self.set_font(self.font_family, 'B', 11)
        self.cell(0, 8, self.process_text("تقييم المواد الدراسية"), ln=True, align='R')

        self.set_font(self.font_family, 'B', 9)
        self.set_fill_color(230, 230, 230)

        self.cell(40, 8, self.process_text("المادة"), border=1, fill=True, align='C')
        self.cell(100, 8, self.process_text("المهارة"), border=1, fill=True, align='C')
        self.cell(50, 8, self.process_text("التقييم"), border=1, fill=True, align='C')
        self.ln()

        self.set_font(self.font_family, '', 8)

        for subject, skills in evaluation_data.get("academic", {}).items():
            first = True
            for skill, score in skills.items():
                status = "مكتسب" if score == 2 else "بالمسار" if score == 1 else "غير مكتسب"

                self.cell(40, 7,
                          self.process_text(subject) if first else "",
                          border=1, align='R')
                self.cell(100, 7,
                          self.process_text(skill),
                          border=1, align='R')
                self.cell(50, 7,
                          self.process_text(status),
                          border=1, align='C')
                self.ln()
                first = False

        # =====================================================
        #              جدول تقييم المهارات السلوكية
        # =====================================================
        self.ln(5)
        self.set_font(self.font_family, 'B', 11)
        self.cell(0, 8, self.process_text("تقييم المهارات السلوكية"), ln=True, align='R')

        self.set_font(self.font_family, 'B', 9)
        self.set_fill_color(230, 230, 230)

        self.cell(50, 8, self.process_text("المجال"), border=1, fill=True, align='C')
        self.cell(90, 8, self.process_text("المهارة"), border=1, fill=True, align='C')
        self.cell(50, 8, self.process_text("التقييم"), border=1, fill=True, align='C')
        self.ln()

        self.set_font(self.font_family, '', 8)

        for main_cat, subcats in evaluation_data.get("behavioral", {}).items():
            first_main = True
            for subcat, skills in subcats.items():
                for skill, score in skills.items():
                    status = "مكتسب" if score == 2 else "بالمسار" if score == 1 else "غير مكتسب"

                    self.cell(50, 7,
                              self.process_text(main_cat) if first_main else "",
                              border=1, align='R')
                    self.cell(90, 7,
                              self.process_text(skill),
                              border=1, align='R')
                    self.cell(50, 7,
                              self.process_text(status),
                              border=1, align='C')
                    self.ln()
                    first_main = False

        return bytes(self.output())


# =====================================================
#                 الدالة الرئيسية
# =====================================================
def create_pdf(student_name, data, narrative, action_plan):
    try:
        pdf = PDFReport(student_name)

        total = max_score = weaknesses = 0

        if "academic" in data:
            for skills in data["academic"].values():
                for score in skills.values():
                    total += score
                    max_score += 2
                    if score == 0:
                        weaknesses += 1

        if "behavioral" in data:
            for main in data["behavioral"].values():
                for skills in main.values():
                    for score in skills.values():
                        total += score
                        max_score += 2
                        if score == 0:
                            weaknesses += 1

        score = (total / max_score * 100) if max_score else 0
        stats = {"score": score, "weaknesses_count": weaknesses}

        return pdf.generate(data, stats, narrative, action_plan), None

    except Exception as e:
        return None, str(e)
