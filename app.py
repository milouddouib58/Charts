import streamlit as st
import pandas as pd
import json
import data_manager as dm
from datetime import datetime

# ==========================================
# 1. إعدادات الصفحة والتهيئة
# ==========================================
st.set_page_config(page_title="نظام التقييم الشامل المطور", layout="wide", page_icon="🎓")

# تحميل التنسيقات (CSS)
def load_css():
    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""
        <style>
            html, body, [class*="css"] { direction: rtl; text-align: right; }
            .stButton button { width: 100%; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

load_css()

# تهيئة البيانات
if 'students' not in st.session_state:
    st.session_state.students = dm.load_data()

# ==========================================
# 2. القائمة الجانبية
# ==========================================
with st.sidebar:
    st.title("🎓 نظام التقييم")
    st.markdown("---")
    menu = st.radio("القائمة الرئيسية:", [
        "سجل التلاميذ", 
        "تقييم المواد الدراسية", 
        "تقييم المهارات السلوكية", 
        "التقييم الجماعي للقسم", 
        "التقرير التشخيصي",
        "تقارير القسم والطباعة الجماعية",
        "متابعة التطور عبر السنة",
        "لوحة التحكم"
    ], index=4) 
    
    st.markdown("---")
    
    if st.session_state.students:
        st.caption(f"عدد التلاميذ: {len(st.session_state.students)}")

# ==========================================
# 3. سجل التلاميذ
# ==========================================
if menu == "سجل التلاميذ":
    st.header("📂 إدارة ملفات التلاميذ")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        with st.form("add_student", clear_on_submit=True):
            st.subheader("تسجيل تلميذ جديد")
            name = st.text_input("الاسم الثلاثي:")
            col_a, col_b = st.columns(2)
            with col_a: dob = st.date_input("تاريخ الميلاد:", value=None)
            with col_b: gender = st.selectbox("الجنس:", ["ذكر", "أنثى"])
            level = st.selectbox("المستوى:", ["تحضيري", "روضة", "سنة أولى"])
            
            if st.form_submit_button("حفظ البيانات", type="primary"):
                if name:
                    info = {"dob": str(dob), "gender": gender, "class_level": level}
                    dm.save_student_info(name, info)
                    st.session_state.students = dm.load_data()
                    st.success(f"تم حفظ {name}")
                else:
                    st.error("الاسم مطلوب")

        st.markdown("---")
        st.subheader("📥 استيراد قائمة كاملة")
        st.caption("يمكنك استيراد ملف CSV أو Excel (.xlsx)، أو لصق قائمة من برنامج الرقمنة/Excel. الأعمدة المقترحة: الاسم، تاريخ الميلاد، الجنس، المستوى، رقم التعريف.")
        template_csv = "الاسم,تاريخ الميلاد,الجنس,المستوى,رقم التعريف\n"
        st.download_button("⬇️ تنزيل نموذج القائمة", data=template_csv.encode("utf-8-sig"), file_name="نموذج_قائمة_الأطفال.csv", mime="text/csv")
        uploaded_list = st.file_uploader("اختر ملف القائمة", type=["csv", "xlsx"], key="bulk_students_file")
        pasted_list = st.text_area("أو الصق القائمة هنا (كل طفل في سطر، والأعمدة مفصولة بعلامة Tab):", height=100, placeholder="الاسم\tتاريخ الميلاد\tالجنس\tالمستوى\nأحمد بن علي\t2020-01-15\tذكر\tتحضيري")
        if st.button("استيراد الأسماء الآن", type="primary", key="import_bulk_students"):
            rows = []
            try:
                if uploaded_list is not None:
                    if uploaded_list.name.lower().endswith(".xlsx"):
                        frame = pd.read_excel(uploaded_list, dtype=str).fillna("")
                    else:
                        uploaded_list.seek(0)
                        try:
                            frame = pd.read_csv(uploaded_list, dtype=str, encoding="utf-8-sig").fillna("")
                        except UnicodeDecodeError:
                            uploaded_list.seek(0)
                            frame = pd.read_csv(uploaded_list, dtype=str, encoding="cp1256").fillna("")
                    rows = frame.to_dict(orient="records")
                elif pasted_list.strip():
                    import csv, io
                    raw_lines = [line for line in pasted_list.splitlines() if line.strip()]
                    delimiter = "\t" if "\t" in raw_lines[0] else (";" if ";" in raw_lines[0] else ",")
                    parsed = list(csv.reader(io.StringIO("\n".join(raw_lines)), delimiter=delimiter))
                    if parsed:
                        headers = parsed[0]
                        known_headers = {"الاسم", "اسم الطفل", "الاسم واللقب", "الاسم الكامل", "الاسم الثلاثي", "name", "nom", "تاريخ الميلاد", "الجنس", "المستوى", "رقم التعريف"}
                        if any(str(h).strip().lower() in {x.lower() for x in known_headers} for h in headers):
                            rows = [dict(zip(headers, row)) for row in parsed[1:]]
                        else:
                            rows = [dict(enumerate(row)) for row in parsed]
                if not rows:
                    st.warning("اختر ملفاً أو الصق قائمة أولاً.")
                else:
                    merged, result = dm.import_students_rows(rows, st.session_state.students)
                    if dm.save_data(merged):
                        st.session_state.students = dm.load_data()
                        st.success(f"اكتمل الاستيراد: أضيف {result['added']}، استُكملت بيانات {result['updated']} سجلاً موجوداً، وتُجاوز {result['skipped']} صفاً.")
                        for issue in result["errors"][:10]:
                            st.warning(issue)
                        if len(result["errors"]) > 10:
                            st.caption(f"توجد {len(result['errors']) - 10} ملاحظات أخرى؛ راجع الملف قبل إعادة الاستيراد.")
                        st.rerun()
                    else:
                        st.error("تعذر حفظ القائمة. تحقق من صلاحيات الكتابة في مجلد البرنامج.")
            except Exception as exc:
                st.error(f"تعذر قراءة القائمة: {exc}. جرّب CSV بترميز UTF-8 أو ملف Excel بصيغة XLSX.")

    with c2:
        st.subheader("القائمة")
        if st.session_state.students:
            for n, d in st.session_state.students.items():
                with st.expander(n):
                    st.write(f"المستوى: {d['info'].get('class_level')}")
                    st.write(f"الجنس: {d['info'].get('gender')}")

# ==========================================
# 4. التقييم الجماعي للقسم
# ==========================================
elif menu == "التقييم الجماعي للقسم":
    st.header("👥 التقييم الجماعي للقسم")
    st.write("قيّم المهارة نفسها لدى مجموعة الأطفال في جدول واحد، ثم احفظ جميع التغييرات دفعة واحدة.")
    if not st.session_state.students:
        st.info("لا توجد أسماء في السجل. أضف الأطفال أو استورد القائمة أولاً.")
    else:
        all_names = list(st.session_state.students.keys())
        levels = sorted({str(d.get("info", {}).get("class_level", "غير محدد")) for d in st.session_state.students.values()})
        level_choice = st.selectbox("اختر القسم أو المستوى:", ["كل المستويات"] + levels, key="group_eval_level")
        class_names = [n for n in all_names if level_choice == "كل المستويات" or str(st.session_state.students[n].get("info", {}).get("class_level", "غير محدد")) == level_choice]
        eval_kind = st.radio("نوع التقييم:", ["المواد الدراسية", "المهارات السلوكية"], horizontal=True, key="group_eval_kind")

        if eval_kind == "المواد الدراسية":
            subject = st.selectbox("المادة:", list(dm.ACADEMIC_SUBJECTS.keys()), key="group_eval_subject")
            skills = dm.ACADEMIC_SUBJECTS[subject]
            rating_path = ("academic", subject)
        else:
            main_category = st.selectbox("المجال السلوكي:", list(dm.BEHAVIORAL_SKILLS.keys()), key="group_eval_main")
            sub_category = st.selectbox("المهارة الفرعية:", list(dm.BEHAVIORAL_SKILLS[main_category].keys()), key="group_eval_sub")
            skills = dm.BEHAVIORAL_SKILLS[main_category][sub_category]
            rating_path = ("behavioral", main_category, sub_category)

        rating_labels = {0: "غير مكتسب", 1: "في طريق الاكتساب", 2: "مكتسب"}
        label_to_value = {v: k for k, v in rating_labels.items()}
        choices = ["لم يقيّم بعد", "غير مكتسب", "في طريق الاكتساب", "مكتسب"]
        rows = []
        for child_name in class_names:
            evaluations = st.session_state.students[child_name].get("evaluations", {})
            node = evaluations
            for part in rating_path:
                node = node.get(part, {}) if isinstance(node, dict) else {}
            row = {"اسم الطفل": child_name}
            for skill in skills:
                current = node.get(skill)
                row[skill] = rating_labels.get(current, "لم يقيّم بعد")
            rows.append(row)

        frame = pd.DataFrame(rows, columns=["اسم الطفل"] + skills)
        st.caption("اختيار «لم يقيّم بعد» يعني أن المهارة لا تدخل في حساب النسب. إذا اخترته لمهارة سبق تقييمها، فسيُزال تقييمها السابق.")
        edited = st.data_editor(
            frame,
            use_container_width=True,
            hide_index=True,
            disabled=["اسم الطفل"],
            column_config={skill: st.column_config.SelectboxColumn(skill, options=choices, required=True) for skill in skills},
            key=f"group_eval_editor_{level_choice}_{eval_kind}_{'_'.join(rating_path)}",
        )
        if st.button("💾 حفظ تقييمات المجموعة", type="primary", key="save_group_evaluations", disabled=not class_names):
            ratings_by_student = {}
            for _, row in edited.iterrows():
                child_name = row["اسم الطفل"]
                ratings_by_student[child_name] = {
                    skill: (None if row[skill] == "لم يقيّم بعد" else label_to_value[row[skill]])
                    for skill in skills
                }
            try:
                changed = dm.apply_group_ratings(st.session_state.students, class_names, rating_path, ratings_by_student)
                if dm.save_data(st.session_state.students):
                    st.success(f"تم حفظ تقييمات {changed} طفل/أطفال بنجاح.")
                    st.rerun()
                else:
                    st.error("تعذر حفظ التقييمات على القرص. لم يتم تأكيد الحفظ.")
            except Exception as exc:
                st.error(f"تعذر حفظ التقييمات: {exc}")

# ==========================================
# 5. التقييم الأكاديمي
# ==========================================

# ==========================================
elif menu == "تقييم المواد الدراسية":
    st.header("📚 التقييم الأكاديمي")
    if not st.session_state.students:
        st.warning("الرجاء إضافة تلاميذ.")
    else:
        student = st.selectbox("اختر التلميذ:", list(st.session_state.students.keys()))
        info = st.session_state.students[student]["info"]
        st.caption(f"البيانات: {info.get('class_level')} | {info.get('gender')}")
        
        with st.form("academic_form"):
            current = st.session_state.students[student].get("evaluations", {}).get("academic", {})
            new_data = {}
            
            tabs = st.tabs(list(dm.ACADEMIC_SUBJECTS.keys()))
            for i, (subj, skills) in enumerate(dm.ACADEMIC_SUBJECTS.items()):
                with tabs[i]:
                    subj_data = {}
                    for skill in skills:
                        prev = current.get(subj, {}).get(skill, 1) 
                        # تم إضافة subj للمفتاح لمنع التكرار
                        val = st.radio(skill, dm.RATING_OPTIONS, index=prev, key=f"ac_{student}_{subj}_{skill}", horizontal=True)
                        subj_data[skill] = dm.RATING_MAP[val]
                    new_data[subj] = subj_data
            
            if st.form_submit_button("حفظ التقييم الأكاديمي"):
                data = st.session_state.students
                if "evaluations" not in data[student]: data[student]["evaluations"] = {}
                data[student]["evaluations"]["academic"] = new_data
                data[student]["evaluations"]["last_update"] = datetime.now().strftime("%Y-%m-%d")
                dm.save_data(data)
                st.session_state.students = dm.load_data()
                st.toast("تم الحفظ!", icon="✅")

# ==========================================
# 5. التقييم السلوكي
# ==========================================
elif menu == "تقييم المهارات السلوكية":
    st.header("🧠 التقييم السلوكي")
    if st.session_state.students:
        student = st.selectbox("اختر التلميذ:", list(st.session_state.students.keys()))
        
        with st.form("behavioral_form"):
            current = st.session_state.students[student].get("evaluations", {}).get("behavioral", {})
            new_data = {}
            
            tabs = st.tabs(list(dm.BEHAVIORAL_SKILLS.keys()))
            for i, (main, subs) in enumerate(dm.BEHAVIORAL_SKILLS.items()):
                with tabs[i]:
                    main_data = {}
                    for sub, skills in subs.items():
                        st.markdown(f"**{sub}**")
                        sub_data = {}
                        for skill in skills:
                            prev = current.get(main, {}).get(sub, {}).get(skill, 1)
                            # تم إضافة main و sub للمفتاح لمنع التكرار نهائياً
                            val = st.radio(skill, dm.RATING_OPTIONS, index=prev, key=f"beh_{student}_{main}_{sub}_{skill}", horizontal=True)
                            sub_data[skill] = dm.RATING_MAP[val]
                        main_data[sub] = sub_data
                        st.markdown("---")
                    new_data[main] = main_data
            
            if st.form_submit_button("حفظ التقييم السلوكي"):
                data = st.session_state.students
                if "evaluations" not in data[student]: data[student]["evaluations"] = {}
                data[student]["evaluations"]["behavioral"] = new_data
                data[student]["evaluations"]["last_update"] = datetime.now().strftime("%Y-%m-%d")
                dm.save_data(data)
                st.session_state.students = dm.load_data()
                st.toast("تم الحفظ!", icon="✅")

# ==========================================
# 6. التقرير التشخيصي (النسخة النهائية)
# ==========================================
elif menu == "التقرير التشخيصي":
    st.header("📈 التقرير التشخيصي الشامل")
    
    if not st.session_state.students:
        st.warning("لا توجد بيانات.")
    else:
        student = st.selectbox("اختر التلميذ:", list(st.session_state.students.keys()))
        
        student_data = st.session_state.students[student]
        info = student_data["info"]
        evals = student_data.get("evaluations", {})
        gender = info.get("gender", "ذكر")
        
        # عرض النتائج بالأرقام
        scores = dm.calculate_scores(evals)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("التحصيل الدراسي", f"{scores['academic_percentage']:.0f}%")
        c2.metric("السلوك والمواظبة", f"{scores['behavioral_percentage']:.0f}%")
        c3.metric("النسبة العامة", f"{scores['overall_percentage']:.0f}%")
        st.progress(scores['overall_percentage'] / 100)
        
        st.divider()

        # إدارة استدعاء الذكاء الاصطناعي لمنع استهلاك الحد المسموح (Rate Limit)
        ai_state_key = f"ai_report_{student}"
        if ai_state_key not in st.session_state:
            st.session_state[ai_state_key] = {"narrative": "", "action_plan": []}

        st.caption("تنبيه خصوصية: عند طلب التحليل الذكي تُرسل تفاصيل التقييم فقط إلى مزود ذكاء اصطناعي خارجي؛ لا يرسل التطبيق اسم الطفل ضمن نص التحليل. استخدم الميزة وفق سياسة المؤسسة والموافقات اللازمة، وتجنب إدخال أي بيانات تعريفية داخل التقييمات أو الملاحظات.")
        if st.button("🤖 توليد / تحديث التحليل التربوي الذكي", type="secondary"):
            with st.spinner("يتصل بالذكاء الاصطناعي لتحليل البيانات..."):
                narr, plan = dm.analyze_student_performance(student, evals, gender)
                st.session_state[ai_state_key] = {"narrative": narr, "action_plan": plan}

        narrative = st.session_state[ai_state_key]["narrative"]
        action_plan = st.session_state[ai_state_key]["action_plan"]
        
        # عرض التحليل والخطة
        col_text, col_plan = st.columns([2, 1])
        
        with col_text:
            st.subheader("📝 التحليل التربوي")
            if narrative:
                st.markdown(
                    f"""
                    <div style="background-color:#f8f9fa; padding:20px; border-radius:10px; border-right: 5px solid #2e86de; font-size:16px; line-height:1.8; color:#2c3e50;">
                    {narrative.replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True
                )
            else:
                st.info("اضغط على الزر أعلاه لتوليد التحليل باستخدام الذكاء الاصطناعي.")

        with col_plan:
            st.subheader("💡 الخطة المقترحة")
            if action_plan:
                for item, rec in action_plan:
                    with st.expander(f"📌 {item}"):
                        st.info(rec)
            elif narrative and ("خطأ" in narrative or "Error" in narrative):
                st.warning("تعذر جلب الخطة المقترحة بسبب مشكلة في الاتصال. حاول لاحقاً.")
            elif narrative:
                st.success("الأداء ممتاز، استمر في التشجيع!")
            else:
                st.caption("في انتظار التوليد...")

        st.divider()
        
        # قسم PDF
        st.subheader("📄 إصدار التقرير الرسمي")
        
        pdf_key = f"pdf_{student}_{evals.get('last_update', 'new')}"
        
        if pdf_key not in st.session_state:
            if st.button("🔄 إنشاء ملف PDF (جاهز للطباعة)", type="primary"):
                try:
                    import pdf_generator
                    with st.spinner("جاري صياغة التقرير، رسم الجداول، وضبط التنسيق..."):
                        pdf_bytes, error = pdf_generator.create_pdf(
                            student, info, evals, narrative, action_plan
                        )
                        
                        if pdf_bytes:
                            st.session_state[pdf_key] = pdf_bytes
                            st.rerun()
                        else:
                            st.error(f"خطأ: {error}")
                except ImportError:
                    st.error("المكتبات مفقودة (fpdf2, arabic-reshaper, python-bidi)")
        
        if pdf_key in st.session_state:
            c_d1, c_d2 = st.columns([1, 4])
            with c_d1:
                st.download_button(
                    label="📥 تحميل PDF",
                    data=st.session_state[pdf_key],
                    file_name=f"Report_{student}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
            with c_d2:
                if st.button("إعادة إنشاء"):
                    del st.session_state[pdf_key]
                    st.rerun()


# ==========================================
# 8. متابعة التطور عبر السنة الدراسية
# ==========================================
elif menu == "متابعة التطور عبر السنة":
    st.header("📈 متابعة تطور الطفل عبر السنة")
    st.write("احفظ لقطة من التقييم في كل فترة، ثم قارن النتائج دون فقدان التقييمات السابقة.")
    if not st.session_state.students:
        st.info("أضف الأطفال أو استورد قائمتهم أولًا.")
    else:
        student_name = st.selectbox("اختر الطفل:", list(st.session_state.students.keys()), key="history_student")
        record = st.session_state.students[student_name]
        today = datetime.now()
        default_year = f"{today.year}/{today.year + 1}" if today.month >= 9 else f"{today.year - 1}/{today.year}"
        h1, h2 = st.columns(2)
        with h1:
            school_year = st.text_input("السنة الدراسية:", value=default_year, key="history_school_year")
        with h2:
            period = st.selectbox(
                "فترة التقييم:",
                ["تقييم تشخيصي", "الفصل الأول", "الفصل الثاني", "الفصل الثالث", "تقييم ختامي"],
                key="history_period"
            )
        existing_history = record.get("assessment_history", [])
        duplicate = any(x.get("period") == period and x.get("school_year") == school_year.strip() for x in existing_history)
        if duplicate:
            st.warning("توجد لقطة محفوظة لهذه الفترة والسنة. الضغط على الحفظ سيحدّث اللقطة السابقة بهذه النتائج الحالية.")
        st.caption("تُحفظ لقطة مستقلة من التقييم الحالي. تعديل تقييم الطفل لاحقًا لا يغيّر اللقطات المحفوظة.")
        if st.button("💾 حفظ لقطة تقييم هذه الفترة", type="primary", key="save_assessment_snapshot"):
            try:
                action, _snapshot = dm.save_assessment_snapshot(record, period, school_year)
                if dm.save_data(st.session_state.students):
                    st.success("تم حفظ لقطة التقييم." if action == "added" else "تم تحديث لقطة هذه الفترة.")
                    st.rerun()
                else:
                    st.error("تعذر حفظ البيانات على القرص.")
            except Exception as exc:
                st.error(f"تعذر حفظ اللقطة: {exc}")

        history = record.get("assessment_history", [])
        if history:
            st.subheader("سجل التقييمات المحفوظة")
            history_labels = [
                f"{item.get('school_year', '')} — {item.get('period', '')} — {item.get('date', '')}"
                for item in history
            ]
            hist_rows = []
            for item in history:
                sc = item.get("scores", {})
                hist_rows.append({
                    "السنة الدراسية": item.get("school_year", ""),
                    "الفترة": item.get("period", ""),
                    "تاريخ الحفظ": item.get("date", ""),
                    "الأكاديمي": f"{float(sc.get('academic_percentage', 0)):.1f}%",
                    "السلوكي": f"{float(sc.get('behavioral_percentage', 0)):.1f}%",
                    "الأداء العام": f"{float(sc.get('overall_percentage', 0)):.1f}%",
                })
            st.dataframe(pd.DataFrame(hist_rows), use_container_width=True, hide_index=True)

            if len(history) >= 2:
                st.subheader("مقارنة فترتين")
                c1, c2 = st.columns(2)
                with c1:
                    first_label = st.selectbox("التقييم الأقدم/الأول:", history_labels, index=0, key="history_first")
                with c2:
                    second_label = st.selectbox("التقييم الأحدث/الثاني:", history_labels, index=len(history)-1, key="history_second")
                first_index = history_labels.index(first_label)
                second_index = history_labels.index(second_label)
                first_snapshot, second_snapshot = history[first_index], history[second_index]
                if first_index == second_index:
                    st.info("اختر فترتين مختلفتين لإظهار الفرق.")
                else:
                    delta = dm.compare_assessment_snapshots(first_snapshot, second_snapshot)
                    m1, m2, m3 = st.columns(3)
                    m1.metric("الأداء الأكاديمي", f"{float(second_snapshot['scores'].get('academic_percentage', 0)):.1f}%", f"{delta['academic_percentage']:+.1f} نقطة")
                    m2.metric("المهارات السلوكية", f"{float(second_snapshot['scores'].get('behavioral_percentage', 0)):.1f}%", f"{delta['behavioral_percentage']:+.1f} نقطة")
                    m3.metric("الأداء العام", f"{float(second_snapshot['scores'].get('overall_percentage', 0)):.1f}%", f"{delta['overall_percentage']:+.1f} نقطة")

                    # عرض التغير عبر الفترات حسب ترتيبها الزمني.
                    chart_rows = []
                    for item in history:
                        sc = item.get("scores", {})
                        chart_rows.append({
                            "الفترة": f"{item.get('school_year', '')} {item.get('period', '')}",
                            "الأكاديمي": float(sc.get("academic_percentage", 0)),
                            "السلوكي": float(sc.get("behavioral_percentage", 0)),
                            "الأداء العام": float(sc.get("overall_percentage", 0)),
                        })
                    st.line_chart(pd.DataFrame(chart_rows).set_index("الفترة"))
                    st.caption("الفروق معروضة بالنقاط المئوية، وليست نسبة مئوية من النتيجة السابقة.")
        else:
            st.info("لم تُحفظ أي لقطات بعد. سجّل تقييم الطفل الحالي ثم احفظ لقطة الفترة.")

# ==========================================
# 7. تقارير القسم والطباعة الجماعية
# ==========================================
elif menu == "تقارير القسم والطباعة الجماعية":
    st.header("🖨️ تقارير القسم والطباعة الجماعية")
    st.write("أنشئ تقارير PDF لعدة أطفال دفعة واحدة، ثم نزّلها في ملف ZIP واحد لتسهيل الطباعة والأرشفة.")
    if not st.session_state.students:
        st.info("لا توجد أسماء في السجل. أضف الأطفال أو استورد القائمة أولاً.")
    else:
        all_names = list(st.session_state.students.keys())
        levels = sorted({str(d.get("info", {}).get("class_level", "غير محدد")) for d in st.session_state.students.values()})
        level_choice = st.selectbox("تصفية حسب المستوى:", ["كل المستويات"] + levels)
        eligible = [n for n in all_names if level_choice == "كل المستويات" or str(st.session_state.students[n].get("info", {}).get("class_level", "غير محدد")) == level_choice]
        selected_names = st.multiselect("اختر الأطفال الذين تريد تقاريرهم:", eligible, default=eligible)
        st.caption(f"سيتم إعداد تقارير لـ {len(selected_names)} طفل/أطفال. لا يُستدعى الذكاء الاصطناعي عند إنشاء هذه المجموعة؛ لذلك لا توجد تكلفة API أو إرسال بيانات إلى خدمة خارجية من هذه العملية.")
        if st.button("إنشاء حزمة التقارير ZIP", type="primary", disabled=not selected_names):
            import io, zipfile, re
            import pdf_generator
            archive_buffer = io.BytesIO()
            successes, failures = 0, []
            with zipfile.ZipFile(archive_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
                progress = st.progress(0)
                status = st.empty()
                for index, child_name in enumerate(selected_names, start=1):
                    record = st.session_state.students[child_name]
                    child_info = record.get("info", {})
                    evaluations = record.get("evaluations", {})
                    # تقرير جماعي محلي دون إرسال أسماء أو تقييمات إلى مزود ذكاء اصطناعي.
                    scores = dm.calculate_scores(evaluations)
                    narrative = (
                        f"بلغت نسبة الأداء الأكاديمي المسجلة {scores['academic_percentage']:.1f}%، "
                        f"ونسبة المهارات السلوكية المسجلة {scores['behavioral_percentage']:.1f}%. "
                        "تُقرأ هذه النتائج في ضوء المهارات التي قيّمها المربي والملاحظات المباشرة داخل القسم. "
                        "يوصى بمواصلة الملاحظة التربوية وتقديم أنشطة دعم مناسبة للمهارات التي ما زالت في طور الاكتساب. "
                        "لا تمثل النسب وحدها تشخيصاً نهائياً لمستوى الطفل."
                    )
                    pdf_bytes, error = pdf_generator.create_pdf(child_name, child_info, evaluations, narrative, [])
                    if pdf_bytes:
                        safe_name = re.sub(r'[\\/:*?"<>|]+', '_', child_name).strip(' ._') or f"child_{index}"
                        archive.writestr(f"{index:03d}_{safe_name}.pdf", pdf_bytes)
                        successes += 1
                    else:
                        failures.append(f"{child_name}: {error}")
                    progress.progress(index / len(selected_names))
                    status.write(f"جاري إعداد التقرير {index} من {len(selected_names)}")
            if successes:
                st.session_state["batch_reports_zip"] = archive_buffer.getvalue()
                st.session_state["batch_reports_count"] = successes
                st.session_state["batch_reports_failures"] = failures
                st.success(f"تم إنشاء {successes} تقريراً بنجاح.")
            if failures:
                st.warning(f"تعذر إنشاء {len(failures)} تقرير/تقارير. التفاصيل:")
                for issue in failures[:10]:
                    st.caption(issue)
        if st.session_state.get("batch_reports_zip"):
            st.download_button(
                "📦 تنزيل تقارير الأطفال في ملف ZIP",
                data=st.session_state["batch_reports_zip"],
                file_name="تقارير_القسم.zip",
                mime="application/zip",
                type="primary"
            )
            st.caption(f"عدد التقارير داخل آخر حزمة: {st.session_state.get('batch_reports_count', 0)}")

# ==========================================
# 8. لوحة التحكم
# ==========================================
elif menu == "لوحة التحكم":
    st.header("📊 إحصائيات عامة")
    if st.session_state.students:
        df = []
        for name, data in st.session_state.students.items():
            scores = dm.calculate_scores(data.get("evaluations", {}))
            df.append({
                "الاسم": name,
                "المستوى": data["info"].get("class_level"),
                "الأداء العام": f"{scores['overall_percentage']:.1f}%"
            })
        st.dataframe(pd.DataFrame(df), use_container_width=True)
        
        if st.button("🗑️ حذف جميع البيانات"):
            st.session_state.students = {}
            dm.save_data({})
            st.rerun()
    else:
        st.info("لا توجد بيانات.")

