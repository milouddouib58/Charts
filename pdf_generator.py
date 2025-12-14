from fpdf import FPDF
import os
import math

class PDFReport(FPDF):
    def __init__(self, student_name):
        super().__init__()
        self.student_name = student_name
        self.custom_font_loaded = False
        self.font_family = 'Helvetica'
        
        # إعداد الخطوط
        base_path = os.path.dirname(os.path.abspath(__file__))
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
        self.set_font(self.font_family, 'B', 14)
        title = self.process_text('تقرير التقييم الشامل')
        self.cell(0, 8, title, border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font(self.font_family, '', 10)
        subtitle = self.process_text(f'اسم التلميذ: {self.student_name}')
        self.cell(0, 6, subtitle, border='B', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def draw_symbol(self, x, y, w, h, score):
        """رسم الرموز (+, ┴, -)"""
        cx, cy = x + (w / 2), y + (h / 2)
        r = 2.5
        self.set_line_width(0.4)
        self.set_draw_color(0) # Black

        if score == 2: # مكتسب (+)
            self.line(cx - r, cy, cx + r, cy)
            self.line(cx, cy - r, cx, cy + r)
        elif score == 1: # في طريق الاكتساب (┴)
            self.line(cx - r, cy, cx + r, cy)
            self.line(cx, cy - r, cx, cy)
        elif score == 0: # غير مكتسب (-)
            self.line(cx - r, cy, cx + r, cy)

    def draw_columnar_table(self, title, data_groups, columns_count):
        """
        رسم جدول يعتمد على الأعمدة (كل عمود يمثل مادة/مجالاً)
        data_groups: قاموس { 'اسم المادة': [ (مهارة, درجة), (مهارة, درجة)... ] }
        columns_count: عدد الأعمدة في الصف الواحد (مثلاً 4 مواد في الصف)
        """
        if not data_groups: return

        # 1. عنوان الجدول الرئيسي
        self.set_font(self.font_family, 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, self.process_text(title), ln=True, align='C', fill=True, border=1)
        
        # إعدادات الأبعاد
        page_width = 190
        col_width = page_width / columns_count # عرض "المادة" الواحدة
        # داخل كل مادة، نحتاج تقسيم العرض إلى (اسم المهارة) و (الرمز)
        # نسبة 75% للنص و 25% للرمز
        skill_w = col_width * 0.75
        mark_w = col_width * 0.25
        
        # تحويل القاموس إلى قائمة للتعامل مع الفهارس
        groups_list = list(data_groups.items())
        total_groups = len(groups_list)
        
        # حلقة للمرور على المواد (مجموعة كل columns_count مادة)
        for i in range(0, total_groups, columns_count):
            batch = groups_list[i : i + columns_count]
            
            # --- رسم رؤوس الأعمدة (أسماء المواد) ---
            self.set_font(self.font_family, 'B', 10)
            self.set_fill_color(245, 245, 245)
            
            # نحفظ موقع Y قبل الرؤوس
            top_y = self.get_y()
            if top_y > 270: self.add_page(); top_y = self.get_y()
            
            # رسم عناوين المواد لهذا الصف
            current_x = self.get_x() # يفترض أن يبدأ من اليسار (FPDF standard)
            # ولكن لترتيب عربي (المادة الأولى يمين)، سنقوم بقراءة الـ batch وعكس أماكن الرسم،
            # أو رسمها بترتيبها كما هي في القائمة (حسب الترتيب الوارد في البيانات)
            
            # لرسم العناوين
            for subject_name, _ in batch:
                self.set_xy(current_x, top_y)
                self.cell(col_width, 8, self.process_text(subject_name), border=1, align='C', fill=True)
                current_x += col_width
            
            # إذا كان الصف ناقصاً (أقل من العدد المطلوب)، نترك فراغاً
            self.ln(8) 
            
            # --- رسم المهارات تحت كل مادة ---
            # التحدي: كل مادة لديها عدد مختلف من المهارات.
            # يجب أن نجد "أقصى عدد مهارات" في هذا الصف لنعرف ارتفاع الصف الكلي،
            # لكن الطلب هو أن تكون المهارات تحت بعضها.
            # سنقوم برسم عمود كل مادة بشكل مستقل بدءاً من Y الحالي.
            
            content_start_y = self.get_y()
            max_y_reached = content_start_y
            
            # إعادة ضبط X للبدء
            current_x = 10 # هامش الصفحة الأيسر الافتراضي
            
            self.set_font(self.font_family, '', 8)
            row_h = 6 # ارتفاع سطر المهارة
            
            for subject_name, skills in batch:
                # نحفظ بداية العمود لهذه المادة
                col_y = content_start_y
                
                for skill_name, score in skills:
                    # التحقق من الصفحة
                    if col_y > 280: 
                        # هذا السيناريو معقد في الجداول العمودية، سنفترض أن الصفحة تكفي 
                        # أو يتم تقليص الخط. للتبسيط لن نعالج كسر الصفحة بداخل العمود الواحد هنا.
                        pass

                    # 1. اسم المهارة
                    self.set_xy(current_x, col_y)
                    # MultiCell لاسم المهارة في حال كان طويلاً
                    # نحتاج حفظ Y بعد الـ MultiCell
                    self.multi_cell(skill_w, row_h, self.process_text(skill_name), border=1, align='R')
                    
                    # ارتفاع الخلية الفعلي الذي تم رسمه
                    actual_h = self.get_y() - col_y
                    
                    # 2. رمز التقييم (بجانب الاسم)
                    # يجب أن يكون ارتفاعه مساوياً لارتفاع خلية الاسم (actual_h)
                    self.set_xy(current_x + skill_w, col_y)
                    self.rect(current_x + skill_w, col_y, mark_w, actual_h)
                    self.draw_symbol(current_x + skill_w, col_y, mark_w, actual_h, score)
                    
                    # تحديث Y للمهارة التالية
                    col_y += actual_h
                
                # تتبع أقصى ارتفاع وصل إليه أي عمود في هذا الصف
                if col_y > max_y_reached:
                    max_y_reached = col_y
                
                # الانتقال للعمود (المادة) التالية
                current_x += col_width

            # بعد الانتهاء من رسم كل أعمدة هذا الصف (Batch)، نحرك المؤشر لأقصى نقطة وصل لها أطول عمود
            # ونضيف مسافة صغيرة
            self.set_y(max_y_reached + 2)

    def generate(self, evaluation_data, summary_stats, narrative, action_plan):
        self.add_page()
        
        # ملخص الرموز والإحصائيات
        self.set_font(self.font_family, '', 9)
        info = f"النسبة: {summary_stats['score']:.1f}% | نقاط الضعف: {summary_stats['weaknesses_count']}"
        key = "(+) مكتسب | (┴) في طريق الاكتساب | (-) غير مكتسب"
        
        self.set_fill_color(240, 240, 240)
        self.cell(90, 8, self.process_text(info), 1, 0, 'C', 1)
        self.cell(100, 8, self.process_text(key), 1, 1, 'C', 1)
        self.ln(2)

        # ---------------------------------------------------------
        # الجدول الأول: المواد الدراسية (التحصيل الأكاديمي)
        # ---------------------------------------------------------
        # نريد إعادة هيكلة البيانات لتكون: { 'لغة عربية': [(مهارة, درجة)...], 'رياضيات': [...] }
        academic_grouped = {}
        if "academic" in evaluation_data:
            for subject, skills_dict in evaluation_data["academic"].items():
                if isinstance(skills_dict, dict):
                    skill_list = []
                    for skill, score in skills_dict.items():
                        skill_list.append((skill, score))
                    academic_grouped[subject] = skill_list
        
        # رسم الجدول (4 مواد في الصف الواحد)
        # الأعمدة في الجدول = عدد المواد في الصف. 
        # لكل مادة عمود خاص يحتوي مهاراتها تحته.
        self.draw_columnar_table('التحصيل الدراسي', academic_grouped, columns_count=4)
        
        self.ln(3)

        # ---------------------------------------------------------
        # الجدول الثاني: المهارات السلوكية
        # ---------------------------------------------------------
        # البيانات تأتي: MainCategory -> SubCategory -> Skills
        # سنعتبر "SubCategory" هي "المادة/المجال" ونضعها في الرأس
        behavioral_grouped = {}
        if "behavioral" in evaluation_data:
            for main, subs in evaluation_data["behavioral"].items():
                if isinstance(subs, dict):
                    for sub_cat, skills_dict in subs.items():
                        # اسم الرأس سيكون الفئة الفرعية (مثلاً: "انضباط صفي")
                        # أو دمجها مع الرئيسي إذا لزم الأمر
                        header_name = sub_cat 
                        
                        skill_list = []
                        if isinstance(skills_dict, dict):
                            for skill, score in skills_dict.items():
                                skill_list.append((skill, score))
                        behavioral_grouped[header_name] = skill_list

        # رسم الجدول السلوكي (3 مجالات في الصف الواحد ليكون أوسع قليلاً)
        self.draw_columnar_table('المهارات السلوكية والشخصية', behavioral_grouped, columns_count=3)

        # ---------------------------------------------------------
        # الملاحظات
        # ---------------------------------------------------------
        # التحقق من المساحة المتبقية
        if self.get_y() < 270:
            self.ln(3)
            self.set_font(self.font_family, 'B', 11)
            self.cell(0, 6, self.process_text('ملاحظات وتوصيات'), 'B', 1, 'R')
            self.set_font(self.font_family, '', 9)
            text = narrative
            if action_plan:
               text += " | خطة مقترحة: " + " - ".join([f"{k}: {v}" for k,v in action_plan])
            
            self.multi_cell(0, 5, self.process_text(text), 0, 'R')

        return bytes(self.output())

def create_pdf(student_name, data, narrative, action_plan):
    try:
        pdf = PDFReport(student_name)
        
        # حساب الإحصائيات (نفس المنطق السابق)
        total = 0
        max_score = 0
        weaknesses = 0
        
        # Helper to traverse
        def calc_stats(d):
            t, m, w = 0, 0, 0
            if isinstance(d, dict):
                for k, v in d.items():
                    if isinstance(v, (int, float)): # Reached score
                        t += v
                        m += 2
                        if v == 0: w += 1
                    else:
                        st, sm, sw = calc_stats(v)
                        t += st; m += sm; w += sw
            return t, m, w

        t1, m1, w1 = calc_stats(data.get("academic", {}))
        t2, m2, w2 = calc_stats(data.get("behavioral", {}))
        
        final_score = ((t1+t2) / (m1+m2) * 100) if (m1+m2) > 0 else 0
        stats = {"score": final_score, "weaknesses_count": w1+w2}
        
        pdf_bytes = pdf.generate(data, stats, narrative, action_plan)
        return pdf_bytes, None
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, str(e)

