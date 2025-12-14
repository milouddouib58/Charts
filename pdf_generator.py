from fpdf import FPDF
import os

class PDFReport(FPDF):
    def __init__(self, student_name):
        super().__init__()
        self.student_name = student_name
        self.custom_font_loaded = False
        self.font_family = 'Helvetica' # Default
        
        # إعداد المسارات للخطوط
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
                raise ValueError(f"Failed to load fonts: {e}")
        else:
            raise ValueError(f"Font files not found at {path_reg}")

    def process_text(self, text):
        """إعادة تشكيل النص العربي ليظهر بشكل صحيح"""
        if not self.custom_font_loaded:
            return str(text)
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        except ImportError:
            return str(text)

    def get_status_label(self, score):
        """نصوص تقييم مختصرة لتناسب الجدول الضيق"""
        if score == 2: return "مكتسب"
        if score == 1: return "في الطريق" # اختصار لـ في طريق الاكتساب
        return "غير مكتسب"

    def header(self):
        # رأس صفحة مدمج
        self.set_font(self.font_family, 'B', 14)
        title = self.process_text('تقرير التقييم الشامل')
        self.cell(0, 8, title, border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        
        self.set_font(self.font_family, '', 10)
        subtitle = self.process_text(f'اسم التلميذ: {self.student_name} | نظام التقييم التربوي')
        self.cell(0, 6, subtitle, border='B', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font(self.font_family, '', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def draw_grid_table(self, title, items, columns_per_row, col_widths):
        """
        دالة مساعدة لرسم الجداول بنظام الشبكة
        items: قائمة من (اسم, درجة)
        columns_per_row: عدد الأزواج في الصف (مثلا 4 أزواج = 8 أعمدة)
        col_widths: قائمة بعرض العمودين [عرض_الاسم, عرض_الدرجة]
        """
        if not items: return

        # رسم عنوان الجدول
        self.set_font(self.font_family, 'B', 12)
        self.set_fill_color(240, 240, 240)
        processed_title = self.process_text(title)
        self.cell(0, 8, processed_title, ln=True, align='R', fill=True)
        
        # إعدادات الخط للجدول
        self.set_font(self.font_family, '', 9) 
        row_height = 7
        
        # تقسيم البيانات إلى مجموعات (Chunks)
        # إذا كان columns_per_row = 4 (يعني 8 أعمدة فعلية)، نأخذ 4 عناصر في كل صف
        total_items = len(items)
        
        for i in range(0, total_items, columns_per_row):
            chunk = items[i : i + columns_per_row]
            
            # لأن العربية من اليمين لليسار، سنقوم برسم الخلايا بالترتيب
            # ولكن نجعل محاذاة النص لليمين.
            # للحفاظ على الترتيب البصري العربي (العمود الأول يمين)، يعتمد ذلك على ترتيب البيانات في القائمة
            # سنقوم بعكس ترتيب الـ chunk لطباعتها من اليسار لليمين فتظهر اليمين هو الأول منطقياً
            # أو نتركها كما هي ونعتمد تدفق الصفحة. سنتركها لتملأ من اليمين لليسار بصرياً عبر محاذاة النص.
            
            # لحساب التموضع الدقيق، سنستخدم x, y
            start_x = self.get_x()
            
            # نريد طباعة العناصر بحيث يظهر العنصر الأول في القائمة في أقصى اليمين
            # FPDF يطبع من اليسار. لذا سنعكس الـ Chunk الحالية ليتم طباعة العنصر الأخير أولاً (يسار) والأول أخيراً (يمين)
            # هذا يخلق وهم الجدول العربي الصحيح
            reversed_chunk = chunk[::-1] 
            
            # إذا كان الصف غير مكتمل (أقل من العدد المطلوب)، نحتاج لإزاحة المؤشر ليبدأ من المكان الصحيح
            empty_slots = columns_per_row - len(chunk)
            if empty_slots > 0:
                # نحسب المسافة الفارغة على اليسار
                total_pair_width = col_widths[0] + col_widths[1]
                self.set_x(start_x + (empty_slots * total_pair_width))

            for item_name, item_score in reversed_chunk:
                # الاسم
                self.set_font(self.font_family, '', 8) # خط صغير للاسم
                name_txt = self.process_text(item_name)
                # قد نحتاج لقص النص إذا كان طويلاً جداً
                if len(name_txt) > 25: name_txt = name_txt[:22] + ".."
                
                self.cell(col_widths[0], row_height, name_txt, border=1, align='R')
                
                # التقييم
                self.set_font(self.font_family, 'B', 8)
                score_txt = self.process_text(self.get_status_label(item_score))
                
                # تلوين الخلفية حسب الدرجة لتحسين الرؤية
                if item_score == 0: self.set_fill_color(255, 235, 235) # أحمر فاتح
                elif item_score == 2: self.set_fill_color(235, 255, 235) # أخضر فاتح
                else: self.set_fill_color(255, 255, 255)
                
                self.cell(col_widths[1], row_height, score_txt, border=1, align='C', fill=True)
            
            self.ln()
        
        self.ln(3) # مسافة بعد الجدول

    def generate(self, evaluation_data, summary_stats, narrative, action_plan):
        self.add_page()
        
        # 1. الملخص السريع (أفقي لتوفير المساحة)
        self.set_font(self.font_family, 'B', 11)
        score_txt = self.process_text(f"النسبة العامة: {summary_stats['score']:.1f}%")
        weak_txt = self.process_text(f"نقاط الضعف: {summary_stats['weaknesses_count']}")
        
        # رسم مربع للملخص
        self.set_fill_color(245, 245, 245)
        self.cell(95, 8, score_txt, border=1, align='C', fill=True)
        self.cell(95, 8, weak_txt, border=1, align='C', fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # 2. تحضير بيانات الجدول الأول (المواد الدراسية)
        # الهدف: قائمة مسطحة [(المادة: المهارة, الدرجة), ...]
        academic_items = []
        if "academic" in evaluation_data:
            for subject, skills in evaluation_data["academic"].items():
                if isinstance(skills, dict):
                    for skill, score in skills.items():
                        # دمج اسم المادة والمهارة لتوفير مساحة أو استخدام المهارة فقط إذا كانت المادة واضحة
                        # سنستخدم (المادة - المهارة) بخط صغير
                        label = f"{subject}-{skill}"
                        academic_items.append((label, score))
        
        # المواصفات: 8 أعمدة = 4 أزواج (اسم + تقييم)
        # عرض الصفحة 190. 190 / 4 = 47.5 ملم لكل زوج.
        # تقسيم الزوج: الاسم 32 ملم، التقييم 15 ملم.
        self.draw_grid_table(
            title='المواد الدراسية (التحصيل الأكاديمي)',
            items=academic_items,
            columns_per_row=4,   # 4 أزواج = 8 أعمدة
            col_widths=[32, 15.5]  # [عرض الاسم, عرض التقييم]
        )

        # 3. تحضير بيانات الجدول الثاني (المهارات السلوكية)
        behavioral_items = []
        if "behavioral" in evaluation_data:
            for main, subs in evaluation_data["behavioral"].items():
                if isinstance(subs, dict):
                    for sub, skills in subs.items():
                        if isinstance(skills, dict):
                            for skill, score in skills.items():
                                behavioral_items.append((skill, score))
        
        # المواصفات: 6 أعمدة = 3 أزواج
        # عرض الصفحة 190. 190 / 3 = 63.3 ملم لكل زوج.
        # تقسيم الزوج: الاسم 45 ملم، التقييم 18 ملم.
        self.draw_grid_table(
            title='المهارات السلوكية والشخصية',
            items=behavioral_items,
            columns_per_row=3,   # 3 أزواج = 6 أعمدة
            col_widths=[45, 18.3]
        )

        # 4. الملاحظات وخطة العمل (بشكل مختصر في الأسفل)
        left_y = self.get_y()
        
        # تقسيم المساحة المتبقية لعمودين إن أمكن، أو وضعهم تحت بعض
        self.set_font(self.font_family, 'B', 11)
        self.cell(0, 8, self.process_text('توصيات وملاحظات'), border='B', ln=True, align='R')
        
        self.set_font(self.font_family, '', 10)
        # دمج النص وتحديد الطول
        full_text = "- " + narrative + "\n"
        if action_plan:
            for skill, act in action_plan:
                full_text += f"- {skill}: {act}\n"
        
        proc_text = self.process_text(full_text)
        self.multi_cell(0, 6, proc_text, align='R')

        return bytes(self.output())

def create_pdf(student_name, data, narrative, action_plan):
    try:
        pdf = PDFReport(student_name)
        
        total = 0
        max_score = 0
        weaknesses = 0
        
        # Calculate Stats Logic (Same as before)
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
        print(f"PDF Gen Error: {e}")
        return None, str(e)

