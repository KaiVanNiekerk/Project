# Citation and claims audit: full thesis

## 0. Progress tracker

*Last updated: 22 Oct 2026 (Chapter 3 resolved apart from Kai's Koopman network and RevIN), against snapshot v6. Regenerate with `python Thesis/Sources/audit_stats.py <thesis.qmd> citation-audit.md references.bib`.*

**Sentences in the thesis.** Counted from the text. A sentence is "cited" if it contains a `@key` from `references.bib`.

| Chapter | Sentences | Cited | Uncited | % cited |
|---|--:|--:|--:|--:|
| 1 Introduction | 127 | 36 | 91 | 28% |
| 2 Preliminaries | 168 | 41 | 127 | 24% |
| 3 K²VAE | 255 | 28 | 227 | 11% |
| 4 Results | 586 | 12 | 574 | 2% |
| 5 Conclusion | 89 | 6 | 83 | 7% |
| Appendix | 8 | 0 | 8 | 0% |
| **Total** | **1233** | **123** | **1110** | **10%** |

**Claims in this audit.** Counted from the rows in Sections 4–9. A row is one claim, and may span several short sentences.

| Chapter | Claim rows | No cite needed or accepted | ✅ Cited on sentence | ✅ Covered by nearby cite | ✅ Needs cite, supported | 🚩⬇️ Needs cite, unsupported | ⚠️↔ Needs cite, partial or differs | Cited but flawed | ❌ Factual error |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 Introduction | 79 | 16 | 35 | 28 | 0 | 0 | 0 | 0 | 0 |
| 2 Preliminaries | 109 | 12 | 41 | 42 | 7 | 3 | 1 | 3 | 0 |
| 3 K²VAE | 126 | 46 | 27 | 28 | 11 | 6 | 5 | 2 | 1 |
| 4 Results | 265 | 185 | 7 | 0 | 38 | 16 | 17 | 0 | 2 |
| 5 Conclusion | 33 | 23 | 3 | 0 | 5 | 0 | 1 | 1 | 0 |
| Appendix | 4 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| **Total** | **616** | **285** | **113** | **98** | **61** | **25** | **24** | **6** | **4** |

**Column meanings.**
- **No cite needed or accepted:** our own work, definitions, signposting, captions, draft notes, and rows the user accepted as is (🛠 ➖ 🖼 📝 ☑️).
- **✅ Cited on sentence:** done.
- **✅ Covered by nearby cite:** supported, but the citation sits on a neighbouring sentence.
- **✅ Needs cite, supported:** the quick wins. The source is in Sources; add the citation.
- **🚩⬇️ Needs cite, unsupported:** no source yet, or the PDF is still to download.
- **⚠️↔ Needs cite, partial or differs:** add a citation *and* fix the wording.
- **Cited but flawed:** a citation exists, but the source only partly supports the sentence or says something different.
- **❌ Factual error:** contradicted by our code, tables, the paper, or other text. It needs correcting, not citing.
- If a row has several labels, it is counted once, by severity: ❌ > 🚩/⬇️ > ↔/⚠️ > ✅.

**Math checks (all pass)**
- Each chapter's columns sum to its claim-row total: 285 + 113 + 98 + 61 + 25 + 24 + 6 + 4 = **616** ✓.
- 616 = number of table rows in Sections 4–9 ✓.
- Citations in the text: 123 cited sentences + 4 cited figure captions = **127**, which matches the **127** audit rows carrying a key ✓. No per-line differences remain (grouped rows at L129, L207, L229 and L235 were split so that each cited sentence has its own row).
- Sentences (1,233) and claim rows (616) are different units. The ~1,110 uncited sentences are mostly our own results (Results alone has 574). The rows that actually need work are the last five columns: 61 + 25 + 24 + 6 + 4 = **120**.

**Corrections made while building this tracker.** 11 rows had the wrong Cite column and were fixed:
- the text cites K²VAE but the row said "—": L55, L75, L466, L694, L700, L744, L916 (L694 had wrongly been called a missing citation);
- the row claimed a citation the text doesn't have: L63 s4, L912 s7, L918, L936.

---

**Snapshot (v6).** `docs/K2VAE/Reports/thesis.qmd`, working tree on 22 Oct 2026: commit `fa1a87c` plus uncommitted edits to Chapters 1–3 and the Exchange flag (L724). 1,012 lines, MD5 `e7f41b01…`. All line numbers (L###) refer to this version. Line history, with each step's numbers in that step's own version: v1→v2 inserted the Exchange flag (+2 from v1 L725 on); v2→v3 merged Prelims L259–261 into one line and added a sentence in the loss section (−2 for v2 L262–460); v3→v4 changed L217 and L243 only; v4→v5 merged L436–438 into L436 (−2 for v4 L439 on); v5→v6 changed L393 only. Each shift was spot-checked against the text.
**Scope.** Every sentence in Chapters 1–5 and the appendix captions. Sentence numbers (s1, s2, …) count from the start of the paragraph on that line. A row may cover a run of consecutive sentences when they share one verdict.
**Rebuilt from scratch.** The 14 Oct audit (Ch. 2–3 only) was not reused. Every row was re-checked against the current text. The old version is in git at `7ea0d76`.
**Nothing in `thesis.qmd` or `references.bib` was changed.**

**What was checked against what**
- Literature claims: text extracts in `Thesis/Sources/` (outside the repo), read in context. Page numbers are **PDF pages**.
- Claims about our implementation: `src/`, `baselines/`, `configs/` (file:line given).
- Claims about the authors' code: `decisionintelligence/K2VAE` (master), read this pass.
- Numbers in the prose: recomputed from our tables and from K²VAE Tables 1, 2, 9 and 10.
- Figure descriptions: checked against the PNGs in `artifacts/plots/`.
- Nothing was downloaded. Candidate sources are listed for you to fetch (Section 10).

**Status labels**

| Label | Meaning |
|---|---|
| ✅ | The source says this, with the same meaning. The location is given. "Missing cite" means the support exists but the sentence has no citation. |
| ⚠️ | Partly supported, or supported with a caveat (wording stronger than the source, code-only confirmation, or similar). |
| ☑️ | **Accepted as is** by the user after review. The original verdict is kept in the Notes. Counts as resolved. |
| ↔ | **Meaning differs** from the cited or nearest source: strength, scope, rationale or attribution. The source's own words are quoted. |
| 🚩 | No support in Sources or K²VAE's references, or our argument stated as established fact. Needs softening, our own evidence, or a new source. |
| ❌ | **Factually wrong**: contradicted by our code, our own tables, the cited paper, or another part of the thesis. |
| ⬇️ | A likely source exists (mostly in K²VAE's reference list) but is not in Sources. **Unverified** until you supply the PDF. |
| 🛠 | Our own work: implementation, experiments or design choices. "✓" means checked against code, tables or figures. |
| ➖ | No citation needed: definition, algebra, signposting or figure description. |
| 🖼 | Figure or table caption or credit. |
| 📝 | Draft note left in the text. It will render in the PDF. |

**Label totals.** 616 rows: ✅ 275 · 🛠 245 · ⚠️ 23 · ☑️ 10 · ➖ 42 · 🚩 23 · ↔ 8 · 🖼 15 · ⬇️ 7 · ❌ 4 · 📝 5. These sum to more than the row count because some rows carry two labels. The tracker in Section 0 counts each row once.

---

## 1. Headline flags

### 1.1 Factual errors (❌). Fix these first.

1. **L368: the Koopman rollout start state is wrong.** The text says the forecast "isolates the final state … z₀ = x_n*". Our code (`src/koopman.py:121-138`) starts from the **first** token and runs n reconstruction steps, so forecast step 1 = 𝒦ⁿx₁*. That is exactly K²VAE Eq. (11). The z₀ = x_n* belongs to the **Kalman** filter (K²VAE Eq. 15; `src/k2vae.py:109`). *This corrects my 14 Oct audit, which called it "an implementation difference" without reading the code.* 👤 **Assigned to Kai.** (Koopman network section)
2. **L476 / L481: say which Exchange data we use (⚠️ needs a sentence; not an error).** It is the **same exchange-rate series** as the paper's Exchange-S, but over a longer period. ProbTS's Exchange-S (GluonTS `exchange_rate_nips`) is the first 6,221 days of our file: 6,071 training days, which is the number in K²VAE Table 1, plus 5 rolling 30-day test windows. Our file is the full 7,588 days, the length the paper lists for Exchange-L, run under the Exchange-S protocol (T = L = 30). The thesis gives 7,588 without explaining this, then compares with the paper's Exchange claims (L668, L912, L916). Suggested wording is under the L476 row. *Corrects the earlier "wrong file" framing.*
3. **L746: "the two benchmark models, which we did not write".** This contradicts L545 and L571–573, which say we **reimplemented both baselines in our own codebase**.
4. ~~**L438: the decoder misrepresents the paper.** The thesis says the paper describes the decoder "simply as an inverse measurement function". K²VAE §3.1.3, Eq. (24), p. 5 already specifies two MLPs, μ⁻¹ and σ⁻¹.~~ **Resolved 22 Oct (Ch. 3 edits, v5).** Now L436: the paper's two-MLP decoder is described correctly.
5. **L342–346: the RevIN inverse equation is not our code.** The (γ + ε²) form is the official RevIN code. Ours divides by a clamped |γ| ≥ 0.1 with no ε² (`src/revIN.py:96,111-114`), and σ uses |γ|. 👤 **Assigned to Kai.** (RevIN section)
6. ~~**L406: "a single learnable matrix at each time step".** Q and R come from one **global** L_Q and one L_R (`src/kalman.py:23-24`).~~ **Resolved 22 Oct (Ch. 3 edits, v5).** Now "shared across all time steps".
7. **L519: "Datasets in the same tier share these dimensions".** Our own Table 4.1 gives Exchange-S 8 variables vs Congestion-S 3.
8. **L983: the appendix promises all horizons for all three models.** The PatchTST 720-step figure is missing.

### 1.2 Our wording changes the source's meaning (↔)

- ~~**L65: Deep Kalman Filter.** Krishnan says "the addition of non-linearities … makes learning more difficult" about **earlier** nonlinear Kalman filters, the problem DKF then solves (§1, pp. 1–2). The thesis presents it as DKF's own weakness.~~ **Resolved 22 Oct (Ch. 1 edits).**
- ~~**L69: Koopman 1931.** Brunton §1, p. 3: Koopman's 1931 work concerned "**Hamiltonian** systems", not nonlinear systems in general.~~ **Resolved 22 Oct (Ch. 1 edits).**
- ~~**L35, L71: "designed for / developed for short horizons".** K²VAE §1, p. 2 says these models "**excel at**" short-term settings.~~ **Resolved 22 Oct (Ch. 1 edits).**
- ~~**L35 s9: why errors accumulate.** We give step-on-step compounding. K²VAE gives "more intricate target distributions".~~ **Resolved 22 Oct (Ch. 1 edits).**
- ~~**L129: "has become widely used in NLP [Vaswani]".**~~ **Resolved 22 Oct (Ch. 2 edits):** now cited to PatchTST.
- ~~**L397: Z′ = Z + U.** "We set" implies our choice, but it is the paper's Eq. (22). Our rationale (the gain dampens U) differs from the paper's (§4.3.2, p. 8).~~ **Resolved 22 Oct (Ch. 3 edits, v5).** Credited to the paper with the paper's reason (§4.3.2).
- ~~**L415: "The Joseph form preserves PSD".** The paper says it "**better ensures**" positive definiteness.~~ **Resolved 22 Oct (Ch. 3 edits, v5).** Now "helps preserve".
- **L858: purpose of the reconstruction term (ablation).** The paper says it "facilitates the linearization of the measurement space" (p. 5). We say it retains information. *L460 was resolved in v5 (now quotes the paper).*
- **L537: Koopa.** "Classical Koopman theory assumes stationarity" and "rather than requiring complex spectral mathematics" both misdescribe Koopa, whose filter is an FFT. Already parked in memory.
- **L539: "Koopa lacks any correction mechanism".** Koopa has residual correction across blocks (App. D.4) and operator adaptation with incoming ground truth (p. 9).
- **L567: "also equipped both with RevIN".** PatchTST already uses instance normalisation (PatchTST §3.1).
- **L684: "tracks closely on all six".** The same paragraph then says the reconstruction is weaker on LUFL and LULL.
- **L706, L752 ("no coefficients" / "None").** The paper's text says the objective is "**weightsumed**", but gives no weights.
- **L916: "Our test sets do not overlap theirs".** This is true for both datasets (ETTh1: L722; Exchange: their test rows 6,071–6,221 vs our 6,449–7,588, verified 22 Oct). The thesis only shows the ETTh1 numbers. Add the Exchange ones at L722.

### 1.3 Unsupported claims (🚩), grouped

- **Our arguments stated as fact:**
  - Markov / non-Markov (L89);
  - "more stable … longer horizons" and "without compounding error" (L95, L125);
  - AE latent space (L217, L243): **mostly resolved in v4.** Sampling wording, KL (Kingma) and noise-injection (Ghosh) attributions now match. **Still open:** L217 s4–s5 "disjoint clusters / empty regions" (not in Ghosh). L243 s3–s4 overridden by the user;
  - scale entanglement (L326) 👤 Kai;
  - ~~"residuals contain sequential patterns" and "standard NNs struggle with long-range" (L379, L381);~~ **Resolved 22 Oct (Ch. 3 edits, v5).**
  - capacity and transfer arguments (L491, L519);
  - PatchTST and Koopa weaknesses, and "resulting in better stability" (L531, L539, L541);
  - "covariates that genuinely drive it" (L647).
- **Attributed to K²VAE but ours:** orthogonal SVD init of 𝒦_glo (L119). 👤 **Assigned to Kai.**
- **Contradicted by a source:** "Standard implementations apply patchification during data loading" (L348). PatchTST §3.1 normalises before patching. Also "standard configurations" of the variance head (L350) is unidentified. 👤 **Assigned to Kai.** (RevIN section)
- **Needs a source outside the chain:**
  - ~~Cholesky / Joseph names (L406, L408);~~ **Resolved 22 Oct (Ch. 3 edits, v5).** Cholesky name removed; Joseph sourced to Zanetti 2013;
  - Bayesian optimisation and Expected Improvement (L495–501), plus we have **not checked W&B actually uses EI**;
  - the CRPS sample identity (L614–618; Gneiting & Raftery 2007);
  - ~~residual connections and layer norm "stabilise training" (L155)~~: **resolved** (claim removed, Vaswani cited).
- **"Fair comparison" (L567)** conflicts with untuned baselines (L934).

### 1.4 Quick wins: support is already in Sources but uncited

- ~~**Kalman filter equations (L163–205).**~~ **Done:** Welch cited at L161, L177, L205.
- ~~**Chapter 3 equations taken from K²VAE.** Eqs. 3–8, 12–13, 15, 17–22 and 24–28 mostly lack sentence-level citations.~~ **Resolved 22 Oct (Ch. 3 edits, v5).** Except the Koopman network and RevIN sections (👤 Kai).
- **NMAE and CRPS definitions (L592, L602).** K²VAE App. C.3, Eqs. (37–38).
- **§4.3.1 PatchTST.** No citation in the whole subsection.
- **L694 exchange rate ≈ random walk.** PatchTST App. A.1.1, p. 13 (citing Rossi 2013).
- ~~**L251 CVAE.**~~ **Done:** `sohn2015learning` added and cited.
- ~~**L138 attention equation; L136.**~~ **Done.**
- **L649: K²VAE's stability claim.** K²VAE §4.2. *(L49 was resolved by the 22 Oct Ch. 1 edits.)*
- **L748 "up to 8 configurations", "5 runs".** K²VAE App. C.4 and the Table 9 caption.

---

## 2. Changes since the 14 Oct audit

| Item | Then | Now |
|---|---|---|
| **Chapter 1 re-audit (22 Oct, v2)** | 5 ↔, several missing cites | DKF reversal, Koopman 1931, "excel at" (L35, L71), error-accumulation rationale and missing paragraph cites (L33, L49, L53, L71) **all fixed**. Koopman 1931 and fpp3 Ch. 8–9 are now in Sources and verified. Remaining ⚠️ and secondary-citation rows were accepted as is by the user, optional citations are covered by surrounding cites, and the draft FLAGs are ignored for now. **Chapter 1 resolved.** |
| **Chapter 2 re-audit (22 Oct, v3 → v4)** | Transformer ↔/⚠️, uncited KF and CVAE | Transformer (L129, L136, L155, L157), Kalman filter (Welch now cited) and CVAE (generic Sohn form) **fixed**. v4 rework of L217/L243 fixed the sampling wording and the KL/noise attributions. L153 s2 and L235 s3–s5 accepted as is. L217 s8–s9 and L243 s3–s4 overridden by the user. **Open:** L217 s4–s5. Koopman (5.1) and RevIN (6.3) are **assigned to Kai**. |
| **Chapter 3 re-audit (22 Oct, v5)** | Decoder ❌, Q/R ❌, skip and reconstruction ↔, Joseph and Cholesky 🚩, Integrator 🚩, many missing cites | All **fixed**: decoder now matches the paper; Q/R "shared across all time steps"; skip connection and reconstruction purpose use the paper's own reasons; "dual form (Joseph stabilisation)" sourced to K²VAE and Zanetti 2013; Cholesky name removed; Integrator claims now attributed (K²VAE, Vaswani §4). Koopman network and RevIN (👤 Kai) not re-audited. L393 s8 fixed in v6; L415 s2 accepted as is. **Chapter 3 resolved apart from Kai's sections.** |
| Positional encoding (L157, L387) | 🚩 | ✅ Resolved |
| Autoregressive and diffusion wording (L356, L368) | 🚩 Contradicted the paper | ✅ Now hedged and consistent with K²VAE §5.1. Needs a ⬇️ source for autoregressive diffusion and flows. |
| Forecast start state (L368) | Called an "implementation difference" | ❌ **Wrong vs our own code.** My earlier note was itself wrong. |
| Markov (L89), SVD cite (L119), AE latent space (L217/243), Cholesky/Joseph, patch-at-load (L348), decoder (L438), Vaswani NLP (L129), residual/LN (L155) | Flagged | **Still open** |
| Welch for the KF section | Proposed | **Cited** at L161, L177, L205 (22 Oct, v3) |
| Sohn 2015 for the CVAE | Proposed | **Added** as `sohn2015learning` and cited (L251, L257); CVAE section made generic (22 Oct, v3) |
| RevIN citation | Missing | Now cited (`kim2021reversible`). **The bib author list is wrong** (Section 3). The PDF is still not in Sources. |

---

## 3. Bibliography hygiene

| Key | Issue |
|---|---|
| `kim2021reversible` | **Wrong author:** "Choi, Jung-Woo". PatchTST and Koopa's reference lists both give **Jang-Ho Choi**. The key says 2021 but the year field is 2022 (cosmetic). |
| `kalmannet2021` | Key 2021, year 2022 (cosmetic). |
| `welch1995` | ~~cited nowhere~~ Now cited (v3). |
| `klushyn2019learning` | In the bib, cited nowhere. |
| `hyndman2021fpp` | Only our quote notes are in Sources (`hyndman2021_fpp3_notes.txt`). The quotes match the text. |
| `black1992global`, `satchell2000demystification` | Cited (L946). **No PDFs in Sources**, and not in K²VAE's references. |
| `sohn2015learning` | ~~no bib entry~~ Added and cited (v3). |
| Draft notes | `--FLAG…--` at **L47, L51, L59, L61, L914** will render in the PDF. |

---

**Detailed tables**

Sections 4–9 below go chapter by chapter in thesis order.
---

## 4. Chapter 1: Introduction

*Re-audited 22 Oct against snapshot v2, after the user's Chapter 1 edits. Changed lines: L33, 35, 49, 53, 65, 69, 71. All other Chapter 1 lines are unchanged and were re-checked against the same evidence.*

### 4.1 Introduction (L33–55)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 33 s1 | Time-series forecasting predicts future values of a sequence from its past and supports decisions in many fields. | — | — | ➖ | Definition. |
| 33 s2 | Energy operators forecast load and wind, financial institutions forecast exchange rates, and transport authorities forecast traffic. | — | K²VAE §1, p. 2 ("economics … traffic … energy, and AIOps") | ☑️ | Unchanged. K²VAE names the fields, not these actors. The examples are illustrative. Cite K²VAE §1 if you want backing. **Accepted as is by the user (22 Oct)**, was ⚠️. |
| 33 s3–s4 | A single best guess is rarely enough; decision-makers need to know how uncertain it is. | — | K²VAE §1, p. 1 ("provides significant support for decision-making") | ☑️ | Unchanged. Supports the motivation, not the "rarely enough" wording. **Accepted as is by the user (22 Oct)**, was ⚠️. |
| 33 s5 | Probabilistic forecasting predicts a full distribution instead of a point estimate. | K²VAE | K²VAE §5.1, p. 9 ("Probabilistic forecasting aims to provide the predictive distribution of the target variable") | ✅ | **Fixed:** citation added. |
| 35 s1 | Most probabilistic models **excel at** short horizons, such as 48 steps or fewer. | K²VAE | K²VAE §1, p. 2 ("Most existing methods excell at short-term problem settings, such as predicting up to 48 steps or fewer") | ✅ | **Fixed:** the meaning now matches the source. |
| 35 s2 | Many applications need forecasts much further ahead, for planning and early warning. | (K²VAE, s3) | K²VAE §1, p. 2 ("long-term planning and early warning") | ✅ | |
| 35 s3 | K²VAE call this LPTSF. | K²VAE | K²VAE §1, p. 2 | ✅ | |
| 35 s4–s7 | Harder because series are nonlinear; non-stationarity and interdependencies make transitions hard to describe; so uncertainty is hard to quantify. | (K²VAE, s9) | K²VAE §1, p. 2 | ✅ | Covered by the citations on s3 and s9. |
| 35 s8 | Errors accumulate as the horizon extends. | (K²VAE, s9) | K²VAE §1, p. 2 ("remarkable error accumulation") | ✅ | |
| 35 s9 | Longer horizons have more complex target distributions, which drives this accumulation. | K²VAE | K²VAE §1, p. 2 ("Longer foreacasting horizons lead to more intricate target distributions, which causes remarkable error accumulation") | ✅ | **Fixed:** the rationale is now the paper's own. |
| 37 s1 | Fig. 1 is reproduced from K²VAE, on our standard electricity benchmark. | K²VAE | K²VAE Fig. 1, p. 1 (ETTh1) | ✅ | |
| 37 s2 | CRPS measures probabilistic error; lower is better. | (K²VAE, s1) | K²VAE Fig. 1 caption; App. C.3, p. 17 | ✅ | Covered by the figure credit. Covered by the surrounding citation (user decision 22 Oct: not every line is cited). |
| 37 s3 | Compares native probabilistic models with point forecasters given a distributional output. | (K²VAE, s1) | K²VAE Fig. 1 caption | ✅ | Covered by the surrounding citation (user decision 22 Oct: not every line is cited). |
| 37 s4–s7 | Probabilistic models best at short horizons; order reverses; their error rises sharply; point forecasters roughly level. | — | Figure checked | ☑️ | Unchanged. True for TimeGrad and CSDI. GRU MAF rises gradually, not sharply. **Accepted as is by the user (22 Oct)**, was ⚠️. |
| 37 s8 | At long horizons a point forecaster with a distributional output is the stronger competitor. | (K²VAE, s1) | K²VAE Fig. 1 caption ("even worse than point forecasting models") | ✅ | Covered by the surrounding citation (user decision 22 Oct: not every line is cited). |
| 39 | Figure caption. | K²VAE | K²VAE Fig. 1 | ✅ | |
| 41–45 | K²VAE builds on a VAE, a Koopman step and a KalmanNet-style refinement. | K²VAE | K²VAE abstract, p. 1; §1, p. 2 | ✅ | |
| 47 | `--FLAG: … --` | — | — | 📝 | Draft note. **Still present. It will render.** |
| 49 s1–s2 | The Koopman step targets nonlinearity: approximately linear evolution, rolled forward by one linear map. | (K²VAE, s6) | K²VAE §1, p. 2 ("captured by a linear Koopman Operator") | ✅ | **Fixed:** the paragraph is now cited. |
| 49 s3–s4 | KalmanNet targets error accumulation, correcting forecast and uncertainty using what the linear step misses. | (K²VAE, s6) | K²VAE §1, p. 2 ("mitigate the error accumulation"; "integrating the residual nonlinear information as control inputs") | ✅ | |
| 49 s5 | The authors credit stable performance as the horizon grows. | (K²VAE, s6) | K²VAE §4.2, obs. 3, p. 8 | ✅ | |
| 49 s6 | …and a clear advantage on drifting series (statistics change over time). | K²VAE | K²VAE §4.2, obs. 2, p. 8 | ✅ | The gloss of drift is definitional. |
| 49 s7 | Chapter 3 describes both components. | — | — | ➖ | Signposting. |
| 51 | `--FLAG: … --` | — | — | 📝 | Draft note. **Still present.** |
| 53 s1 | K²VAE report it outperforms state-of-the-art at short and long horizons. | K²VAE | K²VAE abstract, p. 1 | ✅ | **Fixed:** citation added. |
| 53 s2–s4 | We test the claim; the two research questions. | — | — | 🛠 | |
| 55 s1 | Our focus is long-term forecasting, the setting K²VAE was designed for. | (K²VAE, s8) | K²VAE §1, p. 2 ("tailored for LPTSF") | ✅ | Covered by the surrounding citation (user decision 22 Oct: not every line is cited). |
| 55 s2 | PatchTST and Koopa get a distributional output; all three use the same code. | — | `baselines/` | 🛠 | |
| 55 s3 | Both baselines are point forecasters of the kind Fig. 1 shows is strongest at long horizons. | — | K²VAE §4.1, p. 7 | ☑️ | Unchanged. PatchTST is in Fig. 1; Koopa is not. **Accepted as is by the user (22 Oct)**, was ⚠️. |
| 55 s4–s6 | Two long-term datasets; the paper claims a short-term advantage too, so two short-term datasets. | (K²VAE, s8) | K²VAE abstract | ✅ / 🛠 | Covered by the surrounding citation (user decision 22 Oct: not every line is cited). |
| 55 s7–s9 | Compare with published results; record gaps; run an ablation. | K²VAE | — | 🛠 | |

### 4.2 Literature Review (L59–71)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 59, 61 | `-- FLAG for Jake … --` | — | — | 📝 | Draft notes. **Still present.** |
| 63 s1–s2 | Classical state-space models; hidden state encodes level, trend and seasonality. | DeepState | DeepState §3, p. 6; §1, p. 1 | ✅ | |
| 63 s3 | ES and ARIMA are the two most widely used approaches. | (Hyndman, s5) | fpp3 Ch. 9 opening ("the two most widely used approaches to time series forecasting") | ✅ | **Now verified against the full chapter text** (`hyndman2021_fpp3_ch9_arima.txt`). |
| 63 s4 | ES, proposed in the late 1950s, describes trend and seasonality. | (Hyndman, s5) | fpp3 Ch. 8 opening ("proposed in the late 1950s"); Ch. 9 opening ("based on a description of the trend and seasonality") | ✅ | Verified against the full text. |
| 63 s5 | ARIMA describes autocorrelations. | Hyndman | fpp3 Ch. 9 opening | ✅ | |
| 63 s6 | Both are state-space models and work well when the structure is understood. | DeepState | DeepState §1, p. 1 | ✅ | |
| 63 s7–s8 | Estimating the hidden state from noisy observations; the KF does this for linear models. | Kalman 1960 | Kalman 1960 abstract, p. 1; Eqs. (16–17, 21), p. 9 | ✅ | |
| 63 s9–s10 | Systems are often nonlinear and models rarely known; EKF and UKF were developed. | (KalmanNet, s11) | KalmanNet §I, p. 1 | ✅ | |
| 63 s11 | Both rely on accurate model knowledge and suffer when it is wrong. | KalmanNet | KalmanNet §I, p. 1 | ✅ | |
| 63 s12–s13 | Classical models are fitted per series and need manual effort. | DeepState | DeepState §1, p. 1 | ✅ | |
| 65 s1–s2 | Deep learning offered an alternative; RNNs and CNNs learn temporal patterns from data. | Koopa | Koopa §1, p. 1; DeepState §1, p. 1 | ✅ | |
| 65 s3–s4 | They learn shared patterns with less effort, but need more data, are harder to interpret, and make smoothness hard to impose. | DeepState | DeepState §1, p. 1 | ✅ | |
| 65 s5 | This prompted work combining deep networks with state-space models. | (DeepState, s4) | DeepState §1, p. 1 ("bridge the gap … fusing SSMs with deep (recurrent) neural networks") | ✅ | Unchanged. Covered by the surrounding citation (user decision 22 Oct: not every line is cited). |
| 65 s6 | The VAE provided a key tool. | (Krishnan, s13) | Krishnan §3, p. 3 | ✅ | Framing, supported by how DKF describes itself. Covered by the surrounding citation (user decision 22 Oct: not every line is cited). |
| 65 s7–s8 | A VAE encodes inputs as distributions, decodes samples, and is trained on a lower bound. | Kingma | Kingma §2.2, Eq. (3), p. 3; §3, p. 5 | ✅ | |
| 65 s9–s10 | DKF brought this to sequential data; its transition and observation models are neural networks. | (Krishnan, s13) | Krishnan §2, p. 2 ("replace all the linear transformations with non-linear transformations parameterized by neural nets") | ✅ | |
| 65 s11 | This nonlinearity makes the posterior over the hidden states intractable, which makes learning difficult. | (Krishnan, s13) | Krishnan §2–3, pp. 2–3 ("the non-linearity makes learning much more challenging, as the posterior distribution … becomes intractable to compute") | ✅ | **Fixed:** the earlier ↔ meaning reversal is resolved, and this is now a close paraphrase. |
| 65 s12–s13 | DKF handles this as a VAE does: an encoder approximates the posterior, trained by maximising the lower bound. | Krishnan | Krishnan §3, p. 3 ("we make use of recently introduced variational autoencoders … to optimize a variational lower bound … a recognition network … approximates the intractable posterior") | ✅ | **Fixed.** |
| 65 s14–s17 | KVAE: linear latent dynamics; a VAE encodes each observation; exact Kalman filtering; an RNN adapts the matrices each step. | Fraccaro | Fraccaro abstract and §1, p. 1; §3.3, p. 4 | ✅ | |
| 65 s18–s19 | DeepState: an RNN outputs per-series linear SSM parameters, giving a forecast distribution. | DeepState | DeepState abstract, p. 1 | ✅ | |
| 65 s20–s22 | KalmanNet keeps the KF structure, learns the gain with an RNN, and needs only partial model knowledge. | KalmanNet | KalmanNet abstract, p. 1; §I, p. 2 | ✅ | |
| 65 s23 | Most depend on RNNs, which Klushyn argue can limit how accurately they learn the dynamics. | Klushyn 2021 | Klushyn §1(iii), p. 1 | ✅ | |
| 67 s1–s2 | RNNs process one step at a time, preventing parallelism; critical for long sequences. | (Vaswani, s5) | Vaswani §1, p. 2 | ✅ | Unchanged. |
| 67 s3–s4 | The transformer removed recurrence; each position attends to every other. | (Vaswani, s5) | Vaswani abstract; §3.2.3, p. 5 | ✅ | |
| 67 s5 | Introduced for machine translation. | Vaswani | Vaswani abstract, p. 1 | ✅ | |
| 67 s6 | Adapted to long-term forecasting; attention cost is quadratic in input length. | (Triformer, s7) | Triformer abstract and §1, p. 1 | ✅ | |
| 67 s7 | Triformer patches the series and applies attention within each patch. | Triformer | Triformer §1, p. 1 | ✅ | |
| 67 s8–s9 | Doubts remained; a simple linear model outperformed transformer forecasters. | (PatchTST) | PatchTST §1, p. 1 (reporting Zeng et al.) | ☑️ | Unchanged. **Secondary citation** (the L59 flag notes this). Primary: Zeng et al. 2023, in K²VAE refs → ⬇️. **Accepted as is by the user (22 Oct)**, was ⚠️. |
| 67 s10–s13 | PatchTST: patches as tokens, channel independence, outperformed earlier transformers at long horizons. | PatchTST | PatchTST abstract and §1, p. 1 | ✅ | |
| 69 s1 | A separate line of work came from dynamical systems. | — | — | ➖ | Signposting. |
| 69 s2 | Koopman introduced his operator in 1931 to describe Hamiltonian systems. | Koopman 1931 | Koopman 1931, p. 315 ("extended in such a way as to include classical Hamiltonian mechanics") | ✅ | **Fixed:** the primary source is now cited and the meaning matches. Bib entry `koopman1931hamiltonian` added. |
| 69 s3 | Later work extended it to more general nonlinear systems. | (Brunton, s4) | Brunton §1, p. 3 (generalised by Koopman and von Neumann in 1932); abstract, p. 1 (modern theory for nonlinear systems) | ✅ | Covered by the citation on s4. |
| 69 s4 | The operator acts on measurements of a system's state. | Brunton | Brunton §1, Eq. (1.5), p. 4; §2.1, p. 10 | ✅ | |
| 69 s5 | These measurements evolve linearly even when the system does not. | (Brunton, s4) | Brunton abstract and §1, p. 2 | ✅ | |
| 69 s6–s7 | Infinite-dimensional, so approximated; DMD became the standard estimator. | Brunton | Brunton §2.3.1, p. 18; §5.1, p. 55 | ✅ | |
| 69 s8–s10 | DMD relies on linear measurements; eDMD adds nonlinear ones; choosing them remains a challenge. | Brunton | Brunton §5 intro and §5.1, p. 55 | ✅ | |
| 69 s11–s12 | Deep learning offered a way forward; neural networks learn the measurement functions, often in an autoencoder with the operator. | (Koopa, s13) | Koopa §2.2, p. 3; Brunton §5.4, pp. 61–62 | ✅ | |
| 69 s13 | Koopman methods were applied to sequence prediction. | Koopa | Koopa §2.2, p. 3 | ✅ | |
| 69 s14–s15 | Real series are non-stationary; changing statistics challenge deep forecasters. | (Koopa, s17) | Koopa abstract, p. 1 | ✅ | |
| 69 s16–s17 | Koopa uses learned Koopman operators, including local per-window operators. | Koopa | Koopa abstract, p. 1; Eq. (10), p. 6 | ✅ | |
| 71 s1 | PatchTST and Koopa are point forecasters. | (K²VAE, s2) | K²VAE §4.1, p. 7 | ✅ | Covered by the surrounding citation (user decision 22 Oct: not every line is cited). |
| 71 s2 | K²VAE note native probabilistic models **mostly excel at** short horizons and often perform poorly on long ones. | K²VAE | K²VAE §1, p. 2 | ✅ | **Fixed:** the meaning now matches the source. |
| 71 s3 | Point forecasters with a distributional output hold up better but were designed for values. | (K²VAE, s2) | K²VAE Fig. 1 (first half); definitional (second half) | ✅ / ➖ | Covered by the surrounding citation (user decision 22 Oct: not every line is cited). |
| 71 s4 | K²VAE brought these lines together in a VAE built for LPTSF. | K²VAE | K²VAE §1, p. 2 | ✅ | |
| 71 s5 | Combines Koopman linearisation, a learned KF, and a transformer passing the residual. | (K²VAE, s6) | K²VAE §3.1–3.1.2, pp. 3–4 | ✅ | |
| 71 s6 | K²VAE report it outperforms both kinds of model at short and long horizons, within ProbTS. | K²VAE | K²VAE §4.1–4.2, pp. 6–8 | ✅ | **Fixed:** citation added. |
| 71 s7 | To our knowledge, no independent implementation has been published. | — | — | 🛠 | Hedged. |
| 75 | Chapter outline. | K²VAE | — | ➖ | Signposting. |

---

## 5. Chapter 2: Preliminaries

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 79 | Chapter intro. | — | — | ➖ | Signposting. |

### 5.1 Koopman Theory (L83–125)

*👤 **Assigned to Kai** (22 Oct). Not re-audited in v3; the rows below are from v1/v2 and the lines are unchanged.*

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 83 | Forecasting is hard because dynamics are noisy, complex and nonlinear, as in x_{k+1} = f(x_k). | — | Brunton §1, Eq. (1.4), p. 4; K²VAE §2, p. 2 | ✅ | Missing cite for the equation. |
| 89 s1–s2 | This is a strictly Markovian assumption; it holds in ideal systems where x_k fully describes the state. | — | — | ➖ | Definition. |
| 89 s3–s5 | Real data is rarely Markovian (hidden variables, shocks, long-range dependencies); forcing a Markov transition turns missing context into noise; this causes compounding error and drift as the horizon grows. | — | — | 🚩 | **No source.** Brunton §5.2, p. 58 links hidden variables to Koopman only through time-delay coordinates. |
| 89 s6 | Koopman linearises by mapping to a higher, potentially infinite-dimensional space where evolution is linear, via a measurement function. | (Brunton) | Brunton abstract and §1, p. 2; Fig. 5.2(b), p. 62 ("lifted to a higher dimension where the evolution is approximately linear") | ✅ | |
| 89 s7 | Expanding dimensionality implicitly encodes historical dependencies, bridging non-Markovian reality and Markovian linear algebra. | (Brunton) | Brunton §5.2, p. 58 (only via time-delay embeddings, which K²VAE does not use) | 🚩 | **Not supported.** The paragraph's single Brunton citation does not back this. |
| 89 s8 | The operator acts on observables of the state, not the state itself. | Brunton | Brunton §1, Eq. (1.5), p. 4; §2.1, p. 10 ("advances measurement functions of the state") | ✅ | |
| 91–93 | ψ(x_{k+1}) = 𝒦 ψ(x_k). | (Brunton) | Brunton Eq. (1.5), p. 4; K²VAE Eq. (1), p. 2 | ✅ | |
| 95 s1 | 𝒦 models evolution linearly in the transformed space, even for a nonlinear system. | — | Brunton abstract, p. 1 | ✅ | Missing cite. |
| 95 s2 | So linear techniques give **more stable and accurate forecasts over longer horizons**. | — | Brunton abstract, p. 1 only says linear representations "enable the prediction, estimation, and control … with standard textbook methods" | 🚩 | **Overclaim.** Koopa "Learning stable operators", p. 9 and App. D.4, p. 19 warn that operators with eigenvalues off the unit circle explode over long horizons. The long-horizon claim is K²VAE's claim about its whole model. |
| 97 s1 | The true operator is infinite-dimensional, so a finite approximation is needed. | (Brunton) | Brunton §2.3.1, p. 18 | ✅ | |
| 97 s2 | Measurement functions are observables that extract properties of the state. | (Brunton) | Brunton §2.1, p. 10 | ✅ | |
| 97 s3 | Manually defining such functions is notoriously difficult. | (Brunton) | Brunton §5, p. 55 ("still a central challenge"); Koopa §3.2, p. 3 ("avoid handcrafting measurement functions") | ✅ | |
| 97 s4 | So a neural network jointly learns ψ and 𝒦. | Brunton | Brunton §5.4, pp. 61–62, Fig. 5.2 | ✅ | In K²VAE only 𝒦_glo is learned. 𝒦_loc is solved in closed form. The sentence is fine at the level of the general method. |
| 97 s5–s6 | The model applies the transform to the patches; linearising makes later state estimation and uncertainty modelling tractable. | — | K²VAE §1, p. 2 ("a 'biased' linear dynamical system easy to describe and model") | ⚠️ | Missing cite. "Mathematically tractable" is stronger than "easy to describe and model". |
| 99–101 | X^{P*} = ψ(X^{P'}). | — | K²VAE Eq. (5), p. 4 | ✅ | Missing cite. |
| 103 s1 | eDMD is used to learn 𝒦 "during training". | Brunton | Brunton §5.1, Eqs. (5.2–5.3), p. 56 | ✅ | "During training" is inaccurate: 𝒦_loc is also solved at inference (`src/koopman.py`). Minor. |
| 103 s2–s4 | Split the token sequence into past and future (shifted) matrices. | — | Brunton Eq. (5.2a), p. 56; K²VAE Eqs. (6–7), p. 4; Koopa Eq. (10), p. 6 (same X_back/X_fore naming) | ✅ | Missing cite. |
| 105–111 | The two matrices. | — | K²VAE Eqs. (6–7), p. 4 | ✅ | |
| 113–117 | 𝒦_loc = X_fore X_back^† via Moore–Penrose, equivalent to least squares. | — | Brunton §3.1, Eq. (3.4), p. 22; Eq. (5.3), p. 56; K²VAE Eq. (8), p. 4 | ✅ | Missing cite. |
| 119 s1 | 𝒦_loc captures the local rule; relying on it alone causes instability and wrong convergence. | (K²VAE) | K²VAE §3.1.2, p. 4; §4.3.1, p. 8 | ✅ | |
| 119 s2 | A global 𝒦_glo is learned across all training sequences. | (K²VAE) | K²VAE §3.1.2, p. 4 ("learnable part … global-shared dynamics") | ✅ | |
| 119 s3 | 𝒦_glo is initialised orthogonal via SVD to stop values exploding early. | (K²VAE, end of paragraph) | Not in K²VAE. `src/koopman.py:30-33`. | 🚩 / 🛠 | **The paragraph-end citation attributes our choice to the paper.** |
| 119 s4–s5 | 𝒦_glo stabilises 𝒦_loc; the combination gives more robust and accurate long-horizon forecasts. | K²VAE | K²VAE §4.3.1 and Table 4, p. 8 ("better performance on both short- and long-term tasks while providing robustness") | ✅ | |
| 121–123 | 𝒦 = 𝒦_loc + 𝒦_glo. | (K²VAE) | K²VAE §3.1.2, p. 4 | ✅ | |
| 125 s1 | 𝒦 forecasts with greater stability and accuracy "without the compounding error that arises from nonlinear dynamics", but a bias remains in the residual. | — | Bias: K²VAE §1, p. 2; §3.1.2, p. 4 ("biased linear system"). No-compounding claim: none. | 🚩 / ✅ | "Without compounding error" is unsupported, and contradicts L368, which says error still grows linearly. The bias half is ✅. |
| 125 s2 | The Integrator and KalmanNet are added to fix this. | — | K²VAE §3.1.2, p. 4 | ✅ | Missing cite. |

### 5.2 Transformer Encoder (L129–157)

*Re-audited 22 Oct (v3) after the user's edits.*

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 129 s1 | The transformer was introduced for machine translation. | (Vaswani, s2) | Vaswani abstract, p. 1 | ✅ | |
| 129 s2 | Self-attention weighs the importance of different parts of the input. | Vaswani | Vaswani §2, p. 2; §3.2, p. 3 | ✅ | |
| 129 s3 | It has since become widely used in NLP and applied to time-series forecasting. | (PatchTST, s4) | PatchTST §1, p. 1 ("great success on … natural language processing … and more recently time series") | ✅ | **Fixed:** the earlier ↔ (Vaswani for "widely used") is resolved. |
| 129 s4 | Because attention learns the connections between elements, it suits sequential data such as time series. | PatchTST | PatchTST §1, p. 1 ("automatically learn the connections between elements in a sequence, thus becomes ideal for sequential modeling tasks") | ✅ | **Fixed:** the "complex and nonlinear" gloss was removed. |
| 131–134 | Q, K, V are linear projections of X. | Vaswani | Vaswani §3.2.2, p. 4 | ✅ | Unchanged. |
| 136 s1 | W^Q, W^K, W^V are learnable. | (Vaswani, s5) | Vaswani §3.2.2 | ✅ | |
| 136 s2 | Each token takes a weighted average of V, by query–key similarity with **all tokens**. | (Vaswani, s5) | Vaswani §3.2, p. 3 | ✅ | **Fixed** ("all other tokens" → "all tokens"). |
| 136 s3–s4 | Scaled dot-product attention; relates tokens regardless of position. | (Vaswani, s5) | Vaswani §3.2.1, p. 4; §1, p. 2 | ✅ | |
| 136 s5 | Attention output (introduces the equation). | Vaswani | Vaswani §3.2.1, Eq. (1), p. 4 | ✅ | **Fixed:** citation added. |
| 138–139 | Attention equation. | (Vaswani, L136) | Vaswani Eq. (1), p. 4 | ✅ | |
| 141 s1–s2 | Multi-head attention jointly evaluates different representation subspaces. | (Vaswani, s4) | Vaswani §3.2.2, p. 5 | ✅ | Unchanged. |
| 141 s3–s4 | Heads compute separately; outputs concatenated and projected. | Vaswani | Vaswani §3.2.2, pp. 4–5 | ✅ | Unchanged. |
| 143–145 | MultiHead equation; W^O projects back to the embedding space. | (Vaswani, L141) | Vaswani §3.2.2, p. 5 | ✅ | |
| 147 | Vaswani pass the attention output through a position-wise FFN (two linear maps, ReLU, per position). | Vaswani | Vaswani §3.3, Eq. (2), p. 5 | ✅ | |
| 149–151 | FFN equation. | (Vaswani, L147) | Vaswani Eq. (2), p. 5 | ✅ | |
| 153 s1 | W and b are learnable. | (Vaswani, L147) | Vaswani §3.3 | ✅ | |
| 153 s2 | FFN captures interactions within a token; attention captures dependencies between tokens. | — | Vaswani §3.3, p. 5 ("applied to each position separately and identically") | ☑️ | Unchanged. Our interpretation built on Vaswani's description. **Accepted as is by the user (22 Oct)**, was ⚠️. |
| 155 | Attention and FFN are wrapped in residual connections and layer norm. | Vaswani | Vaswani §3.1, p. 3 ("LayerNorm(x + Sublayer(x))") | ✅ | **Fixed:** the unsourced "stabilise training" claim was removed and a citation added. |
| 157 s1–s2 | Attention is order-agnostic, so order is injected; the original uses fixed sinusoidal encodings. | (Vaswani, s3) | Vaswani §3.5, p. 6 | ✅ | |
| 157 s3 | Vaswani found learned embeddings performed almost identically. | Vaswani | Vaswani §3.5, p. 6; Table 3 row (E), p. 9 | ✅ | |
| 157 s4 | Stacking layers without masking or cross-attention gives the encoder-only variant. | (Vaswani, s5) | Vaswani §3.1, §3.2.3, pp. 3–5 | ✅ | |
| 157 s5 | It is a bidirectional token mixer capturing dependencies across the whole sequence. | Vaswani | Vaswani §3.2.3, p. 5 ("Each position in the encoder can attend to all positions") | ✅ | **Fixed** ("local and global" gloss removed). |
| 157 s6–s8 | K²VAE's Integrator is a transformer encoder on the residual; its output is the Kalman control input. | K²VAE | K²VAE §3.1.2, Eqs. (12–13), p. 4 | ✅ | |

### 5.3 Kalman Filter (L161–207)

*Re-audited 22 Oct (v3). `welch1995` is now cited at L161, L177 and L205, so the surrounding equations are covered by those citations.*

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 161 s1–s2 | The KF is a recursive estimator from noisy observations; linear state-space model alternating process and observation models. | Kalman 1960; Welch | Kalman 1960 abstract, p. 1; Eqs. (16–17), p. 9. Welch abstract, p. 1; §1, p. 4. | ✅ | **Fixed:** Welch added for the alternation. |
| 163–166 | Process model with Bu_k and w ~ 𝒩(0,Q). | (Welch, L161/L177) | Welch §1, Eqs. (1.1, 1.3), p. 2; K²VAE Eq. (14), p. 4 | ✅ | Welch indexes u_{k−1}; the thesis follows K²VAE's u_k. |
| 168 | Meanings of x, A, B, u, w. | (Welch, L161/L177) | Welch §1, p. 2 | ✅ | |
| 170–175 | Observation model and meanings. | (Welch, L177) | Welch Eqs. (1.2, 1.4), p. 2 | ✅ | |
| 177 | Following Welch, each step uses the models in turn: predict, then update. | Welch | Welch §1, p. 4; Fig. 1-1, p. 5 | ✅ | **Fixed:** citation added. |
| 179–189 | Predict-step equations and meanings. | (Welch, L177/L205) | Welch Table 1-1, Eqs. (1.9–1.10), p. 5 | ✅ | |
| 191–194 | Gain balances prediction vs observation; gain equation. | (Welch, L205) | Welch Table 1-2, Eq. (1.11), p. 5; §1, p. 3 | ✅ | |
| 196 | Gain weighs P̂ against R; H maps state to observation space. | (Welch, L205) | Welch §1, p. 3 | ✅ | |
| 197–203 | Update equations. | (Welch, L205) | Welch Eqs. (1.12–1.13), p. 5 | ✅ | |
| 205 s1–s7 | Innovation; scalar-case gain interpretation; P_k update reflects new information. | Welch | Welch §1, Eq. (1.7), p. 3 (innovation; R→0 gives K→H⁻¹; P⁻→0 gives K→0); Eq. (1.13), p. 5 | ✅ | **Fixed:** citation added at the paragraph end. |
| 207 s1 | The standard KF assumes linearity. | (KalmanNet, s2) | KalmanNet §I, p. 1 | ✅ | |
| 207 s2 | As KalmanNet note, EKF and UKF extend it to nonlinear dynamics. | KalmanNet | KalmanNet §I, p. 1 | ✅ | |
| 207 s3 | KalmanNet: an RNN learns the gain. | KalmanNet | KalmanNet abstract, p. 1; §I, p. 2 | ✅ | |
| 207 s4–s5 | Here nonlinearity is handled by Koopman; a KF refines in the latent space. | K²VAE | K²VAE §1, p. 2; §3.1.2, p. 4 | ✅ | |
| 207 s6 | The K²VAE paper also calls its filter a KalmanNet, but it differs from Revach's model. | KalmanNet | KalmanNet abstract, p. 1 (learns the gain); K²VAE §3.1.2, p. 4 | ✅ | |
| 207 s7 | Rather than learning the gain, it treats A, B, H, Q and R as learnable. | K²VAE | K²VAE §3.1.2, p. 4 ("all the matrices are learnable") | ✅ | |
| 207 s8 | This lets the filter adapt to learned latent dynamics. | (K²VAE, s7) | K²VAE §3.1.2, p. 4 ("model and refine the uncertainty adaptively") | ✅ | |

### 5.4 Variational Autoencoders (L211–259)

*Re-audited 22 Oct (v3, and L217/L243 again in v4). The CVAE part is now generic (Sohn). The K²VAE-specific note moved to the loss-function section (L456). L259–261 were merged into L259.*

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 211 | An AE reconstructs its input rather than predicting a target. | (Hinton, L213) | Hinton abstract, p. 2 | ✅ | |
| 213 s1–s2 | The encoder narrows to a code; the decoder reconstructs. | (Hinton, s4) | Hinton abstract, p. 2; Fig. 1, p. 3 | ✅ | |
| 213 s3–s4 | A narrower latent layer forces a compact encoding. | Hinton | Hinton abstract, p. 2 ("small central layer … low-dimensional codes") | ✅ | |
| 215 | Figure, adapted from Riebesell. | Riebesell | — | 🖼 | |
| 217 s1–s2 | AEs minimise reconstruction error; the latent learns a compact representation. | (Hinton, L213; Kingma, s3) | Hinton, p. 3; Kingma §4, p. 6 ("the negative reconstrution error") | ✅ | |
| 217 s3 | Kingma note that reconstruction alone is not enough to make this representation useful. | Kingma | Kingma §4 (Related work), p. 6: "it is well known that this reconstruction criterion is in itself not sufficient for learning useful representations" | ✅ | **New and verified.** Kingma attributes this to Bengio et al. (BCV13). |
| 217 s4–s5 | "For example, the latent space may contain **disjoint clusters** … **regions** that do not correspond to valid data." | (Ghosh, s7) | **Not in Ghosh** (no mention of clusters or empty regions). | ⚠️ | The citation on s7 does not cover these specifics. Either drop "for example …" or find a source. *Still unchanged in v4 (22 Oct).* |
| 217 s6–s7 | It has no structure, so there is **no direct way to sample** from it. | Ghosh | Ghosh §4, pp. 5–6 ("we lose the simple mechanism provided by p(z) to sample from Z") | ✅ | **Fixed (v4):** the wording now matches Ghosh. |
| 217 s8–s9 | The decoder is trained only on encoded points, so nearby points need not decode meaningfully. | (Ghosh, s7) | Ghosh §3, p. 4 (decoder regularisation is "motivated by the goal to learn a smooth latent space … small variations in Z lead to reconstructions … that vary only slightly") | ☑️ | Implied by Ghosh (the reason regularisation is needed), not stated about plain AEs. Acceptable, given the user's surrounding-support rule. **Overridden by the user (22 Oct): accepted as is**, was ⚠️. |
| 219 s1–s2 | A VAE takes a probabilistic approach that structures the latent space and allows sampling new data. | Doersch | Doersch §2, p. 5 ("samples of z can be drawn from a simple distribution, i.e., N(0, I)"); Fig. 1, p. 4 ("it is possible to sample from the model without any input") | ✅ | **Fixed:** the earlier 🚩 (framing attributed to Kingma) is resolved. |
| 219 s3–s4 | The encoder outputs μ(x) and σ(x), defining a Gaussian approximate posterior. | Kingma | Kingma §3, Eq. (9), p. 5 | ✅ | |
| 221–223 | ℚ(z∣x) = 𝒩(μ, diag σ²). | (Kingma, L219) | Kingma Eq. (9), p. 5 | ✅ | |
| 225 s1 | It approximates the intractable true posterior. | Kingma | Kingma §2.1, p. 2 | ✅ | Unchanged. |
| 225 s2–s3 | A sample is drawn; the decoder maps it back. | (Kingma, s1) | Kingma §3, p. 5 | ✅ | |
| 225 s4–s6 | Figure description. | — | — | ➖ | |
| 227 | Figure, adapted from Riebesell. | Riebesell | — | 🖼 | |
| 229 s1–s2 | log ℙ(x) is intractable because it integrates over z. | Kingma | Kingma §2.1, p. 2 | ✅ | |
| 229 s3–s4 | Maximise the ELBO; minimise its negative, which has two terms. | Kingma | Kingma §2.2, Eq. (3), p. 3 | ✅ | |
| 231–233 | Loss equation with prior 𝒩(0, I). | (Kingma, L229) | Kingma Eq. (3); §3, p. 5 | ✅ | |
| 235 s1 | The first term is the AE's reconstruction loss. | (Kingma, s6) | Kingma §2.3, p. 4 | ✅ | |
| 235 s2 | A fixed-variance Gaussian decoder gives NLL ∝ squared distance. | Doersch | Doersch §2, p. 7 | ✅ | |
| 235 s3–s5 | The KL from a pre-chosen prior, "usually a standard normal". | (Kingma, s6) | Kingma §3, p. 5 | ☑️ | Unchanged. "Usually" generalises from Kingma's example. Minor. **Accepted as is by the user (22 Oct)**, was ⚠️. |
| 235 s6 | KL is a regulariser keeping the posterior near the prior. | Kingma | Kingma §2.3, p. 4 | ✅ | |
| 235 s7 | Closed-form KL for Gaussians. | Kingma | Kingma §3, Eq. (10), p. 5; App. B | ✅ | |
| 237–239 | KL equation. | (Kingma, L235) | Kingma Eq. (10), p. 5 | ✅ | |
| 241 | Trade-off derivation. | — | Follows from Eq. (10) | ➖ | |
| 243 s1 | This regularisation addresses the lack of structure in a standard AE. | (Kingma, s2) | Kingma §2.3, p. 4 (KL as a regulariser) | ✅ | Framing sentence. Rewritten in v4. |
| 243 s2 | The KL term pulls every input's posterior towards the same prior. | Kingma | Kingma §2.3, p. 4 ("encouraging the approximate posterior to be close to the prior p(z)") | ✅ | **Fixed (v4):** the KL mechanism is now cited to Kingma, not Ghosh. |
| 243 s3–s4 | So encodings of different groups are kept close and overlap, and isolated clusters are less likely. | (Kingma, s2) | Kingma says the KL pulls each posterior to the prior. It does not discuss overlap or clusters. | ☑️ | Our inference from s2 (reasonable, hedged with "less likely"). Not stated by Kingma. **Overridden by the user (22 Oct): accepted as is**, was ⚠️. |
| 243 s5–s7 | Sampling has a second effect: z lands near but not at μ(x), and the decoder learns to reconstruct from these samples. | (Ghosh, s8) | Ghosh §3, p. 4 ("a VAE can be seen as a deterministic autoencoder where (Gaussian) noise is added to the decoder's input … a key factor in having a regularized decoder") | ✅ | **Fixed (v4):** attributed as Ghosh frames it. |
| 243 s8 | Points near an encoding are therefore more likely to decode to plausible outputs. | Ghosh | Ghosh §3, p. 4 ("small variations in Z lead to reconstructions by D that vary only slightly") | ✅ | |
| 245–249 | Reparameterisation trick and equation. | Kingma | Kingma §2.4, p. 4; Eq. (10), p. 5 | ✅ | Unchanged. |
| 251 s1–s4 | Forecasting models Y given X; we want a distribution; uncertainty matters. | — | — | ➖ | Framing. |
| 251 s5–s6 | A point forecaster trained on distance predicts between plausible futures. | Doersch | Doersch §3, p. 15 | ✅ | |
| 251 s7 | Sohn introduced the CVAE, conditioning the generative process on the input. | Sohn | Sohn abstract, p. 1; §4, p. 3 | ✅ | **Fixed:** primary CVAE source now cited. Bib `sohn2015learning` added. |
| 251 s8 | It learns ℙ(Y∣X) that can be sampled. | (Sohn, s9) | Sohn §4, p. 3 | ✅ | |
| 251 s9 | In training the encoder sees context and target; minimise the negative conditional ELBO. | Sohn | Sohn §4, Eqs. (4–5), p. 3 (recognition network q(z∣x,y)) | ✅ | |
| 253–255 | ℒ = −𝔼_{ℚ(Z∣Y,X)}[log ℙ(Y∣Z,X)] + KL(ℚ(Z∣Y,X) ‖ ℙ(Z∣X)). | (Sohn, L251) | Sohn Eq. (4), p. 3 (sign-flipped) | ✅ | **Now the general CVAE form.** It resolves the deferred memory item. |
| 257 s1–s3 | Same two-term structure, conditioned on context; NLL term. | — | — | ➖ | |
| 257 s4 | The KL is between the posterior and a prior ℙ(Z∣X). | (Sohn, s5) | Sohn Eq. (4), p. 3 | ✅ | |
| 257 s5 | The prior may depend on context but is often fixed to 𝒩(0, I). | Sohn; Doersch | Sohn §4, p. 3 ("can be easily relaxed … p(z∣x) = p(z)"); Doersch §3, p. 16 ("P(z∣X) is still N(0, I)") | ✅ | |
| 259 s1–s4 | KoopmanNet, Integrator and KalmanNet form the encoder; the decoder is the inverse measurement function; this gives forecasts with uncertainty. | K²VAE | K²VAE §3.1, p. 3 | ✅ | Merged from old L259–261. |

---

## 6. Chapter 3: K²VAE

### 6.1 Chapter intro and Model pipeline (L263–273)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 263 | Chapter intro. | — | — | ➖ | |
| 267 | Split into train/val/test; the figure gives an overview. | — | — | 🛠 | |
| 269 | Overview figure. | — | — | 🖼 | Our figure. |
| 271 s1 | Takes past observations and gives a probabilistic forecast. | (K²VAE, s13) | K²VAE §3.1, p. 3 | ✅ | |
| 271 s2–s3 | In our implementation, RevIN normalises each window first. | — | `src/k2vae.py:97` | 🛠 | Now explicitly labelled as ours. |
| 271 s4–s12 | Patches → tokens → Koopman linear forecast X̂_H → residual → Integrator U → Kalman combines → Z′, P; the three components are the encoder; sample Z. | (K²VAE, s13) | K²VAE §3.1, p. 3; Figs. 2–3, pp. 3–4 | ✅ | **Fixed (v5).** Paragraph now cited. |
| 271 s13 | The decoder maps the sample to μ̂_Y and σ̂_Y. | K²VAE | K²VAE §3.1.3, Eq. (24), p. 5 | ✅ | |
| 271 s14–s15 | RevIN is reversed to the standardised scale; the result is a distribution over futures. | — | `src/k2vae.py:114-138` | 🛠 | |
| 273 | Signposting. | — | — | ➖ | |

### 6.2 Pre-processing (L277–322)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 277 s1 | We apply the pipeline to all datasets. | — | — | 🛠 | |
| 277 s2 | K²VAE treat PTSF as a conditional generative task. | K²VAE | K²VAE §2, p. 3 ("PTSF can be treated as a conditional generative task") | ✅ | **Fixed (v5).** |
| 279–289 | X ∈ ℝ^{N×T}; Y ∈ ℝ^{N×L}; model P(Y∣X); N, T, L defined. | (K²VAE, L277) | K²VAE §2, p. 3 | ✅ | The paper writes the horizon as ending at x̂_L, which is a typo. The thesis's x_{T+L} is correct. Covered by the surrounding citation (user rule, 22 Oct). |
| 291 | Chronological split; standardise on train statistics; apply the same values to val/test. | — | `src/preprocessing.py:35-55` | 🛠 | Our protocol. It differs from ProbTS, so do not cite ProbTS for it. |
| 293 | Three scales (original, standardised, RevIN-normalised); outputs on the standardised scale; NMAE reverses standardisation. | — | `src/run.py:94-96`; `src/k2vae.py:114-138` | 🛠 ✓ | Matches code. |
| 295–302 | Sliding windows, offsets, window count length − T − L + 1. | — | `src/preprocessing.py` (`swDataset`) | 🛠 / ➖ | Formula correct. |
| 304–308 | n non-overlapping patches of size s, s = T/n. | K²VAE | K²VAE §3.1.1, Eq. (3), p. 3 | ✅ | **Fixed (v5).** |
| 310 s1–s2 | A patch holds all variables over s steps; windows overlap but patches are disjoint. | (K²VAE, L304) | K²VAE §3.1.1, p. 3 | ✅ / ➖ | Covered by the surrounding citation (user rule, 22 Oct). |
| 310 s3–s4 | T must be divisible by s; m = L/s. | (K²VAE, L304) | K²VAE §3.1.2, p. 4 ("m = L/s") | ✅ | Covered by the surrounding citation (user rule, 22 Oct). |
| 310 s5–s9 | m counts latent tokens; Y kept raw; both conditions checked at load time. | — | `src/CLI.py:71-77` | 🛠 ✓ | |
| 312–316 | Flatten each patch to N·s, then one shared linear projection to d. | (K²VAE, L318) | K²VAE §3.1.1, Eq. (4), p. 3 | ✅ | Covered by the surrounding citation (user rule, 22 Oct). |
| 318 s1–s2 | Flattening across variables is deliberate; channel-independent models project each variable separately; multivariate tokens model cross-variable interaction. | K²VAE | K²VAE §3.1.1, p. 3. Channel independence: PatchTST §1, p. 2. | ✅ | |
| 318 s3 | The projection is learned jointly and only sees the training split. | — | — | 🛠 | |
| 320 | Patching and embedding happen inside the model, after RevIN. | — | `src/k2vae.py:97-100` | 🛠 ✓ | |
| 322 | Batch size fixed at 32 following K²VAE. | K²VAE | K²VAE App. C.4, p. 18 ("the batch size is set to 32"); `src/CLI.py:56` | ✅ | **Fixed (v5).** |

### 6.3 RevIN (L326–352)

*👤 **Assigned to Kai** (22 Oct).*

The RevIN paper PDF is **not in Sources** (⬇️). Implementation details below were confirmed against the official code (`ts-kim/RevIN`, read on 14 Oct). Rows that need the paper itself stay ⚠️ or ⬇️.

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 326 s1 | Real data is often non-stationary: local mean and variance shift over time. | — | RevIN README abstract (official repo); Koopa abstract, p. 1; PatchTST §3.1, p. 5 | ✅ | Missing cite. |
| 326 s2–s3 | Global standardisation fails to mitigate localised shift; this leads to prediction drift. | — | RevIN paper (not read) | ⬇️ | Cannot verify without the RevIN PDF. |
| 326 s4–s7 | Scale entanglement: mixed magnitudes complicate modelling; a single variance is a compromise. | — | — | 🚩 / 🛠 | Our reasoning, stated as fact. No source. |
| 326 s8 | RevIN, proposed by Kim et al., is integrated. | Kim | RevIN README; PatchTST §3.1, p. 5 and Koopa ref [16] confirm the attribution | ⬇️ | PDF needed. **The bib entry's author list is wrong** (see Section 3). |
| 328–332 | Per-variable instance mean and std, with ε inside the square root. | Kim | Official RevIN code (`_get_statistics`); our `src/revIN.py:64-66` | ⚠️ | Matches both codes. Paper equation numbers unverified. |
| 334–338 | Normalise, then scale and shift with γ_j, b_j. | — | Official RevIN code (`_normalize`); `src/revIN.py` | ⚠️ | Code-confirmed. |
| 340 s1 | γ and b are learnable, initialised to 1 and 0. | — | Official RevIN `_init_params`; `src/revIN.py:31-34` | ⚠️ | Code-confirmed. |
| 340 s2–s5 | Normalising strips baseline and amplitude; affine parameters let the model partly undo it when magnitude is informative. | — | RevIN paper (not read) | ⬇️ / 🚩 | Rationale unverified. Our interpretation unless the paper says it. |
| 342–346 | Inverse transform: (Ỹ − b)/(γ + ε²) · σ + μ. | — | Official RevIN code has `/(affine_weight + eps*eps)`. **Our code** (`src/revIN.py:96,111-114`) divides by a clamped weight with \|γ\| ≥ 0.1 and **no ε²**. | ↔ | **The equation describes the official RevIN code, not ours.** σ is also mapped back with \|γ\| (`denormalize_sigma`). |
| 348 s1 | Integrating RevIN required structural deviations to prevent collapse and leakage. | — | — | 🛠 | |
| 348 s2 | "Standard implementations apply patchification during data loading." | — | **Contradicted:** PatchTST §3.1, p. 5 ("we normalize each x(i) before patching") | 🚩 | If you mean the official K²VAE/ProbTS pipeline, name it. |
| 348 s3–s8 | We patch after RevIN inside the model; RevIN is a learnable module; statistics come from context only; the horizon uses context statistics. | — | `src/k2vae.py:97-100`; RevIN README ("remove and restore the statistical information of a time-series instance") | 🛠 ✓ | |
| 350 s1–s2 | We adapted RevIN; "in standard configurations" the variance head works on the standardised scale without per-window scaling. | — | — | 🚩 | "Standard configurations" is not identified or sourced. Name the baseline being compared against. |
| 350 s3 | Under mixed scales, the variance collapses toward the dominant scale and the NLL explodes at evaluation. | — | — | 🛠 | Our development observation. State it as observed. |
| 350 s4–s6 | Instance-rescaled variance decoding: σ scaled by σ_X before the floor. | — | `src/k2vae.py:124-138` | 🛠 ✓ | |
| 352 | Reconstruction MSE scaled by detached σ_X; NLL on the standardised scale; then patch and embed. | — | `src/train.py:80-92,163-168` | 🛠 ✓ | |

### 6.4 The Koopman Network (L356–375)

*👤 **Assigned to Kai** (22 Oct). Not re-audited in v5.*

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 356 s1 | RNNs and autoregressive diffusion and flow models predict iteratively. | — | K²VAE reference titles: Rasul 2021a "*Autoregressive* denoising diffusion …", Rasul 2021b "… conditioned normalizing flows"; Salinas 2020 DeepAR (autoregressive RNN). Not in Sources. | ⬇️ | Much improved from the earlier "diffusion and flow models" wording. Needs a source. |
| 356 s2–s3 | Predictions are fed back, so early errors distort later inputs and "compound nonlinearly". | — | K²VAE §1, p. 2 ("remarkable error accumulation") | ⚠️ | Accumulation is supported. The mechanism and "nonlinearly" are ours. |
| 356 s4 | The Koopman network bypasses the nonlinear feedback loop. | — | K²VAE §5.1, p. 9 ("autoregressively models the time series in a linear dynamical system") | ✅ | Now consistent with the paper. |
| 356 s5–s6 | Maps to a higher-dimensional space with approximately linear dynamics; steps forward by matrix multiplication. | — | Brunton Fig. 5.2(b), p. 62; K²VAE Eq. (11), p. 4 | ✅ | Missing cite. |
| 358 s1–s2 | ψ is an MLP with dropout. | — | K²VAE §3.1.2, p. 4 ("learnable MLP-based network"); dropout: `src/koopman.py:21-26` | ✅ / 🛠 | |
| 358 s3–s4 | ψ gives X^{P*}; find 𝒦 with x*_{t+1} ≈ 𝒦x*_t. | — | K²VAE Eq. (5), p. 4 | ✅ | |
| 360 s1 | 𝒦_loc is computed "for each batch" by eDMD. | — | K²VAE Eqs. (6–8), p. 4; `src/koopman.py:63-100` | ⚠️ | The code solves one operator **per window** (batched shape B×d×d), not one per batch. Wording. |
| 360 s2 | X_back and X_fore partition. | — | K²VAE Eqs. (6–7) | ✅ | |
| 360 s3 | Short windows "frequently" give an underdetermined system. | — | — | 🛠 | With our configs it is **always** underdetermined: ETTh1 has n − 1 = 3 transitions vs d = 128; Exchange has 2 vs 32. "Frequently" understates it. |
| 360 s4–366 | We solve ridge least squares instead. | — | `src/koopman.py:79-100` | 🛠 ✓ | Our deviation. No ridge-DMD source in the chain. Fine as our choice. |
| 366 s1 | Ridge keeps 𝒦_loc bounded. | — | — | 🛠 | |
| 366 s2–s3 | The local window alone is unstable across batches; 𝒦_glo is learnable and shared. | — | K²VAE §3.1.2, p. 4; §4.3.1, p. 8 | ✅ | Missing cite. |
| 366 s4 | Orthogonal SVD initialisation to prevent early gradient explosions. | — | `src/koopman.py:30-33` | 🛠 ✓ | Correctly uncited here. |
| 366 s5 | The final operator is the sum. | — | K²VAE §3.1.2 | ✅ | |
| 368 s1 | Spectral norm clamped to ≤ 1. | — | `src/koopman.py:12,113-115` (ord = 2, max = 1.0) | 🛠 ✓ | Optional motivation: Koopa "Learning stable operators", p. 9; App. D.4, p. 19. |
| 368 s2 | Identity fallback on NaN. | — | `src/koopman.py:117-120` | 🛠 ✓ | |
| 368 s3 | Reconstruct X̂_C and forecast X̂_H. | — | K²VAE Eqs. (9–11), p. 4 | ✅ | |
| 368 s4 | "The forecasting phase isolates the final state of the context window, z₀ = x_n*, and projects it forward." | — | **Our code** (`src/koopman.py:121-138`) starts from the **first** token x₁* and runs n reconstruction steps, so forecast step 1 = 𝒦ⁿx₁*. This **matches K²VAE Eq. (11)** (x̂ᴴ_i = 𝒦^{i+n−1}x₁*). z₀ = x_n* is the **Kalman** initial state (K²VAE Eq. 15; `src/k2vae.py:109`). | ❌ | **Factually wrong about our own code.** It conflates the Koopman rollout with the Kalman z₀. *Correction to the 14 Oct audit, which called this "an implementation difference" without checking the code.* |
| 368 s5–s7 | In theory matrix powers; we loop z_t = 𝒦z_{t−1}; each step reuses the same linear matrix. | — | K²VAE Eq. (11); `src/koopman.py:128-138` | ✅ / 🛠 | Rewrite with the start state fixed (𝒦^t applied to x₁*). |
| 368 s8–s10 | Breaks the nonlinear loop; the clamp bounds the rollout; error still grows linearly. | — | — | 🛠 | Our reasoning. Hedged appropriately. |
| 370–375 | X^Res = X^{P*} − X̂_C; it feeds the Integrator. | — | K²VAE Eq. (12), p. 4; `src/k2vae.py:104` | ✅ | Missing cite. |

### 6.5 The Integrator (L379–387)

*Re-audited 22 Oct (v5). Sections 6.1, 6.2 (changed lines) and 6.5–6.8 were re-checked after the user's citation and fix pass.*

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 379 s1–s3 | 𝒦 is linear, so it misses nonlinear behaviour; the residual isolates it. | (K²VAE, s5) | K²VAE §3.1.2, p. 4 ("biased linear system"; residual Eq. 12) | ✅ | |
| 379 s4 | K²VAE treats the residuals as nonlinear information to reuse, not noise to discard. | (K²VAE, s5) | K²VAE §3.1.2, p. 4 ("we first fully reuse the nonlinear residual through the Integrator"); §1, p. 2 ("integrating the residual nonlinear information as control inputs") | ✅ | **Fixed (v5).** The earlier 🚩 ("sequential patterns" as fact) is resolved. |
| 379 s5 | K²VAE uses the Integrator to turn this into a correction sequence. | K²VAE | K²VAE §3.1.2, Eq. (13), p. 4 | ✅ | |
| 381 s1 | K²VAE implement the Integrator as an encoder-only transformer. | K²VAE | K²VAE §3.1.2, p. 4 ("Encoder-Only Vanilla Transformer") | ✅ | **Fixed (v5).** The design is now attributed to the paper, without our "because". |
| 381 s2 | Self-attention connects every pair of time steps directly, easing long-range learning. | Vaswani | Vaswani §4, p. 6 ("The shorter these paths between any combination of positions … the easier it is to learn long-range dependencies") | ✅ | **Fixed (v5).** Replaces the unsupported "standard NN" claim. |
| 381 s3 | So the Integrator can relate early deviations to later errors. | (Vaswani, s2) | Vaswani §4, p. 6 | ✅ | Application of s2, hedged with "might". |
| 381 s4–385 | Outputs control inputs U over the horizon (equation). | (K²VAE, s1) | K²VAE Eq. (13), p. 4 | ✅ | |
| 387 | Three stages; no positional encoding; the head recovers order; U goes to the Kalman network. | — | `src/integrator.py:33-62`. The official K²VAE Integrator also has no positional encoding (`auxiliarynet.py`, checked 14 Oct). | 🛠 ✓ | |

### 6.6 The Kalman Network (L391–422)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 391 s1–s9 | Intuition: two sources (X̂_H as measurement, own prediction Ẑ plus U), weighted by certainty, giving a refined Z and its uncertainty. | K²VAE; Welch | K²VAE §1, p. 2 ("fuses observations from multiple sensors"); §3.1.2, p. 4; Welch §1, p. 3 (gain limits) | ✅ | **Fixed (v5).** |
| 393 s1–s3 | A learnable KF; A, B, H, Q, R trained by backprop. | K²VAE | K²VAE §3.1.2, p. 4 | ✅ | |
| 393 s4–s6 | X̂_H is the measurement; X̂_H and U are inputs; outputs Z′ and P. | (K²VAE, s7) | K²VAE §3.1.2, p. 4 ("we treat the prediction X̂_H as the prior observation in Update Step (20)") | ✅ | |
| 393 s7 | z₀ = embedding of the last RevIN-normalised context patch. | K²VAE | K²VAE Eq. (15), p. 4 (z₀ = x_n*); `src/k2vae.py:109` | ✅ | **Fixed (v5).** |
| 393 s8 | The paper initialises Q and R as identity; our implementation does the same for P, A, B and H. | (K²VAE, s7) | K²VAE, p. 5 ("initialize the covariance matrices Q and R as identity matrices"); `src/kalman.py:16-24,123` | ✅ / 🛠 ✓ | **Fixed (v6):** paper and our choice now separated. |
| 395 s1–s7 | Predict with U as control; gain; update with innovation X̂_H − HẐ; P updated by the "dual form" then symmetrised. | K²VAE | K²VAE Eqs. (17–21, 28–29), p. 5 (Thm. 3.1 names P^dual) | ✅ | **Fixed (v5).** "Dual form" is the paper's own name. |
| 395 s8 | Both are described below. | — | — | ➖ | |
| 397 s1 | Repeated over m steps. | (K²VAE, s2) | K²VAE, p. 5 ("conduct the Prediction Step and Update Step iteratively") | ✅ | |
| 397 s2 | To use the Integrator's correction fully, K²VAE add U back by a skip connection: Z′ = Z + U. | K²VAE | K²VAE Eq. (22), p. 5 ("To fully utilize the ability of the Integrator, we make a skip connection") | ✅ | **Fixed (v5).** Now credited to the paper, with the paper's reason. |
| 397 s3 | Without it, the model relies on the Kalman network's linear fit, which struggles to separate nonlinear components early in training. | (K²VAE, s4) | K²VAE §4.3.2, p. 8 ("'w/o skip connection' completely depends on the linear fitting ability of the KalmanNet, which is hard to disentangle the nonlinear components in the early stages of training") | ✅ | **Fixed (v5).** The earlier ↔ (different rationale) is resolved. |
| 397 s4 | As 𝒦 improves, U → 0 and Z′ → Z. | K²VAE | K²VAE, p. 5 ("causing U → 0"); Thm. 3.2 | ✅ | |
| 399 | Errors must not break PSD, else a runtime error stops training. | — | `src/train.py:156` (comment on the Cholesky failure) | 🛠 | |
| 401–404 | Q = L_Q L_Qᵀ, R = L_R L_Rᵀ. | K²VAE | K²VAE, p. 5 | ✅ | |
| 406 s1 | Any matrix built as L Lᵀ is positive semi-definite. | — | — | ➖ | Standard linear algebra. **Fixed (v5):** the unsourced "Cholesky decomposition" name was removed. |
| 406 s2 | L_Q and L_R are each a single learnable matrix shared across all time steps. | — | `src/kalman.py:23-24` | 🛠 ✓ | **Fixed (v5):** the earlier ❌ ("at each time step") is corrected. |
| 406 s3 | So Q and R contain no subtraction and stay PSD. | (K²VAE, L401–404) | K²VAE, p. 5 ("keep the positive definiteness") | ✅ | Covered by the surrounding citation (user rule, 22 Oct). |
| 408 s1–s2 | Floating-point errors lose PD, most often in the update step. | K²VAE | K²VAE §3.2.1, p. 5 | ✅ | |
| 408 s3 | K²VAE use a variation they call the dual form (Joseph stabilisation). | K²VAE | K²VAE Thm. 3.1, Eq. (29), p. 5 (P^dual, "numerically stable form"). "Joseph": Zanetti 2013 §I, p. 1. | ✅ | **Fixed (v5).** Paper's name plus a sourced alternative name. |
| 408 s4 | It is mathematically identical to the standard update when the gain is optimal, as here, but more numerically stable. | Zanetti | Zanetti §I, p. 1 (simplified forms "are only valid when K is chosen as the optimal Kalman gain … Even when the optimal gain is used, the Joseph formulation is still preferable because it possesses greater numerical accuracy"); K²VAE App. A.1, p. 15 (equivalence proof) | ✅ | **New and verified.** Bib `zanetti2013joseph`. |
| 409–411 | P_dual equation. | (Zanetti, L408; K²VAE, L413) | K²VAE Eq. (29), p. 5; Zanetti §I, p. 1 | ✅ | |
| 413 | The dual form sums two PSD terms, which better preserves PD. | K²VAE | K²VAE §3.2.1, p. 5 | ✅ | |
| 415 s1 | The dual form **helps** preserve PSD but doesn't guarantee exact symmetry. | (K²VAE, s3) | K²VAE §3.2.1, p. 5 ("better ensures positive definiteness"; Eq. 28 "ensures the symmetry") | ✅ | **Fixed (v5).** The earlier ↔ ("preserves") is resolved. |
| 415 s2 | Rounding can leave P slightly asymmetric, and errors can accumulate over m steps. | (K²VAE, s3) | K²VAE Eq. (28), p. 5 implies asymmetry can arise | ☑️ | Accumulation over m steps is our reasoning. Minor. **Accepted as is by the user (22 Oct)**, was ⚠️. |
| 415 s3 | So the covariance is symmetrised by averaging with its transpose. | K²VAE | K²VAE Eq. (28), p. 5 | ✅ | **Fixed (v5).** |
| 416–418 | P_k = ½(P + Pᵀ). | (K²VAE, L415) | K²VAE Eq. (28), p. 5; `src/kalman.py:96` | ✅ | |
| 420 | Exact symmetry aids the Cholesky factorisation used in sampling. | — | `src/k2vae.py:75-76` (MultivariateNormal on P + jitter) | 🛠 | |
| 422 | Signposting. | — | — | ➖ | |

### 6.7 How the model acts as a VAE (L426–448)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 426 s1–s2 | Standard-VAE recap. | (§2.4 cross-ref) | Kingma §2–3 | ✅ | Covered in Ch. 2. Covered by the surrounding citation (user rule, 22 Oct). |
| 426 s3–s4 | RevIN, then the encoder (KoopmanNet, Integrator, KalmanNet) gives ℚ. | (K²VAE, L428/L430) | K²VAE §3.1, p. 3 (RevIN is ours) | ✅ / 🛠 | Covered by the surrounding citation (user rule, 22 Oct). |
| 428 | Figure reproduced from K²VAE. | K²VAE | K²VAE Fig. 3, p. 4 | ✅ | |
| 430 s1 | The full architecture is shown in the figure reproduced from K²VAE. | K²VAE | K²VAE Fig. 3, p. 4 | ✅ | **Fixed (v5).** |
| 430 s2–s7 | Walk-through: patch/embed; ψ; 𝒦_loc (eDMD) + 𝒦_glo; iterate for X̂_C and X̂_H; residual to the Integrator. | (K²VAE, s1 / L432) | K²VAE §3.1.1–3.1.2, pp. 3–4 | ✅ | |
| 432 s1–s6 | Kalman with process and observation noise; m recursions; Z, P; Z′ = Z + U; ℚ(Z∣X) = 𝒩(Z′, P); reparameterised sample. | (K²VAE, s7) | K²VAE Eqs. (14–23), pp. 4–5; §3.1.3, p. 5 | ✅ | |
| 432 s7 | The decoder ψ⁻¹ gives ℙ(Y∣Z). | K²VAE | K²VAE §3.1, p. 3 ("inverse measurement function"); §3.1.3, p. 5 | ✅ | **Fixed (v5).** |
| 434 s1–s3 | 𝒩(Z′, P); reparameterised via the Cholesky factor of P. | — | Kingma §2.4 (diagonal case only); `src/k2vae.py:75-78` | 🛠 | Implementation. |
| 434 s4–s6 | Jitter keeps P strictly PD; otherwise sampling crashes. | — | `src/k2vae.py:75` (1e-5·I) | 🛠 ✓ | |
| 434 s7–s9 | Train on the sample; at evaluation decode Z′ for the point forecast; repeated samples for CRPS. | — | `src/k2vae.py:81`; 100 samples: K²VAE App. C.3, p. 18 | 🛠 ✓ | |
| 436 s1 | Unlike a textbook VAE, the decoder has two separate heads. | (K²VAE, s2) | K²VAE Eq. (24), p. 5 | ✅ | |
| 436 s2 | K²VAE describe the decoder as the inverse measurement function ψ⁻¹, built from two MLPs of the same structure. | K²VAE | K²VAE §3.1, p. 3 ("inverse measurement function ψ⁻¹"); §3.1.3, p. 5 ("the Decoder consists of two same MLP structures") | ✅ | **Fixed (v5):** the earlier ❌ (misrepresenting the paper) is resolved. Old L436–438 merged into L436. |
| 436 s3 | One gives μ̂_Y, the other σ̂_Y. | (K²VAE, s2) | K²VAE Eq. (24), p. 5 | ✅ | |
| 436 s4 | In our implementation, both outputs pass back through RevIN. | — | `src/k2vae.py:114-138` | 🛠 ✓ | |
| 438–444 | Decoder equations. | — | `src/k2vae.py:114-138` | 🛠 ✓ | |
| 446 | Softplus keeps σ positive; RevIN rescales; σ floor added; near-zero variance blows up the NLL; the mean is denormalised too. | — | `src/k2vae.py:124-138` (floor 0.05) | 🛠 ✓ / ➖ | The NLL blow-up is basic algebra. |
| 448 | Signposting. | — | — | ➖ | |

### 6.8 The loss function (L452–462)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 452 s1 | Trained to minimise an extension of the CVAE objective. | — | — | 🛠 | |
| 452 s2 | The paper calls its objective a weighted sum of the ELBO and a reconstruction loss, but gives no weights. | K²VAE | K²VAE §3.1.4, p. 5 ("weightsumed by L_ELBO and L_Rec"; Eqs. 26–27 have no weights) | ✅ | **Fixed (v5):** the earlier ↔ ("no coefficients" vs "weightsumed") is resolved here. |
| 452 s3–s4 | Neither β nor λ_rec is in its equations; we added them (see §4.6). | — | K²VAE Eqs. (26–27), p. 5 | 🛠 / ✅ | Higgins (β-VAE) is no longer needed for this sentence. |
| 454–456 | Loss equation. | — | — | 🛠 | Our objective. |
| 458 | K²VAE departs from the standard CVAE: the encoder sees only the context, so the posterior is ℚ(Z∣X) and Y enters only through the loss. | K²VAE | K²VAE §2, Eq. (2), p. 3 (ℚ(Z∣X)); §3.1.3, p. 5 | ✅ | **New** (moved from the old Prelims L259, 22 Oct). Optional: Sohn §4.2, Eq. (8), p. 4 (GSNN, q(z∣x,y) = p(z∣x)) is the closest published analogue. |
| 460 s1 | β and λ_rec let each term be weighted per dataset. | — | — | 🛠 | |
| 460 s2–s4 | NLL of the horizon; pushes accuracy. | (K²VAE, L452/s8) | K²VAE Eq. (26) | ✅ | Covered by the surrounding citation (user rule, 22 Oct). |
| 460 s5 | The KL term is between 𝒩(Z′, P) and the standard normal prior. | (K²VAE, L452) | K²VAE §3.1.3–3.1.4, p. 5 | ✅ | |
| 460 s6 | It encourages a structured latent space (see §2.4) and penalises straying from the prior. | (§2.4 cross-ref; Kingma) | Kingma §2.3, p. 4 (cross-reference to the VAE section) | ✅ | **Fixed (v5).** "Ensures" softened to "encourages". Covered by the surrounding citation (user rule, 22 Oct). |
| 460 s7 | Reconstruction is the MSE of the Koopman-reconstructed context. | (K²VAE, s8) | K²VAE Eqs. (25, 27), p. 5; `src/k2vae.py:158` | ✅ | Covered by the surrounding citation (user rule, 22 Oct). |
| 460 s8 | K²VAE state this term facilitates the linearisation of the measurement space. | K²VAE | K²VAE §3.1.4, p. 5 ("L_Rec facilitates the linearization of the measurement space") | ✅ | **Fixed (v5).** The earlier ↔ (different purpose) is resolved. |
| 460 s9–s11 | Intuition: the linear operator's reconstruction can only match if the dynamics are near-linear, so the term pushes towards a good linear representation. | — | — | 🛠 | Our explanation, framed as intuition and consistent with s8. |
| 462 | Backprop; early stopping on validation loss; keep the best epoch; test it. | — | `src/train.py:37,262-287` (patience 5) | 🛠 ✓ | |
---

## 7. Chapter 4: Results and Experiments (set-up)

### 7.1 Chapter intro and Datasets (L466–487)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 466 s1–s4 | Chapter overview. | K²VAE | — | ➖ | |
| 466 s5 | Input window 96 (long-term) and 30 (short-term). | — | Config YAMLs. K²VAE §4.1, p. 6 uses T = 96 (long) and T = L = 30 (Exchange-S). | 🛠 ✓ / ✅ | |
| 470 | CSV layout, column order, -L/-S naming, YAML configs. | — | `configs/datasets_yaml/` | 🛠 ✓ | |
| 474 | ETTh1-L: 7 vars, range ℝ, hourly, 17,420 rows. | — | K²VAE Table 1, p. 6: 7 vars, **ℝ⁺**, H, 17,420 | 🛠 ✓ / ↔ | Our "ℝ" is likely correct (the load columns go negative, see Fig. 4.1). It differs from K²VAE's table without comment. |
| 475 | Wind-L: 7 vars, 15-min, 48,673 rows, forecast and measured wind with weather covariates. | — | `Wind-L.yaml` (7 features incl. `pred_*`, `ture_w_speed`, `target`) | 🛠 | Row count not re-checked against the CSV. The provenance source (TFB) is not in Sources. |
| 476 | Exchange-S: 8 vars, ℝ⁺, daily, **7,588** rows. | — | Our `exchange_rate.csv` = 7,588 rows ✓. K²VAE Table 1, p. 6 / Table 7, p. 17 list Exchange-S = 6,071 and Exchange-L = 7,588. Verified 22 Oct: GluonTS `exchange_rate_nips` (used by ProbTS for Exchange-S) is the **same 8 series** as our CSV. Its training series equal our rows 0–6,070 exactly (two columns swapped in order). Its 5 rolling test windows end at row 6,221. Our file continues to 7,588. | ⚠️ / 🛠 ✓ | **Correct for our file, but unexplained.** Suggested sentence: *"Exchange-S and Exchange-L in @k2vae2025 come from the same daily exchange-rate series. Their short-term version uses only the first 6,221 days, of which 6,071 are training data. We use the full 7,588-day series under the short-term protocol, so our series extends 1,367 days beyond theirs."* |
| 477 | Congestion-S: 3 vars, ℝ⁺, hourly, 8,761 rows. | — | 2017-09-30 to 2018-09-30 = 365 × 24 + 1 = 8,761 ✓ | 🛠 ✓ | Range: `temp` is in Kelvin (~290–305, Fig. 4.5) and stays positive. ✓ |
| 479 | Table caption. | — | — | ➖ | |
| 481 s1–s2 | ETTh1-L and Exchange-S were obtained from the K²VAE Google Drive, identified via their repo. | — | K²VAE §1, p. 2 ("all datasets and code are avaliable at https://github.com/decisionintelligence/K2VAE") | ✅ / 🛠 | The Exchange file is the full series. The paper's Exchange-S uses its first 6,221 days (see L476). |
| 481 s3 | They were cleaned externally and are common PTSF benchmarks. | — | K²VAE App. C.1, p. 16 ("derived from the authoritative probabilistic forecasting benchmark, ProbTS") | ✅ | Missing cite. |
| 481 s4 | No additional preprocessing. | — | — | 🛠 | |
| 483 s1 | Wind-L is "another well-known probabilistic time series dataset". | — | TFB (Qiu et al. 2024, in K²VAE refs) | ⬇️ | No source in folder says this. |
| 483 s2–s3 | Identified via the TFB repo; reshaped long → wide. | — | — | 🛠 | |
| 485 | Congestion: Kaggle source; dropped categoricals and rain/snow; kept 3 vars; truncated to 2017-09-30 → 2018-09-30; no gaps. | — | `Congestion.yaml` feature list matches | 🛠 ✓ | Original dataset is UCI Metro Interstate Traffic Volume. Credit optional. |
| 487 | Chronological, unshuffled 0.70 / 0.15 / 0.15 split. | — | `src/CLI.py:54-55`; `src/preprocessing.py:40` | 🛠 ✓ | |

### 7.2 Hyperparameter Tuning (L491–521)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 491 s1–s2 | Tuning balances continuous and discrete parameters; datasets vary. | — | — | 🛠 | |
| 491 s3 | Small models fit short series without overfitting; long sequences need larger latent dimensions. | — | — | 🚩 | General ML claim stated as fact. No source. Soften to our rationale. |
| 491 s4–s7 | A joint search would explode combinatorially; two tiers anchored by Exchange-S (30 steps) and ETTh1-L (96 steps). | — | — | 🛠 / ➖ | |
| 493 | Selection by minimum total validation loss; KL and reconstruction terms penalise collapsing variance or ignoring reconstruction. | — | `src/train.py:262` | 🛠 | Design intent is ours. Memory flags this selection choice as a limitation. |
| 495 s1–s2 | Two-phase W&B pipeline; phase 1 = lr, KL weight, reconstruction weight. | — | `configs/sweep_yaml/` | 🛠 | |
| 495 s3–s5 | f(θ) = validation loss; expensive, so Bayesian optimisation; it builds a probabilistic surrogate. | — | — | 🚩 | **No source for Bayesian optimisation** in the folder or in K²VAE's refs (candidates: Snoek et al. 2012; Jones et al. 1998). |
| 495 s6–s7 | The algorithm computes Expected Improvement, which balances exploration and exploitation. | — | — | 🚩 | No source. **We have not verified that W&B's Bayes sweep actually uses EI.** Check the W&B docs before stating it. |
| 497–501 s1 | EI formula; θ* is the best so far. | — | — | 🚩 | Standard formula, but no source. |
| 501 s2 | The algorithm "systematically zeros in on the optimal configuration with far fewer training runs". | — | — | 🚩 | Overclaim, and unsourced. With 6–12 runs over 27 points, "optimal" is not guaranteed. |
| 501 s3–s5 | Candidates in the table; 3 × 3 × 3 = 27 per tier; phase 1 trained 6 (ETTh1-L) and 12 (Exchange-S). | — | Table 4.2 | 🛠 ✓ | Arithmetic and table agree. |
| 503 s1–s2 | Phase 2 is an exhaustive grid over d, hidden size and depth. | — | — | 🛠 | |
| 503 s3 | "Discrete combinations exhibit clear transitions in parameter count, so grid evaluation gives a deterministic map." | — | — | 🛠 | Our rationale. |
| 503 s4–s5 | 27 runs per tier; 33 + 39 = 72 total. | — | 6 + 27 = 33 ✓; 12 + 27 = 39 ✓; 72 ✓ | 🛠 ✓ | |
| 505–517 | Search-space table and caption. | — | Matches the YAMLs: ETTh1 lr 0.002, β 0.01, λ 0.5, d 128, hidden 256, depth 2; Exchange lr 0.001, β 1e-4, λ 0.5, d 32, hidden 256, depth 1 (all within the listed grids) | 🛠 ✓ | |
| 519 s1–s2 | Full sweeps only on the two anchors; configs transferred within tier. | — | `Wind-L.yaml` ("copied from ETTh1-L"); `Congestion.yaml` = Exchange values | 🛠 ✓ | |
| 519 s3–s5 | Transfer is justified: with RevIN and patching, needed capacity depends mainly on sequence length and channel rank. | — | — | 🚩 | Our argument stated as fact. Untested (the L932 Limitations admit this). |
| 519 s6 | "Datasets in the same tier share these dimensions." | — | Table 4.1: Exchange-S **8** vars vs Congestion-S **3** vars | ❌ | **Contradicted by our own table** for the short tier. True for the long tier (7 and 7). |
| 519 s7–s9 | Because RevIN gives zero mean and unit variance, the loss balance "depends primarily on the latent dimension d", so tuned weights stay balanced. | — | — | 🚩 | Unsupported. Parked in memory (Ch. 4 item 5). RevIN's affine parameters also mean the scale is not exactly unit. |
| 521 | The best ETTh1 config had d = 256 (val 1.009); the second-best d = 128 (1.013); 2 h 38 vs 47 min; gap ~0.4%; we used d = 128. | — | (1.013 − 1.009)/1.009 = 0.40% ✓; `ETTh1-L.yaml` d = 128 ✓ | 🛠 ✓ | Times are not checked (W&B). |

### 7.3 External Model Benchmarks (L525–584)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 525 s1 | We compare against two "foundational long-sequence architectures". | — | — | 🛠 | |
| 525 s2–s4 | K²VAE combines patch attention, Koopman theory and Kalman filtering; we pick the leading model from each paradigm. | — | K²VAE §3.1 | ✅ / 🛠 | |
| 525 s5 | PatchTST is "the representative state-of-the-art transformer model". | — | PatchTST abstract, p. 1 ("improve the long-term forecasting accuracy significantly when compared with that of SOTA Transformer-based models") | ✅ | SOTA at publication (2023). |
| 525 s6 | Koopa is "the representative state-of-the-art operator model". | — | Koopa abstract, p. 1 ("achieves competitive performance") | ⚠️ | Koopa claims *competitive*, not state of the art. |
| 529 s1 | PatchTST introduces patching and channel independence. | — | PatchTST abstract, p. 1 | ✅ | **No citation anywhere in §4.3.1.** Add `nie2023patchtst`. |
| 529 s2 | It divides the context into **overlapping** patches. | — | PatchTST §3.1, p. 4 ("either overlapped or non-overlapped"); our baseline patch 16 / stride 8 (`baselines/patchtst_model.py:22-23`) | ⚠️ | PatchTST allows both. True of our baseline and PatchTST's defaults. |
| 529 s3 | Patches shorten the token sequence and aggregate local patterns. | — | PatchTST §1, p. 2 | ✅ | |
| 529 s4 | Channels are processed independently through a shared backbone, with no cross-variable attention. | — | PatchTST abstract; Fig. 1 caption, p. 4 | ✅ | |
| 529 s5 | Flatten, then a linear head to the horizon. | — | PatchTST §3.1, p. 5 ("a flatten layer with linear head") | ✅ | |
| 531 s1 | Main advantage: efficiency and resistance to overfitting. | — | PatchTST §1, p. 2 (training time); App. A.7.1, p. 21 ("Channel-independent models are less likely to overfit") | ✅ | |
| 531 s2 | Patching cuts the quadratic cost, making it "remarkably fast compared to point-wise attention". | — | PatchTST §1, p. 2 ("reducing the complexity quadratically"; "training time … reduced as much as 22 times") | ✅ | |
| 531 s3 | Channel independence stops attention learning noisy correlations between variables. | — | PatchTST App. A.7.1, p. 21 (adaptability; channel-mixing models need more data and overfit) | ⚠️ | "Noisy correlations" is our gloss on A.7.1. |
| 531 s4 | Strict channel independence "completely ignores cross-variable dynamics, which are critical in physical or financial systems". | — | K²VAE §3.1.1 motivates multivariate tokens but makes no "critical" claim | 🚩 | Partly definitional ("ignores"). "Critical" is unsupported. |
| 531 s5–s6 | It relies on an unconstrained linear head and lacks a dynamical model, "making it vulnerable to prediction drift". | — | — | 🚩 | Our argument stated as fact. |
| 533 | Expectations: K²VAE should beat PatchTST on multivariate data; stable matrix rollout; slower training. | — | — | 🛠 | Hypotheses. "Requires more computational time" is later called untimed (L670). Keep hedged. |
| 537 s1 | Koopa is operator-based and built for non-stationary dynamics. | Koopa | Koopa abstract, p. 1 | ✅ | |
| 537 s2 | "Classical Koopman theory assumes the system is stationary and described by a single global operator." | — | Koopa criticises earlier Koopman *forecasters*; App. D.4, p. 19 ("a stable Koopman operator only describes weakly stationary series well") | ↔ | **Not what Koopa says** (parked in memory, Ch. 4 item 4). Brunton covers non-autonomous Koopman (§4.5). |
| 537 s3 | Koopa separates the series into two components by frequency filtering. | — | Koopa abstract, p. 1 ("Fourier Filter") | ✅ | |
| 537 s4 | "Rather than requiring complex spectral mathematics, this filtering simply separates…" | — | Koopa §4, p. 4 (frequency-domain statistics via FFT) | ↔ | Koopa's filter *is* spectral (FFT). The sentence misdescribes it (parked in memory). |
| 537 s5 | The time-invariant part uses a learnable global operator. | — | Koopa §4, p. 4 ("we set the operator as a model parameter to be globally learned") | ✅ | |
| 537 s6 | The time-variant part fits local operators per segment by DMD. | — | Koopa Eqs. (8–10), p. 6 (eDMD, Moore–Penrose) | ✅ | |
| 537 s7 | Blocks are stacked in a residual structure. | — | Koopa abstract, p. 1 | ✅ | |
| 539 s1–s2 | Matrix-multiply rollouts make inference fast and lightweight. | — | Koopa abstract, p. 1 ("saving 77.3% training time and 76.0% memory") | ⚠️ | Koopa reports training time and memory, not inference speed specifically. |
| 539 s3 | Local operators are closed-form. | — | Koopa Eq. (10), p. 6 | ✅ | |
| 539 s4–s5 | Its limitation is linear transitions; real series have abrupt nonlinear shifts that linear operators cannot capture. | — | — | 🚩 | Our argument. The nonlinear encoder and decoder of Koopa are not mentioned. |
| 539 s6–s7 | "Koopa lacks an internal state filtering or correction mechanism … error propagates directly … without recursive refinement." | — | Koopa §1, p. 2 and the "Scaling up forecast horizon" analysis, p. 9 (operator **adaptation** using incoming ground truth); App. D.4, p. 19 (each block "feeds the residual of fitted dynamics for the next block to correct") | ↔ | **Overstated.** Koopa has residual correction across blocks and an operator-adaptation mechanism. It is not a recursive Kalman-type filter, but "lacks any correction" is not accurate. |
| 541 s1–s3 | Expectation: K²VAE should beat Koopa on noisy, nonlinear data. | — | K²VAE §3.1.2 for the mechanism | 🛠 | Hypothesis. |
| 541 s4 | This "provides active noise filtering … resulting in better stability". | — | — | 🚩 | Hypothesis phrased as an outcome. Our results do not support it (Koopa beats K²VAE on ETTh1-L). |
| 541 s5 | K²VAE is computationally more demanding to train than Koopa. | — | — | 🛠 | Untimed (see L670). Hedge. |
| 545 s1–s2 | PatchTST and Koopa were proposed as MSE-trained point forecasters. | — | PatchTST §3.1, p. 5 ("We choose to use the MSE loss"); Koopa Eq. (14), p. 6 (MSE) | ✅ | Missing cites. |
| 545 s3–s5 | Probabilistic metrics cannot score point forecasts; official code uses its own loading and splits. | — | — | ➖ / 🛠 | |
| 545 s6 | We reimplemented both baselines in our codebase, following the official code, with probabilistic heads. | — | `baselines/` | 🛠 | Memory: still to confirm with Kai that "following the official code" is accurate. |
| 545 s7 | This follows K²VAE, which equips both models with Gaussian heads. | K²VAE | K²VAE §4.1, p. 7 ("The point forecasting models are equipped with gaussian heads") | ✅ | |
| 545 s8 | We reused no published results. | — | — | 🛠 | |
| 547–557 | Split the output layer into μ and σ paths; σ = softplus(…) + 0.05. | — | `baselines/koopa_model.py:207-209`; `baselines/patchtst_backbone.py:38` (σ floor 0.05) | 🛠 ⚠️ | Code also rescales σ by RevIN **before** adding the floor. The equation omits this (parked in memory, Ch. 4 item 2). |
| 559 s1–s2 | The floor stops σ hitting 0, which would make the NLL undefined. | — | — | ➖ | |
| 559 s3–565 | MSE replaced by Gaussian NLL (equation). | — | — | 🛠 / ➖ | Standard Gaussian NLL. |
| 565 | t indexes horizon steps, j indexes variables. | — | — | ➖ | Symbol definitions. |
| 567 s1 | "Providing a fair comparison against K²VAE." | — | — | 🚩 | The baselines were untuned, while K²VAE had 72 tuning runs (parked in memory, item 3; the L934 Limitations say so). |
| 567 s2 | We also equipped both baselines with RevIN. | — | `baselines/koopa_model.py:144` (affine = False); `baselines/patchtst_backbone.py:56` | 🛠 ✓ / ↔ | PatchTST **already** uses instance normalisation (PatchTST §3.1, p. 5). "Also equipped" implies it was new for both. |
| 569 | Shared pipeline, optimiser, early stopping, evaluation; other settings follow official values. | — | `baselines/baseline_trainer.py` | 🛠 | |
| 571 | PatchTST is a compact reimplementation with CI patching, an encoder and a flatten head. | — | `baselines/patchtst_backbone.py` | 🛠 | |
| 573 | Koopa follows the original but adds ridge and a norm cap of 1; the faster solver fails when singular; the original lstsq is slower. | — | `baselines/koopa_model.py:38-64` (solve on normal equations + ridge; **Frobenius** norm capped at 1) | 🛠 ✓ | Note: our K²VAE clamps the *spectral* norm, but our Koopa caps the *Frobenius* norm. The text says "norm" generically, so it is not wrong. |
| 575–584 | Repository table. | — | K²VAE Table 8, p. 17 (Koopa, PatchTST, K²VAE URLs ✓) | ✅ | |

### 7.4 Metrics (L588–620)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 588 s1–s2 | We use NMAE and CRPS for all models. | — | K²VAE §4.1, p. 7 | ✅ | |
| 588 s3–s4 | Horizons 96/192/336/720 long, 30 short. | — | K²VAE §4.1, p. 6 | ✅ | |
| 588 s5 | Metrics are not used for model selection. | — | `src/train.py:262` | 🛠 ✓ | |
| 592–596 | NMAE equation and symbols. | — | K²VAE App. C.3, Eq. (37), p. 17 | ✅ | **Missing cite.** |
| 598 s1–s2 | NMAE is a scale-free error relative to the true magnitude, comparable across datasets. | — | K²VAE App. C.3, p. 17 ("dimensionless … facilitates the comparability … across different datasets or scales") | ✅ | Missing cite. |
| 598 s3–s6 | Bounds; NMAE = 1 for an all-zero forecast; good is near 0. | — | — | ➖ | Follows from the formula. |
| 598 s7 | Computed on the original scale. | — | `src/run.py:94-96`; `baselines/run_baseline.py:110-112` | 🛠 ✓ | |
| 602–606 | CRPS integral and symbols. | — | K²VAE App. C.3, Eq. (38), p. 17 (citing Matheson & Winkler 1976, ⬇️) | ✅ | **Missing cite.** |
| 608 | CRPS ≥ 0; 0 only for a point mass at the truth; grows with error and spread; good is near 0. | — | K²VAE App. C.3, p. 18 ("proper scoring function … minimum when the predictive distribution F coincides with the data distribution") | ✅ / ➖ | |
| 610 | CRPS on the standardised scale; each variable divided by its std. | — | `src/train.py:365` (standardised X_H) | 🛠 ✓ | |
| 612 | F has no closed form because the predictive averages over Z, so use samples. | — | — | ➖ | Correct reasoning (a mixture over Z through a nonlinear decoder). |
| 614 s1 | n = 100 samples. | — | K²VAE App. C.3, p. 18 ("100 samples are employed"); `src/run.py:86` | ✅ / 🛠 ✓ | |
| 614 s2–620 | The closed-form identity is exact for the empirical distribution (equation). | — | `src/metrics.py:30-34`. Standard result (Gneiting & Raftery 2007). Not in Sources or K²VAE refs. | 🚩 | Correct, but needs a citation. |
| 620 s1–s4 | NMAE is point accuracy only; CRPS scores the whole distribution and penalises bias and poor calibration. | — | K²VAE App. C.3, pp. 17–18 | ✅ / ➖ | Missing cite. |
| 620 s5 | KalmanNet is designed to model and refine process uncertainty. | — | K²VAE §1, p. 2 | ✅ | Missing cite. |
| 620 s6–s7 | Low NMAE but poor intervals still scores badly on CRPS; reporting both separates the two. | — | — | ➖ | |
### 7.5 Results (L624–700)

Every number in the prose was recomputed from Tables 4.4–4.5 and from K²VAE Tables 2, 9 and 10. Figure descriptions were checked against the PNGs in `artifacts/plots/`.

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 624 | Signposting. | — | — | ➖ | |
| 626 | Hardware, software, uv, libraries, W&B. | — | — | 🛠 | Not checked against `pyproject.toml`. |
| 628 | One unseeded run per model; rankings of close models may reflect the seed. | — | — | 🛠 | Honest. |
| 630–641 | Long-term results table and caption. | — | — | 🛠 | Bolding checked: correct in every row. |
| 643 s1 | Table reports CRPS and original-scale NMAE at 96–720. | — | — | 🛠 ✓ | |
| 643 s2 | On ETTh1-L, K²VAE is last on both metrics at every horizon. | — | Table 4.4 | 🛠 ✓ | All 8 checks hold. |
| 643 s3–s4 | Gap to the best CRPS narrows from 0.044 (96) to 0.018 (336). | — | 0.3841 − 0.3398 = 0.0443 ✓; 0.4251 − 0.4074 = 0.0177 ✓ | 🛠 ✓ | |
| 643 s5 | Both metrics deteriorate sharply at 720. | — | 0.5384 / 0.5098 | 🛠 ✓ | |
| 643 s6 | On Wind-L, K²VAE wins CRPS at most horizons. | — | Wins at 192, 336, 720 (3 of 4) | 🛠 ✓ | |
| 643 s7 | NMAE within 0.0065 of the winner at every horizon. | — | 96: 0.0065; 192: 0.0005; 336: 0.0022; 720: 0.0011 ✓ | 🛠 ✓ | |
| 645 s1 | Wind-L NMAE ≈ 0.08–0.12 vs CRPS 0.5–0.7. | — | NMAE 0.072–0.120 ✓; CRPS 0.4745–0.7425 | 🛠 ⚠️ | CRPS range rounds loosely (0.47–0.74). |
| 645 s2–s3 | This doesn't mean point forecasts are unusually good; NMAE sums across all variables on the original scale. | — | Eq. 4.4; `src/metrics.py` | 🛠 ✓ | |
| 645 s4 | Pressure ≈ 1025, direction ≈ 200, speed ≈ 5. | — | Fig. 4.2 checked ✓ | 🛠 ✓ | |
| 645 s5–s6 | Large channels dominate the denominator; CRPS on the standardised scale weights variables equally. | — | — | ➖ ✓ | |
| 647 s1–s2 | We predicted a K²VAE win on multivariate data; limited support. | — | L533 | 🛠 | |
| 647 s3 | Both long-term datasets have 7 variables. | — | Table 4.1 | 🛠 ✓ | |
| 647 s4 | ETTh1-L records load and temperature readings from one transformer. | — | K²VAE Table 1 only says "Electricity transformer temperature per hour". The original is Informer (Zhou et al. 2021, in K²VAE refs). | ⬇️ | Needs a dataset source. |
| 647 s5 | Wind-L pairs measured wind speed with covariates "that genuinely drive it". | — | — | 🚩 | The causal claim is unsupported, and the covariates are themselves forecasts (`pred_*`). Soften. |
| 647 s6–s7 | So cross-channel information should matter most there, and it is the only dataset where we beat PatchTST. | — | Tables 4.4–4.5 | 🛠 ✓ | Reasoning plus a correct fact. |
| 647 s8 | Wins on CRPS at 192, 336, 720; loses at 96. | — | Table 4.4 | 🛠 ✓ | |
| 647 s9–s10 | On ETTh1-L we lose to PatchTST everywhere; this is the predicted pattern. | — | Table 4.4 | 🛠 ✓ | |
| 647 s11–s12 | CRPS margin over PatchTST is 0.02–0.03. | — | 0.0201, 0.0297, 0.0202 ✓ | 🛠 ✓ | |
| 647 s13 | The 96-step loss margin is larger than any of these. | — | 0.0325 > 0.0297 ✓ | 🛠 ✓ | |
| 647 s14 | NMAE beats PatchTST only at 192, by 0.0008. | — | 0.0934 − 0.0926 ✓ | 🛠 ✓ | |
| 647 s15 | Two datasets, one run each. | — | — | 🛠 | |
| 649 s1 | K²VAE was designed to degrade less over longer horizons. | — | K²VAE §4.2, obs. 3, p. 8; §1, p. 2 | ✅ | Missing cite. |
| 649 s2–s4 | Only partly supported; on ETTh1-L ours degrades most: +0.154 vs +0.117 (Koopa) and +0.138 (PatchTST). | — | 0.1543 ✓; 0.1172 ✓; 0.1377 ✓ | 🛠 ✓ | |
| 649 s5–s6 | Most of the rise is at 720; 96→336: +0.041 vs +0.064 and +0.068. | — | 0.0410 ✓; 0.0637 ✓; 0.0676 ✓ | 🛠 ✓ | |
| 649 s7–s9 | Should not be overstated: we start worst and are still last at 336. | — | — | 🛠 ✓ | |
| 649 s10 | 336→720: +0.113 vs +0.054 and +0.070. | — | 0.1133 ✓; 0.0535 ✓; 0.0701 ✓ | 🛠 ✓ | |
| 649 s11–s12 | Appendix plots; single window; illustrative only. | — | — | 🛠 | |
| 649 s13–s15 | At 720, HUFL and MUFL lose amplitude; HULL, MULL, LUFL are near flat; Koopa still follows the daily cycle. | — | K²VAE L718 and Koopa L718 plots checked ✓ | 🛠 ✓ | |
| 649 s16 | "KoopmanNet and KalmanNet … has not had the intended effect" on ETTh1-L. | — | — | 🛠 | Conclusion from our results. Fair. |
| 651 | On Wind-L ours degrades least: +0.206 vs +0.228 and +0.259. | — | 0.2064 ✓; 0.2277 ✓; 0.2591 ✓ | 🛠 ✓ | |
| 653 s1–s2 | Their K²VAE ETTh1-L CRPS goes 0.264 → 0.314 (+0.050); ours 0.3841 → 0.5384 (+0.154). | K²VAE | K²VAE App. C.5, Table 9 ✓ | ✅ | |
| 653 s3 | NMAE change: theirs 0.060, ours 0.129. | — | K²VAE Table 10: 0.336 → 0.396 ✓; ours 0.1291 ✓ | ✅ / 🛠 ✓ | Missing cite (Table 10). |
| 655 s1–s2 | Our CRPS and theirs are normalised differently. | — | Official ProbTS `probts/utils/evaluator.py:49-60` (quantile loss / Σ\|y\|) | 🛠 (code) | Code-sourced, which is fine. The paper itself (Eq. 38) does not normalise. |
| 655 s3 | Starting higher inflates the absolute change. | — | — | ➖ | |
| 655 s4 | Ratios: ours 1.40 vs 1.19 (CRPS) and 1.34 vs 1.18 (NMAE). | — | 1.4017 ✓; 1.189 ✓; 1.339 ✓; 1.179 ✓ | 🛠 ✓ | |
| 655 s5–s6 | The gap is real but smaller; reasons are in §4.6. | — | — | 🛠 | |
| 657–666 | Short-term table and caption. | — | — | 🛠 | Bolding ✓. |
| 668 s1–s2 | K²VAE is competitive, with similar CRPS. | — | 0.0924 vs 0.0870/0.0877; 0.3194 vs 0.3072/0.3677 | 🛠 ✓ | |
| 668 s3 | NMAE less competitive, "especially on Congestion-S". | — | Congestion: 0.1571 vs best 0.1253 (+25%); Exchange: +6.6% | 🛠 ✓ | Note: on Congestion our NMAE *beats* Koopa (0.1799). The sentence reads more negative than the table. |
| 668 s4–s5 | PatchTST wins every metric; we beat Koopa on Congestion, lose on Exchange. | — | Table 4.5 | 🛠 ✓ | |
| 668 s6 | K²VAE reports a significant advantage on Exchange, attributed to non-stationarity and drift. | K²VAE | K²VAE §4.2, obs. 2, p. 8 | ✅ | Their claim covers Exchange-S and Exchange-L, so it applies to the series we use. Our run covers a longer period than their Exchange-S (see L476). |
| 668 s7 | Competitive, but not consistently better. | — | — | 🛠 ✓ | |
| 670 s1–s3 | Our K²VAE does not consistently beat the baselines; it trails or ties; wins are small. | — | Tables 4.4–4.5 | 🛠 ✓ | |
| 670 s4 | All three of our models have higher CRPS than published; our Koopa and PatchTST often have lower NMAE. | K²VAE | K²VAE Tables 2, 9, 10. CRPS higher in every case ✓. NMAE lower in 9 of 10 baseline comparisons (exception: Koopa ETTh1-L 720, 0.4194 vs 0.412). | ✅ / 🛠 ✓ | "Often" is accurate. |
| 670 s5 | So the meaningful comparison is between our own three models. | — | — | 🛠 | |
| 670 s6 | No timed trials, but K²VAE took noticeably longer to train. | — | — | 🛠 | Honest. Conflicts in tone with the unhedged L533 and L541. |
| 672 | We show only our model at the shortest horizon, to show how it forecasts. | — | — | 🛠 | |
| 674 | Plot legend description. | — | — | 🛠 ✓ | Matches the PNGs. |
| 676 | The reconstruction comes from the Koopman operator alone, before KalmanNet; gaps show residual nonlinearity, and that residual feeds the Integrator. | — | `src/k2vae.py:101-107,158` | 🛠 ✓ | |
| 678 s1–s3 | Reconstruction is in-sample (𝒦_loc fitted on the window); the horizon extrapolates. | — | `src/koopman.py` | 🛠 ✓ | |
| 678 s4–s6 | Decoded in whole patches, so the forecast can start at a different level and jump at boundaries, e.g. steps 120 and 144 on Wind-L. | — | Patch size 24 (`Wind-L.yaml`), so boundaries are at 96 + 24k ✓. Fig. 4.2: band jumps at 120, mean at 144 ✓ | 🛠 ✓ | |
| 680 s1 | The red line is μ decoded from Z′. | — | `src/k2vae.py:81` | 🛠 ✓ | |
| 680 s2–s4 | Band = μ ± 1.96σ, the decoder spread at Z′; it excludes latent uncertainty, which CRPS samples include. | — | `sample_predictive` samples Z and then Y | 🛠 ✓ | |
| 680 s5 | The band is therefore narrower than the full predictive and "a lower bound" on our uncertainty. | — | — | ⚠️ | Not guaranteed. By total variance, Var(Y) = E[σ²(Z)] + Var(μ(Z)), and σ²(Z′) need not be ≤ E[σ²(Z)]. Say "typically narrower" rather than "lower bound". |
| 682 | Figure caption. | — | — | 🖼 | |
| 684 s1–s2 | ETTh1 at 96; six of seven channels shown. | — | Fig. 4.1 ✓ | 🛠 ✓ | |
| 684 s3 | Reconstruction tracks the context closely "on all six". | — | Fig. 4.1: close on HUFL, HULL, MUFL, MULL. Visibly weaker on LUFL and LULL spikes. | ↔ | **Contradicts s10 of the same paragraph** ("on these channels our Koopman reconstruction is weaker"). |
| 684 s4–s7 | HUFL and MUFL best: peaks match in timing and height, troughs overshoot. | — | Fig. 4.1 ✓ | 🛠 ✓ | |
| 684 s8 | HULL and MULL: right shape, damped peaks. | — | Fig. 4.1 ✓ | 🛠 ✓ | |
| 684 s9–s11 | LUFL and LULL worst: weaker reconstruction of spikes, forecast near the mean. | — | Fig. 4.1 ✓ | 🛠 ✓ | |
| 686 | HUFL band ≈ −50 to 25 vs series −20 to 20; consistent with worst CRPS. | — | Fig. 4.1 ✓ | 🛠 ✓ | |
| 688 | Figure caption. | — | — | 🖼 | |
| 690 | Wind: reconstruction close; speed channels follow level and recovery but smooth swings; direction and pressure near flat; humidity damped; temp opposite then recovers after the jump at 144; wide intervals. | — | Fig. 4.2 ✓ | 🛠 ✓ | The text says `true_w_speed`. The plot and YAML label it `ture_w_speed` (typo in the data). |
| 692 | Figure caption. | — | — | 🖼 | |
| 694 s1–s4 | Exchange: six of eight channels; good reconstruction; near-flat forecast; expected for a near random walk ("tomorrow ≈ today"). | — | Fig. 4.3 ✓. Random walk: PatchTST App. A.1.1, p. 13 ("the toughest benchmark for exchange-rate forecasting is a random walk without drift", citing Rossi 2013) | ✅ / 🛠 ✓ | **Missing cite** for the random-walk claim. PatchTST is in Sources. |
| 694 s5–s7 | No structure exploited; bands widen; channel 2 falls away and we miss it. | — | Fig. 4.3 ✓ | 🛠 ✓ | |
| 694 s8 | This is the drift K²VAE credits for its advantage. | K²VAE | K²VAE §4.2, obs. 2, p. 8 | ✅ | |
| 694 s9–s10 | Good reconstruction does not guarantee a good forecast. | — | — | 🛠 | |
| 696–698 | Congestion: traffic_volume best (cycle and trough timing and depth; undershoots the second peak); temp handled well; clouds_all fails, band below zero (impossible for %). | — | Fig. 4.4 ✓ | 🛠 ✓ | |
| 700 | Across plots: good in-sample reconstruction, weak extrapolation; damped cycles; mean reversion on noisy channels; worse with horizon on ETTh1; wide intervals; problem likely in the rollout. | K²VAE | — | 🛠 | Interpretation is fair given the evidence and is hedged ("suggests"). |

### 7.6 Our Implementation vs the Reference Paper (L704–767)

Claims about **the authors' code** were checked this pass against `decisionintelligence/K2VAE` (master).

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 704 | Built from the paper, codebase consulted where silent; we adopted only what was needed to be comparable or to learn. | K²VAE | — | 🛠 | |
| 706 s1 | The paper's loss gave partial posterior collapse. | — | Ablation (Full KL) | 🛠 | |
| 706 s2 | The paper's loss has no coefficients. | — | K²VAE Eqs. (26–27), p. 5 | ↔ | The equations have none, but the text says the objective is "**weightsumed** by L_ELBO and L_Rec". Mention this. |
| 706 s3 | Their code weights the KL by β, adds an MSE between forecast mean and target, and switches the NLL off above 100. | — | Official `prob_forecaster/k2vae.py:115-136` (`F.mse_loss(post_dist.loc, target)`; `weight_alpha = 1 if post_loss < 1e2 else 0`; `weight_beta`) | 🛠 (code) ✓ | ETTh1 config: `weight_beta: 0.01`. |
| 706 s4–s6 | We had to add β (KL dominates otherwise); see figure; β was needed. | — | Ablation; Fig. 4.6 | 🛠 ✓ | |
| 706 s7 | We added λ_rec, which their code does not have. | — | Official: `rec_loss` unweighted (`k2vae.py:131,136`) | 🛠 (code) ✓ | |
| 708 | Figure caption. | — | — | 🖼 | |
| 710 s1 | Reconstruction still tracks, so 𝒦 has not failed. | — | Fig. 4.6 ✓ | 🛠 ✓ | |
| 710 s2–s3 | Forecast flattened; HUFL moves 0–6 vs truth −15 to 15. | — | Fig. 4.6 ✓ | 🛠 ✓ | |
| 710 s4 | Intervals huge and almost constant. | — | Fig. 4.6 ✓ | 🛠 ✓ | |
| 710 s5–s7 | Posterior pulled onto the prior; partial collapse; see §4.7.3. | — | Table 4.7 (Full-KL raw KL 0.0081) | 🛠 ✓ | |
| 712 s1–s2 | Their loss drops Z′ and uses 𝒩(0, P). | — | Official `kalman.py:140` (`loc=torch.zeros_like(prediction)`) | 🛠 (code) ✓ | |
| 712 s3 | We kept the paper's form. | — | K²VAE §3.1.3, p. 5 (𝒩(Z, P)) | ✅ | |
| 712 s4–s7 | Development observation: Z → −U so Z′ → 0, shrinking the KL; not retained; reported as an observation. | — | — | 🛠 | Honestly hedged. |
| 712 s8–s9 | Partial collapse is consistent with it; their form avoids it. | — | — | 🛠 | |
| 714 | RevIN is absent from the paper but present in the code; we added it; see §4.7.5. | — | Paper: no mention (searched). Code: official `k2vae.py:17,52-56` | ✅ / 🛠 ✓ | |
| 716 | Ridge and spectral clamp are ours; neither is in the paper or their code; effect not isolated. | — | Paper: Eq. (8) pseudoinverse. Official `koopman.py:74,78` uses plain `torch.linalg.lstsq` | ✅ / 🛠 ✓ | |
| 718 | All three of our models have larger CRPS; three possible reasons. | — | Tables 2, 9 | 🛠 ✓ | |
| 720 s1 | The paper doesn't state the split; it defers to ProbTS. | — | K²VAE §4.1, p. 6; App. C.1, p. 16 | ✅ | |
| 720 s2–s3 | Their results come from the ProbTS library; GluonTS supplies short-term data. | — | ProbTS: official repo. GluonTS routing: checked 29 Sep (memory), **not re-checked this pass**. | 🛠 ⚠️ | |
| 720 s4–s6 | Out of scope; our procedure judged adequate. | — | — | 🛠 | |
| 722 s1–s2 | Our 70/15/15 split uses the whole dataset; their code uses no ratios. | — | `src/CLI.py:54-55` | 🛠 ✓ | "Uses no ratios" holds for ETT. Other datasets in ProbTS do use ratios (`get_datasets.py:49`, 0.7/0.2). |
| 722 s3–s4 | ETTh1 borders 12/4/4 months of 30 days, at rows 8,640, 11,520 and 14,400; test 11,520–14,400. | — | Official `probts/data/data_utils/get_datasets.py:67-68` ✓. Arithmetic ✓. | 🛠 (code) ✓ | |
| 722 s5–s7 | Our test rows are 14,807–17,420; zero overlap; ours sits in the region they disregard. | — | 0.85 × 17,420 = 14,807 ✓ | 🛠 ✓ | |
| 722 s8–s9 | For Exchange-S they use GluonTS, giving different test sets. | — | Verified 22 Oct against GluonTS `exchange_rate_nips`: their test targets are rows 6,071–6,221 and validation is rows 5,921–6,070. Ours: test rows 6,449–7,588. | 🛠 ✓ | Correct. Consider adding the row numbers, as done for ETTh1: **zero overlap**, and our test set lies entirely after their data ends. |
| 724 | `--FLAG: Address the Exchange-S vs Exchange-L size difference … --` | — | — | 📝 | Draft note added 22 Oct at the user's request. It will render. |
| 726 | Split figure caption. | — | — | 🖼 | Not re-checked visually. |
| 728 s1–s2 | We select on validation loss; their code selects on lowest validation CRPS. | — | Official `run.py:123` (`monitor = 'val_CRPS'`, branch-dependent) | 🛠 (code) ✓ | |
| 728 s3–s7 | Rationale; the baselines are selected on NLL, K²VAE on the weighted loss; CRPS selection would need 100 samples per window per epoch. | — | `src/train.py`; `baselines/baseline_trainer.py` | 🛠 | Good disclosure. |
| 730 s1 | We use the sample identity; they use ProbTS's different method. | — | — | 🛠 | |
| 730 s2–s3 | F is unavailable, so approximate with 100 samples. | — | K²VAE App. C.3, p. 18 | ✅ | |
| 730 s4 | This is similar to the procedure K²VAE report using. | K²VAE | K²VAE App. C.3, p. 18 (empirical CDF from 100 samples) | ✅ | |
| 730 s5–s6 | ProbTS draws 100 samples, takes empirical quantiles and scores them with pinball loss. | — | Official `probts/utils/evaluator.py:49-60`; `metrics.py:127-133` | 🛠 (code) ✓ | Quantile levels are 0.1–0.9 (`evaluator.py:8`). Could state \|Q\| = 9. |
| 732–740 | QL_q and CRPS_ProbTS formulas. | — | `metrics.py:133`; `evaluator.py:53,59-60` | 🛠 (code) ✓ | |
| 742 | Discrete, normalised by Σ\|y\| like NMAE, hence similar magnitudes. | — | As above | 🛠 ✓ | |
| 744 s1–s3 | CRPS scales with data; both are dimensionless but scaled differently. | — | — | ➖ | |
| 744 s4 | ProbTS works on **original unscaled** data. | — | **Not verified this pass** (`data_scaler.py` not read) | ⚠️ | Verify before relying on it. |
| 744 s5–s9 | We use standardised tensors; values not comparable; applies to all three models; part of the gap may be normalisation. | K²VAE | — | 🛠 | |
| 746 s1–s2 | Normalisation doesn't explain faster degradation; NMAE uses the same formula, although ProbTS scores the **median** and we score the mean. | — | Official `evaluator.py:23-38` (`median_forecasts`; ND = abs_error / abs_target_sum) | 🛠 (code) ✓ | |
| 746 s3 | All three of our models degrade more than the published ones. | — | Koopa CRPS +0.117 vs +0.011; PatchTST +0.138 vs +0.011; NMAE similar (Tables 9–10) | ✅ / 🛠 ✓ | |
| 746 s4 | "This also holds for the two benchmark models, **which we did not write**." | — | L545: "we **reimplemented both baselines within our own codebase**"; L571–573 | ❌ | **Internal contradiction.** We did write them (from the official code). |
| 746 s5 | So the degradation may point to our setup rather than K²VAE. | — | — | 🛠 | Reasonable. The L746 s4 premise needs fixing. |
| 748 s1–s5 | Summary: different split, selection and CRPS; not comparable. | — | — | 🛠 ✓ | |
| 748 s6 | They searched up to eight configurations per model per dataset, including baselines. | — | K²VAE App. C.4, p. 18 ("with a limit of 8 sets") | ✅ | Missing cite. |
| 748 s7–s8 | We searched more for K²VAE on two anchors; baselines used published settings. | — | — | 🛠 | |
| 748 s9 | One unseeded run vs their 5, with standard errors. | — | K²VAE Table 9 caption ("five independent runs with different seeds"; "standard errors") | ✅ | Missing cite. |
| 750 | Pointer to the summary table. | — | — | ➖ | Signposting. |
| 752–765 | Comparison table. | — | Paper column: loss weights "None" (↔ "weightsumed"); 𝒩(Z′, P) ✓; RevIN not described ✓; pseudoinverse ✓; batch 32 ✓ (App. C.4); split defers to ProbTS ✓; selection not stated ✓; CRPS integral (⚠️ the paper also states the 100-sample empirical CDF); 5 seeds ✓; ≤ 8 configs ✓. Code column: β + MSE ✓; 𝒩(0, P) ✓; RevIN ✓; lstsq ✓; ProbTS, 100 batches/epoch, batch 64 ✓ (`config/ltsf/etth1/k2vae.yaml:9,43`); month borders ✓; val CRPS ✓; quantile loss / Σ\|y\| ✓. | ✅ / 🛠 ✓ | Two refinements: "None" → "Unspecified (text says weight-summed)"; CRPS → "Integral; empirical CDF from 100 samples". |
| 767 | Could not pin down why we trail our baselines; K²VAE-internal differences are the likely candidates; baselines untuned; the advantage may depend on their setup. | K²VAE | — | 🛠 | Hedged appropriately. |
### 7.7 Ablation Analysis (L771–906)

All numbers were recomputed from Tables 4.8–4.9. The weighted KL, test totals (NLL + βKL + λ·Recon) and best epochs are consistent in every row. The loss-curve and residual figures were checked against the PNGs.

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 771 s1–s3 | Purpose; ETTh1-L; same pipeline; fixed seed 2026 at horizon 96. | — | — | 🛠 | |
| 771 s4–s5 | The control differs from Table 4.4: 0.3787 / 0.3769 vs 0.3841 / 0.3807. | — | Tables 4.4, 4.8 ✓ | 🛠 ✓ | |
| 771 s6 | The gap of about 0.005 indicates run-to-run variation. | — | CRPS gap 0.0054 ✓. NMAE gap is 0.0038. | 🛠 ✓ | One pair of runs is a weak estimate of variation. Implicitly acknowledged. |
| 771 s7 | Focus on one change at a time. | — | — | 🛠 | |
| 773 | CRPS and NMAE are primary; others secondary. | — | — | 🛠 | |
| 775 | Control uses β = 0.01, λ_rec = 0.5; 0 removes a term, 1 applies it unweighted. | — | `ETTh1-L.yaml` ✓ | 🛠 ✓ | |
| 779–790 | Design table. | — | — | 🛠 | |
| 792 | Describes the conditions. | — | — | 🛠 | "Static" = local only, "dynamic" = global only. Naming is ours. |
| 794 s1 | One-factor-at-a-time with two cross-effects. | — | — | 🛠 | |
| 794 s2 | Full KL (β = λ = 1) is the "canonical unweighted ELBO where all terms have unit weight as in standard VAE theory". | — | Kingma Eq. (3), p. 3 (KL at unit weight); K²VAE Eqs. (26–27) (L_Rec unweighted) | ⚠️ | The reconstruction term is K²VAE-specific, not "standard VAE theory". It matches the *paper's* unweighted objective. Say that. |
| 794 s3–s4 | NLL-only rationale; no full factorial. | — | — | 🛠 | |
| 798–809 | Primary results table. | — | Differences checked. **Five are 0.0001 off the displayed values:** Static NMAE +0.0023 (shown values give +0.0022); Dynamic NMAE −0.0003 (−0.0004); No-KL NMAE +0.0103 (+0.0102); NLL-only CRPS +0.0273 (+0.0274); No-RevIN CRPS +0.0446 (+0.0447). | ⚠️ | Probably computed from unrounded values. Either recompute from the displayed values or note it. Prose at L813/L848 reuses 0.0003 and 0.0103. |
| 811 | Positive = worse. | — | — | ➖ | |
| 813 | Dynamic is best but marginal (−0.0022 CRPS, −0.0003 NMAE); RevIN, reconstruction and Full KL are worse; Full KL is worst. | — | Table 4.8 ✓ | 🛠 ✓ | |
| 815–826 | Full metrics table. | — | βKL = β × raw ✓ (all rows); totals ✓ (all rows) | 🛠 ✓ | |
| 828 | Raw KL is before β; the weighted value is what is optimised. | — | — | 🛠 ✓ | |
| 830 | Totals are not comparable when β or λ = 0; use primary metrics. | — | — | 🛠 ✓ | |
| 834 | Figure caption. | — | — | 🖼 | |
| 836 | Control improves NLL and reconstruction; KL stays finite. | — | Control loss-curve PNG ✓ (KL ≈ 6–10; best epoch 8, stops at 14) | 🛠 ✓ | Validation KL rises over training (6.3 → 8.6). Not mentioned. |
| 838 | NLL is noisy (stochastic samples, minibatches, dropout, per-batch 𝒦_loc); validation is smoother but can rise. | — | PNG ✓ | 🛠 ✓ | "Per-batch" should be per-window (see L360). |
| 840 s1–s2 | Static and dynamic stay close; static slightly worse, dynamic slightly better. | — | Table 4.8 ✓ | 🛠 ✓ | |
| 840 s3 | Dynamic has lower NLL (0.9245) and higher reconstruction (0.5262). | — | Table 4.9 ✓ | 🛠 ✓ | |
| 840 s4 | Suggests a trade-off, not a better latent. | — | — | 🛠 | Hedged. |
| 842 | Differences are within seed noise; keep mixed; dynamic is a future direction. | — | — | 🛠 ✓ | |
| 846 | With β = 0 the raw KL rises to ~1198.9; NLL-only ~19214.8. | — | Table 4.9 ✓ | 🛠 ✓ | |
| 848 s1–s4 | This is "latent divergence"; the posterior moves far from the prior; runs stay finite. | — | — | 🛠 | Term is ours. Fine. |
| 848 s5–s7 | Removing KL has a modest effect; CRPS +0.0015 is within the 0.005 variation; necessity is shown by NMAE +0.0103 and the divergence. | — | ✓ (see the 0.0103 rounding note) | 🛠 ✓ | NMAE run-to-run gap was 0.0038, so 0.0102–0.0103 does exceed it. ✓ |
| 850 | Figure caption. | — | — | 🖼 | |
| 852 s1 | The figure "illustrates posterior collapse". | — | Klushyn 2021 §1(ii), p. 1 describes over-regularisation of the approximate posterior | ⚠️ | No source in the chain defines *posterior collapse*. Klushyn is close. Also, L710 and L904 call it "partial" or "near" collapse, which is more accurate. |
| 852 s2–s4 | Early on the KL is large; β = 1 rewards cutting it; the raw KL plummets to ~0.0081. | — | Full-KL PNG ✓ (train KL 3.4 → ~0.2 by epoch 2 → ~0); Table 4.9 ✓ | 🛠 ✓ | |
| 854 s1–s2 | Forced to the prior, the latent loses information; NLL stays high; CRPS 0.5134, NMAE 0.5691. | — | Table 4.9 ✓ (test NLL 1.2525 vs 0.9422) | 🛠 ✓ | |
| 854 s3–s4 | The latent carries little information; full-strength KL is too severe; supports a moderate β. | — | — | 🛠 | |
| 858 | No reconstruction: CRPS 0.3787 → 0.3913, NMAE 0.3769 → 0.3954; it encourages retaining context information. | — | Table 4.8 ✓ | 🛠 ✓ | The rationale differs from the paper's ("facilitates linearisation", K²VAE p. 5). Same ↔ as L460. |
| 860 | Reconstruction error is higher because it is no longer optimised; supports λ = 0.5. | — | Table 4.9 (1.1173) ✓ | 🛠 ✓ | |
| 862–864 | Figure captions. | — | — | 🖼 | Not re-checked visually. |
| 866 | No RevIN: CRPS 0.4234, NMAE 0.4156; NLL and KL worse; visual degradation suggests RevIN handles scale shifts. | — | Table 4.9 ✓ | 🛠 ✓ | |
| 868 | No RevIN stopped at best epoch 2; distribution shifts degrade the landscape; RevIN matters for stable training (single-seed caveat). | — | Table 4.9 ✓ | 🛠 | Hedged. |
| 870 | Keep RevIN; confirm over seeds. | — | — | 🛠 | |
| 874 | Signposting. | — | — | ➖ | |
| 876 | Figure caption. | — | — | 🖼 | |
| 878 s1 | The figure shows the expected increase in error with horizon. | — | Residual PNG: MSE rises ~7 → ~12 over the first ~30 steps, then **plateaus** at ~11.5–13. MAE 1.5 → 2.1, then flat. | ⚠️ | Supported for the first third only. It plateaus after that. |
| 878 s2–s3 | Consistent with §3.4: linear propagation accumulates error with horizon. | — | — | ⚠️ | The plateau does not show continued accumulation. The figure cannot separate rollout error from decoder error. |
| 878 s4–s5 | Later steps are more sensitive; supports aggregate metrics. | — | — | 🛠 | |
| 880 | Figure caption. | — | — | 🖼 | |
| 882 | Removing KL removes its contribution, not the raw KL; the posterior diverges; the loss still falls. | — | Table 4.9 ✓ | 🛠 ✓ | PNG not re-checked. |
| 884–886 | NLL-only diagnostic; largest raw KL; worse CRPS and NMAE. | — | Table 4.9 ✓ | 🛠 ✓ | |
| 890–900 | Limitations: one seed, one dataset, selection on total loss, scale conventions, different objectives, ridge-regularised operator. | — | — | 🛠 ✓ | Consistent with the code and text. |
| 904–906 | Concluding remarks: keep RevIN, moderate KL, reconstruction; mixed operator stays the default. | — | — | 🛠 ✓ | |

---

## 8. Chapter 5: Conclusion (L910–950)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 910 | Recap of aims and set-up. | K²VAE | — | 🛠 | |
| 912 s1–s3 | Did not consistently outperform; last on ETTh1-L at every horizon; close to 336, falls at 720. | — | Table 4.4 ✓ | 🛠 ✓ | |
| 912 s4 | The stable long-horizon performance reported by K²VAE did not hold on ETTh1-L. | K²VAE | K²VAE §4.2, obs. 3, p. 8 | ✅ | |
| 912 s5 | Only wins over both baselines were on Wind-L, and marginal. | — | Wind-L CRPS at 192/336/720 beats both ✓ | 🛠 ✓ | |
| 912 s6 | Short-term: competitive; PatchTST best on every metric. | — | Table 4.5 ✓ | 🛠 ✓ | |
| 912 s7 | On Exchange-S, where the paper credits drift, we were last on both metrics. | — | Table 4.5 ✓; K²VAE §4.2, obs. 2, p. 8 | ✅ / 🛠 ✓ | Missing cite for the paper's drift claim. Same series as theirs, over a longer period (see L476). |
| 912 s8–s11 | Plots: good in-sample reconstruction; damped cycles, mean reversion, wide intervals. | — | Figs. 4.1–4.4 ✓ | 🛠 ✓ | |
| 914 | `--FLAG: Add out of scope --` | — | — | 📝 | Draft note. It will render. |
| 916 s1 | We could not match K²VAE, which reported superior results on Exchange-S and ETTh1-L. | K²VAE | K²VAE Tables 2, 9 (best on Exchange-S and ETTh1-L at all horizons) | ✅ | |
| 916 s2–s3 | Not directly comparable; "**our test sets do not overlap theirs**". | — | ETTh1: L722. Exchange: rows 6,071–6,221 (theirs) vs 6,449–7,588 (ours), verified 22 Oct. | ✅ / 🛠 ✓ | **True for both datasets.** The thesis evidences only ETTh1, so add the Exchange numbers at L722. |
| 916 s4–s5 | Different selection and CRPS normalisation; published values can't judge ours. | — | §4.6 | 🛠 ✓ | |
| 916 s6–s9 | Our own-baseline comparison is fair on pipeline; the advantage didn't appear; future work. | K²VAE | — | 🛠 | |
| 918 s1–s2 | The paper's loss has no KL weight and RevIN isn't described; their code uses both. | — | K²VAE Eqs. (26–27), p. 5; official code ✓ | ✅ / 🛠 ✓ | Missing cite. ↔ minor: "weightsumed" (L706). |
| 918 s3–s5 | Both omissions held our model back: partial collapse; best epoch 2 without RevIN. | — | Tables 4.8–4.9 ✓ | 🛠 ✓ | |
| 918 s6 | Their code removes Z′ from the KL; we kept the paper's form. | — | Official `kalman.py:140` ✓ | 🛠 ✓ | |
| 918 s7–s8 | The ablation confirmed the KL weight and RevIN, showed reconstruction helps, and the Koopman operator choice made little difference. | — | Table 4.8 ✓ | 🛠 ✓ | |
| 920 | Overall: not consistently better than simpler PatchTST and Koopa; good past, weak future; the paper lacks detail; we relied on their code for β and RevIN. | — | — | 🛠 ✓ | "Simpler" is a judgement call. Fine. |
| 924 | Recommendations: RevIN, reconstruction, small KL weight, mixed operator; single seed and dataset. | — | Table 4.8 ✓ | 🛠 ✓ | |
| 926 | Comparisons should match the reference split, selection and CRPS normalisation. | — | §4.6 | 🛠 ✓ | |
| 930 s1–s3 | Single unseeded run; cannot separate model differences from noise. | — | — | 🛠 ✓ | |
| 930 s4 | K²VAE retrains five times with different seeds and reports mean and standard error. | K²VAE | K²VAE Table 9 caption | ✅ | |
| 932 | Tuned only on two anchors; transfer argued, not tested; Wind and Congestion may have better configs. | — | — | 🛠 ✓ | Contrast with L519, which states the transfer as fact. |
| 934 | Baselines untuned; settings from a different set-up; a stronger comparison would tune all equally. | — | — | 🛠 ✓ | Contradicts the "fair comparison" wording at L567. |
| 936 | Baselines chosen for long-term; on ETTh1, Fig. 1.1 shows native probabilistic models best at short horizons; short-term comparison is only against point forecasters. | — | K²VAE Fig. 1 ✓ | ✅ | Refers to Fig. 1.1, whose caption credits K²VAE. A citation is optional. |
| 938 | Ablation scope limited (one dataset, one seed); selection on total loss. | — | — | 🛠 ✓ | |
| 942 s1–s2 | K²VAE regularises to an uninformative 𝒩(0, I). | — | K²VAE §3.1.4, p. 5 | ✅ | Missing cite. |
| 942 s3–s5 | That prior encodes no system knowledge; a Bayesian prior could reflect it. | — | — | 🛠 / ➖ | Proposal. |
| 944 s1–s4 | Bayesian basics: prior beliefs, posterior combines them, weighted by confidence. | — | — | ➖ | Textbook. Arguably needs no citation. |
| 944 s5–s6 | Express beliefs as linear relations on the latent; Gaussian priors keep the KL closed-form. | — | Kingma App. B (closed form only for 𝒩(0, I) shown) | ⚠️ / ➖ | General Gaussian–Gaussian KL is standard. Fine without a citation. |
| 946 s1–s2 | Black–Litterman blends a market prior with investor views expressed as linear relations with confidence. | Black & Litterman; Satchell & Scowcroft | **Neither PDF is in Sources**, and neither is in K²VAE's references | ⬇️ | Cannot verify. Supply the PDFs. |
| 946 s3 | This shows the approach is workable and interpretable. | — | — | 🛠 | |
| 948 | An informative prior could narrow intervals, discourage flat means, and combine KalmanNet with expertise. | — | — | 🛠 | Speculative, hedged with "could". |
| 950 | Explain the gap: our implementation differs, or K²VAE is sensitive to unstated choices; test by cross-running. | — | — | 🛠 | |

---

## 9. Appendix (L967–1012)

| Line | Statement (abridged) | Cite | Source → location | Status | Notes |
|---|---|---|---|---|---|
| 967–979 | Sweep dashboards and captions. | — | — | 🖼 | Not checked. |
| 983 s1 | Plots for **all three models at all four horizons**. | — | File contents: K²VAE ×4, Koopa ×4, **PatchTST ×3** (96, 192, 336) | ❌ | **The PatchTST 720 figure is missing.** The file ends at line 1012 with PatchTST 336. |
| 983 s2–s6 | Plot conventions; only K²VAE shows reconstruction; six of seven channels. | — | PNGs ✓ | 🛠 ✓ | "The model's 95% PI" here, but L680 says the band is the decoder's spread only. Keep the wording consistent. |
| 987–1012 | Figure captions. | — | — | 🖼 | |
---

## 10. Sources

### 10.1 In `Thesis/Sources/` and used

| File | Bib key | Used for |
|---|---|---|
| `k2vae` | `k2vae2025` | Throughout. Tables 1, 2, 9 and 10 for the numbers. |
| `brunton2021_koopman` | `koopman2021modern` | Koopman, DMD, eDMD, NN embeddings. |
| `koopa2023` | `liu2023koopa` | Lit review, §4.3.2, stability motivation, eDMD notation. |
| `patchtst2023` | `nie2023patchtst` | Lit review, §4.3.1, channel independence, overfitting, random walk, instance norm before patching. |
| `vaswani2017` | `vaswani2017attention` | Transformer section. |
| `ba2016_layernorm`, `he2016_resnet` | *(not in bib)* | L155 benefit claim (optional). |
| `triformer2022` | `cirstea2022triformer` | Lit review. |
| `kalman1960` | `kalman1960new` | KF (general). |
| `welch1995` | `welch1995` | KF equations (cited). |
| `kalmannet2021` | `kalmannet2021` | EKF/UKF, KalmanNet. |
| `krishnan2015_dkf` | `krishnan2015deep` | Lit review (↔ at L65). |
| `fraccaro2017_kvae` | `fraccaro2017disentangled` | Lit review. |
| `klushyn2021_latent` | `klushyn2021latent` | Lit review; nearest source for over-regularisation (L852). |
| `rangapuram2018_deepstate` | `rangapuram2018deepstate` | Lit review. |
| `hyndman2021_fpp3_notes` | `hyndman2021fpp` | Lit review (quotes only). |
| `kingma2014` | `kingma2014vae` | VAE section. |
| `doersch2016` | `doersch2016tutorial` | VAE and CVAE section. |
| `sohn2015` | `sohn2015learning` | CVAE. |
| `ghosh2020_rae` | `ghosh2020variational` | AE latent-space and VAE smoothness (L217, L243). Partial support (see rows). |
| `hinton2006` | `hinton2006reducing` | AE section. |
| `lan_mezic2013` | — | Not needed. Brunton covers it. |

### 10.2 ⬇️ Please download (all but RevIN are in K²VAE's reference list)

| Source | Needed for | K²VAE ref |
|---|---|---|
| Kim et al. 2022, *RevIN*, ICLR. https://openreview.net/pdf?id=cGDAkQo1C0p | L326 claims about global standardisation, drift and the affine rationale; equation numbers. | No (cited by PatchTST and Koopa) |
| Higgins et al. 2017, *β-VAE*, ICLR. https://openreview.net/pdf?id=Sy2fzU9gl | β-weighted KL (L455–460, ablation). | Yes |
| Zhou et al. 2021, *Informer*, AAAI | ETTh1 description (L474, L647). | Yes |
| Qiu et al. 2024, *TFB*, PVLDB | Wind dataset provenance and "well-known" (L483). | Yes |
| Zhang et al. 2024, *ProbTS*, NeurIPS | Benchmark and protocol (L481, L720). | Yes |
| Zeng et al. 2023, *Are Transformers Effective…*, AAAI | Optional: L67 secondary citation accepted as is (22 Oct). Only needed if Jake wants primary sources (L59 flag). | Yes |
| Rasul et al. 2021a (*TimeGrad*), 2021b (*conditioned flows*) | Autoregressive diffusion and flows (L356). | Yes |
| Matheson & Winkler 1976 | CRPS origin (L602). | Yes |
| Black & Litterman 1992; Satchell & Scowcroft 2000 | L946 (already cited). | No |
| *Optional:* Koopman 1931; Schmid 2010; Simon 2001; Salinas 2020 (DeepAR) | Primary sources for history, DMD, KF, autoregressive RNNs. | Yes |

### 10.3 No candidate in Sources or K²VAE's references (new search needed)

- Joseph-form name (a Kalman-filter text, e.g. Simon 2006 *Optimal State Estimation*).
- Cholesky name (e.g. Golub & Van Loan).
- Bayesian optimisation and EI (e.g. Jones et al. 1998; Snoek et al. 2012), plus W&B documentation for the EI claim.
- CRPS sample identity (Gneiting & Raftery 2007).
- AE "disjoint clusters / empty regions" detail (L217 s4–s5). Not in Ghosh. Drop it or find a source.
- Markov / non-Markov argument (L89), unless reframed or cut.
- eDMD primary source (Williams et al. 2015, cited inside Brunton), only if a primary source is wanted.
