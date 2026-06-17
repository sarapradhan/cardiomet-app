# SAHC RiskLens — A Briefing for Clinical Reviewers

> **Purpose of this document:** to explain a patient-education tool clearly enough that you can evaluate it, tell us where it's wrong, and decide whether it's worth developing further. We are asking for your clinical judgment, not your endorsement of a finished product.
>
> **What this tool is:** an educational aid that helps a patient understand their own lab values before an appointment. **What it is not:** a diagnostic tool, a risk calculator, a medical device, or anything that gives medical advice. Those boundaries are deliberate and built in.

---

## 1. The one-paragraph summary

A patient enters their own cardiometabolic lab values (lipids, glucose, HbA1c, blood pressure, BMI). The tool does three things: it classifies each value against published guideline thresholds and *names the guideline*; it shows where the value sits relative to a public reference population (NHANES Non-Hispanic Asian); and, for patients of South Asian descent, it surfaces the relevant guideline-recognized risk context. It then generates a short list of plain-language questions to bring to you. It stores nothing, diagnoses nothing, and recommends no treatment. The intent is a better-prepared patient in your exam room — not a substitute for it.

---

## 2. Why we built it — the clinical rationale

We want to be measured here, because the space is full of overclaiming health apps and we'd rather earn your trust than lose it in the first paragraph.

Two observations motivated this:

**First, patients struggle to interpret their own labs.** A lab report's generic reference flags tell a patient *that* something is out of range but rarely *how far*, *relative to whom*, or *what's worth asking about*. The result is either unwarranted alarm or false reassurance, and appointments spent re-explaining basics instead of making decisions.

**Second, South Asian cardiometabolic risk is real, documented in major guidelines, and under-surfaced by generic tools.** We're not introducing a novel claim. The 2018 ACC/AHA Cholesterol Guideline names South Asian ancestry as a risk-enhancing factor. The WHO Expert Consultation (2004) describes lower BMI action points for Asian populations. The epidemiology of earlier-onset diabetes and CAD at lower BMI in South Asian populations is well established. A patient who is "normal" on a standard BMI chart may sit in an increased-risk band by these references — and most consumer tools never tell them.

The tool simply applies these *existing, published* references consistently and puts them in front of the patient before they see you. We are not asking the software to know anything a guideline doesn't already say.

**What we are explicitly NOT claiming:**
- We are not claiming to predict any individual's risk. There is no risk score.
- We are not claiming NHANES gives us a South Asian–specific dataset (it does not — see §5).
- We are not claiming to improve outcomes. That would require evidence we don't have.
- We are not claiming to replace any part of your role.

---

## 3. What the patient actually sees

Walking through a result, in order:

1. **A disclaimer**, at the top, every time: educational only, not a diagnosis, discuss with your clinician.
2. **Threshold classification cards** — one per value, showing the category (e.g. LDL "High," HbA1c "Prediabetes") and the named guideline source. Missing values are shown as "not provided," never imputed.
3. **A distribution view** — the patient's value against the 10th–90th percentile of the reference population, which is labeled exactly "NHANES Non-Hispanic Asian," with sample size.
4. **South Asian context** (only if the patient indicates South Asian ancestry) — a qualitative panel explaining ancestry as a risk-enhancing factor and showing South Asian BMI action points *alongside* the standard ones. No risk percentage.
5. **A discussion guide** — plain-language questions for each non-normal value, each citing its guideline. This is fixed template text, not AI-generated prose.
6. **A limitations panel**, always visible, that cannot be hidden.

---

## 4. The specific things we need your judgment on

This is the core of the ask. We've organized it so you can give targeted feedback. For each, the most useful answer is "correct," "correct but needs this edit," or "not acceptable, because."

### 4a. Are the thresholds correct and current?
We have a single reference document (`CLINICAL_LOGIC_APPENDIX.md`) listing every cut-point and its source. The categories in use:
- **LDL, Triglycerides** — ACC/AHA 2018 Cholesterol Guideline
- **HDL, Total Cholesterol** — NCEP ATP III
- **HbA1c, Fasting Glucose** — ADA Standards of Medical Care 2024
- **Blood Pressure** — ACC/AHA 2017
- **BMI (standard)** — WHO
- **BMI (South Asian context)** — WHO Expert Consultation 2004 (23 / 27.5)

**Questions for you:** Are these the cut-points you'd use today? Is anything out of date or superseded? Would you prefer different guideline sources for any of them (e.g. a more recent lipid or hypertension reference)?

### 4b. Is the South Asian framing accurate and appropriately bounded?
This is our highest-stakes area and where we most want pushback.

**Questions for you:** Is it accurate and responsible to present South Asian ancestry as a "risk-enhancing factor" in the way the 2018 guideline does? Are the lower BMI action points appropriate to show as discussion context? And critically — does anything in the tool *imply more South Asian–specific precision than we actually have*, given the NHANES limitation in §5? Where is the line between helpful context and overreach, and are we on the right side of it?

### 4c. Is the language safe and non-diagnostic?
We've worked to keep every output educational. We scan the code to block diagnostic phrasing, and the discussion guide is fixed template text.

**Questions for you:** Reading the actual output, does anything read as a diagnosis, a prediction, or treatment advice? Would you be comfortable with one of your own patients bringing this printout to an appointment? Does any phrasing risk causing undue alarm or false reassurance?

### 4d. Is anything clinically missing or misleading by omission?
**Questions for you:** Should we say more about non-fasting glucose being uninterpretable? About medications confounding values (we flag this but don't adjust classifications)? Is showing standard and South Asian BMI side by side clarifying, or confusing for a layperson? Is there a value we include that shouldn't be patient-facing, or one we omit that should be there?

### 4e. The net effect on your encounter
**The question that matters most:** On balance, would a patient arriving with this *help* your appointment (focused, prepared, better questions) or *hinder* it (anxious, misinformed, arguing with a printout)? If the latter, what would have to change for it to help?

---

## 5. The honest limitations — what we want you to scrutinize

We'd rather you hear these from us than find them yourself.

**The NHANES caveat is the big one.** Our population benchmark uses NHANES, the U.S. national health survey, which groups South, East, and Southeast Asians into a single "Non-Hispanic Asian" category. So our *benchmark* is genuinely Non-Hispanic Asian, **not** South Asian specifically — and we label it that way everywhere, deliberately. The South Asian *context* layer comes from clinical guidelines, not from a South Asian dataset, and is presented as qualitative context. We think this separation is honest; we want you to tell us if it's honest *enough*, or if a layperson could still come away over-reading it.

**Other limitations we state plainly to the user:**
- Fasting glucose requires fasting; we apply the standard fasting filter to the benchmark and would flag non-fasting interpretation issues if you advise it.
- Medications affect values; we flag medication use but do not adjust classifications.
- Missing values are never imputed — they're shown as missing.
- The South Asian BMI action points are discussion context, not an empirical cohort.

**What we don't yet have:** a clinical review (this conversation), a regulatory determination, or any outcome evidence. We're not pretending otherwise.

---

## 6. How we think AI and software should — and shouldn't — be used in medicine

A brief statement of philosophy, because it shapes every design choice and may affect your comfort.

Software is genuinely good at a narrow set of things: applying published rules instantly and identically every time, never getting tired, and surfacing relevant context a busy person would miss. It is genuinely bad at — and should not be trusted with — judgment, diagnosis, the whole-person picture, and treatment decisions. Those are yours.

So we built the tool to occupy only the first category. It applies guidelines the way a careful person with the PDFs open would, and then it deliberately routes every meaningful decision back to a clinician. Concretely: the patient-facing product generates *no* free-form AI text — the discussion guide is fixed, reviewable template wording — so its output is predictable and auditable rather than improvised. We see this as the responsible division of labor: software does the rote organizing; clinicians do the medicine. We'd welcome your view on whether we've drawn that line correctly.

---

## 7. What we're asking of you, concretely

1. **Review the threshold reference** (`CLINICAL_LOGIC_APPENDIX.md`) and tell us what's wrong or out of date.
2. **Look at a sample patient result** and react to the framing and language.
3. **Give us your read on the South Asian context** — defensible, or overreaching?
4. **Tell us, on balance, whether this helps or hinders an appointment**, and what would change your answer.

Written, itemized feedback is ideal — even "section 4a fine, 4b too strong, soften the BMI language, 4c add a non-fasting caveat" is enormously useful. There is no wrong answer, including "this isn't ready" or "this shouldn't exist in this form." We'd rather learn that from you now than from a patient later.

If this clears your review, the next steps are a documented sign-off, a regulatory determination (we believe this fits the non-device Clinical Decision Support category, but that's a question for regulatory counsel, not for you), and then careful expansion. None of that happens without your input first.

Thank you for the time. Your judgment is the gate here, and we mean that literally.
