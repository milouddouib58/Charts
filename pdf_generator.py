from fpdf import FPDF
import os
import math

class PDFReport(FPDF):
    def __init__(self, student_name, student_info):
        super().__init__()
        self.student_name = student_name
        self.student_info = student_info
        self.custom_font_loaded = False
        self.font_family = 'Helvetica'
        
        # إعداد مسارات الخطوط (تأكد من وجود ملفات الخطوط في assets/fonts)
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.path_reg = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Regular.ttf')
        self.path_bold = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Bold.ttf')
        
        # محاولة تحميل الخط العربي
        if os.path.exists(self.path_reg) and os.path.exists(self.path_bold):
             try:
                self.add_font('Amiri', '', self.path_reg)
                self.add_font('Amiri', 'B', self.path_bold)
                self.font_family = 'Amiri'
                self.custom_font_loaded = True
             except Exception as e:
                print(f"Font load error: {e}")
        else:
            print("Warning: Amiri font not found. Arabic text might not render correctly.")

    def process_text(self, text):
        """معالجة النص العربي (تشكيل + اتجاه)"""
        if not self.custom_font_loaded: return str(text)
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(str(text)))
        except ImportError:
            return str(text)

    def header(self):
        # نترك الترويسة فارغة لأننا نرسم التفاصيل يدوياً في البداية
        pass

    def footer(self):
        # تذييل الصفحة برقم الصفحة
        self.set_y(-15)
        self.set_font(self.font_family, '', 8)
        self.cell(0, 10, self.process_text(f'صفحة {self.page_no()}'), 0, 0, 'C')

    # =========================================================================
    # دالة رسم تفاصيل الطالب (المصححة لمنع التداخل)
    # =========================================================================
    def draw_student_details(self):
        """رسم جدول معلومات التلميذ بتنسيق معدل لمنع التداخل"""
        self.set_y(10) # ضمان البدء من الأعلى
        self.set_font(self.font_family, 'B', 16)
        self.cell(0, 10, self.process_text('تقرير التقييم الفصلي الشامل'), 0, 1, 'C')
        self.ln(5)

        # إطار المعلومات الخلفي
        start_y = self.get_y()
        self.set_fill_color(248, 249, 250) # لون رمادي فاتح جداً
        self.set_draw_color(200, 200, 200)
        self.rect(10, start_y, 190, 35, 'FD')
        
        # إعدادات الخط للبيانات
        self.set_draw_color(0) # إعادة الأسود للنصوص

        # --- الصف الأول (الاسم + المستوى) ---
        y = start_y + 8
        
        # 1. الجهة اليمنى: الاسم واللقب
        # خانة العنوان (الاسم واللقب)
        self.set_xy(160, y) 
        self.set_font(self.font_family, '', 11)
        # العرض 30 ليتسع للكلمة
        self.cell(30, 6, self.process_text("الاسم واللقب:"), 0, 0, 'R') 
        
        # خانة القيمة (اسم الطالب الفعلي)
        self.set_xy(100, y) 
        self.set_font(self.font_family, 'B', 12) 
        # العرض 60 والموقع 100 يعطي مسافة آمنة عن العنوان
        self.cell(60, 6, self.process_text(self.student_name), 0, 0, 'R')

        # 2. الجهة اليسرى: المستوى
        # خانة العنوان
        self.set_xy(65, y)
        self.set_font(self.font_family, '', 11)
        self.cell(25, 6, self.process_text("المستوى:"), 0, 0, 'R')
        
        # خانة القيمة
        self.set_xy(15, y)
        self.set_font(self.font_family, 'B', 11)
        lvl = self.student_info.get('class_level', 'غير محدد')
        self.cell(50, 6, self.process_text(lvl), 0, 0, 'R')

        # --- الصف الثاني (تاريخ الميلاد + الجنس) ---
        y += 12 # زيادة المسافة العمودية بين الصفوف
        
        # 3. الجهة اليمنى: تاريخ الميلاد
        # خانة العنوان
        self.set_xy(160, y)
        self.set_font(self.font_family, '', 11)
        self.cell(30, 6, self.process_text("تاريخ الميلاد:"), 0, 0, 'R')
        
        # خانة القيمة
        self.set_xy(100, y)
        self.set_font(self.font_family, 'B', 11)
        dob = self.student_info.get('dob', '-')
        self.cell(60, 6, self.process_text(dob), 0, 0, 'R')

        # 4. الجهة اليسرى: الجنس
        # خانة العنوان
        self.set_xy(65, y)
        self.set_font(self.font_family, '', 11)
        self.cell(25, 6, self.process_text("الجنس:"), 0, 0, 'R')
        
        # خانة القيمة
        self.set_xy(15, y)
        self.set_font(self.font_family, 'B', 11)
        gender = self.student_info.get('gender', '-')
        self.cell(50, 6, self.process_text(gender), 0, 0, 'R')
        
        self.ln(20) # مسافة بعد الجدول

    def draw_custom_symbol(self, x, y, size, score):
        """
        رسم الرموز المخصصة
        score 2: ✔ (صح خضراء)
        score 1: ◐ (دائرة برتقالية)
        score 0: ✖ (خطأ حمراء)
        """
        self.set_line_width(0.4)
        
        if score == 2: # مكتسب (أخضر)
            self.set_draw_color(46, 204, 113) 
            # رسم علامة صح
            self.line(x, y + size/2, x + size/3, y + size)
            self.line(x + size/3, y + size, x + size, y)
            
        elif score == 1: # في طريق الاكتساب (برتقالي)
            self.set_draw_color(243, 156, 18)
            self.set_fill_color(243, 156, 18)
            # رسم دائرة صغيرة مملوءة
            r = size / 2.5
            cx, cy = x + size/2, y + size/2
            self.circle(cx, cy, r, 'F')

        elif score == 0: # غير مكتسب (أحمر)
            self.set_draw_color(231, 76, 60)
            # رسم علامة خطأ X
            self.line(x, y, x + size, y + size)
            self.line(x + size, y, x, y + size)

        # إعادة الألوان للأسود
        self.set_draw_color(0)
        self.set_fill_color(0)

    def draw_legend(self):
        """رسم مفتاح الرموز"""
        self.set_y(self.get_y() + 5)
        
        page_w = 190
        box_w = 60
        margin = (page_w - (box_w * 3)) / 2 + 10
        y = self.get_y()
        
        def draw_key_item(x, text, score):
            # رسم الرمز
            self.draw_custom_symbol(x + box_w - 15, y + 2, 5, score)
            # كتابة النص
            self.set_xy(x, y + 2)
            self.set_font(self.font_family, '', 10)
            self.cell(box_w - 20, 6, self.process_text(text), 0, 0, 'C')

        draw_key_item(margin + box_w * 2, "مكتسب", 2)
        draw_key_item(margin + box_w, "في طريق الاكتساب", 1)
        draw_key_item(margin, "غير مكتسب", 0)
        
        self.ln(12)

    def draw_columnar_table(self, title, data_groups, columns_count):
        """رسم الجدول العمودي مع النسب المئوية وحماية الصفحة"""
        if not data_groups: return

        # عنوان الجدول
        self.set_font(self.font_family, 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, self.process_text(title), ln=True, align='C', fill=True, border=1)
        
        # الأبعاد
        page_width = 190
        col_width = page_width / columns_count
        skill_w = col_width * 0.80 # 80% للنص
        mark_w = col_width * 0.20 # 20% للرمز
        
        groups_list = list(data_groups.items())
        total_groups = len(groups_list)
        
        # المرور على المجموعات (Batching)
        for i in range(0, total_groups, columns_count):
            batch = groups_list[i : i + columns_count]
            
            # التحقق من بداية صفحة جديدة للرؤوس
            top_y = self.get_y()
            if top_y > 250: 
                self.add_page()
                top_y = self.get_y()
            
            current_x = self.get_x()
            self.set_font(self.font_family, 'B', 10)
            self.set_fill_color(245, 245, 245)
            
            # --- رسم رؤوس الأعمدة مع النسب ---
            for subject_name, skills in batch:
                # حساب النسبة
                total_score = sum(score for _, score in skills)
                max_score = len(skills) * 2
                percent = (total_score / max_score * 100) if max_score > 0 else 0
                
                header_text = f"{subject_name} ({percent:.0f}%)"
                
                self.set_xy(current_x, top_y)
                self.multi_cell(col_width, 8, self.process_text(header_text), border=1, align='C', fill=True)
                current_x += col_width
            
            # النزول لأسفل الرؤوس
            self.set_y(top_y + 8) 
            content_start_y = self.get_y()
            max_y_reached = content_start_y
            
            current_x = 10 
            self.set_font(self.font_family, '', 9)
            row_h = 7
            
            # --- رسم محتوى الأعمدة ---
            for subject_name, skills in batch:
                col_y = content_start_y
                
                for skill_name, score in skills:
                    # حماية تجاوز الصفحة (Overflow)
                    if col_y > 270: 
                        self.set_xy(current_x, col_y)
                        self.set_font(self.font_family, 'I', 7)
                        self.cell(skill_w + mark_w, row_h, self.process_text("...يتبع"), 0, 0, 'C')
                        self.set_font(self.font_family, '', 9)
                        break 

                    # 1. اسم المهارة
                    self.set_xy(current_x, col_y)
                    self.multi_cell(skill_w, row_h, self.process_text(skill_name), border=1, align='R')
                    
                    actual_h = self.get_y() - col_y
                    
                    # 2. رمز التقييم
                    self.set_xy(current_x + skill_w, col_y)
                    self.rect(current_x + skill_w, col_y, mark_w, actual_h)
                    
                    # رسم الرمز وسط الخلية
                    symbol_size = 4
                    sym_x = current_x + skill_w + (mark_w - symbol_size)/2
                    sym_y = col_y + (actual_h - symbol_size)/2
                    self.draw_custom_symbol(sym_x, sym_y, symbol_size, score)
                    
                    col_y += actual_h
                
                if col_y > max_y_reached:
                    max_y_reached = col_y
                
                current_x += col_width

            self.set_y(max_y_reached + 5)

    def draw_signatures_footer(self):
        """رسم التوقيعات في الأسفل"""
        if self.get_y() > 250: self.add_page()
        
        self.ln(5)
        y = self.get_y()
        self.set_font(self.font_family, 'B', 11)
        
        w = 63 # ثلث الصفحة تقريباً
        
        # المربي
        self.set_xy(10 + w*2, y)
        self.cell(w, 8, self.process_text("توقيع المربي(ة):"), 0, 0, 'C')
        
        # المدير
        self.set_xy(10 + w, y)
        self.cell(w, 8, self.process_text("توقيع المدير(ة):"), 0, 0, 'C')
        
        # الولي
        self.set_xy(10, y)
        self.cell(w, 8, self.process_text("إمضاء الولي:"), 0, 0, 'C')
        
        # خطوط التوقيع
        self.set_draw_color(150)
        line_y = y + 25
        self.line(25, line_y, 60, line_y)    # الولي
        self.line(88, line_y, 123, line_y)   # المدير
        self.line(151, line_y, 186, line_y)  # المربي

    def generate(self, evaluation_data, narrative, action_plan):
        self.add_page()
        
        # 1. التفاصيل
        self.draw_student_details()
        
        # 2. المفتاح
        self.draw_legend()
        
        # 3. جدول الأكاديمي
        academic_grouped = {}
        if "academic" in evaluation_data:
            for subject, skills_dict in evaluation_data["academic"].items():
                if isinstance(skills_dict, dict):
                    skill_list = []
                    for skill, score in skills_dict.items():
                        skill_list.append((skill, score))
                    academic_grouped[subject] = skill_list
        
        self.draw_columnar_table('التحصيل الدراسي', academic_grouped, columns_count=4)
        
        # 4. جدول السلوك
        behavioral_grouped = {}
        if "behavioral" in evaluation_data:
            for main, subs in evaluation_data["behavioral"].items():
                if isinstance(subs, dict):
                    for sub_cat, skills_dict in subs.items():
                        skill_list = []
                        if isinstance(skills_dict, dict):
                            for skill, score in skills_dict.items():
                                skill_list.append((skill, score))
                        # دمج الاسم ليكون واضحاً في العمود
                        full_name = f"{sub_cat}" 
                        behavioral_grouped[full_name] = skill_list

        self.draw_columnar_table('المهارات السلوكية والشخصية', behavioral_grouped, columns_count=3)

        # 5. الملاحظات والخطة
        if self.get_y() < 240:
            self.ln(5)
            self.set_font(self.font_family, 'B', 11)
            self.cell(0, 8, self.process_text('ملاحظات وتوصيات:'), 'B', 1, 'R')
            self.set_font(self.font_family, '', 10)
            
            full_text = narrative
            if action_plan:
                full_text += "\n\nخطة العمل المقترحة:\n" + "\n".join([f"- {k}: {v}" for k,v in action_plan])
            
            self.multi_cell(0, 6, self.process_text(full_text), 0, 'R')

        # 6. التوقيعات
        self.draw_signatures_footer()

        return bytes(self.output())

# =============================================================================
# الوظيفة الرئيسية التي يستدعيها التطبيق
# =============================================================================
def create_pdf(student_name, student_info, data, narrative, action_plan):
    try:
        # إنشاء الكائن وتمرير البيانات
        pdf = PDFReport(student_name, student_info)
        
        # توليد المحتوى
        pdf_bytes = pdf.generate(data, narrative, action_plan)
        
        return pdf_bytes, None
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, str(e)
