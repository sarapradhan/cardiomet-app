'use client';
/**
 * frontend/src/app/page.tsx — the home route.
 *
 * Ported from the standalone marketing page that previously lived in
 * `CardioMetLens Website/website/` and deployed as its own Vercel project.
 * Folding it in here means one codebase and one deploy: the app shell in
 * layout.tsx now supplies the disclaimer bar, brand, primary nav and footer,
 * so this file drops the standalone page's own header/footer/skip-link and
 * keeps only its content. Styles live under `.home` in globals.css.
 *
 * Three claims from the standalone page were corrected on the way in, because
 * the product changed underneath it when the unsourced "sahc" cohort was
 * removed (see docs/SAHC_COHORT.md and the removal commit):
 *   1. The approach list named "the South Asian Heart Center clinical cohort"
 *      as a second registered cohort. There is only one registered cohort now.
 *   2. A capability card implied peer matching is live. No strata table ships
 *      today (sahc_risklens/data/strata_tables.py), so matching always degrades
 *      to the whole-cohort distribution with matched=false.
 *   3. A guardrail row listed three reference sources as distinct. One of the
 *      three no longer exists.
 * The hero's "Check Your Labs" link pointed at the deployed app by absolute
 * URL; it is now an in-app route.
 */
import Link from 'next/link';
import { Legend } from '@/components/Legend';
import { GuidedTour, TourButton, type TourStep } from '@/components/GuidedTour';

const TOUR: TourStep[] = [
  { anchor: '', title: 'Welcome to CardioMet Lens',
    body: 'A quick 4-step tour. This tool puts your cardiometabolic labs in clinical and population context — educational only, never a diagnosis.' },
  { anchor: 'legend', title: 'The color legend',
    body: 'Every value is coded by status (in range / elevated / high) and grouped by panel (lipids, glucose, blood pressure, body). You will see this language throughout.' },
  { anchor: 'cta', title: 'Two ways in',
    body: 'Check a single set of labs, or track values over time to see trends. Try the example data on the next page if you do not have your own numbers handy.' },
  { anchor: 'cta', title: 'Honest by design',
    body: 'The benchmark is NHANES Non-Hispanic Asian (labeled honestly), South Asian ancestry is shown as risk context, and nothing is stored on a server.' },
];

const WORKFLOW = [
  ['01', 'Enter what you have.',
    'Provide available values across lipids, glucose, blood pressure, body measures, and optional advanced markers. Missing inputs are never guessed, and each value you do enter lands in a named guideline category rather than a raw number.'],
  ['02', 'Read the layers.',
    'See population context under its real cohort label. Peer matching stays off until a properly sourced cohort exists to match against, and South Asian context and advanced markers surface only when relevant, as discussion points, never a score.'],
  ['03', 'Carry the useful questions forward.',
    'Turn the result into a discussion guide and a copy-ready pre-visit brief. For dated draws, track descriptive trends over time in a portable health file you keep.'],
];

export default function Home() {
  return (
    <div className="home">
      <GuidedTour steps={TOUR} tourId="home" autoStart />

      {/* ============================ HERO ============================ */}
      <section className="hero shell" id="top" aria-labelledby="hero-heading">
        <div className="hero-copy">
          <h1 id="hero-heading">Context before conclusions.</h1>
          <p className="hero-intro">
            CardioMet Lens puts your lab values in context: published guideline
            categories and clearly labeled population data, organized so you can
            walk into your next appointment ready to ask better questions.
          </p>
          <div className="hero-actions" data-tour="cta">
            <Link className="button button-primary" href="/benchmark">
              Check my labs <span aria-hidden="true">&rarr;</span>
            </Link>
            <a className="text-link" href="#workflow">
              See how it works <span aria-hidden="true">&darr;</span>
            </a>
            <TourButton />
          </div>
          <p className="disclaimer">
            Educational tool only. Not a diagnosis, individual risk score, or treatment
            recommendation.
          </p>
        </div>

        {/* An illustrative composition of the product's output, drawn in CSS and
            labeled as such — deliberately not passed off as a screenshot. */}
        <div className="hero-art" aria-label="An illustrative product workflow, not a patient result">
          <div className="art-halo halo-one" aria-hidden="true" />
          <div className="art-halo halo-two" aria-hidden="true" />
          <div className="lens-card">
            <div className="lens-card-top">
              <span className="lens-caption">Your lab context</span>
              <span className="secure-note"><b /> Educational view</span>
            </div>
            <div className="lens-card-title-row">
              <div>
                <span className="mini-label">LDL cholesterol</span>
                <strong>Guideline category</strong>
              </div>
              <span className="status-chip">High</span>
            </div>
            <p className="source-line">2026 ACC/AHA/Multisociety Dyslipidemia Guideline</p>
            <div className="range-block">
              <div className="range-labels">
                <span>Reference distribution</span><span>Population context</span>
              </div>
              <div className="range-track" aria-hidden="true">
                <span className="range-fill" /><i className="value-pin" />
              </div>
              <p>Benchmarks are shown with a plainly named cohort, not a relabeled proxy.</p>
            </div>
            <div className="context-row">
              <span className="context-orb" aria-hidden="true">01</span>
              <div>
                <b>South Asian context, when relevant</b>
                <small>Qualitative guideline-backed discussion points.</small>
              </div>
            </div>
            <div className="guide-row">
              <span>For your appointment</span>
              <b>Discussion guide <span aria-hidden="true">&#8599;</span></b>
            </div>
          </div>
          <p className="art-caption">Illustrative workflow, not a patient report or a product screenshot.</p>
        </div>
      </section>

      {/* ========================= PROOF STRIP ========================= */}
      <section className="proof-strip" aria-label="Key product foundations">
        <div className="shell proof-grid">
          <p>Published guideline categories</p>
          <p>Clearly labeled cohort context</p>
          <p>Template-based patient-facing language</p>
          <p>Entered values are not stored by the service</p>
        </div>
      </section>

      {/* ========================== APPROACH ========================== */}
      <section className="approach shell section" id="approach" aria-labelledby="approach-heading">
        <div className="section-intro">
          <p className="eyebrow"><span /> The problem is not another score</p>
          <h2 id="approach-heading">A lab report gives you numbers. It rarely gives you a place to begin.</h2>
        </div>
        <div className="approach-layout">
          <div className="approach-statement">
            <p>
              When results come back, it&rsquo;s hard to know what deserves a question,
              what fits a larger pattern, and what a generic reference range leaves out.
              CardioMet Lens organizes that starting point. It doesn&rsquo;t replace
              clinical judgment.
            </p>
            <a className="text-link" href="#guardrails">
              Why the limits matter <span aria-hidden="true">&rarr;</span>
            </a>
          </div>
          <ol className="approach-list">
            <li>
              <span>01</span>
              <div>
                <b>Move from a raw value to a named category.</b>
                <p>Each supplied measure is placed against a source-identified clinical threshold.</p>
              </div>
            </li>
            <li>
              <span>02</span>
              <div>
                <b>See a benchmark without blurring what it represents.</b>
                <p>
                  Cohort labels stay explicit. The population benchmark is NHANES
                  Non-Hispanic Asian, named as such, and never relabeled as South Asian
                  data it isn&rsquo;t.
                </p>
              </div>
            </li>
            <li>
              <span>03</span>
              <div>
                <b>Take better questions into the room.</b>
                <p>A fixed-template discussion guide helps organize a conversation with a qualified clinician.</p>
              </div>
            </li>
          </ol>
        </div>
      </section>

      {/* ========================== WORKFLOW ========================== */}
      <section className="workflow-section" id="workflow" aria-labelledby="workflow-heading">
        <div className="shell">
          <div className="workflow-heading">
            <div>
              <p className="eyebrow eyebrow-light"><span /> A focused path, not an overload of data</p>
              <h2 id="workflow-heading">From lab panel to better prepared.</h2>
            </div>
            <p>Designed as education before an appointment, not an alternative to one.</p>
          </div>

          <div className="workflow-grid">
            {WORKFLOW.map(([n, title, body]) => (
              <article key={n}>
                <p className="step-number">{n}</p>
                <h3>{title}</h3>
                <p>{body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ====================== THE COLOUR LANGUAGE ====================== */}
      <section className="legend-strip" aria-labelledby="legend-heading">
        <div className="shell">
          <p className="eyebrow"><span /> One vocabulary, used everywhere</p>
          <h2 id="legend-heading">The colour language you will see in a result.</h2>
          <p>
            Status describes where a value sits against its guideline. Panel colour groups
            the markers that belong together. The same coding carries across every screen.
          </p>
          <div data-tour="legend"><Legend /></div>
        </div>
      </section>

      {/* ========================== AUDIENCES ========================== */}
      <section className="audience-shell" id="audiences" aria-labelledby="audiences-heading">
        <div className="shell audiences">
          <div className="audience-intro">
            <p className="eyebrow"><span /> Better prepared, on both sides of the appointment</p>
            <h2 id="audiences-heading">One tool, two perspectives in the same conversation.</h2>
            <p>
              CardioMet Lens is designed for the person bringing the lab report and the
              clinician helping make sense of the whole picture. It does not replace either role.
            </p>
          </div>
          <div className="audience-panels">
            <article className="audience-panel audience-person">
              <p className="audience-label">For you or a caregiver</p>
              <h3>Arrive informed, not alarmed.</h3>
              <ul>
                <li>See supplied values in clear, guideline-backed language.</li>
                <li>Understand population context without mistaking it for a diagnosis.</li>
                <li>Keep a private, user-owned record of dated draws if tracking over time.</li>
                <li>Bring a concise set of questions to the appointment.</li>
              </ul>
            </article>
            <article className="audience-panel audience-clinician">
              <p className="audience-label">For the clinician joining the conversation</p>
              <h3>Start with a more focused patient conversation.</h3>
              <ul>
                <li>A patient can bring a copy-ready pre-visit brief instead of a stack of lab pages.</li>
                <li>Guideline sources and cohort labels remain visible alongside the context.</li>
                <li>South Asian considerations are discussion context, not a shortcut to judgment.</li>
                <li>The product stays out of diagnosis, prediction, and treatment decisions.</li>
              </ul>
            </article>
          </div>
        </div>
      </section>

      {/* ========================== GUARDRAILS ========================== */}
      <section className="guardrails-shell" id="guardrails" aria-labelledby="guardrails-heading">
        <div className="shell guardrails">
          <div className="guardrails-copy">
            <p className="eyebrow"><span /> Designed for a responsible role</p>
            <h2 id="guardrails-heading">A complete picture. Deliberate limits.</h2>
            <p>
              What makes this trustworthy is what it refuses to do. CardioMet Lens
              draws a hard line between information and clinical judgment, so you can
              prepare without drifting into self-diagnosis.
            </p>
          </div>
          <dl className="guardrail-list">
            <div>
              <dt>It does</dt>
              <dd>Organize lab values around published thresholds, cohort context, and clinician-discussion prompts.</dd>
            </div>
            <div>
              <dt>It does not</dt>
              <dd>Diagnose a condition, calculate an individual risk score, or tell someone what treatment to take.</dd>
            </div>
            <div>
              <dt>It keeps clear</dt>
              <dd>
                NHANES Non-Hispanic Asian reference data and qualitative South Asian
                guideline context are different things, and are never merged into one number.
              </dd>
            </div>
            <div>
              <dt>It leaves with you</dt>
              <dd>Entered values are not persisted by the service; longitudinal records are user-owned exports.</dd>
            </div>
          </dl>
        </div>
      </section>

      {/* ========================== FINAL CTA ========================== */}
      <section className="final-cta shell section" aria-labelledby="cta-heading">
        <p className="eyebrow"><span /> A more useful starting point</p>
        <h2 id="cta-heading">Bring the right questions to your next appointment.</h2>
        <p>
          Enter the values you have, and CardioMet Lens turns your lab panel into a
          clearer starting point for that conversation.
        </p>
        <div className="final-actions">
          <Link className="button button-primary" href="/benchmark">
            Check my labs <span aria-hidden="true">&rarr;</span>
          </Link>
          <Link className="text-link" href="/timeline">
            Track values over time <span aria-hidden="true">&rarr;</span>
          </Link>
        </div>
      </section>
    </div>
  );
}
