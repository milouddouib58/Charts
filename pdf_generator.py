from fpdf import FPDF
import os

class PDFReport(FPDF):
    def __init__(self, student_name):
        super().__init__()
        self.student_name = student_name
        self.custom_font_loaded = False
        self.font_family = 'Helvetica' # Default placeholder
        
        # Fonts (Bundled in repo)
        base_path = os.path.dirname(os.path.abspath(__file__))
        path_reg = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Regular.ttf')
        path_bold = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Bold.ttf')
        
        # Verify fonts exist (Use bundled fonts ONLY for stability)
        if os.path.exists(path_reg) and os.path.exists(path_bold):
             try:
                self.add_font('Amiri', '', path_reg)
                self.add_font('Amiri', 'B', path_bold)
                self.font_family = 'Amiri'
                self.custom_font_loaded = True
             except Exception as e:
                print(f"Font load error: {e}")
                raise ValueError(f"Failed to load bundled fonts: {e}")
        else:
            # Debugging info
            print(f"Current Directory: {os.getcwd()}")
            print(f"Base Path: {base_path}")
            print(f"Expected Font Path: {path_reg}")
            raise ValueError(f"Font files not found at {path_reg}. Please ensure the 'assets/fonts' folder is uploaded to the server.")

    def process_text(self, text):
        """
        Reshapes Arabic text. Explicitly requires custom_font_loaded.
        """
        if not self.custom_font_loaded:
            return "Font Error" # Should be caught by init exception usually
            
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except ImportError as e:
            print(f"RTL Library Error: {e}")
            return text

    def header(self):
        self.set_font(self.font_family, 'B', 15)
        # Apply process_text to all Arabic strings
        title = self.process_text('تقرير التقييم الشامل')
        self.cell(0, 10, title, border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font(self.font_family, '', 10)
        subtitle = self.process_text('نظام التقييم التربوي - الإصدار 4.0')
        self.cell(0, 10, subtitle, border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family, '', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def generate(self, evaluation_data, summary_stats, narrative, action_plan):
        self.add_page()
        
        # Student Info
        self.set_font(self.font_family, 'B', 14)
        info_text = self.process_text(f'اسم التلميذ: {self.student_name}')
        self.cell(0, 10, info_text, new_x="LMARGIN", new_y="NEXT", align='R')
        self.ln(5)
        
        # Summary
        self.set_font(self.font_family, 'B', 12)
        summary_title = self.process_text('ملخص الأداء')
        self.cell(0, 10, summary_title, new_x="LMARGIN", new_y="NEXT", align='R')
        self.set_font(self.font_family, '', 12)
        
        score_text = self.process_text(f"النسبة العامة: {summary_stats['score']:.1f}%")
        weak_text = self.process_text(f"عدد نقاط الضعف: {summary_stats['weaknesses_count']}")
        
        self.cell(0, 10, score_text, new_x="LMARGIN", new_y="NEXT", align='R')
        self.cell(0, 10, weak_text, new_x="LMARGIN", new_y="NEXT", align='R')
        self.ln(5)
        
        # Qualitative Analysis (Narrative)
        self.set_font(self.font_family, 'B', 12)
        narrative_title = self.process_text('التحليل النوعي')
        self.cell(0, 10, narrative_title, new_x="LMARGIN", new_y="NEXT", align='R')
        self.set_font(self.font_family, '', 11)
        
        # FIX: Ensure cursor is at left margin and provide prompt width
        self.set_x(10)
        # Note: Narrative is long text. reshaping whole paragraph might work but line wrapping is tricky.
        # usually bidi handles it but fpdf multi_cell wraps by characters.
        # We will try passing the full reshaped block.
        proc_narrative = self.process_text(narrative)
        self.multi_cell(190, 8, proc_narrative, align='R')
        self.ln(5)

        # Action Plan (Recommendations)
        if action_plan:
            self.set_font(self.font_family, 'B', 12)
            plan_title = self.process_text('خطة العمل المقترحة')
            self.cell(0, 10, plan_title, new_x="LMARGIN", new_y="NEXT", align='R')
            self.set_font(self.font_family, '', 10)
            for skill, activity in action_plan:
                bg_color = (255, 255, 255) # White
                self.set_fill_color(*bg_color)
                # Bullet point
                self.set_x(10)
                item_text = self.process_text(f"- {skill}: {activity}")
                self.multi_cell(190, 7, item_text, align='R', border=0)
            self.ln(5)

        # Detailed Table
        self.add_page() # Start table on new page if needed, or just continue
        self.set_font(self.font_family, 'B', 12)
        table_title = self.process_text('التفاصيل حسب المجالات')
        self.cell(0, 10, table_title, new_x="LMARGIN", new_y="NEXT", align='R')
        
        # Table Header
        self.set_fill_color(200, 220, 255)
        self.set_font(self.font_family, 'B', 10)
        
        h1 = self.process_text('الدرجة')
        h2 = self.process_text('المهارة')
        h3 = self.process_text('المجال')
        
        self.cell(60, 10, h1, border=1, align='C', fill=True)
        self.cell(70, 10, h2, border=1, align='C', fill=True)
        self.cell(60, 10, h3, border=1, align='C', fill=True)
        self.ln()
        
        self.set_font(self.font_family, '', 10)
        
        # Helper to add row
        def add_row(domain, skill_name, score_val):
            status_raw = "مكتسب" if score_val == 2 else "في طريق الاكتساب" if score_val == 1 else "غير مكتسب"
            status = self.process_text(status_raw)
            skill_processed = self.process_text(skill_name)
            sub_processed = self.process_text(domain)
            
            self.cell(60, 10, status, border=1, align='C')
            self.cell(70, 10, skill_processed, border=1, align='R') 
            self.cell(60, 10, sub_processed, border=1, align='R')
            self.ln()

        # Handle Academic (2 levels: Subject -> Skill -> Score)
        if "academic" in evaluation_data and isinstance(evaluation_data["academic"], dict):
            for subject, skills in evaluation_data["academic"].items():
                if isinstance(skills, dict):
                    for skill, score in skills.items():
                        add_row(subject, skill, score)

        # Handle Behavioral (3 levels: MainCat -> SubCat -> Skill -> Score)
        if "behavioral" in evaluation_data and isinstance(evaluation_data["behavioral"], dict):
            for main_cat, sub_cats in evaluation_data["behavioral"].items():
                if isinstance(sub_cats, dict):
                    for sub_cat, skills in sub_cats.items():
                        if isinstance(skills, dict):
                            for skill, score in skills.items():
                                # Combine Main and Sub for domain column or just use Sub
                                domain_label = f"{main_cat} - {sub_cat}"
                                add_row(domain_label, skill, score)

        return bytes(self.output())

def create_pdf(student_name, data, narrative, action_plan):
    try:
        pdf = PDFReport(student_name)
        
        # Calculate stats for the report
        total = 0
        max_score = 0
        weaknesses = 0
        
        # Explicitly handle academic and behavioral to avoid str errors and structure mismatch
        
        # Academic
        if "academic" in data and isinstance(data["academic"], dict):
             for subject, skills in data["academic"].items():
                 if isinstance(skills, dict):
                     for score in skills.values():
                         total += score
                         max_score += 2
                         if score == 0: weaknesses += 1

        # Behavioral
        if "behavioral" in data and isinstance(data["behavioral"], dict):
             for main_cat, sub_cats in data["behavioral"].items():
                 if isinstance(sub_cats, dict):
                     for skills in sub_cats.values():
                         if isinstance(skills, dict):
                             for score in skills.values():
                                 total += score
                                 max_score += 2
                                 if score == 0: weaknesses += 1
        
        score = (total / max_score * 100) if max_score else 0
        stats = {"score": score, "weaknesses_count": weaknesses}
        
        pdf_bytes = pdf.generate(data, stats, narrative, action_plan)
        return pdf_bytes, None
    except Exception as e:
        print(f"PDF Gen Error: {e}")
        return None, str(e)
