from fpdf import FPDF
import os

class PDFReport(FPDF):
    def __init__(self, student_name):
        super().__init__()
        self.student_name = student_name
        self.custom_font_loaded = False
        self.font_family = 'Helvetica' 
        
        # إعداد المسارات للخطوط (يرجى التأكد من وجود ملفات الخطوط)
        base_path = os.path.dirname(os.path.abspath(__file__))
        # مسارات الخطوط (تأكد من وجود مجلد assets/fonts وبداخله الخطوط)
        path_reg = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Regular.ttf')
        path_bold = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Bold.ttf')
        
        if os.path.exists(path_reg) and os.path.exists(path_bold):
             try:
                self.add_font('Amiri', '', path_reg)
                self.add_font('Amiri', 'B', path_bold)
                self.font_family = 'Amiri'
                self.custom_font_loaded = True
             except Exception as e:
                print(f"Font load error: {e}")
        else:
            print("Warning: Amiri font not found. Using default.")

    def process_text(self, text):
        """إعادة تشكيل النص العربي"""
        if not self.custom_font_loaded: return str(text)
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(str(text)))
        except ImportError:
            return str(text)

    def draw_symbol(self, x, y, w, h, score):
        """
        رسم الرموز الهندسية بناءً على الدرجة
        x, y: إحداثيات الزاوية اليسرى العليا للخلية
        w, h: عرض وارتفاع الخلية
        """
        # حساب مركز الخلية
        cx = x + (w / 2)
        cy = y + (h / 2)
        r = 3 # نصف طول الخط (حجم الرمز)

        self.set_line_width(0.4)
        self.set_draw_color(0, 0, 0) # أسود

        if score == 2: # مكتسب (+)
            self.line(cx - r, cy, cx + r, cy)       # أفقي
            self.line(cx, cy - r, cx, cy + r)       # عمودي كامل
            
        elif score == 1: # في طريق الاكتساب (زائد بدون خط سفلي ┴)
            self.line(cx - r, cy, cx + r, cy)       # أفقي
            self.line(cx, cy - r, cx, cy)           # عمودي (من الأعلى للمنتصف فقط)

        elif score == 0: # غير مكتسب (-)
            self.line(cx - r, cy, cx + r, cy)       # أفقي فقط

    def header(self):
        self.set_font(self.font_family, 'B', 14)
        title = self.process_text('تقرير التقييم الشامل')
        self.cell(0, 8, title, border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font(self.font_family, '', 10)
        subtitle = self.process_text(f'اسم التلميذ: {self.student_name}')
        self.cell(0, 6, subtitle, border='B', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def draw_grid_table(self, title, items, columns_per_row, col_widths):
        """
        رسم جدول بنظام الشبكة مع رؤوس ونصوص ملتفة
        """
        if not items: return

        # 1. العنوان الرئيسي للجدول
        self.set_font(self.font_family, 'B', 12)
        self.set_fill_color(230, 230, 230)
        processed_title = self.process_text(title)
        self.cell(0, 8, processed_title, ln=True, align='C', fill=True, border=1)
        
        # 2. رسم رؤوس الأعمدة (Header Row)
        # نحتاج تكرار (المهارة | التقييم) بعدد columns_per_row
        self.set_font(self.font_family, 'B', 9)
        self.set_fill_color(245, 245, 245)
        
        # حفظ مكان البداية
        start_x = self.get_x()
        
        # نظرًا لأننا نكتب بالعربي (اليمين لليسار بصرياً)، ولكن FPDF يكتب LTR
        # سنقوم برسم الخلايا من اليسار لليمين ولكن بترتيب معكوس للمحتوى لتبدو عربية
        # لكن الأسهل هنا هو رسمها بالترتيب الطبيعي 1..8 وتسمية الأعمدة.
        
        # سنفترض الترتيب: [المادة 4] [تقييم] ... [المادة 1] [تقييم] (من اليمين)
        # أو الترتيب الخطي: المجموعة 1، المجموعة 2..
        
        # رسم صف العناوين
        header_h = 7
        # لحساب العرض الكلي للمجموعة (اسم + تقييم)
        pair_width = col_widths[0] + col_widths[1]
        
        # بما أننا نريد الجدول يملأ الصفحة، نحسب بداية X
        # عرض الصفحة المتاح تقريباً 190.
        
        # رسم العناوين لكل عمود
        # سنقوم بالتكرار ورسم (المهارة | التقييم)
        for _ in range(columns_per_row):
            # عمود الاسم
            self.cell(col_widths[0], header_h, self.process_text("المهارة / المادة"), border=1, align='C', fill=True)
            # عمود التقييم
            self.cell(col_widths[1], header_h, self.process_text("التقييم"), border=1, align='C', fill=True)
        self.ln()

        # 3. رسم البيانات
        self.set_font(self.font_family, '', 8)
        
        # تحديد ارتفاع السطر (بما أننا سنستخدم MultiCell للنصوص الطويلة، نحتاج ارتفاعاً ثابتاً يكفي لسطرين أو ثلاثة)
        row_height = 10 # ارتفاع ثابت لضمان تناسق الشبكة
        
        total_items = len(items)
        
        for i in range(0, total_items, columns_per_row):
            chunk = items[i : i + columns_per_row]
            
            # حفظ موقع Y الحالي لبداية الصف
            y_start = self.get_y()
            if y_start > 270: # فحص نهاية الصفحة
                self.add_page()
                y_start = self.get_y()

            current_x = self.get_x() # بداية الهامش الأيسر
            
            # حلقة لرسم خلايا الصف
            for idx, (item_name, item_score) in enumerate(chunk):
                # 1. رسم خلية الاسم (نص طويل)
                # نستخدم xy للتحكم التام بالموقع
                self.set_xy(current_x, y_start)
                
                # معالجة النص
                name_txt = self.process_text(item_name)
                
                # رسم مربع الحدود أولاً (لضمان ظهور الإطار كاملاً)
                self.rect(current_x, y_start, col_widths[0], row_height)
                
                # كتابة النص بداخل المربع (MultiCell)
                # نقوم بإزاحة بسيطة للهوامش داخل الخلية
                self.set_xy(current_x + 1, y_start + 1) # هامش داخلي 1 مم
                # MultiCell(w, h, txt, border, align)
                # h هنا هو ارتفاع السطر الواحد داخل النص وليس ارتفاع الخلية الكلي
                self.multi_cell(col_widths[0] - 2, 4, name_txt, border=0, align='R')
                
                # تحديث X للخلية التالية (خلية التقييم)
                current_x += col_widths[0]
                
                # 2. رسم خلية التقييم (رمز)
                self.set_xy(current_x, y_start)
                self.rect(current_x, y_start, col_widths[1], row_height) # الإطار
                
                # رسم الرمز داخل الخلية
                self.draw_symbol(current_x, y_start, col_widths[1], row_height, item_score)
                
                # تحديث X للمجموعة التالية
                current_x += col_widths[1]

            # تعبئة الخلايا الفارغة في الصف الأخير للحفاظ على الشبكة
            remaining = columns_per_row - len(chunk)
            for _ in range(remaining):
                self.set_xy(current_x, y_start)
                self.rect(current_x, y_start, col_widths[0], row_height)
                current_x += col_widths[0]
                
                self.set_xy(current_x, y_start)
                self.rect(current_x, y_start, col_widths[1], row_height)
                current_x += col_widths[1]

            # الانتقال للصف التالي
            self.set_y(y_start + row_height)
        
        self.ln(2)

    def generate(self, evaluation_data, summary_stats, narrative, action_plan):
        self.add_page()
        
        # --- الملخص ---
        self.set_font(self.font_family, 'B', 10)
        score_txt = self.process_text(f"النسبة العامة: {summary_stats['score']:.1f}%")
        weak_txt = self.process_text(f"نقاط الضعف: {summary_stats['weaknesses_count']}")
        
        # مفتاح الرموز
        key_txt = self.process_text("مفتاح الرموز: (+) مكتسب | (┴) في طريق الاكتساب | (-) غير مكتسب")
        
        self.set_fill_color(240, 240, 240)
        self.cell(40, 8, score_txt, border=1, align='C', fill=True)
        self.cell(40, 8, weak_txt, border=1, align='C', fill=True)
        self.cell(110, 8, key_txt, border=1, align='C', fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        # --- البيانات ---
        # 1. المواد الدراسية (8 أعمدة = 4 مجموعات)
        academic_items = []
        if "academic" in evaluation_data:
            for subject, skills in evaluation_data["academic"].items():
                if isinstance(skills, dict):
                    for skill, score in skills.items():
                        # دمج اسم المادة والمهارة
                        label = f"{subject}: {skill}"
                        academic_items.append((label, score))
        
        # العرض الإجمالي 190. 4 مجموعات. كل مجموعة = 47.5
        # الاسم = 35، التقييم = 12.5
        self.draw_grid_table(
            title='المواد الدراسية',
            items=academic_items,
            columns_per_row=4,
            col_widths=[35, 12.5]
        )

        # 2. المهارات السلوكية (6 أعمدة = 3 مجموعات)
        behavioral_items = []
        if "behavioral" in evaluation_data:
            for main, subs in evaluation_data["behavioral"].items():
                if isinstance(subs, dict):
                    for sub, skills in subs.items():
                        if isinstance(skills, dict):
                            for skill, score in skills.items():
                                behavioral_items.append((skill, score))
        
        # العرض الإجمالي 190. 3 مجموعات. كل مجموعة = 63.3
        # الاسم = 50، التقييم = 13.3
        self.draw_grid_table(
            title='المهارات السلوكية',
            items=behavioral_items,
            columns_per_row=3,
            col_widths=[50, 13.3]
        )

        # --- الملاحظات (تظهر في المساحة المتبقية) ---
        remain_y = 285 - self.get_y()
        if remain_y > 20:
            self.set_font(self.font_family, 'B', 11)
            self.cell(0, 8, self.process_text('ملاحظات وتوصيات'), border='B', ln=True, align='R')
            self.set_font(self.font_family, '', 9)
            
            full_text = narrative + "\n"
            if action_plan:
                full_text += "الخطة المقترحة:\n"
                for skill, act in action_plan:
                    full_text += f"- {skill}: {act}\n"
            
            self.multi_cell(0, 5, self.process_text(full_text), align='R')

        return bytes(self.output())

def create_pdf(student_name, data, narrative, action_plan):
    try:
        pdf = PDFReport(student_name)
        
        total = 0
        max_score = 0
        weaknesses = 0
        
        # حساب الإحصائيات
        if "academic" in data and isinstance(data["academic"], dict):
             for subject, skills in data["academic"].items():
                 if isinstance(skills, dict):
                     for score in skills.values():
                         total += score
                         max_score += 2
                         if score == 0: weaknesses += 1

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
        import traceback
        traceback.print_exc()
        return None, str(e)

