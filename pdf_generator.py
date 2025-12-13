from fpdf import FPDF
import os

class PDFReport(FPDF):
    def __init__(self, student_name):
        super().__init__()
        self.student_name = student_name
        self.custom_font_loaded = False
        self.font_family = 'Helvetica' # Default placeholder
        
        # Strategy 1: Noto Naskh Arabic (Download)
        font_url = "https://github.com/google/fonts/raw/main/ofl/notonaskharabic/NotoNaskhArabic-Regular.ttf"
        font_url_bold = "https://github.com/google/fonts/raw/main/ofl/notonaskharabic/NotoNaskhArabic-Bold.ttf"
        
        path_reg = 'assets/fonts/NotoNaskhArabic-Regular.ttf'
        path_bold = 'assets/fonts/NotoNaskhArabic-Bold.ttf'
        
        os.makedirs('assets/fonts', exist_ok=True)
        
        # Strategy 2: Windows System Font (Backup)
        sys_font_reg = 'C:/Windows/Fonts/arial.ttf'
        sys_font_bold = 'C:/Windows/Fonts/arialbd.ttf'

        loaded_success = False

        # Attempt 1: Download
        try:
            import urllib.request
            def download_if_missing(url, path):
                if not os.path.exists(path) or os.path.getsize(path) < 1000:
                    print(f"Downloading {path}...")
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(url, path)
            
            download_if_missing(font_url, path_reg)
            download_if_missing(font_url_bold, path_bold)
            
            self.add_font('NotoNaskhArabic', '', path_reg)
            self.add_font('NotoNaskhArabic', 'B', path_bold)
            self.font_family = 'NotoNaskhArabic'
            self.custom_font_loaded = True
            loaded_success = True
            
        except Exception as e:
            print(f"Download failed: {e}")
            # Try cleanup
            if os.path.exists(path_reg): os.remove(path_reg)

        # Attempt 2: System Fonts (if Attempt 1 failed)
        if not loaded_success:
            print("Attempting System Fonts...")
            if os.path.exists(sys_font_reg) and os.path.exists(sys_font_bold):
                try:
                    self.add_font('SystemArial', '', sys_font_reg)
                    self.add_font('SystemArial', 'B', sys_font_bold)
                    self.font_family = 'SystemArial'
                    self.custom_font_loaded = True # Arial supports reshaping usually
                    loaded_success = True
                    print("Using Windows System Arial.")
                except Exception as e:
                    print(f"System font load error: {e}")

        # Final Check
        if not loaded_success:
            raise ValueError("Could not load any Arabic-supporting font (Internet download failed and System Arial not found). PDF generation aborted to prevent crash.")

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
        for main, subs in evaluation_data.items():
            for sub, skills in subs.items():
                for skill, score in skills.items():
                    status_raw = "مكتسب" if score == 2 else "في طريق الاكتساب" if score == 1 else "غير مكتسب"
                    status = self.process_text(status_raw)
                    skill_processed = self.process_text(skill)
                    sub_processed = self.process_text(sub)
                    
                    self.cell(60, 10, status, border=1, align='C')
                    self.cell(70, 10, skill_processed, border=1, align='R') 
                    self.cell(60, 10, sub_processed, border=1, align='R')
                    self.ln()

        return bytes(self.output())

def create_pdf(student_name, data, narrative, action_plan):
    try:
        pdf = PDFReport(student_name)
        
        # Calculate stats for the report
        total = 0
        max_score = 0
        weaknesses = 0
        for m in data.values():
            for s in m.values():
                for v in s.values():
                    total += v
                    max_score += 2
                    if v == 0: weaknesses += 1
        
        score = (total / max_score * 100) if max_score else 0
        stats = {"score": score, "weaknesses_count": weaknesses}
        
        pdf_bytes = pdf.generate(data, stats, narrative, action_plan)
        return pdf_bytes, None
    except Exception as e:
        print(f"PDF Gen Error: {e}")
        return None, str(e)
