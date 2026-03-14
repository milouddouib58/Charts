import json
import os
import random
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

# ==============================================================================
# 1. الثوابت والبيانات (الجداول المحدثة حسب طلبك)
# ==============================================================================
DATA_FILE = "students_data.json"

RATING_OPTIONS = ["غير مكتسب", "في طريق الاكتساب", "مكتسب"]
RATING_MAP = {"غير مكتسب": 0, "في طريق الاكتساب": 1, "مكتسب": 2}

ACADEMIC_SUBJECTS = {
    "اللغة العربية": [
        "يسمي الحروف الهجائية المدروسة",
        "يميز صواتيا بين الحروف",
        "يمسك القلم بطريقة صحيحة"
    ],
    "الرياضيات": [
        "يعد شفويا إلى 20",
        "يربط العدد بالمعدود",
        "يميز الأشكال الهندسية",
        "يصنف الأشياء حسب خاصية معينة",
        "يتعرف على الأعداد حتى 10"
    ],
    "التربية الإسلامية والمدنية": [
        "يحفظ قصار السور المقررة",
        "يلقي التحية ويردها",
        "يحافظ على نظافة مكانه",
        "يتعاون مع زملائه",
        "يحترم المعلم والزملاء"
    ],
    "التربية العلمية": [
        "يسمي أعضاء جسم الإنسان",
        "يميز بين الحواس الخمس",
        "يعرف الحيوانات الأليفة والمتوحشة"
    ]
}

BEHAVIORAL_SKILLS = {
    "الوظائف التنفيذية": {
        "الانتباه والذاكرة": ["التركيز على نشاط لمدة 15 دقيقة", "إكمال المهمة للنهاية دون تشتت", "تذكر تعليمات من 3 خطوات", "تذكر أحداث قصة قصيرة", "ينتبه للتفاصيل المهمة"],
        "المرونة والتفكير": ["الانتقال بين الأنشطة بسلاسة", "تقبل التغيير في الروتين", "إدراك التسلسل المنطقي للأحداث", "حل المشكلات البسيطة", "يطرح أسئلة ذكية"]
    },
    "الكفاءة الاجتماعية": {
        "التطور الشخصي والاجتماعي": ["التعبير عن المشاعر بدقة", "الثقة بالنفس والمبادرة", "المشاركة في اللعب الجماعي", "احترام الدور والقوانين", "التحكم في الانفعالات", "تقدير الذات والإيجابية"],
        "المهارات العاطفية": ["التعاطف مع الآخرين", "التعبير عن الحاجة للمساعدة", "تحمل المسؤولية", "التكيف مع المواقف الجديدة"]
    },
    "المهارات الحركية": {
        "النمو الحركي": ["استخدام المقص بدقة", "تلوين داخل الحدود", "التوازن (الوقوف على قدم واحدة)", "التقاط الكرة ورميها", "القفز على قدمين معا"],
        "الاستقلالية": ["الاعتماد على النفس (لبس، حمام، ترتيب)", "تناول الطعام بنفسه", "ترتيب الأدوات المدرسية", "العناية بالنظافة الشخصية"]
    }
}

ANALYSIS_TEMPLATES = {
    "opening": {
        "excellent": [
            "أبان{adj} {student} {name} عن كفاءة عالية في استيعاب الكفاءات القاعدية المقررة، محققاً تقدماً نوعياً وشاملاً في مختلف المجالات التعلمية.",
            "{vs}تميز {student} {name} بجاهزية ذهنية ممتازة، حيث {vs}ظهر تحكماً دقيقاً في توظيف المكتسبات التي تم تناولها خلال هذه المرحلة."
        ],
        "good": [
            "{vs}سير {student} {name} بخطى ثابتة نحو تحقيق الأهداف التعلمية المسطرة، حيث {vs}ظهر تجاوباً إيجابياً وملحوظاً مع التعلمات المقررة.",
            "أظهر{adj} {student} {name} تطوراً مستمراً في اكتساب المعارف الأساسية، مع نمو تدريجي وواضح في مهارات{s} المعرفية والتواصلية."
        ],
        "needs_support": [
            "{vs}واجه {student} {name} بعض التحديات في مسايرة وتيرة بناء التعلمات، مما يتطلب تكييفاً للمفاهيم الرياضية واللغوية لدعم استيعاب{s} التدريجي.",
            "تشير الملاحظات إلى أن {student} {name} {vs}مر بمرحلة بناء أساسيات تتطلب دعماً فردياً مكثفاً لترسيخ المكتسبات وتجاوز صعوبات الاستيعاب."
        ]
    },
    "cognitive_style": { 
        "analytical": "من الناحية المعرفية، {vs}ظهر تفوقاً ملموساً في المجالين الرياضي والعلمي، حيث {vs}تحكم في بناء المفاهيم العددية، مع قدرة واضحة على تصنيف الأشياء واستنتاج خصائصها.",
        "verbal": "{vs}تميز بتقدم لافت في اللغة العربية، حيث {vs}جيد التعبير الشفوي، مع قدرة ممتازة على التمييز السمعي للأصوات وتجريد الحروف.",
        "balanced": "{vs}عكس مسار{s} التعلمي توازناً ممتازاً؛ حيث {vs}جمع بين التمكن من أنشطة القراءة لغوياً، وبين الاستيعاب السليم للعمليات المنطقية والأعداد رياضياً.",
        "struggling": "{vs}جد صعوبة نسبية في تجريد المفاهيم اللغوية والرياضية، و{vs}حتاج إلى توظيف مكثف للوسائل الحسية والملموسة لترسيخ الأعداد والحروف وتجاوز هذه العقبة."
    },
    "social_emotional": {
        "leader": "اجتماعياً، {vs}جسد القيم المدروسة في التربية الإسلامية والمدنية بامتياز، حيث {vs}ظهر روحاً قيادية وتفاعلاً إيجابياً في تطبيق قواعد النظافة، التعاون، واحترام الآخرين.",
        "introvert": "{vs}ميل إلى الهدوء في القسم، إلا أن{s} {vs}ستوعب جيداً قواعد الحياة الجماعية والسلوكيات المدنية المدروسة، حيث {vs}فضل تطبيقها بصمت وتأمل بعيداً عن الصخب.",
        "impulsive": "{vs}تسم سلوك{s} بالحركية والاندفاع، مما {vs}جعل{s} يتألق في الأنشطة الحركية، مع الحاجة لتهذيب هذه الطاقة في مواقف التعلم التي تتطلب هدوءاً.",
        "dependent": "{vs}ظهر تردداً في المبادرات الاجتماعية، و{vs}حتاج إلى تعزيز ثقت{s} بنفس{s} لترجمة ما تعلم{s} في مجالي التربية الإسلامية والمدنية إلى ممارسات وسلوكيات يومية واثقة."
    },
    "work_habits": {
        "focused": "{vs}تميز بتركيز عالٍ ودقة في إنجاز المهام، والتزام{s} الصارم بتعليمات العمل الموجهة.",
        "distracted": "{vs}تأثر انتباه{s} بسرعة بالمحيط، مما يستوجب دمج الألعاب والأنشطة الحركية ضمن مسار{s} التعلمي لتجديد نشاط{s} وضمان استمرارية تركيز{s}."
    }
}

# ==============================================================================
# 2. الدوال المساعدة ومعالجة البيانات
# ==============================================================================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def save_student_info(name, info):
    data = load_data()
    if name not in data: data[name] = {"info": info, "evaluations": {}, "history": []}
    else:
        if "info" not in data[name]: data[name]["info"] = {}
        data[name]["info"].update(info)
    save_data(data)

def calculate_scores(evaluations):
    academic_total, academic_max = 0, 0
    behavioral_total, behavioral_max = 0, 0
    weaknesses, strengths = [], []
    
    if "academic" in evaluations:
        for subj, skills in evaluations["academic"].items():
            for skill, score in skills.items():
                if isinstance(score, int):
                    academic_total += score; academic_max += 2
                    if score == 0: weaknesses.append(f"{subj}: {skill}")
                    elif score == 2: strengths.append(skill)
    
    if "behavioral" in evaluations:
        for main, subs in evaluations["behavioral"].items():
            for sub, skills in subs.items():
                for skill, score in skills.items():
                    if isinstance(score, int):
                        behavioral_total += score; behavioral_max += 2
                        if score == 0: weaknesses.append(f"{main}: {skill}")
                        elif score == 2: strengths.append(skill)

    ac_pct = (academic_total / academic_max * 100) if academic_max > 0 else 0
    beh_pct = (behavioral_total / behavioral_max * 100) if behavioral_max > 0 else 0
    ov_pct = ((academic_total+behavioral_total)/(academic_max+behavioral_max)*100) if (academic_max+behavioral_max) > 0 else 0
    
    return {
        "academic_percentage": ac_pct,
        "behavioral_percentage": beh_pct,
        "overall_percentage": ov_pct,
        "weaknesses": weaknesses,
        "strengths": strengths
    }

def analyze_student_performance(name, data, gender="ذكر"):
    stats = calculate_scores(data)
    ac_score = stats['academic_percentage']
    beh_score = stats['behavioral_percentage']
    is_female = (gender == "أنثى")
    
    T = {
        "{name}": name,
        "{student}": "المتعلمة" if is_female else "المتعلم",
        "{dem}": "هذه" if is_female else "هذا",
        "{vs}": "ت" if is_female else "ي",      
        "{s}": "ها" if is_female else "ه",      
        "{adj}": "ت" if is_female else "",      
        "{adj_p}": "ها" if is_female else "ه",  
    }

    narrative_parts = []

    if stats['overall_percentage'] >= 85: opening = random.choice(ANALYSIS_TEMPLATES["opening"]["excellent"])
    elif stats['overall_percentage'] >= 60: opening = random.choice(ANALYSIS_TEMPLATES["opening"]["good"])
    else: opening = random.choice(ANALYSIS_TEMPLATES["opening"]["needs_support"])
    narrative_parts.append(opening)

    if ac_score < 50: cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["struggling"]
    elif ac_score >= 85: cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["analytical"]
    else: cog_text = ANALYSIS_TEMPLATES["cognitive_style"]["balanced"]
    narrative_parts.append(cog_text)

    if beh_score >= 85: soc_text = ANALYSIS_TEMPLATES["social_emotional"]["leader"]
    elif beh_score < 50: soc_text = ANALYSIS_TEMPLATES["social_emotional"]["dependent"]
    else: soc_text = "{vs}ظهر تفاعلاً اجتماعياً متزناً، و{vs}بدي احتراماً للقواعد الصفية مع رغبة في المشاركة."
    narrative_parts.append(soc_text)

    weakness_str = " ".join(stats['weaknesses'])
    if "تشتت" in weakness_str or "تركيز" in weakness_str: work_text = ANALYSIS_TEMPLATES["work_habits"]["distracted"]
    else: work_text = ANALYSIS_TEMPLATES["work_habits"]["focused"] if ac_score > 70 else "{vs}حتاج إلى مزيد من المثابرة لإتمام المهام."
    narrative_parts.append(work_text)

    narrative_parts.append("ختاماً، نوصي بالتركيز على الجانب النفسي وتعزيز الشعور بالإنجاز.")

    full_text = "\n\n".join(narrative_parts)
    for k, v in T.items(): full_text = full_text.replace(k, v)
    if is_female:
        full_text = full_text.replace("متميز ", "متميزة ").replace("مبدع ", "مبدعة ")

    action_plan = []
    for w in stats['weaknesses'][:4]:
        clean = w.split(": ")[-1] if ":" in w else w
        action_plan.append((clean, "المتابعة والتدريب المستمر."))

    return full_text, action_plan

# ==============================================================================
# 3. توليد ملف الـ PDF (المحرك الذكي لمعالجة السطور العربية)
# ==============================================================================
class PDFReport(FPDF):
    def __init__(self, student_name, student_info):
        super().__init__()
        self.student_name = student_name
        self.student_info = student_info
        self.custom_font_loaded = False
        self.font_family = 'Helvetica'
        
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
        """ لمعالجة الكلمات القصيرة والسطور الفردية فقط """
        if not self.custom_font_loaded or not text: 
            return str(text)
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except: 
            return str(text)

    def get_arabic_lines(self, width, text):
        """
        الحل السحري: هذه الدالة تحسب طول الكلمات وتقوم بتكسير الأسطر بشكل صحيح
        بناءً على العرض المتاح، قبل أن تقوم بتطبيق Bidi، مما يمنع قلب الكلمات!
        """
        if not self.custom_font_loaded:
            return [str(text)]
            
        lines = []
        for para in str(text).split('\n'):
            para = para.strip()
            if not para:
                continue
                
            reshaped = arabic_reshaper.reshape(para)
            words = reshaped.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                # التأكد من عرض الكلمة باستخدام get_string_width
                if self.get_string_width(test_line) > (width - 2):
                    if current_line:
                        lines.append(get_display(current_line))
                        current_line = word
                    else: # الكلمة نفسها أكبر من الخانة!
                        lines.append(get_display(word))
                        current_line = ""
                else:
                    current_line = test_line
                    
            if current_line:
                lines.append(get_display(current_line))
        return lines

    def header(self):
        self.set_fill_color(240, 240, 240)
        self.set_draw_color(200, 200, 200)
        self.set_y(15)
        self.set_font(self.font_family, 'B', 18)
        self.cell(0, 10, self.process_text('بطاقة التقييم الفصلي'), 0, 1, 'C')
        self.set_font(self.font_family, '', 10)
        self.cell(0, 5, self.process_text('السنة الدراسية: 2024 / 2025'), 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(44, 62, 80)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_draw_color(0)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family, '', 8)
        self.cell(0, 10, self.process_text(f'صفحة {self.page_no()}'), 0, 0, 'C')

    def draw_signatures_fixed(self):
        self.set_y(-50) 
        self.set_font(self.font_family, 'B', 11)
        w = 63 
        y = self.get_y()
        self.set_xy(10 + w*2, y)
        self.cell(w, 8, self.process_text("توقيع المربي(ة):"), 0, 0, 'C')
        self.set_xy(10 + w, y)
        self.cell(w, 8, self.process_text("توقيع المدير(ة):"), 0, 0, 'C')
        self.set_xy(10, y)
        self.cell(w, 8, self.process_text("إمضاء الولي:"), 0, 0, 'C')
        self.set_draw_color(180)
        self.set_line_width(0.2)
        line_y = y + 25
        self.line(30, line_y, 55, line_y)    
        self.line(93, line_y, 118, line_y)   
        self.line(156, line_y, 181, line_y)
        self.set_draw_color(0)

    def draw_student_details(self):
        start_y = self.get_y()
        self.set_fill_color(250, 250, 252)
        self.set_draw_color(220)
        self.rect(10, start_y, 190, 30, 'DF')
        self.set_draw_color(0) 

        y = start_y + 6
        self.set_xy(160, y); self.set_font(self.font_family, '', 11)
        self.cell(30, 6, self.process_text("الاسم واللقب:"), 0, 0, 'R') 
        self.set_xy(100, y); self.set_font(self.font_family, 'B', 12) 
        self.cell(60, 6, self.process_text(self.student_name), 0, 0, 'R')

        self.set_xy(65, y); self.set_font(self.font_family, '', 11)
        self.cell(25, 6, self.process_text("المستوى:"), 0, 0, 'R')
        self.set_xy(15, y); self.set_font(self.font_family, 'B', 11)
        self.cell(50, 6, self.process_text(self.student_info.get('class_level','')), 0, 0, 'R')

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

    def draw_custom_symbol(self, x, y, size, score):
        self.set_line_width(0.4)
        if score == 2: 
            self.set_draw_color(39, 174, 96) 
            self.line(x, y + size/2, x + size/3, y + size)
            self.line(x + size/3, y + size, x + size, y)
        elif score == 1: 
            self.set_draw_color(243, 156, 18) 
            self.set_fill_color(243, 156, 18)
            r = size / 2.5
            self.circle(x + size/2, y + size/2, r, 'F')
        elif score == 0: 
            self.set_draw_color(192, 57, 43) 
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
            
            # طباعة العناوين العلوية لكل عمود
            for subj, skills in batch:
                total = sum(s for _, s in skills); max_s = len(skills)*2
                pct = (total/max_s*100) if max_s else 0
                self.set_xy(curr_x, top_y)
                self.cell(col_width, 7, self.process_text(f"{subj} ({pct:.0f}%)"), 1, 0, 'C', True)
                curr_x += col_width
            
            self.set_y(top_y + 7)
            start_y = self.get_y()
            max_y = start_y
            curr_x = 10
            self.set_font(self.font_family, '', 8)
            
            # طباعة الدروس والمهارات
            for subj, skills in batch:
                col_y = start_y
                for skill, score in skills:
                    if col_y > 270: break
                    
                    # استخدام الدالة الجديدة للحصول على الأسطر الصحيحة
                    lines = self.get_arabic_lines(skill_w, skill)
                    line_height = 6
                    h = len(lines) * line_height
                    
                    # رسم إطارات الخانات
                    self.set_xy(curr_x, col_y)
                    self.rect(curr_x, col_y, skill_w, h)
                    self.rect(curr_x + skill_w, col_y, mark_w, h)
                    
                    # كتابة النص داخل الإطار
                    ty = col_y
                    for sl in lines:
                        self.set_xy(curr_x, ty)
                        self.cell(skill_w, line_height, sl, 0, 0, 'R')
                        ty += line_height
                    
                    # رسم الرمز (الصح/الدائرة/الخطأ)
                    self.draw_custom_symbol(curr_x + skill_w + (mark_w - 3.5)/2, col_y + (h - 3.5)/2, 3.5, score)
                    col_y += h
                    
                if col_y > max_y: max_y = col_y
                curr_x += col_width
            self.set_y(max_y + 5)

    def draw_analysis_section(self, narrative):
        self.add_page()
        self.set_font(self.font_family, 'B', 14)
        self.cell(0, 10, self.process_text("التقرير التربوي الختامي"), 0, 1, 'C')
        self.ln(5)
        
        box_top = self.get_y()
        self.set_fill_color(245, 247, 250)
        # نرسم المستطيل بارتفاع افتراضي، سنعدله لاحقاً
        self.rect(10, box_top, 190, 100, 'F') 
        
        self.set_xy(15, box_top + 5)
        self.set_font(self.font_family, 'B', 12)
        self.set_text_color(44, 62, 80) 
        self.cell(0, 10, self.process_text("📝 تحليل شخصية وأداء المتعلم:"), 0, 1, 'R')
        
        self.set_xy(15, box_top + 15)
        self.set_font(self.font_family, '', 11)
        self.set_text_color(0)

        # الاعتماد على الدالة الجديدة لتقسيم النص بطريقة احترافية
        lines = self.get_arabic_lines(180, narrative)
        for line in lines:
            if line == "":
                self.ln(3) # مسافة بين الفقرات
            else:
                self.set_x(15)
                self.cell(180, 7, line, 0, 1, 'R')

        final_y = self.get_y() + 5
        height = final_y - box_top
        
        # رسم الإطار النهائي على حسب طول النص
        self.set_draw_color(100, 100, 150)
        self.set_line_width(0.3)
        self.rect(10, box_top, 190, height, 'D')
        self.set_y(final_y + 10)

    def generate(self, evaluation_data, narrative, action_plan):
        self.add_page()
        self.draw_student_details()
        self.draw_legend()
        
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

        self.draw_analysis_section(narrative)
        self.draw_signatures_fixed()

        return bytes(self.output())

def create_pdf(student_name, student_info, data, narrative, action_plan):
    try:
        pdf = PDFReport(student_name, student_info)
        return pdf.generate(data, narrative, action_plan), None
    except Exception as e:
        return None, str(e)

