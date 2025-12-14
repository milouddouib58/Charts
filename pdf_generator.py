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

    # الدالة الجديدة لتوليد التقرير في صفحة واحدة
    def generate(self, evaluation_data, summary_stats, narrative, action_plan):
        self.add_page()
        
        # 1. الترويسة والبيانات الأساسية (مضغوطة)
        self.set_font(self.font_family, 'B', 11)
        self.cell(0, 8, self.process_text(f'اسم التلميذ: {self.student_name}'), ln=True, align='R')
        
        self.set_font(self.font_family, '', 9)
        stats_text = f"النسبة العامة: {summary_stats['score']:.1f}% | نقاط الضعف: {summary_stats['weaknesses_count']}"
        self.cell(0, 6, self.process_text(stats_text), ln=True, align='R')
        
        # 2. التحليل النوعي وخطة العمل (في سطرين فقط لتوفير المساحة)
        self.set_font(self.font_family, 'B', 9)
        self.cell(0, 6, self.process_text("التحليل النوعي وخطة العمل:"), ln=True, align='R')
        self.set_font(self.font_family, '', 8)
        short_narrative = narrative[:150] + "..." # اختصار النص السردي
        self.multi_cell(190, 4, self.process_text(short_narrative), align='R')
        
        # 3. جدول المواد الدراسية (8 أعمدة = 4 أزواج من مادة/تقييم)
        self.ln(2)
        self.set_fill_color(230, 230, 230)
        self.set_font(self.font_family, 'B', 9)
        # تم إضافة border='B' لإظهار الحد السفلي للعنوان
        self.cell(0, 6, self.process_text("المواد الدراسية"), ln=True, align='C', fill=True, border='B')
        
        self.set_font(self.font_family, '', 7)
        col_w = 190 / 8  # تقسيم العرض على 8 أعمدة (23.75 مم لكل عمود)
        
        # تحويل بيانات المواد لقائمة مسطحة لتوزيعها
        academic_list = []
        for subj, skills in evaluation_data.get("academic", {}).items():
            for skill, score in skills.items():
                status = "مكتسب" if score == 2 else "بالمسار" if score == 1 else "غير مكتسب"
                academic_list.append((skill, status))

        # رسم الأسطر (كل سطر يحتوي 4 مهارات وتقييماتها)
        for i in range(0, len(academic_list), 4):
            # التأكد من بدأ الرسم من الهامش الأيسر
            self.set_x(10)
            
            row_items = academic_list[i:i+4]
            num_cells_to_draw = len(row_items) * 2
            
            # حساب الخلية الفارغة في البداية لضمان المحاذاة لليمين
            empty_cells = 8 - num_cells_to_draw
            
            # رسم الخلايا الفارغة
            self.cell(col_w * empty_cells, 6, "", border=0, align='C')

            for item in reversed(row_items): # عكس الترتيب للعربية
                self.cell(col_w, 6, self.process_text(item[1]), border=1, align='C') # التقييم
                self.cell(col_w, 6, self.process_text(item[0]), border=1, align='R') # المهارة
            self.ln()
            # إعادة ضبط X بعد سطر البيانات
            self.set_x(10)

        # 4. جدول المهارات السلوكية (6 أعمدة = 3 أزواج من مهارة/تقييم)
        self.ln(2)
        self.set_fill_color(230, 230, 230)
        self.set_font(self.font_family, 'B', 9)
        # تم إضافة border='B' لإظهار الحد السفلي للعنوان
        self.cell(0, 6, self.process_text("المهارات السلوكية والوظائف الذهنية"), ln=True, align='C', fill=True, border='B')
        
        self.set_font(self.font_family, '', 7)
        col_w_6 = 190 / 6 # 31.6 مم لكل عمود
        
        behavioral_list = []
        # تجميع المهارات السلوكية والذهنية من التقرير 
        for main_cat, sub_cats in evaluation_data.get("behavioral", {}).items():
            for sub_cat, skills in sub_cats.items():
                for skill, score in skills.items():
                    status = "مكتسب" if score == 2 else "بالمسار" if score == 1 else "غير مكتسب"
                    behavioral_list.append((skill, status))

        for i in range(0, len(behavioral_list), 3):
            # التأكد من بدأ الرسم من الهامش الأيسر
            self.set_x(10)
            
            row_items = behavioral_list[i:i+3]
            num_cells_to_draw = len(row_items) * 2
            
            empty_cells = 6 - num_cells_to_draw
            
            # رسم الخلايا الفارغة
            self.cell(col_w_6 * empty_cells, 6, "", border=0, align='C')
            
            for item in reversed(row_items):
                self.cell(col_w_6, 6, self.process_text(item[1]), border=1, align='C')
                self.cell(col_w_6, 6, self.process_text(item[0]), border=1, align='R')
            self.ln()
            # إعادة ضبط X بعد سطر البيانات
            self.set_x(10)

        # 5. خطة العمل المتبقية (بعد الجداول)
        if action_plan:
            self.ln(2)
            self.set_font(self.font_family, 'B', 9)
            plan_title = self.process_text('خطة العمل المقترحة')
            self.cell(0, 6, plan_title, ln=True, align='R')
            
            self.set_font(self.font_family, '', 7)
            
            # طباعة خطة العمل في multiline cell واحدة ومضغوطة
            plan_lines = [self.process_text(f"- {skill}: {activity}") for skill, activity in action_plan]
            plan_text = "\n".join(plan_lines)
            
            self.multi_cell(190, 4, plan_text, align='R', border=0)
        
        return bytes(self.output())

# دالة التشغيل الرئيسية تبقى كما هي وتستدعي generate
def create_pdf(student_name, data, narrative, action_plan):
    try:
        pdf = PDFReport(student_name)
        
        # Calculate stats for the report
        total = 0
        max_score = 0
        weaknesses = 0
        
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
