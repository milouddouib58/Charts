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
        
        # إعداد مسارات الخطوط
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.path_reg = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Regular.ttf')
        self.path_bold = os.path.join(base_path, 'assets', 'fonts', 'Amiri-Bold.ttf')
        
        if os.path.exists(self.path_reg) and os.path.exists(self.path_bold):
             try:
                self.add_font('Amiri', '', self.path_reg)
                self.add_font('Amiri', 'B', self.path_bold)
                self.font_family = 'Amiri'
                self.custom_font_loaded = True
             except Exception as e:
                print(f"Font load error: {e}")
        else:
            print("Warning: Amiri font not found.")

    def process_text(self, text):
        if not self.custom_font_loaded: return str(text)
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(str(text)))
        except ImportError:
            return str(text)

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family, '', 8)
        self.cell(0, 10, self.process_text(f'صفحة {self.page_no()}'), 0, 0, 'C')

    # =========================================================================
    # 1. تفاصيل الطالب (التنسيق المصحح)
    # =========================================================================
    def draw_student_details(self):
        self.set_y(10)
        self.set_font(self.font_family, 'B', 16)
        self.cell(0, 10, self.process_text('تقرير التقييم الفصلي الشامل'), 0, 1, 'C')
        self.ln(5)

        start_y = self.get_y()
        self.set_fill_color(248, 249, 250)
        self.set_draw_color(200, 200, 200)
        self.rect(10, start_y, 190, 35, 'FD')
        self.set_draw_color(0) 

        y = start_y + 8
        # الاسم واللقب
        self.set_xy(160, y) 
        self.set_font(self.font_family, '', 11)
        self.cell(30, 6, self.process_text("الاسم واللقب:"), 0, 0, 'R') 
        self.set_xy(100, y) 
        self.set_font(self.font_family, 'B', 12) 
        self.cell(60, 6, self.process_text(self.student_name), 0, 0, 'R')

        # المستوى
        self.set_xy(65, y)
        self.set_font(self.font_family, '', 11)
        self.cell(25, 6, self.process_text("المستوى:"), 0, 0, 'R')
        self.set_xy(15, y)
        self.set_font(self.font_family, 'B', 11)
        lvl = self.student_info.get('class_level', 'غير محدد')
        self.cell(50, 6, self.process_text(lvl), 0, 0, 'R')

        y += 12
        # تاريخ الميلاد
        self.set_xy(160, y)
        self.set_font(self.font_family, '', 11)
        self.cell(30, 6, self.process_text("تاريخ الميلاد:"), 0, 0, 'R')
        self.set_xy(100, y)
        self.set_font(self.font_family, 'B', 11)
        dob = self.student_info.get('dob', '-')
        self.cell(60, 6, self.process_text(dob), 0, 0, 'R')

        # الجنس
        self.set_xy(65, y)
        self.set_font(self.font_family, '', 11)
        self.cell(25, 6, self.process_text("الجنس:"), 0, 0, 'R')
        self.set_xy(15, y)
        self.set_font(self.font_family, 'B', 11)
        gender = self.student_info.get('gender', '-')
        self.cell(50, 6, self.process_text(gender), 0, 0, 'R')
        
        self.ln(20)

    # =========================================================================
    # 2. رسم الرموز
    # =========================================================================
    def draw_custom_symbol(self, x, y, size, score):
        self.set_line_width(0.4)
        if score == 2: # مكتسب (أخضر)
            self.set_draw_color(46, 204, 113) 
            self.line(x, y + size/2, x + size/3, y + size)
            self.line(x + size/3, y + size, x + size, y)
        elif score == 1: # في طريق الاكتساب (برتقالي)
            self.set_draw_color(243, 156, 18)
            self.set_fill_color(243, 156, 18)
            r = size / 2.5
            cx, cy = x + size/2, y + size/2
            self.circle(cx, cy, r, 'F')
        elif score == 0: # غير مكتسب (أحمر)
            self.set_draw_color(231, 76, 60)
            self.line(x, y, x + size, y + size)
            self.line(x + size, y, x, y + size)
        self.set_draw_color(0)
        self.set_fill_color(0)

    def draw_legend(self):
        self.set_y(self.get_y() + 5)
        page_w = 190
        box_w = 60
        margin = (page_w - (box_w * 3)) / 2 + 10
        y = self.get_y()
        
        def draw_key_item(x, text, score):
            self.draw_custom_symbol(x + box_w - 15, y + 2, 5, score)
            self.set_xy(x, y + 2)
            self.set_font(self.font_family, '', 10)
            self.cell(box_w - 20, 6, self.process_text(text), 0, 0, 'C')

        draw_key_item(margin + box_w * 2, "مكتسب", 2)
        draw_key_item(margin + box_w, "في طريق الاكتساب", 1)
        draw_key_item(margin, "غير مكتسب", 0)
        self.ln(12)

    # =========================================================================
    # 3. الجدول العمودي (إصلاح مشكلة العرض والخط)
    # =========================================================================
    def draw_columnar_table(self, title, data_groups, columns_count):
        if not data_groups: return

        # العنوان
        self.set_font(self.font_family, 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, self.process_text(title), ln=True, align='C', fill=True, border=1)
        
        page_width = 190
        col_width = page_width / columns_count
        
        # تعديل النسب: إعطاء مساحة أكبر للنص لتفادي الخطأ
        skill_w = col_width * 0.88  # 88% للنص
        mark_w = col_width * 0.12   # 12% للرمز
        
        groups_list = list(data_groups.items())
        total_groups = len(groups_list)
        
        for i in range(0, total_groups, columns_count):
            batch = groups_list[i : i + columns_count]
            
            # التحقق من بداية الصفحة للرؤوس
            top_y = self.get_y()
            if top_y > 240: 
                self.add_page()
                top_y = self.get_y()
            
            current_x = self.get_x()
            self.set_font(self.font_family, 'B', 9) # خط العناوين صغير قليلاً
            self.set_fill_color(245, 245, 245)
            
            # رسم رؤوس الأعمدة
            for subject_name, skills in batch:
                total_score = sum(score for _, score in skills)
                max_score = len(skills) * 2
                percent = (total_score / max_score * 100) if max_score > 0 else 0
                header_text = f"{subject_name} ({percent:.0f}%)"
                
                self.set_xy(current_x, top_y)
                self.multi_cell(col_width, 8, self.process_text(header_text), border=1, align='C', fill=True)
                current_x += col_width
            
            self.set_y(top_y + 8) 
            content_start_y = self.get_y()
            max_y_reached = content_start_y
            
            current_x = 10 
            
            # === تصغير الخط لـ 8 لتفادي خطأ المساحة ===
            self.set_font(self.font_family, '', 8) 
            row_h = 6 # ارتفاع السطر أقل قليلاً
            
            for subject_name, skills in batch:
                col_y = content_start_y
                for skill_name, score in skills:
                    # التحقق من نهاية الصفحة
                    if col_y > 270: 
                        self.set_xy(current_x, col_y)
                        self.set_font(self.font_family, 'I', 7)
                        self.cell(skill_w + mark_w, row_h, self.process_text("..."), 0, 0, 'C')
                        self.set_font(self.font_family, '', 8)
                        break 

                    # رسم اسم المهارة
                    self.set_xy(current_x, col_y)
                    self.multi_cell(skill_w, row_h, self.process_text(skill_name), border=1, align='R')
                    
                    actual_h = self.get_y() - col_y
                    
                    # رسم مربع الرمز
                    self.set_xy(current_x + skill_w, col_y)
                    self.rect(current_x + skill_w, col_y, mark_w, actual_h)
                    
                    # رسم الرمز
                    symbol_size = 3.5 
                    sym_x = current_x + skill_w + (mark_w - symbol_size)/2
                    sym_y = col_y + (actual_h - symbol_size)/2
                    self.draw_custom_symbol(sym_x, sym_y, symbol_size, score)
                    
                    col_y += actual_h
                
                if col_y > max_y_reached:
                    max_y_reached = col_y
                current_x += col_width

            self.set_y(max_y_reached + 5)

    # =========================================================================
    # 4. قسم التحليل (في صفحة جديدة إجبارياً)
    # =========================================================================
    def draw_analysis_section(self, narrative, action_plan):
        # === إجبار الانتقال لصفحة جديدة للتحليل ===
        self.add_page()
        
        # العنوان الرئيسي للصفحة الثانية
        self.set_font(self.font_family, 'B', 14)
        self.cell(0, 10, self.process_text("التحليل التربوي والخطة العلاجية"), 0, 1, 'C')
        self.ln(5)
        
        # 1. التحليل التربوي
        self.set_fill_color(240, 248, 255) 
        self.set_font(self.font_family, 'B', 12)
        self.cell(0, 10, self.process_text("📝 تحليل أداء المتعلم:"), 0, 1, 'R', True)
        
        self.set_font(self.font_family, '', 11)
        self.ln(2)
        self.multi_cell(0, 7, self.process_text(narrative), 0, 'R')
        self.ln(8)

        # 2. الخطة العلاجية
        if action_plan:
            self.set_fill_color(255, 248, 225) 
            self.set_font(self.font_family, 'B', 12)
            self.cell(0, 10, self.process_text("💡 الحلول المقترحة (الخطة العلاجية):"), 0, 1, 'R', True)
            self.ln(2)
            
            self.set_font(self.font_family, '', 11)
            
            for skill, recommendation in action_plan:
                if self.get_y() > 270: self.add_page()
                
                # استخدام نقطة سوداء
                bullet = "• "
                text = f"{skill}: {recommendation}"
                
                # طباعة النقطة
                self.set_x(180) # بداية السطر من اليمين تقريباً
                
                # طباعة النص
                self.multi_cell(0, 7, self.process_text(f"• {text}"), 0, 'R')
            
            self.ln(5)

    # =========================================================================
    # 5. التوقيعات (في ذيل الصفحة الثانية)
    # =========================================================================
    def draw_signatures_footer(self):
        # نضع التوقيعات في أسفل الصفحة الحالية (الصفحة الثانية)
        # نحسب الموقع للتأكد أنه في الأسفل
        
        current_y = self.get_y()
        # إذا بقي مساحة كبيرة، ندفع التوقيع للأسفل قليلاً ليكون شكله جميل
        if current_y < 220:
            self.set_y(230)
        elif current_y > 250:
            self.add_page()
            self.set_y(230)
            
        self.ln(5)
        y = self.get_y()
        self.set_font(self.font_family, 'B', 11)
        
        w = 63 
        
        self.set_xy(10 + w*2, y)
        self.cell(w, 8, self.process_text("توقيع المربي(ة):"), 0, 0, 'C')
        
        self.set_xy(10 + w, y)
        self.cell(w, 8, self.process_text("توقيع المدير(ة):"), 0, 0, 'C')
        
        self.set_xy(10, y)
        self.cell(w, 8, self.process_text("إمضاء الولي:"), 0, 0, 'C')
        
        self.set_draw_color(150)
        line_y = y + 25
        self.line(25, line_y, 60, line_y)    
        self.line(88, line_y, 123, line_y)   
        self.line(151, line_y, 186, line_y)  

    # =========================================================================
    # دالة التوليد الرئيسية
    # =========================================================================
    def generate(self, evaluation_data, narrative, action_plan):
        self.add_page()
        
        # الصفحة الأولى: البيانات والجداول
        self.draw_student_details()
        self.draw_legend()
        
        academic_grouped = {}
        if "academic" in evaluation_data:
            for subject, skills_dict in evaluation_data["academic"].items():
                if isinstance(skills_dict, dict):
                    skill_list = []
                    for skill, score in skills_dict.items():
                        skill_list.append((skill, score))
                    academic_grouped[subject] = skill_list
        
        # 3 أعمدة لتجنب الخطأ
        self.draw_columnar_table('التحصيل الدراسي', academic_grouped, columns_count=3)
        
        behavioral_grouped = {}
        if "behavioral" in evaluation_data:
            for main, subs in evaluation_data["behavioral"].items():
                if isinstance(subs, dict):
                    for sub_cat, skills_dict in subs.items():
                        skill_list = []
                        if isinstance(skills_dict, dict):
                            for skill, score in skills_dict.items():
                                skill_list.append((skill, score))
                        full_name = f"{sub_cat}" 
                        behavioral_grouped[full_name] = skill_list

        self.draw_columnar_table('المهارات السلوكية والشخصية', behavioral_grouped, columns_count=3)
        
        # الصفحة الثانية: التحليل والتوقيعات
        self.draw_analysis_section(narrative, action_plan)
        self.draw_signatures_footer()

        return bytes(self.output())

def create_pdf(student_name, student_info, data, narrative, action_plan):
    try:
        pdf = PDFReport(student_name, student_info)
        pdf_bytes = pdf.generate(data, narrative, action_plan)
        return pdf_bytes, None
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, str(e)

