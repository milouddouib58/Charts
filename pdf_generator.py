from fpdf import FPDF
import os

class PDFReport(FPDF):
    def __init__(self, student_name, student_info):
        super().__init__()
        self.student_name = student_name
        self.student_info = student_info
        self.custom_font_loaded = False
        self.font_family = 'Helvetica'
        
        # إعداد الخطوط
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.path_reg = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Regular.ttf')
        self.path_bold = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Bold.ttf')
        
        if os.path.exists(self.path_reg) and os.path.exists(self.path_bold):
             try:
                self.add_font('Amiri', '', self.path_reg)
                self.add_font('Amiri', 'B', self.path_bold)
                self.font_family = 'Amiri'
                self.custom_font_loaded = True
             except: pass

    def process_text(self, text):
        if not self.custom_font_loaded: return str(text)
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(str(text)))
        except: return str(text)

    # --- 5. ترويسة التقرير (Header) ---
    def header(self):
        # 1. مكان الشعار (مربع رمادي مؤقت)
        # إذا توفرت صورة: self.image('logo.png', 10, 8, 33)
        self.set_fill_color(240, 240, 240)
        self.set_draw_color(200, 200, 200)
        # self.rect(10, 8, 25, 25, 'F') # فعل هذا السطر إذا أردت مربعاً للشعار
        
        # 2. العناوين
        self.set_y(15)
        self.set_font(self.font_family, 'B', 18)
        self.cell(0, 10, self.process_text('بطاقة التقييم الفصلي'), 0, 1, 'C')
        
        self.set_font(self.font_family, '', 10)
        self.cell(0, 5, self.process_text('السنة الدراسية: 2024 / 2025'), 0, 1, 'C')
        
        # 3. خط فاصل ملون (أزرق غامق)
        self.ln(5)
        self.set_draw_color(44, 62, 80) # Dark Blue
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_draw_color(0) # Reset
        self.ln(5)

    # --- 1. تذييل التوقيعات (Fixed Footer) ---
    def footer(self):
        # رقم الصفحة
        self.set_y(-15)
        self.set_font(self.font_family, '', 8)
        self.cell(0, 10, self.process_text(f'صفحة {self.page_no()}'), 0, 0, 'C')

    def draw_signatures_fixed(self):
        """رسم التوقيعات في أسفل الصفحة الثانية دائماً"""
        # نذهب لموقع ثابت في الأسفل (مثلاً 240 من أصل 297)
        self.set_y(-50) 
        
        self.set_font(self.font_family, 'B', 11)
        w = 63 
        
        # رسم العناوين
        y = self.get_y()
        self.set_xy(10 + w*2, y)
        self.cell(w, 8, self.process_text("توقيع المربي(ة):"), 0, 0, 'C')
        
        self.set_xy(10 + w, y)
        self.cell(w, 8, self.process_text("توقيع المدير(ة):"), 0, 0, 'C')
        
        self.set_xy(10, y)
        self.cell(w, 8, self.process_text("إمضاء الولي:"), 0, 0, 'C')
        
        # خطوط التوقيع
        self.set_draw_color(180)
        self.set_line_width(0.2)
        line_y = y + 25
        self.line(30, line_y, 55, line_y)    
        self.line(93, line_y, 118, line_y)   
        self.line(156, line_y, 181, line_y)
        self.set_draw_color(0) # Reset

    # --- تفاصيل الطالب (كما هي، جيدة) ---
    def draw_student_details(self):
        start_y = self.get_y()
        self.set_fill_color(250, 250, 252)
        self.set_draw_color(220)
        self.rect(10, start_y, 190, 30, 'DF')
        self.set_draw_color(0) 

        y = start_y + 6
        # الصف الأول
        self.set_xy(160, y); self.set_font(self.font_family, '', 11)
        self.cell(30, 6, self.process_text("الاسم واللقب:"), 0, 0, 'R') 
        self.set_xy(100, y); self.set_font(self.font_family, 'B', 12) 
        self.cell(60, 6, self.process_text(self.student_name), 0, 0, 'R')

        self.set_xy(65, y); self.set_font(self.font_family, '', 11)
        self.cell(25, 6, self.process_text("المستوى:"), 0, 0, 'R')
        self.set_xy(15, y); self.set_font(self.font_family, 'B', 11)
        self.cell(50, 6, self.process_text(self.student_info.get('class_level','')), 0, 0, 'R')

        # الصف الثاني
        y += 10
        self.set_xy(160, y); self.set_font(self.font_family, '', 11)
        self.cell(30, 6, self.process_text("تاريخ الميلاد:"), 0, 0, 'R')
        self.set_xy(100, y); self.set_font(self.font_family, 'B', 11)
        self.cell(60, 6, self.process_text(self.student_info.get('dob','')), 0, 0, 'R')

        self.set_xy(65, y); self.set_font(self.font_family, '', 11)
        self.cell(25, 6, self.process_text("الجنس:"), 0, 0, 'R')
        self.set_xy(15, y); self.set_font(self.font_family, 'B', 11)
        self.cell(50, 6, self.process_text(self.student_info.get('gender','')), 0, 0, 'R')
        
        self.ln(20)

    # --- 6. الأيقونات والرموز الملونة ---
    def draw_custom_symbol(self, x, y, size, score):
        self.set_line_width(0.4)
        if score == 2: # مكتسب (أخضر)
            self.set_draw_color(39, 174, 96) # Green
            self.line(x, y + size/2, x + size/3, y + size)
            self.line(x + size/3, y + size, x + size, y)
        elif score == 1: # في طريق الاكتساب (برتقالي)
            self.set_draw_color(243, 156, 18) # Orange
            self.set_fill_color(243, 156, 18)
            r = size / 2.5
            self.circle(x + size/2, y + size/2, r, 'F')
        elif score == 0: # غير مكتسب (أحمر)
            self.set_draw_color(192, 57, 43) # Red
            self.line(x, y, x + size, y + size)
            self.line(x + size, y, x, y + size)
        self.set_draw_color(0)
        self.set_fill_color(0)

    def draw_legend(self):
        self.set_y(self.get_y() + 2)
        page_w = 190; box_w = 60
        margin = (page_w - (box_w * 3)) / 2 + 10
        y = self.get_y()
        
        def item(x, text, score):
            self.draw_custom_symbol(x + box_w - 15, y + 2, 4, score)
            self.set_xy(x, y + 2)
            self.set_font(self.font_family, '', 9)
            self.cell(box_w - 20, 6, self.process_text(text), 0, 0, 'C')

        item(margin + box_w * 2, "مكتسب", 2)
        item(margin + box_w, "في طريق الاكتساب", 1)
        item(margin, "غير مكتسب", 0)
        self.ln(10)

    def draw_columnar_table(self, title, data_groups, columns_count):
        if not data_groups: return
        self.set_font(self.font_family, 'B', 11)
        self.set_fill_color(235, 235, 235)
        self.cell(0, 9, self.process_text(title), 1, 1, 'C', True)
        
        col_width = 190 / columns_count
        skill_w = col_width * 0.88; mark_w = col_width * 0.12
        
        groups = list(data_groups.items())
        
        for i in range(0, len(groups), columns_count):
            batch = groups[i : i + columns_count]
            top_y = self.get_y()
            if top_y > 230: self.add_page(); top_y = self.get_y()
            
            curr_x = 10
            self.set_font(self.font_family, 'B', 9)
            self.set_fill_color(248, 248, 248)
            
            for subj, skills in batch:
                # حساب النسبة
                total = sum(s for _, s in skills); max_s = len(skills)*2
                pct = (total/max_s*100) if max_s else 0
                
                self.set_xy(curr_x, top_y)
                self.multi_cell(col_width, 7, self.process_text(f"{subj} ({pct:.0f}%)"), 1, 'C', True)
                curr_x += col_width
            
            self.set_y(top_y + 7)
            start_y = self.get_y()
            max_y = start_y
            curr_x = 10
            self.set_font(self.font_family, '', 8)
            
            for subj, skills in batch:
                col_y = start_y
                for skill, score in skills:
                    if col_y > 270: break
                    
                    self.set_xy(curr_x, col_y)
                    self.multi_cell(skill_w, 6, self.process_text(skill), 1, 'R')
                    
                    h = self.get_y() - col_y
                    self.set_xy(curr_x + skill_w, col_y)
                    self.cell(mark_w, h, "", 1) # Border
                    
                    self.draw_custom_symbol(curr_x+skill_w+(mark_w-3.5)/2, col_y+(h-3.5)/2, 3.5, score)
                    col_y += h
                
                if col_y > max_y: max_y = col_y
                curr_x += col_width
            self.set_y(max_y + 5)

    # --- 4. صندوق التحليل (الملاحظات الختامية) ---
    def draw_analysis_section(self, narrative):
        self.add_page()
        
        # العنوان الرئيسي للصفحة 2
        self.set_font(self.font_family, 'B', 14)
        self.cell(0, 10, self.process_text("التقرير التربوي الختامي"), 0, 1, 'C')
        self.ln(5)
        
        # الإطار والعنوان الفرعي
        self.set_fill_color(245, 247, 250) # أزرق/رمادي فاتح جداً
        self.set_draw_color(100, 100, 150) # إطار ملون خفيف
        self.set_line_width(0.3)
        
        # رسم خلفية الصندوق
        box_top = self.get_y()
        self.rect(10, box_top, 190, 100, 'DF') # ارتفاع مبدئي 100، النص سيحدد الفعلي
        
        self.set_xy(15, box_top + 5)
        self.set_font(self.font_family, 'B', 12)
        self.set_text_color(44, 62, 80) # لون كحلي للعنوان
        # أيقونة بسيطة (حرف)
        self.cell(0, 10, self.process_text("📝 تحليل شخصية وأداء المتعلم:"), 0, 1, 'R')
        
        # متن التحليل
        self.set_xy(15, box_top + 15)
        self.set_font(self.font_family, '', 11)
        self.set_text_color(0)
        self.multi_cell(180, 7, self.process_text(narrative), 0, 'R')
        
        # إعادة رسم الإطار ليتناسب مع طول النص الفعلي
        final_y = self.get_y() + 5
        height = final_y - box_top
        self.set_xy(10, box_top)
        self.rect(10, box_top, 190, height, 'D')
        
        self.set_y(final_y + 10)

    # دالة التوليد
    def generate(self, evaluation_data, narrative, action_plan):
        self.add_page()
        self.draw_student_details()
        self.draw_legend()
        
        # رسم الجداول (كما هي 3 أعمدة)
        for cat in ["academic", "behavioral"]:
            groups = {}
            if cat in evaluation_data:
                source = evaluation_data[cat]
                if cat == "academic":
                    for k, v in source.items(): groups[k] = list(v.items())
                else:
                    for m, sub in source.items():
                        for k, v in sub.items(): groups[k] = list(v.items())
            
            title = "التحصيل الدراسي" if cat == "academic" else "المهارات السلوكية"
            self.draw_columnar_table(title, groups, 3)

        # الصفحة الثانية: التحليل فقط
        self.draw_analysis_section(narrative)
        
        # التوقيعات في الأسفل دائماً
        self.draw_signatures_fixed()

        return bytes(self.output())

def create_pdf(student_name, student_info, data, narrative, action_plan):
    try:
        pdf = PDFReport(student_name, student_info)
        return pdf.generate(data, narrative, action_plan), None
    except Exception as e:
        return None, str(e)

