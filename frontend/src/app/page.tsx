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
    'Provide available values across lipids, glucose, blood pressure, body measures, and optional advanced markers. Missing inputs are never guessed.'],
  ['02', 'Read the layers.',
    'See guideline categories, population context, and South Asian discussion context when it applies — each kept distinct.'],
  ['03', 'Carry the useful questions forward.',
    'Use a plain-language appointment guide. For dated draws, explore descriptive trends in a user-owned health file.'],
];

const CAPABILITIES = [
  ['01', 'Classify the essentials.',
    'Place supplied lipids, glucose, blood pressure, body measures, and optional markers in a named guideline category.'],
  ['02', 'Compare with care.',
    'Show population context with its actual cohort label. Peer matching stays switched off until a cohort with established provenance is registered — no comparison beats an unsourced one.'],
  ['03', 'Surface what is relevant.',
    'Bring forward South Asian guideline context and advanced-marker categories when the input calls for them — never as a personal risk score.'],
  ['04', 'Make time visible.',
    'Review descriptive changes across dated draws in a portable health file the user keeps and controls.'],
  ['05', 'Prepare for the visit.',
    'Turn the result into a discussion guide and a copy-ready pre-visit brief for a clinician conversation.'],
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
            CardioMet Lens brings your lab values into clearer view &mdash; alongside
            published guidelines and clearly labeled population context &mdash; so you
            can arrive ready for a better clinician conversation.
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
            <p className="source-line">ACC/AHA 2018 Cholesterol Guideline</p>
            <div className="range-block">
              <div className="range-labels">
                <span>Reference distribution</span><span>Population context</span>
              </div>
              <div className="range-track" aria-hidden="true">
                <span className="range-fill" /><i className="value-pin" />
              </div>
              <p>Benchmarks are shown with a plainly named cohort &mdash; not a relabeled proxy.</p>
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
          <p className="art-caption">Illustrative workflow &mdash; not a patient report or a product screenshot.</p>
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
              When results arrive, it can be hard to tell what deserves a question, what
              belongs in a broader pattern, and what generic reference ranges leave out.
              CardioMet Lens organizes that starting point without pretending to replace
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
                  Non-Hispanic Asian and is named as such &mdash; never relabeled as South
                  Asian data it is not.
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
            <p>Designed as education before an appointment &mdash; not an alternative to one.</p>
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

          <div className="workflow-note">
            <span className="note-mark" aria-hidden="true">+</span>
            <p>
              <b>What stays out of scope:</b> diagnosis, individual risk prediction,
              medication advice, and treatment recommendations.
            </p>
          </div>

          <div className="capability-deck" aria-labelledby="capabilities-heading">
            <div className="capability-deck-head">
              <p className="eyebrow eyebrow-light"><span /> A more complete read, kept deliberately descriptive</p>
              <h3 id="capabilities-heading">The layers behind a better conversation.</h3>
            </div>
            <div className="capability-rail">
              {CAPABILITIES.map(([n, title, body]) => (
                <article key={n}>
                  <span>{n}</span>
                  <h4>{title}</h4>
                  <p>{body}</p>
                </article>
              ))}
            </div>
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

      {/* ========================== BENEFITS ========================== */}
      <section className="benefits shell section" aria-labelledby="benefits-heading">
        <div className="benefits-lead">
          <p className="eyebrow"><span /> Useful by design</p>
          <h2 id="benefits-heading">The difference is in the detail it refuses to hide.</h2>
          <p>
            CardioMet Lens is built around careful distinctions that make the information
            more trustworthy &mdash; and more useful in a real conversation.
          </p>
        </div>
        <div className="benefit-cards">
          <article className="benefit-card benefit-featured">
            <p className="card-kicker">Guideline-first</p>
            <h3>Know what a category is anchored to.</h3>
            <p>Results name the guideline source behind the classification rather than presenting an unexplained flag.</p>
            <div className="source-pills">
              <span>ACC/AHA</span><span>ADA</span><span>NCEP</span><span>WHO</span>
            </div>
          </article>
          <article className="benefit-card">
            <p className="card-kicker">Honest context</p>
            <h3>Keep population labels precise.</h3>
            <p>
              Reference context is presented with its actual cohort label, and a comparison
              is withheld rather than shown when there is not enough data to support it.
            </p>
          </article>
          <article className="benefit-card">
            <p className="card-kicker">Safety in the structure</p>
            <h3>Boundaries don&rsquo;t disappear when the page gets busy.</h3>
            <p>
              Disclaimers lead; limitations remain visible; and patient-facing language is
              fixed and reviewable rather than generated on the fly.
            </p>
          </article>
          <article className="benefit-card">
            <p className="card-kicker">User-owned history</p>
            <h3>Follow a trajectory without building a patient database.</h3>
            <p>Descriptive longitudinal context can travel in a portable health file the user controls.</p>
          </article>
        </div>
      </section>

      {/* ========================== AUDIENCES ========================== */}
      <section className="audience-shell" id="audiences" aria-labelledby="audiences-heading">
        <div className="shell audiences">
          <div className="audience-intro">
            <p className="eyebrow"><span /> Better prepared, on both sides of the appointment</p>
            <h2 id="audiences-heading">One tool. Two perspectives that belong in the same conversation.</h2>
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
          <p className="audience-note">
            CardioMet Lens is an education and appointment-preparation tool &mdash; not a
            clinician portal, patient record, or replacement for professional care.
          </p>
        </div>
      </section>

      {/* ========================== GUARDRAILS ========================== */}
      <section className="guardrails-shell" id="guardrails" aria-labelledby="guardrails-heading">
        <div className="shell guardrails">
          <div className="guardrails-copy">
            <p className="eyebrow"><span /> Designed for a responsible role</p>
            <h2 id="guardrails-heading">A complete picture. Deliberate limits.</h2>
            <p>
              The product&rsquo;s most important feature is not a claim &mdash; it is its
              restraint. CardioMet Lens makes the transition from information to clinical
              judgment explicit, so a person can prepare without being nudged into
              self-diagnosis.
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
          Enter the values you have and see how CardioMet Lens turns a lab panel into
          context for a clinician conversation &mdash; without stepping into diagnosis or
          treatment.
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
