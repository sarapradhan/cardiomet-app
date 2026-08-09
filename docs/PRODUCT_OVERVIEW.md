# SAHC RiskLens — Product Overview

> **South Asian Heart & Cardiometabolic RiskLens**
> An educational tool that helps people understand their cardiometabolic lab values in context — clinical guidelines, a population benchmark, and South Asian–specific risk considerations — and prepare better conversations with their clinician.
>
> Educational only. Not a diagnostic tool, not a medical device, not a substitute for professional medical advice.

---

## 1. The Why

### The problem in one sentence
A person receives a page of lab numbers, has little idea which ones matter or how they compare to people like them, and walks into a short doctor's appointment unprepared to ask the right questions — and for people of South Asian descent, the standard reference points may understate their cardiovascular risk.

### Why this matters

**Lab results are hard for non-specialists to interpret.** A typical lipid-and-metabolic panel returns a dozen numbers. Reference ranges printed on the report are generic, sometimes lab-specific, and rarely explain *how far* a value sits outside the desirable range or *what to do about the question* — only that a flag is or isn't raised.

**South Asians carry well-documented, elevated cardiometabolic risk.** This is not a fringe claim — it is reflected in major cardiology guidance. The 2018 ACC/AHA Cholesterol Guideline explicitly lists South Asian ancestry as a "risk-enhancing factor," and the WHO has published lower BMI action points for Asian populations (overweight from 23, not 25). South Asians tend to develop type 2 diabetes and coronary disease earlier and at lower BMIs than the populations most risk calculators were built around. A person who looks "normal" on a standard BMI chart may already be in an increased-risk band by South Asian standards.

**Appointments are short, and preparation is the highest-leverage moment.** Primary care visits are often 15 minutes. The difference between a productive visit and a wasted one is frequently whether the patient arrives knowing which two or three things to ask about. A tool that turns raw numbers into a focused, guideline-grounded set of discussion points raises the quality of that conversation without trying to replace it.

### Where this fits — and where it deliberately does not

This is a **preparation and education** tool, sitting *before* the clinical encounter, not inside it. It does not diagnose, does not predict an individual's risk percentage, and does not recommend treatment. It organizes what the person already has (their numbers) against trustworthy references (published guidelines and public NHANES data) and hands them a better starting point for a professional conversation.

The honest framing: most of what this tool does, a motivated person could assemble themselves with enough time, several guideline PDFs, and a statistics background. The value is doing it accurately, instantly, and in plain language — and surfacing the South Asian context that generic tools omit.

A single snapshot is also something a general-purpose AI assistant can now interpret on its own. The capability that a stateless chat session *cannot* easily replicate — and the one that is most clinically meaningful — is tracking values **over time**: rate of change, whether a value crossed a guideline line, and what moved after a medication started. That longitudinal view is the product's durable differentiator, and it matters more for South Asians, who tend to develop disease earlier and at lower BMI, where catching an adverse trend early is higher-value. See `docs/INCREMENTAL_VALUE_SPEC.md`.

---

## 2. The What

### Product summary
The user enters cardiometabolic lab values, vitals, basic demographics, and medication flags. The tool returns four layers of context, then steps out of the way:

1. **Clinical threshold classification** — each value placed into a published guideline category (e.g. LDL "High," HbA1c "Prediabetes"), with the guideline source named.
2. **Population benchmark** — the value positioned against the NHANES Non-Hispanic Asian reference distribution (10th–90th percentile), clearly and accurately labeled.
3. **South Asian risk context** — guideline-backed, qualitative discussion points shown only when the user reports South Asian ancestry (ancestry as a risk-enhancing factor; lower BMI action points).
4. **Physician discussion guide** — plain-language prompts the user can raise with their clinician, generated from a fixed template.

### What it explicitly is not (and why that's a feature)

| It is | It is not |
|---|---|
| Educational context for your numbers | A diagnosis |
| A comparison to a public reference population | A South Asian–specific clinical study result |
| A set of questions to ask a clinician | Treatment or medication advice |
| A preparation aid before an appointment | A replacement for an appointment |
| A guideline-sourced summary | A personalized risk score or prediction |

The constraints are deliberate. By refusing to diagnose or predict, the tool stays in the low-risk, high-trust zone of patient education — and avoids both the regulatory burden and the real harm of a tool that overclaims.

### The honest data caveat, stated plainly
The benchmark uses NHANES, the large U.S. public health survey. NHANES groups South, East, and Southeast Asians together under a single "Non-Hispanic Asian" category. So the *population benchmark* is genuinely "Non-Hispanic Asian," not South Asian specifically — and the tool labels it exactly that way, everywhere. The South Asian *context* layer is sourced separately from clinical guidelines, and is presented as qualitative discussion context, never as an empirical cohort statistic. Being scrupulous about this distinction is central to the product's credibility.

---

## 3. The How

### How it works, end to end
1. The person enters their numbers in a clean web form. Every field is optional; anything left blank is flagged as "not provided," never guessed.
2. The values are sent to a backend service that holds all the clinical logic.
3. The service classifies each value against published thresholds, positions it against the NHANES benchmark, assembles the South Asian context (if applicable) and the discussion guide, and returns a structured result.
4. The browser renders the result: a disclaimer first, classification cards, a distribution chart showing where the person sits, the context panels, the discussion guide, and an always-visible limitations panel.
5. Nothing is stored. The result lives only in the browser tab and disappears when it closes.

### How accuracy and safety are built in
- **Every threshold value is sourced from a named guideline** (ACC/AHA, ADA, NCEP, WHO) and lives in a single authoritative document, mirrored exactly in the code.
- **The reference benchmark uses real public NHANES data** — the actual Non-Hispanic Asian cohort percentiles, computed from the 2017–2018 survey files.
- **Safety guarantees are enforced by the software's structure**, not left to discipline: the cohort label is fixed at the type level, a disclaimer is a required part of every response, and the limitations panel cannot be hidden.
- **The physician discussion guide is template-generated** — fixed, reviewable wording, with no AI text generation in the live product, so its output is predictable and auditable.
- **The system is verified by 184 automated tests** spanning every clinical threshold boundary, the data pipeline, the API, and a real end-to-end run.

### How it can be used responsibly to support — not replace — medicine
The design philosophy is "AI and software in a supporting role." Software is good at instant, consistent, tireless application of published rules and at surfacing relevant context a busy person would miss. Clinicians are irreplaceable for judgment, diagnosis, the whole-person picture, and treatment. This tool deliberately occupies only the first half: it does the rote organizing and contextualizing, and explicitly routes every meaningful decision back to a human clinician. That division of labor is where software genuinely helps medicine without overreaching.

---

## 4. Key Personas

### Persona 1 — Priya, the proactive patient (primary)
**Age 38, software professional, South Asian, family history of diabetes and heart disease.** Health-literate but not medically trained. Tracks her labs in a spreadsheet, reads widely, and is frustrated that her "normal" BMI doesn't square with her family history. She wants to understand her numbers and walk into her annual physical with sharp questions.
- **Goal:** understand whether her values are something to act on, especially given her ancestry.
- **Frustration:** generic reference ranges ignore that she's South Asian; she doesn't know what to prioritize.
- **What success looks like:** she arrives at her appointment with two or three specific, guideline-grounded questions.

### Persona 2 — Rajesh, the recently-flagged (primary)
**Age 52, small-business owner, South Asian.** A routine check flagged borderline glucose and elevated cholesterol. He's anxious, googling, and getting a mix of alarmism and ads. He needs a calm, trustworthy way to understand where he actually stands before his follow-up.
- **Goal:** get grounded, non-sensational context without self-diagnosing.
- **Frustration:** the internet is either terrifying or trying to sell him something.
- **What success looks like:** he understands which values are flagged, sees them in population context, and has a level-headed list to discuss with his doctor.

### Persona 3 — The caregiver (secondary)
**Adult child managing an aging parent's health.** Often the one who collects lab results, books appointments, and tries to make sense of trends across visits. Frequently South Asian families where an adult child coordinates care for a parent at elevated risk.
- **Goal:** make sense of a parent's numbers and prepare for appointments on their behalf.
- **What success looks like:** a clear, shareable summary to bring to the parent's clinician.

### Persona 4 — Dr. Mehta, the reviewing clinician (stakeholder, not a user)
**Primary care physician or cardiologist.** Not a day-to-day user, but the gatekeeper of credibility. Will a patient bringing this printout *help* or *hinder* the visit? Are the thresholds current? Is the South Asian framing defensible? Her review is the gate for taking the project beyond a demo.
- **Goal:** confirm the tool is accurate, safe, and additive to the encounter rather than a source of misinformation.
- **What success looks like:** she'd be comfortable with her own patients using it to prepare.

### Persona 5 — The developer/maintainer (internal stakeholder)
Extends the tool safely: adds biomarkers, updates thresholds when guidelines change, keeps the data current. Relies on the single-source-of-truth design and the test suite to make changes without breaking clinical correctness.

---

## 5. User Stories

Written in standard form, grouped by persona, with acceptance criteria. These map directly to the implemented feature set.

### Epic A — Understand my numbers in context

**A1.** *As Priya, I want to enter my lab values and see each one classified against clinical guidelines, so that I know which are in a normal range and which are not.*
- Given I enter values, when I submit, then each biomarker shows a category (e.g. "High," "Normal," "Prediabetes") and the guideline it came from.
- Values I leave blank are shown as "not provided," never guessed.
- No result uses diagnostic language ("you have…") or tells me to take a medication.

**A2.** *As Rajesh, I want to see where my value sits relative to a comparable population, so that "high" means something concrete rather than just a label.*
- Given a value, when results render, then I see a distribution (10th–90th percentile) with my value marked.
- The reference population is labeled exactly and honestly ("NHANES Non-Hispanic Asian"), with its sample size shown.

**A3.** *As any user, I want each classification to name its source guideline, so that I can trust it and look it up.*
- Every threshold card displays its guideline source (e.g. "ADA Standards of Medical Care 2024").

### Epic B — South Asian–specific context

**B1.** *As Priya, I want the tool to account for my South Asian ancestry, so that I'm not measured only against references that may understate my risk.*
- Given I indicate South Asian ancestry, when results render, then a context panel explains ancestry as a guideline-recognized risk-enhancing factor.
- Given my BMI, the panel shows the South Asian BMI action points (23 / 27.5) *alongside* — never replacing — the standard categories.
- The context is qualitative and explicitly framed for physician discussion; it never states a personal risk percentage.

**B2.** *As a skeptical user, I want the tool to be honest about what the data can and can't say, so that I trust it.*
- The South Asian BMI context is clearly distinguished from the NHANES benchmark.
- A limitations panel is always visible and explains that NHANES aggregates Asian subgroups.

### Epic C — Prepare for my appointment

**C1.** *As Rajesh, I want a list of specific questions to ask my doctor, so that I use my short appointment well.*
- Given results, when I view the discussion guide, then I see plain-language prompts for each non-normal value, each citing the relevant guideline.
- If all my values are normal, the guide says so and still encourages me to raise personal concerns.

**C2.** *As the caregiver, I want a clear summary I can bring to a clinician, so that I can advocate for my parent.*
- The results page is a coherent, printable summary: disclaimer, classifications, benchmark, context, questions, limitations.

### Epic C2 — Track my numbers over time

**C2.1.** *As Priya, I want to enter lab draws from different dates and see how each value is trending, so that I can tell whether things are getting better or worse — not just where they are today.*
- Given two or more dated draws, when I view my timeline, then each biomarker shows a sparkline over time and a plain-language direction (improving / worsening / stable / not enough data).
- "Improving" means moving toward the guideline-preferred range (correctly inverted for HDL).
- The tool describes what has happened; it never predicts a future value or gives a risk score.

**C2.2.** *As Rajesh, I want to see when a value crossed a clinical line and what changed after I started a medication, so that I have something concrete to discuss.*
- Category transitions are shown (e.g. "Prediabetes → Normal").
- When a medication was started between draws, the timeline marks it and describes the observed change in the affected values — without claiming the medication caused it.

**C2.3.** *As a privacy-conscious user, I want to own my history, so that tracking over time doesn't mean a company stores my health data.*
- I can export my history as a file I keep, and import it later to continue.
- An optional cache lives only on my own device and I can clear it.
- The server stores nothing; it computes on what I send and returns.

### Epic D — Trust, safety, and privacy

**D1.** *As any user, I want to know this isn't a diagnosis, so that I don't act on it inappropriately.*
- A disclaimer appears at the top of every results view and is part of every response.
- A limitations panel is always visible and cannot be dismissed.

**D2.** *As a privacy-conscious user, I want my health numbers not to be stored, so that I'm not creating a record somewhere.*
- No biomarker value is persisted server-side; results exist only in the browser session and clear when the tab closes.

**D3.** *As Rajesh (anxious), I want calm, non-sensational framing, so that I'm informed without being frightened.*
- Copy is factual and neutral; no alarmist language, no risk scores, no urgency cues.

### Epic E — Clinical and engineering trust (stakeholders)

**E1.** *As Dr. Mehta, I want to review the exact thresholds and sources, so that I can confirm they're current before endorsing the tool.*
- All thresholds and their citations are in one authoritative reference document.

**E2.** *As the maintainer, I want guideline updates to be a single, safe change, so that the tool stays current without risking correctness.*
- Each threshold lives in exactly one place; changing it requires updating the matching test, and the validation gate enforces consistency.

---

## 6. Success measures (pragmatic)

This is a demo, so success is qualitative and gate-oriented, not adoption metrics:
- A clinician reviews the output and would be comfortable with patients using it to prepare.
- Test users report the results were clear and the questions useful for an appointment.
- No output is found that reads as diagnosis, prediction, or treatment advice.
- The South Asian framing is judged accurate and not overstated by a clinical reviewer.

Adoption, engagement, and outcome measures belong to a later stage, only after clinical sign-off.

---

## 7. What's next
The tool is complete and demo-ready, and the longitudinal trajectory capability (the key differentiator) is implemented end-to-end — stateless API plus a timeline UI with user-owned data. The gate to going further is **clinical review** — a licensed clinician confirming the thresholds are current, the South Asian framing is defensible, and the language is safe. Everything beyond that (deployment at scale, regulatory determination, accessibility, security hardening) follows that sign-off.
