# CALCULUS RESEARCH STANDARD OPERATING PROCEDURES MANUAL

**Document Classification:** CONFIDENTIAL -- INTERNAL USE ONLY
**Version:** 1.0
**Effective Date:** March 3, 2026
**Review Cycle:** Annual (Next Review: March 2027)
**Document Owner:** Chief Credit Officer / Chief Technology Officer
**Approved By:** Board Risk Committee

---

## TABLE OF CONTENTS

- Section I: Governance Framework
- Section II: Deal Lifecycle Workflow
- Section III: Underwriting SOP
- Section IV: Due Diligence SOP
- Section V: Legal Execution SOP
- Section VI: Portfolio Monitoring SOP
- Section VII: Investor Reporting SOP
- Section VIII: AI Governance and Model Oversight
- Section IX: Data Security and Compliance
- Section X: Incident and Risk Management
- Appendix A: Glossary of Terms
- Appendix B: Engine Reference Architecture
- Appendix C: Approval Authority Matrix (Summary)
- Appendix D: Revision History

---

## SECTION I: GOVERNANCE FRAMEWORK

### 1.1 Purpose and Scope

This Standard Operating Procedures Manual governs all operational processes executed within the Calculus Research AI-Powered Institutional Credit Operating System. Every engine, workflow, decision checkpoint, and human oversight requirement documented herein constitutes a binding operational standard. Deviation from these procedures requires written authorization from the appropriate authority as defined in the Decision Authority Matrix (Section 1.4).

This manual applies to all personnel, contractors, and automated systems operating within or interfacing with the Calculus Research platform, including but not limited to: Calculus Intelligence, Lex Intelligence Ultimate, Forge Intelligence, the Lead Ranking Engine, Skip Trace Engine, Shovels Engine, Underwriting Engine, Due Diligence Engine, Demand Letter Engine, Portfolio Monitoring Engine, and the Investor Reporting Engine.

### 1.2 Organizational Roles and Responsibilities

#### 1.2.1 Board Risk Committee

- **Composition:** Minimum three independent directors, the Chief Risk Officer (CRO), and the Chief Executive Officer (CEO).
- **Meeting Cadence:** Quarterly; emergency sessions convened within 24 hours upon material risk event.
- **Responsibilities:**
  1. Approve and ratify risk appetite statements and credit policy limits.
  2. Review and approve all AI model deployment decisions for engines with credit-decisioning authority.
  3. Oversee aggregate portfolio risk metrics, concentration limits, and watchlist trends.
  4. Approve exceptions to underwriting policy exceeding $10,000,000 in exposure.
  5. Receive and act upon quarterly Model Risk Management reports.
  6. Approve changes to this SOP Manual.

#### 1.2.2 Chief Credit Officer (CCO)

- **Reports to:** CEO, with dotted line to Board Risk Committee.
- **Responsibilities:**
  1. Final credit approval authority for exposures between $5,000,000 and $10,000,000.
  2. Oversight of all Underwriting Engine output and credit memo quality.
  3. Chair the Credit Committee (weekly).
  4. Approve or reject escalated exceptions from Senior Underwriters.
  5. Annual review and certification of underwriting model parameters.
  6. Sign-off on Investment Committee (IC) memoranda prior to committee presentation.

#### 1.2.3 Chief Risk Officer (CRO)

- **Reports to:** CEO, with independent reporting line to Board Risk Committee.
- **Responsibilities:**
  1. Ownership of the Model Risk Management framework.
  2. Approval authority for all model changes, recalibrations, and new engine deployments.
  3. Oversight of the Due Diligence Engine output and fraud detection protocols.
  4. Management of the portfolio watchlist and early warning system triggers.
  5. Quarterly stress testing coordination and reporting.
  6. Incident command authority for credit events, model failures, and data breaches.

#### 1.2.4 Chief Technology Officer (CTO)

- **Reports to:** CEO.
- **Responsibilities:**
  1. Technical ownership of all engine infrastructure, deployment pipelines, and system availability.
  2. Management of Forge Intelligence code generation standards and review protocols.
  3. Oversight of data security architecture, encryption standards, and access controls.
  4. Disaster recovery and business continuity plan ownership.
  5. Coordination with CRO on model version control, rollback procedures, and drift detection.
  6. Approval authority for infrastructure changes affecting engine performance or availability.

#### 1.2.5 Head of Legal and Compliance

- **Reports to:** CEO, with independent reporting line to Board Risk Committee.
- **Responsibilities:**
  1. Oversight of Lex Intelligence Ultimate output and legal analysis quality.
  2. Final review authority for all Demand Letter Engine outputs prior to dispatch.
  3. Regulatory compliance monitoring and reporting.
  4. Management of documentation retention policies.
  5. Coordination with external counsel on complex matters.
  6. Regulatory inquiry response coordination.

#### 1.2.6 Senior Underwriter

- **Reports to:** CCO.
- **Responsibilities:**
  1. Review and validate all Underwriting Engine outputs for deals assigned.
  2. Credit approval authority for exposures up to $2,500,000.
  3. Escalate exceptions, policy deviations, and risk flags to CCO.
  4. Conduct secondary review of peer underwriting when assigned.
  5. Document all manual overrides with written justification in the audit log.

#### 1.2.7 Credit Analyst

- **Reports to:** Senior Underwriter.
- **Responsibilities:**
  1. Prepare data inputs for Underwriting Engine ingestion.
  2. Verify third-party data accuracy (appraisals, rent rolls, financial statements).
  3. Review and annotate Underwriting Engine outputs for completeness.
  4. Draft initial sections of IC memoranda under Senior Underwriter supervision.
  5. No independent credit approval authority.

#### 1.2.8 Due Diligence Analyst

- **Reports to:** CRO.
- **Responsibilities:**
  1. Review and validate all Due Diligence Engine outputs.
  2. Conduct manual verification of flagged items (litigation hits, entity discrepancies).
  3. Escalate confirmed fraud indicators to CRO within 2 hours of detection.
  4. Maintain chain-of-custody documentation for all due diligence artifacts.

#### 1.2.9 Portfolio Manager

- **Reports to:** CCO, with dotted line to CRO.
- **Responsibilities:**
  1. Review Portfolio Monitoring Engine alerts and covenant compliance reports.
  2. Manage watchlist additions, upgrades, and removals per established criteria.
  3. Coordinate remediation plans for underperforming credits.
  4. Prepare quarterly portfolio performance summaries for Board Risk Committee.

#### 1.2.10 AI/ML Engineer

- **Reports to:** CTO, with dotted line to CRO for model risk matters.
- **Responsibilities:**
  1. Develop, test, and deploy model updates across all engines.
  2. Execute model validation testing per Section VIII procedures.
  3. Monitor drift detection dashboards and escalate threshold breaches.
  4. Maintain model documentation, version logs, and rollback packages.
  5. No authority to deploy model changes to production without CRO sign-off.

### 1.3 Committee Structure

#### 1.3.1 Credit Committee

- **Chair:** CCO
- **Members:** CRO, Senior Underwriters (rotating), Head of Legal (as needed)
- **Cadence:** Weekly (Tuesday, 10:00 AM); ad hoc sessions for time-sensitive deals.
- **Quorum:** CCO plus minimum two Senior Underwriters.
- **Authority:**
  - Approve/deny/condition credit requests from $2,500,001 to $10,000,000.
  - Approve underwriting exceptions within policy tolerances.
  - Refer deals exceeding $10,000,000 to Board Risk Committee with recommendation.
- **Documentation:** Meeting minutes recorded, decisions logged in deal management system within 24 hours. All votes recorded by name.

#### 1.3.2 Model Risk Committee

- **Chair:** CRO
- **Members:** CTO, Head of AI/ML Engineering, CCO, external model validation consultant (annual review).
- **Cadence:** Monthly; emergency sessions within 48 hours upon model incident.
- **Quorum:** CRO plus CTO.
- **Authority:**
  - Approve or reject new engine deployments to production.
  - Approve or reject model recalibrations and parameter changes.
  - Order model suspension upon confirmed performance degradation.
  - Commission independent model validation reviews.
- **Documentation:** All decisions logged in the Model Risk Register. Meeting minutes retained for 7 years.

#### 1.3.3 Technology Steering Committee

- **Chair:** CTO
- **Members:** CRO, Head of Information Security, Lead AI/ML Engineer, Infrastructure Lead.
- **Cadence:** Bi-weekly.
- **Authority:**
  - Approve infrastructure changes affecting engine availability.
  - Prioritize engineering backlog items with risk or compliance impact.
  - Approve disaster recovery test schedules.

### 1.4 Decision Authority Matrix

| Decision Type | Up to $1,000,000 | $1,000,001 - $2,500,000 | $2,500,001 - $5,000,000 | $5,000,001 - $10,000,000 | Over $10,000,000 |
|---|---|---|---|---|---|
| Credit Approval | Senior Underwriter | Senior Underwriter | Credit Committee | Credit Committee + CCO | Board Risk Committee |
| Exception to LTV Policy | Senior Underwriter + CCO notification | CCO | Credit Committee | Credit Committee + CCO | Board Risk Committee |
| Exception to DSCR Policy | Senior Underwriter + CCO notification | CCO | Credit Committee | Credit Committee + CCO | Board Risk Committee |
| Loan Modification | Senior Underwriter | CCO | Credit Committee | Credit Committee + CCO | Board Risk Committee |
| Watchlist Addition | Portfolio Manager | Portfolio Manager + CCO notification | CCO | Credit Committee | Board Risk Committee |
| Demand Letter Issuance | Head of Legal | Head of Legal | Head of Legal + CCO | Credit Committee + Head of Legal | Board Risk Committee |
| Write-off/Charge-off | CCO | CCO | Credit Committee | Board Risk Committee | Board Risk Committee |

| Decision Type | Authority |
|---|---|
| New Engine Deployment | CRO + CTO joint approval via Model Risk Committee |
| Model Parameter Change | CRO approval via Model Risk Committee |
| Emergency Model Suspension | CRO (unilateral authority, report to Board within 24 hours) |
| Data Schema Change | CTO approval, CRO notification |
| Access Control Modification | CTO + CISO joint approval |
| Vendor Data Source Change | CRO + CTO joint approval |
| SOP Manual Amendment | Board Risk Committee ratification |

### 1.5 Model Approval Process for New Engine Deployment

#### 1.5.1 Pre-Deployment Requirements

Before any new engine or material engine modification is deployed to production, the following steps shall be completed in sequence:

1. **Development Specification Review**
   - AI/ML Engineer submits a Model Development Specification document to the CRO.
   - Specification includes: purpose, input variables, output schema, training data description, performance benchmarks, known limitations, and intended use constraints.
   - CRO reviews within 5 business days and returns approval to proceed to testing, or requests revisions.

2. **Development and Unit Testing**
   - Forge Intelligence generates code per approved specification.
   - All generated code undergoes mandatory peer review by a second AI/ML Engineer.
   - Unit test coverage must achieve minimum 90% for all decision-logic modules.
   - Test results documented and appended to the Model Development file.

3. **Model Validation (Independent)**
   - An independent validator (internal team member not involved in development, or external consultant) conducts validation testing.
   - Validation includes: back-testing on historical data (minimum 24 months), sensitivity analysis, stress testing under adverse scenarios, and bias assessment.
   - Validation report submitted to CRO within 15 business days of test initiation.
   - Validation must confirm model performs within acceptable tolerance bands (defined per engine type in Section VIII).

4. **Model Risk Committee Review**
   - CRO presents validation results and deployment recommendation to Model Risk Committee.
   - Committee reviews: validation findings, risk assessment, operational readiness, rollback plan, and monitoring plan.
   - Committee votes to approve, approve with conditions, or deny deployment.
   - Approval requires unanimous consent of CRO and CTO.

5. **Staged Deployment**
   - Approved models deploy first to a shadow environment running parallel to production for minimum 10 business days.
   - Shadow outputs compared against production engine outputs; discrepancies exceeding 5% trigger review.
   - Upon successful shadow period, CTO authorizes production cutover.
   - Rollback package must be tested and confirmed operational before production cutover.

6. **Post-Deployment Monitoring**
   - Heightened monitoring for 30 calendar days post-deployment.
   - Daily drift detection checks (versus weekly standard cadence).
   - Any performance degradation exceeding tolerance thresholds triggers immediate escalation per Section VIII.

#### 1.5.2 Model Change Classification

| Change Type | Classification | Approval Required |
|---|---|---|
| New engine deployment | Material | Full Model Risk Committee |
| Algorithm change to existing engine | Material | Full Model Risk Committee |
| Training data refresh (same schema) | Moderate | CRO approval |
| Parameter recalibration within approved bounds | Moderate | CRO approval |
| User interface change (no model logic impact) | Minor | CTO approval |
| Bug fix (no model logic impact) | Minor | CTO approval |
| Documentation update only | Administrative | AI/ML Engineering Lead |

---

## SECTION II: DEAL LIFECYCLE WORKFLOW

### 2.1 Overview

Every credit opportunity processed through the Calculus Research platform follows a standardized eight-stage lifecycle. No stage may be skipped. Each stage produces defined outputs that serve as mandatory inputs to the subsequent stage. The Calculus Intelligence engine serves as the Master Reasoning Engine coordinating workflow orchestration, stage-gate validation, and cross-engine data integrity checks throughout the lifecycle.

**Lifecycle Stages:**

```
Lead Intake --> Scoring --> Underwriting --> Due Diligence --> Legal --> Closing --> Monitoring --> Reporting
```

### 2.2 Stage 1: Lead Intake

- **Responsible Engine:** Shovels Engine (building permit ingestion), Skip Trace Engine (contact discovery)
- **Supporting Engine:** Calculus Intelligence (data normalization and deduplication)
- **Human Oversight:** Credit Analyst (data quality review)

#### 2.2.1 Inputs

1. Building permit records ingested via Shovels Engine (jurisdiction feeds, batch uploads, API integrations).
2. Property data from integrated third-party sources (tax records, deed records, zoning data).
3. Manual lead submissions from origination team (via standardized intake form, Form OG-001).
4. Referral submissions from existing borrower relationships.

#### 2.2.2 Process Steps

1. Shovels Engine ingests raw permit data per configured jurisdiction schedule (daily batch at 02:00 UTC for automated feeds; real-time for API integrations).
2. Calculus Intelligence normalizes ingested data to the platform standard schema: property address (USPS-validated), owner entity name, permit type, permit value, filing date, jurisdiction code.
3. Calculus Intelligence executes deduplication logic against the existing lead database. Duplicate threshold: 95% match on address + entity name. Duplicates are flagged, not deleted, and routed to Credit Analyst queue for manual resolution.
4. Skip Trace Engine enriches each unique lead record with contact information: primary contact name, phone numbers (up to 3), email addresses (up to 3), registered agent information, mailing address.
5. Skip Trace Engine assigns a Contact Confidence Score (0-100) to each enriched record based on source reliability, recency, and cross-reference validation.
6. Credit Analyst reviews the intake queue daily. Analyst verifies: (a) data completeness -- all required fields populated, (b) data plausibility -- permit values within expected range for jurisdiction and property type, (c) duplicate resolution -- confirm or override deduplication flags.
7. Validated leads are promoted to "Intake Complete" status and queued for scoring.

#### 2.2.3 Outputs

- Validated lead record with standardized property data, enriched contact information, and Contact Confidence Score.
- Intake validation log (analyst name, timestamp, actions taken, flags resolved).

#### 2.2.4 Approval Checkpoint

- No credit approval required at this stage.
- Credit Analyst confirms data quality sign-off via system checkbox (logged with timestamp and user ID).

#### 2.2.5 Audit Trail Requirements

- All raw ingested records retained in immutable data store for 7 years.
- All deduplication decisions logged (automated and manual).
- Skip Trace Engine source attributions retained per record.
- Analyst validation actions logged with user ID, timestamp, and action description.

#### 2.2.6 Exception Handling

- **Incomplete Data:** If mandatory fields cannot be populated after Skip Trace enrichment, lead is placed in "Intake Hold" status. Credit Analyst may request manual research (maximum 5 business day hold before disposition to "Intake Rejected" or "Intake Complete").
- **High Volume Anomaly:** If daily intake volume exceeds 150% of the trailing 30-day average, Calculus Intelligence generates an alert to the Senior Underwriter and CTO for review of potential data feed anomaly.
- **Skip Trace Failure:** If Skip Trace Engine returns Contact Confidence Score below 30 for all contact methods, lead is flagged for manual outreach attempt before scoring.

### 2.3 Stage 2: Scoring

- **Responsible Engine:** Lead Ranking Engine (composite scoring + AI risk analysis)
- **Supporting Engine:** Calculus Intelligence (scoring orchestration and threshold application)
- **Human Oversight:** Senior Underwriter (threshold review, override authority)

#### 2.3.1 Inputs

1. Validated lead record from Stage 1 (Intake Complete status required).
2. Property data enrichments (tax assessed value, zoning classification, recent comparable sales).
3. Entity data enrichments (business registration status, years in operation, prior lending relationships).
4. Permit data attributes (permit type, estimated project value, contractor information).
5. Market data overlays (MSA-level vacancy rates, rent growth trends, cap rate benchmarks).

#### 2.3.2 Process Steps

1. Lead Ranking Engine receives validated lead record from Calculus Intelligence workflow queue.
2. Engine computes the Composite Lead Score (CLS) on a 0-1000 scale using the following weighted components:
   - Property Quality Score (25% weight): based on location, zoning, tax assessed value, comparable sales data, environmental risk indicators.
   - Project Viability Score (20% weight): based on permit type, estimated project value relative to property value, contractor track record (if available).
   - Entity Creditworthiness Score (25% weight): based on business age, registration status, prior borrowing history (if available), industry risk classification.
   - Market Strength Score (15% weight): based on MSA vacancy, rent growth, cap rate trends, employment growth.
   - Contact Reachability Score (15% weight): derived from Skip Trace Engine Contact Confidence Score.
3. Lead Ranking Engine applies AI risk analysis layer: Calculus Intelligence evaluates the composite score in context, identifying non-obvious risk correlations and generating a Risk Narrative (plain-language explanation of key risk factors and mitigants).
4. Calculus Intelligence applies tier classification based on CLS:
   - **Tier 1 (Priority):** CLS 750-1000. Auto-queued for underwriting. Senior Underwriter notified within 1 hour.
   - **Tier 2 (Standard):** CLS 500-749. Queued for underwriting in standard priority order.
   - **Tier 3 (Review Required):** CLS 300-499. Routed to Senior Underwriter for manual review before underwriting decision.
   - **Tier 4 (Decline):** CLS 0-299. Auto-declined. Decline reason logged. Available for Senior Underwriter override within 10 business days.
5. Senior Underwriter reviews Tier 3 leads within 3 business days and renders a disposition: (a) Promote to Tier 2 with written justification, (b) Decline with documented rationale, (c) Request additional information (returns to Intake with specific data request).
6. All scoring outputs are logged and the lead record advances to the appropriate queue.

#### 2.3.3 Outputs

- Composite Lead Score (0-1000) with component breakdowns.
- Tier classification (1-4).
- AI-generated Risk Narrative.
- Disposition decision (for Tier 3 and overridden Tier 4 leads).

#### 2.3.4 Approval Checkpoint

- Tier 1 and Tier 2: No human approval required to advance to underwriting.
- Tier 3: Senior Underwriter disposition required before advancement.
- Tier 4: Auto-declined; Senior Underwriter may override with written justification (logged).

#### 2.3.5 Audit Trail Requirements

- Complete scoring inputs and outputs retained for 7 years.
- All component scores, weights, and model version identifier logged per lead.
- Risk Narrative text retained as part of the permanent deal record.
- Manual overrides logged with: user ID, timestamp, original score, override decision, written justification.
- Tier 4 override decisions require CCO notification (automated system alert).

#### 2.3.6 Exception Handling

- **Score Calculation Failure:** If Lead Ranking Engine cannot compute a score due to missing data, lead is returned to Stage 1 with a specific data gap report. Credit Analyst has 3 business days to remediate.
- **Model Version Discrepancy:** If Lead Ranking Engine model version does not match the current approved production version (per Model Risk Register), scoring is suspended and escalated to CTO and CRO immediately.
- **Bulk Override Monitoring:** If more than 10% of Tier 4 leads are overridden in any calendar month, CRO is notified for pattern review. Findings reported to Model Risk Committee at next scheduled meeting.

### 2.4 Stage 3: Underwriting

- **Responsible Engine:** Underwriting Engine
- **Supporting Engine:** Calculus Intelligence (reasoning validation, cross-reference checks)
- **Human Oversight:** Credit Analyst (data preparation), Senior Underwriter (output review and approval), CCO (escalated approvals)

#### 2.4.1 Inputs

1. Scored lead record (Tier 1 or Tier 2, or promoted Tier 3) from Stage 2.
2. Borrower financial statements (minimum 2 years historical; 3 years preferred).
3. Property appraisal (dated within 180 days; 90 days for transitional assets).
4. Rent roll (current, dated within 60 days).
5. Operating statements (minimum 2 years historical).
6. Environmental reports (Phase I minimum; Phase II if triggered).
7. Insurance documentation (current coverage summary).
8. Loan request parameters (requested amount, term, rate type, amortization preference).

#### 2.4.2 Process Steps

1. Credit Analyst assembles the underwriting data package and uploads to the Underwriting Engine intake module. Analyst completes the Data Completeness Checklist (Form UW-001) confirming all required documents are present and within acceptable date ranges.
2. Underwriting Engine ingests the data package and executes the following analytical modules in sequence:
   - **Property Valuation Module:** Triangulates value using income approach (direct capitalization and discounted cash flow), sales comparison approach, and cost approach (where applicable). Engine flags valuation variance exceeding 10% across approaches for human review.
   - **Cash Flow Modeling Module:** Projects net operating income (NOI) over the loan term using base case, upside case, and downside case assumptions. Downside case applies minimum 200 basis point cap rate expansion and 10% revenue decline from base.
   - **Debt Service Coverage Ratio (DSCR) Calculation:** Computes DSCR under all three scenarios. Minimum acceptable DSCR thresholds: Stabilized assets 1.25x, Transitional assets 1.10x (at stabilization), Construction 1.00x (at projected stabilization).
   - **Loan-to-Value (LTV) Calculation:** Computes LTV based on the lower of appraised value and engine-derived value. Maximum LTV thresholds: Stabilized 75%, Transitional 70%, Construction 65%.
   - **Debt Yield Calculation:** Computes debt yield (NOI / Loan Amount). Minimum acceptable: 8.0% for stabilized, 7.0% at projected stabilization for transitional.
   - **Loan Structure Optimization:** Engine recommends optimal loan structure (amount, term, amortization, rate, covenants) to satisfy both borrower request and risk policy constraints.
3. Underwriting Engine generates the draft Investment Committee Memorandum (IC Memo), including:
   - Executive summary with recommendation (Approve, Approve with Conditions, Decline).
   - Property and market analysis.
   - Borrower and guarantor analysis.
   - Financial analysis with all three scenarios.
   - Risk factors and mitigants.
   - Recommended loan terms and covenants.
   - Compliance verification against all policy thresholds.
4. Calculus Intelligence performs a cross-reference validation: checks internal consistency of the IC Memo (e.g., do stated DSCR figures match the cash flow model outputs), verifies market data references against current sources, and flags logical inconsistencies.
5. Credit Analyst reviews the draft IC Memo for: data accuracy, completeness, formatting compliance, and consistency with uploaded source documents. Analyst annotates any discrepancies found.
6. Senior Underwriter conducts substantive review of the IC Memo: evaluates risk assessment quality, validates assumptions, stress-tests the cash flow projections, and renders a recommendation.
7. For deals within the Senior Underwriter approval authority (up to $2,500,000), the Senior Underwriter may approve, approve with conditions, or decline. Decision documented in system with written rationale.
8. For deals exceeding $2,500,000, the Senior Underwriter submits the IC Memo with recommendation to Credit Committee (or CCO/Board per the Decision Authority Matrix).

#### 2.4.3 Outputs

- Completed IC Memorandum with all supporting analyses.
- Property valuation report (engine-generated).
- Cash flow model (base, upside, downside).
- Recommended loan terms and covenant package.
- Credit decision (Approve / Approve with Conditions / Decline) with approver identity and rationale.

#### 2.4.4 Approval Checkpoint

- Credit Analyst data completeness sign-off (Form UW-001).
- Senior Underwriter substantive review sign-off.
- Credit approval per Decision Authority Matrix thresholds.
- CCO sign-off required on all IC Memos presented to Credit Committee or Board.

#### 2.4.5 Audit Trail Requirements

- All uploaded source documents retained in the permanent deal file for the life of the loan plus 7 years.
- Underwriting Engine model version, run timestamp, and full input/output log retained.
- Calculus Intelligence cross-reference validation report retained.
- All human review annotations, comments, and decision rationale retained.
- Manual overrides of engine recommendations logged with: override description, justification, approver identity, and timestamp.
- Credit Committee meeting minutes (for deals presented to committee) cross-referenced to deal file.

#### 2.4.6 Exception Handling

- **Policy Threshold Breach:** If any deal metric falls outside policy limits (e.g., LTV exceeds 75% for stabilized), the Underwriting Engine automatically flags the exception. The deal cannot advance without an Exception Approval, which requires one level of additional authority above the standard approval threshold for the deal size.
- **Appraisal Dispute:** If the engine-derived value differs from the appraised value by more than 15%, Senior Underwriter must document the reconciliation rationale or order a second appraisal.
- **Incomplete Financial Data:** If borrower financials are incomplete, Credit Analyst issues a data request with a 10 business day response deadline. After two unremediated requests, the deal is automatically declined.
- **Engine Error:** If the Underwriting Engine returns an error or incomplete output, the deal is suspended. CTO is notified. No manual underwriting may substitute for engine output without CRO written approval.

### 2.5 Stage 4: Due Diligence

- **Responsible Engine:** Due Diligence Engine
- **Supporting Engine:** Calculus Intelligence (entity resolution, risk correlation analysis), Lex Intelligence Ultimate (litigation analysis)
- **Human Oversight:** Due Diligence Analyst (output validation, escalation), CRO (fraud escalation)

Full procedures detailed in Section IV.

#### 2.5.1 Summary Inputs

1. Approved or conditionally approved credit package from Stage 3.
2. Borrower and guarantor entity information.
3. Property identification and ownership chain.

#### 2.5.2 Summary Outputs

- Due Diligence Report: entity verification, litigation scan results, financial verification, risk flags.
- Clearance status: Cleared, Cleared with Conditions, Hold (pending further investigation), Fail.

#### 2.5.3 Approval Checkpoint

- Due Diligence Analyst clearance sign-off.
- CRO review required for any "Hold" or "Fail" disposition.
- Any confirmed fraud flag requires immediate CRO notification and deal suspension.

### 2.6 Stage 5: Legal Execution

- **Responsible Engine:** Demand Letter Engine (legal document generation), Lex Intelligence Ultimate (compliance validation, legal meta-analysis)
- **Supporting Engine:** Calculus Intelligence (document assembly orchestration)
- **Human Oversight:** Head of Legal (final review and approval)

Full procedures detailed in Section V.

#### 2.6.1 Summary Inputs

1. Approved credit package with all conditions satisfied.
2. Due Diligence clearance.
3. Loan document templates (per asset class and jurisdiction).

#### 2.6.2 Summary Outputs

- Complete loan document package.
- Compliance validation report.
- Legal review certification.

#### 2.6.3 Approval Checkpoint

- Head of Legal review and sign-off on all loan documents.
- External counsel review required for deals exceeding $5,000,000 or involving non-standard structures.

### 2.7 Stage 6: Closing

- **Responsible Engine:** Calculus Intelligence (closing checklist orchestration and verification)
- **Human Oversight:** Senior Underwriter (closing condition verification), Head of Legal (document execution oversight)

#### 2.7.1 Inputs

1. Fully executed loan document package from Stage 5.
2. Closing condition satisfaction evidence (insurance certificates, title policy, organizational documents, legal opinions).
3. Funding authorization (per Decision Authority Matrix).

#### 2.7.2 Process Steps

1. Calculus Intelligence generates the Closing Checklist (Form CL-001) based on the approved loan terms and conditions.
2. Credit Analyst collects and uploads all closing condition satisfaction documents.
3. Calculus Intelligence verifies each checklist item: document present, dated appropriately, names and amounts match approved terms.
4. Senior Underwriter reviews the completed checklist and certifies all conditions satisfied.
5. Head of Legal confirms document execution is proper (authorized signatories, notarization where required, recording instructions prepared).
6. Funding authorization obtained per Decision Authority Matrix.
7. Calculus Intelligence generates a Closing Confirmation Record with: deal identifiers, final loan terms, closing date, funding amount, and all checklist item dispositions.
8. Deal status updated to "Active -- Performing" and automatically enrolled in Portfolio Monitoring Engine.

#### 2.7.3 Outputs

- Completed Closing Checklist with all items verified.
- Closing Confirmation Record.
- Funded loan record enrolled in portfolio monitoring.

#### 2.7.4 Approval Checkpoint

- Senior Underwriter closing condition certification.
- Head of Legal document execution certification.
- Funding authorization per Decision Authority Matrix.

#### 2.7.5 Audit Trail Requirements

- Complete closing file retained for life of loan plus 7 years.
- All closing condition documents retained in original form.
- Funding wire instructions and confirmation retained.
- All checklist verifications logged with user ID and timestamp.

### 2.8 Stage 7: Monitoring

- **Responsible Engine:** Portfolio Monitoring Engine
- **Supporting Engine:** Calculus Intelligence (trend analysis, early warning correlation)
- **Human Oversight:** Portfolio Manager (alert review, watchlist management), CCO (escalated actions)

Full procedures detailed in Section VI.

### 2.9 Stage 8: Reporting

- **Responsible Engine:** Investor Reporting Engine
- **Supporting Engine:** Calculus Intelligence (data aggregation validation, narrative generation)
- **Human Oversight:** Portfolio Manager (report review), CCO (report certification), CFO (financial data sign-off)

Full procedures detailed in Section VII.

---

## SECTION III: UNDERWRITING SOP

### 3.1 Purpose

This section establishes the detailed standard operating procedures for the underwriting function executed through the Underwriting Engine with human oversight. These procedures ensure consistent, auditable, and policy-compliant credit analysis for all commercial real estate (CRE) lending decisions.

### 3.2 Data Ingestion Protocol

#### 3.2.1 Required Data Package

The following documents constitute the minimum required data package. The Underwriting Engine will not initiate analysis until the Credit Analyst certifies completeness via Form UW-001.

| Document | Requirement | Maximum Age |
|---|---|---|
| Borrower Financial Statements (audited preferred) | 2 years minimum, 3 years preferred | Fiscal year end within 15 months |
| Guarantor Personal Financial Statement | Current | Dated within 90 days |
| Property Appraisal (MAI-designated appraiser) | Required | 180 days (90 days for transitional) |
| Current Rent Roll | Required | 60 days |
| Historical Operating Statements | 2 years minimum | Most recent trailing 12 months within 90 days |
| Pro Forma Operating Budget | Required for transitional/construction | Prepared within 120 days |
| Environmental Report (Phase I) | Required | 12 months |
| Environmental Report (Phase II) | If triggered by Phase I | 12 months |
| Title Commitment | Required | 60 days at closing |
| Survey | Required | Current or updated within 5 years with no material changes certified |
| Insurance Summary | Required | Current coverage |
| Organizational Documents (borrower entity) | Required | Current certified copies |
| Zoning Confirmation | Required | 12 months |

#### 3.2.2 Data Ingestion Steps

1. Credit Analyst uploads documents to the secure document management module within the platform.
2. Calculus Intelligence performs automated document classification: identifies document type, extracts metadata (date, author, subject entity), and maps to the required data package checklist.
3. For structured data (financial statements, rent rolls), the Underwriting Engine executes optical character recognition (OCR) and data extraction. Extracted data is presented to the Credit Analyst for verification against source documents.
4. Credit Analyst verifies extracted data accuracy. Any discrepancy is corrected manually with notation of the correction reason. Corrections are logged in the audit trail.
5. Credit Analyst completes Form UW-001, certifying:
   - All required documents present.
   - All documents within acceptable date ranges.
   - All extracted data verified against source documents.
   - Any data gaps identified and documented with explanation.
6. Upon Form UW-001 certification, the Underwriting Engine ingestion process initiates automatically.

#### 3.2.3 Data Quality Controls

- **Automated Validation Rules:** The Underwriting Engine applies validation rules during ingestion: (a) financial statement foot and cross-foot verification, (b) rent roll unit count versus property description reconciliation, (c) operating statement period coverage gap detection, (d) appraisal value reasonableness check against tax assessed value (flag if variance exceeds 30%).
- **Failed Validation:** If any automated validation rule fails, ingestion halts. A specific error report is generated identifying the failed rule, the affected data, and the suggested remediation. Credit Analyst must remediate and re-certify before ingestion resumes.

### 3.3 Risk Scoring Methodology

#### 3.3.1 Primary Credit Metrics

The Underwriting Engine computes the following primary credit metrics for every deal. These metrics form the foundation of the credit recommendation.

**Debt Service Coverage Ratio (DSCR)**

- Formula: Net Operating Income / Annual Debt Service
- Computed under three scenarios:
  - **Base Case:** Using in-place or reasonably projected income and expenses.
  - **Upside Case:** Using borrower's best-case projections, validated against market data.
  - **Downside Case:** Applying stress adjustments -- minimum 200 basis point cap rate expansion and 10% gross revenue decline from base case.
- Minimum Acceptable DSCR Thresholds:

| Asset Type | Base Case Minimum | Downside Minimum |
|---|---|---|
| Stabilized Multifamily | 1.25x | 1.05x |
| Stabilized Office | 1.30x | 1.10x |
| Stabilized Retail | 1.30x | 1.10x |
| Stabilized Industrial | 1.25x | 1.05x |
| Transitional (at stabilization) | 1.10x | 0.95x |
| Construction (at projected stabilization) | 1.00x | 0.90x |

- Deals falling below base case minimums require Exception Approval per Section 1.4.
- Deals falling below downside minimums are automatically declined (no exception available without Board Risk Committee approval).

**Loan-to-Value Ratio (LTV)**

- Formula: Loan Amount / Property Value
- Property Value defined as the LOWER of: (a) independent appraisal (MAI-designated), (b) Underwriting Engine derived value.
- Maximum LTV Thresholds:

| Asset Type | Maximum LTV |
|---|---|
| Stabilized Multifamily | 75% |
| Stabilized Office | 70% |
| Stabilized Retail | 70% |
| Stabilized Industrial | 75% |
| Transitional | 70% (based on as-is value) |
| Construction | 65% (based on as-complete value, 80% of cost) |

- If the Underwriting Engine derived value differs from the appraisal by more than 15%, the Senior Underwriter must document a value reconciliation in the IC Memo.

**Debt Yield**

- Formula: Net Operating Income / Loan Amount
- Minimum Acceptable Thresholds:

| Asset Type | Minimum Debt Yield |
|---|---|
| Stabilized (all types) | 8.0% |
| Transitional (at projected stabilization) | 7.0% |
| Construction (at projected stabilization) | 7.0% |

#### 3.3.2 Secondary Credit Metrics

The Underwriting Engine also computes and reports the following secondary metrics. These do not carry automatic decline thresholds but are incorporated into the AI risk analysis and IC Memo narrative.

- **Breakeven Occupancy:** The occupancy level at which NOI equals debt service. Flagged if exceeding 85%.
- **Interest Coverage Ratio:** NOI / Interest expense only. Reported for comparison to DSCR.
- **Loan Per Unit (Multifamily) / Loan Per SF (Commercial):** Compared against MSA benchmarks. Flagged if exceeding 90th percentile.
- **Borrower Liquidity:** Post-closing liquidity relative to 12 months of debt service. Flagged if below 9 months.
- **Guarantor Net Worth:** Relative to loan amount. Flagged if below 1.0x loan amount.

#### 3.3.3 Composite Risk Rating

The Underwriting Engine assigns a Composite Risk Rating on a 1-10 scale (1 = lowest risk, 10 = highest risk) synthesizing all primary and secondary metrics, market data, and borrower/guarantor strength.

| Rating | Classification | Description |
|---|---|---|
| 1-2 | Exceptional | All metrics significantly exceed minimums; strong market; proven sponsor |
| 3-4 | Strong | All metrics exceed minimums; stable market; experienced sponsor |
| 5-6 | Acceptable | All metrics meet minimums; adequate market; satisfactory sponsor |
| 7 | Watch | One or more metrics at or near minimum thresholds; marginal market or sponsor factors |
| 8 | Substandard | One or more metrics below minimums (exception required); elevated risk factors |
| 9-10 | Doubtful/Loss | Multiple metrics below minimums; material risk of loss; decline recommended |

### 3.4 Cash Flow Modeling Procedure

#### 3.4.1 Base Case Construction

1. The Underwriting Engine constructs the base case cash flow model using the following hierarchy of inputs:
   - **In-place income:** Current rent roll, validated against operating statements.
   - **Market rent comparison:** Engine compares in-place rents to market rents from comparable property data. If in-place rents exceed market rents by more than 10%, the model applies a blended rate that amortizes the above-market rent premium over remaining lease term.
   - **Vacancy assumption:** The greater of: (a) in-place vacancy, (b) trailing 3-year average vacancy for the subject, (c) current MSA submarket vacancy for the property type, with a minimum floor of 5%.
   - **Operating expenses:** Based on historical trailing 12-month actuals, adjusted for: known contractual increases (insurance, taxes per reassessment), inflationary adjustment (CPI-indexed, minimum 2.0% annual growth), and management fee normalization (minimum 3% of effective gross income for third-party managed, 5% for self-managed).
   - **Capital reserves:** Minimum $250 per unit per year for multifamily; $0.25 per SF per year for commercial; or actual reserve study amount if higher.

2. NOI is projected annually over the loan term plus one year.
3. Debt service is computed using the proposed loan terms (or Underwriting Engine recommended terms if different from borrower request).

#### 3.4.2 Upside Case Construction

1. Applies the borrower's projected income growth assumptions, validated against market data.
2. Maximum allowable income growth rate: MSA-specific market rent growth projection plus 100 basis points.
3. Expense growth capped at CPI projection minus 50 basis points (reflecting operational improvement assumptions).
4. Vacancy assumption: In-place vacancy or borrower projection, whichever is lower, with minimum floor of 3%.

#### 3.4.3 Downside Case Construction

1. Revenue reduced by 10% from base case in Year 1, recovering at 2% per annum thereafter.
2. Expenses increased by 5% from base case in Year 1, growing at CPI plus 100 basis points thereafter.
3. Vacancy increased by 500 basis points from base case, not to exceed 25%.
4. Exit cap rate expanded by 200 basis points from base case assumption.
5. No credit for lease-up or value-add execution in downside case.

#### 3.4.4 Sensitivity Analysis

The Underwriting Engine automatically generates a sensitivity matrix showing DSCR, LTV, and debt yield under the following variable permutations:
- Interest rate: proposed rate, +50bps, +100bps, +150bps, +200bps.
- Vacancy: base case, +5%, +10%, +15%.
- Revenue growth: base case, -2%, -5%, flat (0%).
- Cap rate: base case, +50bps, +100bps, +200bps.

### 3.5 Credit Memo Generation Standards

#### 3.5.1 IC Memo Structure

Every IC Memo generated by the Underwriting Engine shall contain the following sections in the prescribed order:

1. **Cover Page:** Deal name, property address, borrower name, loan amount, recommendation, preparer identification, date.
2. **Executive Summary** (maximum 2 pages): Transaction overview, key credit strengths, key credit risks, recommendation with conditions.
3. **Transaction Summary Table:** Loan terms (amount, rate, term, amortization, LTV, DSCR, debt yield), borrower information summary, property summary.
4. **Property Analysis:** Location description, physical description, condition assessment, environmental summary, market positioning.
5. **Market Analysis:** MSA overview, submarket dynamics, supply/demand analysis, comparable sales analysis, comparable rental analysis.
6. **Borrower and Guarantor Analysis:** Entity history, experience, track record, financial strength (net worth, liquidity), other credit obligations.
7. **Financial Analysis:** Historical operating performance, base/upside/downside cash flow projections, sensitivity analysis, valuation analysis and reconciliation.
8. **Risk Assessment:** Identified risk factors (minimum 5) with corresponding mitigants. Risk factors must include: market risk, credit risk, property risk, structural risk, and execution risk.
9. **Recommended Terms and Covenants:** Proposed loan structure with all covenants, reserves, reporting requirements, and performance triggers.
10. **Appendices:** Supporting data tables, comparable property details, maps, photographs.

#### 3.5.2 Quality Standards

- All financial figures must reconcile to source documents. Calculus Intelligence cross-reference validation must pass without unresolved discrepancies.
- Market data must cite the source and date of the data.
- Risk assessment must be balanced (no section may contain only positive or only negative factors).
- Recommendation must be explicitly supported by the analysis presented.
- All acronyms defined at first use.
- No narrative section may exceed 3 pages without CCO approval.

### 3.6 Secondary Review Protocol and Escalation

#### 3.6.1 Mandatory Secondary Review

Every IC Memo undergoes a secondary review before credit decision. The secondary reviewer is a Senior Underwriter who was not involved in the primary underwriting of the deal.

**Secondary Review Scope:**

1. Verify all primary credit metrics are correctly computed and within policy (or properly exceptioned).
2. Evaluate the reasonableness of key assumptions (vacancy, rent growth, expense growth, cap rate).
3. Assess whether the risk assessment is comprehensive and balanced.
4. Confirm the recommendation is supported by the analysis.
5. Review Calculus Intelligence cross-reference validation results.
6. Document findings on Form UW-002 (Secondary Review Checklist).

**Secondary Review Timeline:** Must be completed within 3 business days of submission.

#### 3.6.2 Escalation Triggers

The following conditions require escalation above the standard approval authority:

1. Any primary credit metric below minimum policy threshold (Exception Approval required, one level above standard authority).
2. Borrower or guarantor has any unresolved litigation exceeding $500,000 (escalate to CCO regardless of deal size).
3. Property located in a jurisdiction under Calculus Intelligence regulatory watch (escalate to Head of Legal for compliance review).
4. Underwriting Engine Composite Risk Rating of 7 or above (escalate to CCO for all deal sizes).
5. Disagreement between primary and secondary reviewer on recommendation (escalate to CCO for resolution).
6. Manual override of any Underwriting Engine output or recommendation (escalate to CCO; document override rationale; CRO notification for pattern tracking).

---

## SECTION IV: DUE DILIGENCE SOP

### 4.1 Purpose

This section establishes the standard operating procedures for the due diligence function executed through the Due Diligence Engine, with support from Calculus Intelligence and Lex Intelligence Ultimate. These procedures ensure thorough investigation of borrower entities, guarantors, properties, and associated parties before credit commitment.

### 4.2 Identity Verification Procedures

#### 4.2.1 Entity Verification

For every borrower entity and guarantor entity, the Due Diligence Engine performs the following verification steps:

1. **Corporate Registry Verification:**
   - Confirm entity is registered and in good standing in its state of formation.
   - Verify registered agent information matches submitted documentation.
   - Confirm entity type (LLC, Corporation, LP, etc.) matches organizational documents provided.
   - Flag any entity registered within the past 12 months as "New Entity -- Enhanced Review Required."

2. **Ownership Chain Verification:**
   - Map the complete ownership chain from the borrowing entity to all individuals holding 20% or more direct or indirect ownership.
   - Cross-reference ownership chain against submitted organizational documents.
   - Flag any discrepancy between the ownership chain presented and the chain discovered by the Due Diligence Engine.
   - Flag any ownership structures involving trusts, offshore entities, or entities in jurisdictions with limited transparency.

3. **Beneficial Ownership Identification:**
   - Identify all individuals who are beneficial owners (25% or more ownership, or significant management control) per applicable regulatory requirements.
   - Collect and verify government-issued identification for each beneficial owner.
   - Screen all beneficial owners against applicable sanctions lists (OFAC SDN, UN, EU) and Politically Exposed Persons (PEP) databases.
   - Due Diligence Analyst must manually confirm all sanctions and PEP screening results. Automated screening alone is insufficient.

4. **Tax Identification Verification:**
   - Verify Employer Identification Number (EIN) for all entities.
   - Verify Social Security Number (SSN) or Individual Taxpayer Identification Number (ITIN) for all individual guarantors.
   - Cross-reference against IRS TIN matching database (where available).

#### 4.2.2 Individual Verification (Guarantors and Key Principals)

1. Verify identity via government-issued photo identification.
2. Verify current residential address.
3. Confirm professional background as represented in the loan application.
4. Screen against sanctions lists, PEP databases, and law enforcement databases.
5. Credit report pull (with proper authorization) -- review for: payment history, outstanding obligations, derogatory items, recent inquiries.

### 4.3 Litigation Screening Protocol

#### 4.3.1 Automated Screening

The Due Diligence Engine, supported by Lex Intelligence Ultimate, performs litigation screening across the following databases and sources:

1. Federal court records (PACER -- all districts).
2. State court records (all states where the entity is registered or operates).
3. Bankruptcy court records (all districts).
4. Regulatory enforcement actions (SEC, CFPB, state financial regulators).
5. Tax lien records (federal and state).
6. Judgment records (federal and state).
7. UCC filing records (all states).

#### 4.3.2 Screening Scope

- Screening is conducted for: the borrower entity, all entities in the ownership chain, all guarantors, and all identified key principals.
- Screening covers a 10-year lookback period.
- Name variations and known aliases are included in the search.

#### 4.3.3 Litigation Classification

Lex Intelligence Ultimate classifies all litigation hits into the following categories:

| Category | Criteria | Action Required |
|---|---|---|
| Critical | Fraud, financial crimes, bankruptcy (active or within 5 years), material regulatory enforcement | Automatic deal suspension. CRO notification within 2 hours. |
| Significant | Litigation with claimed damages exceeding $500,000, multiple active lawsuits (3 or more), pattern of contract disputes | Escalate to Senior Underwriter and CCO. Deal may proceed only with documented risk assessment and CCO approval. |
| Moderate | Litigation with claimed damages between $100,000 and $500,000, isolated disputes | Due Diligence Analyst documents in report. Senior Underwriter must acknowledge in underwriting review. |
| Minor | Litigation with claimed damages under $100,000, resolved matters, routine business disputes | Due Diligence Analyst documents in report. No escalation required. |
| False Positive | Name match with no actual connection to the subject entity or individual | Due Diligence Analyst documents the false positive determination with rationale. |

#### 4.3.4 Manual Verification

- All Critical and Significant hits require Due Diligence Analyst manual verification within 1 business day.
- Manual verification includes: review of actual court filings (not just index entries), confirmation that the named party matches the subject (not a name-only match), and assessment of current status and potential exposure.
- Verified findings are documented with supporting evidence (court document excerpts, filing references) in the Due Diligence Report.

### 4.4 Asset Validation Procedures

#### 4.4.1 Property Ownership Verification

1. Due Diligence Engine verifies property ownership via county recorder records.
2. Confirm the selling or pledging entity is the record owner.
3. Identify all existing liens, encumbrances, and easements.
4. Verify property legal description matches the appraisal and survey.
5. Confirm no pending condemnation or eminent domain actions.

#### 4.4.2 Financial Statement Verification

1. Due Diligence Engine cross-references borrower-submitted financial statements against available public data (SEC filings for public entities, state regulatory filings where applicable).
2. For private entities: verify bank account existence (via bank reference letter or verification of deposit), verify key asset holdings (real estate holdings verified against county records), verify insurance coverage (via certificate of insurance from carrier).
3. Due Diligence Analyst contacts borrower's CPA firm to confirm the financial statements were prepared by the stated firm (for reviewed or audited statements).
4. Flag: unaudited statements for borrowers with aggregate exposure exceeding $5,000,000 (recommend audited statements as a loan condition).

#### 4.4.3 Insurance Verification

1. Verify insurance coverage meets minimum requirements: property coverage at replacement cost, general liability minimum $1,000,000 per occurrence, umbrella/excess liability minimum $5,000,000, flood insurance (if in flood zone), earthquake insurance (if in seismic zone, per policy), builder's risk (for construction loans).
2. Confirm lender is named as mortgagee and additional insured.
3. Verify insurance carrier AM Best rating is A- VII or better.
4. Confirm policy term covers the anticipated loan closing date.

### 4.5 Fraud Flag Indicators and Escalation

#### 4.5.1 Automated Fraud Detection

The Due Diligence Engine monitors for the following fraud indicators throughout the due diligence process. Each indicator is assigned a severity weight (1-10). If the cumulative fraud score for a deal exceeds 15, the deal is automatically suspended.

| Fraud Indicator | Severity Weight | Description |
|---|---|---|
| Identity discrepancy | 8 | Beneficial owner identity documents do not match database records |
| Sanctions hit (confirmed) | 10 | Confirmed match on OFAC, UN, or EU sanctions list |
| Shell entity pattern | 7 | Borrower entity has no operating history, no employees, and was formed within 90 days |
| Financial statement inconsistency | 6 | Material discrepancies between submitted financials and verifiable data |
| Multiple applications | 5 | Same principal applying for multiple loans simultaneously at different institutions (detected via inquiry monitoring) |
| Inflated income | 7 | Rent roll income cannot be verified against market data or bank deposits |
| Undisclosed liens | 8 | Liens discovered on the subject property that were not disclosed in the loan application |
| Straw borrower indicators | 9 | Evidence suggesting the named borrower is not the true party in interest |
| Document manipulation | 9 | OCR analysis or metadata analysis suggests document alteration |
| Rapid ownership transfers | 6 | Property transferred multiple times in 24 months without apparent commercial purpose |

#### 4.5.2 Escalation Procedures

1. **Fraud Score 1-10 (Low):** Due Diligence Analyst documents findings in the Due Diligence Report. No automatic escalation. Senior Underwriter reviews during underwriting.
2. **Fraud Score 11-15 (Moderate):** Due Diligence Analyst escalates to CRO within 4 hours. CRO reviews and determines: (a) additional investigation required, (b) deal may proceed with enhanced conditions, or (c) deal declined.
3. **Fraud Score 16+ (High) or any single indicator with severity weight of 9-10:** Automatic deal suspension. CRO notified within 2 hours. Head of Legal notified. No further processing until CRO authorizes resumption. If confirmed fraud is determined, Suspicious Activity Report (SAR) filing procedures initiated per regulatory requirements.

#### 4.5.3 Human Override of Fraud Flags

- Only the CRO may override a fraud flag.
- Override requires: written explanation of why the flag is not indicative of actual fraud, supporting evidence, and documentation in the permanent deal file.
- All overrides reported to the Board Risk Committee in the quarterly Model Risk Management report.
- Pattern of overrides for the same indicator type triggers Model Risk Committee review of the detection algorithm.

### 4.6 Escalation Rules and Human Override

#### 4.6.1 General Escalation Framework

| Condition | Escalation Path | Timeline |
|---|---|---|
| Critical litigation hit | Due Diligence Analyst to CRO | Within 2 hours |
| Confirmed sanctions match | Due Diligence Analyst to CRO and Head of Legal | Immediately (within 1 hour) |
| Fraud score exceeds 15 | Automatic system alert to CRO | Immediate (automated) |
| Entity verification failure | Due Diligence Analyst to Senior Underwriter | Within 4 hours |
| Unresolvable data discrepancy | Due Diligence Analyst to Senior Underwriter | Within 1 business day |
| PEP match (confirmed) | Due Diligence Analyst to CRO and Head of Legal | Within 4 hours |
| Due Diligence Engine system error | Due Diligence Analyst to CTO | Within 2 hours |

#### 4.6.2 Human Override of Due Diligence Engine Output

- Senior Underwriter may override Due Diligence Engine findings classified as Moderate or Minor with documented rationale.
- Only CRO may override findings classified as Critical or Significant.
- All overrides must include: (a) specific finding being overridden, (b) rationale for override, (c) any compensating controls or conditions imposed, (d) approver signature (electronic, with timestamp).
- Overrides are tracked in the Model Risk Register and reported quarterly.

---

## SECTION V: LEGAL EXECUTION SOP

### 5.1 Purpose

This section establishes the standard operating procedures for legal document preparation, review, compliance validation, and execution within the Calculus Research platform, primarily executed through the Demand Letter Engine and Lex Intelligence Ultimate.

### 5.2 Demand Letter Review Flow

#### 5.2.1 Demand Letter Generation Triggers

The Demand Letter Engine is activated under the following circumstances:

1. **Covenant Violation Notification:** Portfolio Monitoring Engine detects a confirmed covenant breach. Demand Letter Engine generates a notice of default or demand for cure.
2. **Payment Default:** Payment is past due beyond the contractual grace period (typically 10 days). Demand Letter Engine generates a payment demand letter.
3. **Maturity Default:** Loan reaches maturity without repayment or approved extension. Demand Letter Engine generates a maturity default and acceleration notice.
4. **Pre-Litigation Demand:** CCO or Head of Legal initiates a pre-litigation demand in connection with a distressed credit.
5. **Regulatory or Contractual Notices:** Any required notice under loan documents or applicable law.

#### 5.2.2 Generation Process

1. The triggering event is logged by the relevant engine (Portfolio Monitoring Engine, Calculus Intelligence) or by manual initiation by authorized personnel (CCO, Head of Legal, Senior Underwriter).
2. Calculus Intelligence assembles the relevant deal data: borrower and guarantor names, loan terms, property description, covenant terms, default details, cure provisions, and applicable notice provisions from the loan documents.
3. Demand Letter Engine generates the letter using the appropriate template (jurisdiction-specific, default-type-specific). The engine selects the correct template based on: (a) jurisdiction of the borrower, (b) jurisdiction of the property, (c) type of default or notice, (d) loan document provisions.
4. Lex Intelligence Ultimate performs a compliance scan of the generated letter: verifies all statutory notice requirements are met (timing, content, delivery method), verifies consistency with loan document provisions, flags any potential defenses that could invalidate the notice.
5. The generated letter with Lex Intelligence Ultimate compliance report is routed to the Legal Review Queue.

#### 5.2.3 Review and Approval Workflow

1. **Initial Review (Paralegal/Junior Counsel):**
   - Verify factual accuracy: borrower names, loan number, default amounts, dates, cure periods.
   - Verify compliance report items are resolved or noted.
   - Timeline: Within 2 business days of generation.

2. **Substantive Review (Head of Legal or Senior Counsel):**
   - Review legal sufficiency of the demand.
   - Evaluate strategic considerations (timing, tone, potential borrower response).
   - Confirm delivery method complies with loan document requirements and applicable law.
   - Approve, revise, or reject the letter.
   - Timeline: Within 3 business days of initial review completion.

3. **Final Approval:**
   - Letters related to exposures up to $5,000,000: Head of Legal approves.
   - Letters related to exposures exceeding $5,000,000: Head of Legal and CCO joint approval.
   - Letters related to exposures exceeding $10,000,000 or involving potential litigation: Board Risk Committee notification required (approval not required for notice issuance, but Committee must be informed).

4. **Dispatch:**
   - Letter dispatched per loan document requirements (typically certified mail, return receipt requested; overnight courier; and email to borrower's designated email address).
   - Dispatch confirmation logged with: date, time, delivery method, tracking numbers, and responsible person.

### 5.3 Compliance Validation Checklist

Lex Intelligence Ultimate applies the following compliance validation checklist to every legal document generated by the Demand Letter Engine.

#### 5.3.1 Statutory Compliance

- [ ] Notice period meets or exceeds the minimum required by applicable state law.
- [ ] Notice content includes all elements required by applicable state law (amount due, cure period, consequences of failure to cure, contact information).
- [ ] Delivery method complies with applicable state law requirements.
- [ ] Language is consistent with state-specific consumer protection requirements (if applicable).
- [ ] Fair Debt Collection Practices Act (FDCPA) requirements met (if applicable).
- [ ] State debt collection licensing requirements verified (if applicable).

#### 5.3.2 Contractual Compliance

- [ ] Default described in the notice matches the actual default condition.
- [ ] Cure period specified matches loan document provisions.
- [ ] Notice address matches the borrower's designated notice address in loan documents.
- [ ] All required parties receiving notice (borrower, guarantor, if specified).
- [ ] Acceleration language matches loan document provisions (if applicable).
- [ ] Cross-default provisions correctly referenced (if applicable).

#### 5.3.3 Internal Policy Compliance

- [ ] Letter generated using the current approved template version.
- [ ] All factual assertions verified against system records.
- [ ] No unauthorized legal conclusions or threats.
- [ ] Tone consistent with institutional standards.
- [ ] Appropriate signature authority identified.

### 5.4 Counsel Review Process

#### 5.4.1 Internal Counsel Review

All demand letters and legal notices undergo internal counsel review per Section 5.2.3. Internal counsel review is mandatory; no letter may be dispatched without it.

#### 5.4.2 External Counsel Engagement Triggers

External counsel must be engaged under the following circumstances:

1. Exposure exceeds $5,000,000 and the matter involves a contested default or anticipated litigation.
2. Default involves allegations of lender misconduct or potential lender liability.
3. Borrower has retained counsel and communicated through counsel.
4. Matter involves complex multi-jurisdictional issues.
5. Regulatory inquiry or enforcement action is pending or anticipated.
6. Bankruptcy filing by the borrower (automatic -- external bankruptcy counsel engaged within 24 hours).
7. Head of Legal determines external expertise is required for any other reason.

#### 5.4.3 External Counsel Management

1. External counsel selected from the Approved Outside Counsel List (maintained by Head of Legal, reviewed annually).
2. Engagement letter executed before work commences.
3. External counsel receives only the information necessary for the engagement (principle of least privilege applied to legal data sharing).
4. All external counsel work product uploaded to the secure document management system within 48 hours of receipt.
5. Head of Legal monitors external counsel billing monthly; invoices exceeding approved budget by more than 15% require CCO approval.

### 5.5 Documentation Storage and Retention Protocol

#### 5.5.1 Retention Schedule

| Document Type | Retention Period |
|---|---|
| Loan documents (executed originals) | Life of loan + 10 years |
| Demand letters and notices (with proof of delivery) | Life of loan + 10 years |
| Due diligence reports and supporting documents | Life of loan + 7 years |
| Underwriting files (IC Memos, financial analyses) | Life of loan + 7 years |
| Correspondence with borrower | Life of loan + 7 years |
| Internal memoranda and legal analyses | Life of loan + 7 years |
| Regulatory filings and correspondence | Permanent |
| Board and committee minutes | Permanent |
| Model validation reports | 7 years from supersession |
| Audit reports (internal and external) | 7 years |
| Email communications (deal-related) | Life of loan + 5 years |

#### 5.5.2 Storage Requirements

1. All documents stored in the platform's secure document management system with:
   - AES-256 encryption at rest.
   - TLS 1.3 encryption in transit.
   - Role-based access control (per Section IX).
   - Immutable audit log of all access events (view, download, edit, delete).
2. Executed original loan documents additionally stored in physical secure storage (fireproof, access-controlled) at a primary location and digital backup at a geographically separate disaster recovery facility.
3. No deal-related documents may be stored on local workstations, personal devices, or unauthorized cloud services.
4. Document destruction at the end of the retention period requires: Head of Legal approval, documented destruction certificate, and removal from all backup systems within 90 days.

---

## SECTION VI: PORTFOLIO MONITORING SOP

### 6.1 Purpose

This section establishes the standard operating procedures for ongoing portfolio monitoring executed through the Portfolio Monitoring Engine, supported by Calculus Intelligence for trend analysis and early warning correlation.

### 6.2 Covenant Testing Cadence

#### 6.2.1 Standard Testing Schedule

| Covenant Type | Testing Frequency | Data Source | Deadline for Completion |
|---|---|---|---|
| DSCR (debt service coverage) | Quarterly | Borrower-submitted operating statements | 45 days after quarter-end |
| LTV (loan-to-value) | Annually (or upon trigger event) | Internal revaluation model or updated appraisal | 90 days after fiscal year-end |
| Occupancy | Quarterly | Borrower-submitted rent roll | 45 days after quarter-end |
| Net Worth / Liquidity (Guarantor) | Annually | Guarantor-submitted personal financial statement | 90 days after fiscal year-end |
| Insurance Compliance | Annually | Certificate of insurance from carrier | 30 days before policy expiration |
| Tax and HOA Payment Compliance | Semi-annually | Tax receipts or escrow verification | 60 days after payment due date |
| Environmental Compliance | As triggered | Phase I update or remediation reports | Per loan document schedule |

#### 6.2.2 Enhanced Monitoring Schedule

Loans on the Watchlist (see Section 6.4) are subject to enhanced monitoring:

| Covenant Type | Testing Frequency (Enhanced) |
|---|---|
| DSCR | Monthly |
| Occupancy | Monthly |
| Cash flow (detailed P&L) | Monthly |
| LTV | Quarterly |
| Guarantor financials | Semi-annually |

#### 6.2.3 Automated Covenant Testing Process

1. Portfolio Monitoring Engine receives borrower-submitted financial data through the platform's secure upload portal or via automated data feeds.
2. Calculus Intelligence validates data completeness and performs automated extraction and normalization.
3. Portfolio Monitoring Engine computes covenant compliance metrics using the same methodologies as the Underwriting Engine (ensuring consistency between underwriting and monitoring calculations).
4. Results are compared against the specific covenant thresholds in the executed loan documents (not generic policy thresholds -- actual deal-specific covenants).
5. Compliance status is logged: Pass, Watch (within 10% of threshold), Fail.
6. Failed covenants trigger automated alerts per Section 6.3.
7. Portfolio Manager reviews all covenant test results within 5 business days of computation.

### 6.3 Risk Trigger Thresholds

#### 6.3.1 Automated Alert Triggers

The Portfolio Monitoring Engine generates automated alerts when the following thresholds are breached. Each alert is classified by severity and routed to the appropriate personnel.

| Trigger Condition | Severity | Alert Recipients | Response Time |
|---|---|---|---|
| DSCR falls below 1.0x | Critical | Portfolio Manager, CCO, CRO | Same business day |
| DSCR falls below 1.10x (stabilized) or below covenant level | High | Portfolio Manager, CCO | Within 1 business day |
| DSCR declines more than 15% from prior period | High | Portfolio Manager, Senior Underwriter | Within 2 business days |
| LTV exceeds 80% | Critical | Portfolio Manager, CCO, CRO | Same business day |
| LTV exceeds 75% (or exceeds covenant level) | High | Portfolio Manager, CCO | Within 1 business day |
| Occupancy falls below 80% | High | Portfolio Manager, Senior Underwriter | Within 2 business days |
| Occupancy declines more than 10 percentage points in one quarter | Critical | Portfolio Manager, CCO | Same business day |
| Payment past due beyond 30 days | High | Portfolio Manager, CCO | Same business day |
| Payment past due beyond 60 days | Critical | Portfolio Manager, CCO, CRO, Head of Legal | Same business day |
| Borrower financial statement more than 30 days past due | Moderate | Portfolio Manager | Within 5 business days |
| Borrower financial statement more than 60 days past due | High | Portfolio Manager, CCO | Within 2 business days |
| Insurance lapse or inadequate coverage | Critical | Portfolio Manager, CCO, Head of Legal | Same business day |
| Guarantor net worth below covenant level | High | Portfolio Manager, CCO | Within 2 business days |
| Property tax delinquency | High | Portfolio Manager, CCO | Within 2 business days |
| Material litigation involving borrower (detected by Due Diligence Engine periodic re-screening) | High | Portfolio Manager, CRO | Within 1 business day |

#### 6.3.2 Trend Alerts

Calculus Intelligence monitors portfolio-level and loan-level trends and generates alerts when:

1. A loan exhibits three consecutive quarters of declining DSCR (regardless of absolute level).
2. A submarket shows vacancy increases exceeding 200 basis points year-over-year (portfolio concentration alert).
3. More than 15% of the portfolio by outstanding balance is on the Watchlist.
4. Aggregate portfolio weighted-average DSCR falls below 1.30x.
5. Any single borrower exposure exceeds 10% of total portfolio balance (concentration alert).

### 6.4 Watchlist Protocol

#### 6.4.1 Watchlist Criteria

A loan shall be added to the Watchlist when any of the following criteria are met:

**Mandatory Addition (Automatic):**
1. DSCR below 1.10x for stabilized assets or below covenant minimum.
2. LTV above 80%.
3. Payment default (any payment past due beyond the contractual grace period).
4. Material litigation involving the borrower discovered post-closing.
5. Fraud flag triggered on a performing loan during periodic re-screening.

**Discretionary Addition (Portfolio Manager Recommendation, CCO Approval):**
1. Deteriorating market conditions specific to the subject property or submarket.
2. Borrower operational concerns (management changes, key tenant vacancy notification).
3. Three consecutive quarters of declining NOI (even if covenants are not yet breached).
4. Construction loan with schedule delays exceeding 90 days.
5. Any condition that, in the Portfolio Manager's judgment, presents a material risk to repayment.

#### 6.4.2 Watchlist Tiers

| Tier | Name | Criteria | Actions Required |
|---|---|---|---|
| Tier 1 | Watch | Early-stage deterioration; covenants may be near breach but not yet failed | Enhanced monitoring schedule. Borrower communication plan established. Quarterly status update to CCO. |
| Tier 2 | Substandard | Confirmed covenant breach or payment default. Clear risk of loss if conditions do not improve. | Enhanced monitoring. Formal default notice issued (if contractually required). Borrower meeting required within 30 days. Remediation plan required within 60 days. Monthly status update to CCO and CRO. |
| Tier 3 | Doubtful | Material doubt regarding full repayment. Loss probable if conditions continue. | All Tier 2 actions plus: External counsel engaged. Loss reserve assessment. Quarterly Board Risk Committee reporting. CCO and CRO co-manage. |
| Tier 4 | Loss | Loss is confirmed or virtually certain. | Write-off or charge-off recommendation. Board Risk Committee approval required. Collection/recovery proceedings initiated per Legal SOP. |

#### 6.4.3 Watchlist Removal Criteria

A loan may be removed from the Watchlist only when:

1. The condition that triggered Watchlist addition has been fully remediated.
2. The loan has demonstrated sustained compliance (minimum 2 consecutive quarters of passing all covenants) after remediation.
3. Portfolio Manager recommends removal with written justification.
4. CCO approves removal (for Tier 1 and Tier 2).
5. CRO approves removal (for Tier 3 and Tier 4).
6. Removal decision is documented in the loan file.

### 6.5 Remediation Workflow

#### 6.5.1 Remediation Plan Development

1. Upon Watchlist Tier 2 or higher classification, Portfolio Manager initiates remediation plan development within 10 business days.
2. Portfolio Manager, in coordination with the Senior Underwriter assigned to the loan, assesses the borrower's capacity to cure and evaluates potential remediation paths:
   - Borrower-funded cash cure (equity injection, reserve deposit).
   - Loan modification (term extension, covenant reset with enhanced conditions, rate adjustment).
   - Additional collateral or guarantor support.
   - Partial paydown.
   - Controlled sale of the property (voluntary or involuntary).
   - Deed-in-lieu or foreclosure (as last resort).
3. Remediation plan presented to CCO for approval within 30 business days of Watchlist Tier 2 assignment.
4. For Tier 3 loans, remediation plan requires CRO approval and Board Risk Committee notification.
5. Approved remediation plan includes: specific actions, responsible parties, deadlines, success criteria, and consequences of failure to execute.

#### 6.5.2 Remediation Tracking

1. Portfolio Monitoring Engine tracks all remediation milestones and deadlines.
2. Calculus Intelligence generates automated alerts for approaching and missed deadlines.
3. Portfolio Manager reports remediation progress to CCO at the defined frequency (monthly for Tier 2, bi-weekly for Tier 3 and Tier 4).
4. If the remediation plan milestones are missed twice, the loan is automatically escalated to the next Watchlist tier.

---

## SECTION VII: INVESTOR REPORTING SOP

### 7.1 Purpose

This section establishes the standard operating procedures for investor reporting executed through the Investor Reporting Engine, supported by Calculus Intelligence for data validation and narrative generation.

### 7.2 Data Aggregation Rules

#### 7.2.1 Data Sources and Reconciliation

1. The Investor Reporting Engine aggregates data from the following internal sources:
   - Portfolio Monitoring Engine: loan-level performance data, covenant compliance status, watchlist status.
   - Underwriting Engine: original underwriting metrics for comparison.
   - Calculus Intelligence: market data overlays, trend analytics.
   - Accounting system (general ledger): cash flows, fee income, expense data.
   - Custodian/trustee records: fund-level cash positions, distributions, capital calls.

2. Data reconciliation process:
   - The Investor Reporting Engine performs automated reconciliation between internal portfolio data and accounting system records daily.
   - Any discrepancy exceeding $1,000 or 0.1% of fund NAV (whichever is less) is flagged for manual resolution.
   - Portfolio Manager and Finance team resolve discrepancies within 3 business days.
   - Unresolved discrepancies are escalated to CFO.
   - All reconciliation items (resolved and unresolved) are documented in the Reconciliation Log.

#### 7.2.2 Data Cutoff and Reporting Calendar

| Report Type | Data Cutoff | Delivery Deadline |
|---|---|---|
| Monthly Investor Flash Report | Last day of month | 15th business day of following month |
| Quarterly Investor Report | Last day of quarter | 45 calendar days after quarter-end |
| Annual Investor Report | December 31 | 90 calendar days after year-end |
| K-1 / Tax Reporting | December 31 | March 15 (or applicable tax deadline) |
| Capital Call Notice | As needed | 10 business days before funding date |
| Distribution Notice | As needed | 5 business days before distribution date |

#### 7.2.3 Data Integrity Controls

1. All data inputs to the Investor Reporting Engine are timestamped and source-tagged.
2. Data used in investor reports must be from the same cutoff period (no mixing of periods).
3. Any manual data adjustment requires: (a) written justification, (b) dual approval (Portfolio Manager + Finance), (c) audit trail entry.
4. Calculus Intelligence performs a logic check on aggregated data: total portfolio balance equals sum of individual loan balances, total income equals sum of individual income line items, fund-level metrics reconcile to loan-level data.

### 7.3 Performance Calculation Standards

#### 7.3.1 Internal Rate of Return (IRR)

- **Gross IRR:** Computed using fund-level cash flows: capital contributions (inflows, negative) and distributions (outflows, positive), plus ending net asset value.
- **Net IRR:** Gross IRR adjusted for all management fees, incentive fees, fund expenses, and carried interest.
- **Calculation Method:** Modified Dietz or exact daily cash flow method (GIPS-compliant). Monthly approximation acceptable for interim reporting; exact calculation required for annual reporting.
- **Since-Inception IRR:** Computed from fund inception date through the current reporting period.
- **Trailing Period IRR:** Computed for trailing 1-year, 3-year, and 5-year periods (where applicable).

#### 7.3.2 Equity Multiples

- **Gross Multiple on Invested Capital (MOIC):** (Total Distributions + Remaining Value) / Total Invested Capital. Calculated before fees and expenses.
- **Net MOIC:** Same calculation after all fees and expenses.
- **Distributed to Paid-In (DPI):** Total Distributions / Total Invested Capital.
- **Residual Value to Paid-In (RVPI):** Remaining Value / Total Invested Capital.
- **Total Value to Paid-In (TVPI):** DPI + RVPI.

#### 7.3.3 Attribution Analysis

- The Investor Reporting Engine computes return attribution at the asset level, identifying each asset's contribution to overall fund return.
- Attribution methodology: Decompose total return into: income return (current yield), appreciation return (unrealized gains/losses), realized gain/loss, leverage effect.
- Attribution analysis included in quarterly and annual investor reports.

#### 7.3.4 Valuation Methodology

- Performing loans: Valued at par (amortized cost), unless market conditions indicate impairment.
- Impaired loans (Watchlist Tier 3 or Tier 4): Valued using discounted cash flow analysis of expected recovery, applying a risk-adjusted discount rate.
- Real estate owned (REO): Valued at fair market value based on current appraisal or broker opinion of value, less estimated disposition costs.
- Valuation changes are reviewed by CCO and CFO quarterly.
- Annual independent valuation review by external auditor.

### 7.4 Distribution Reporting Process

#### 7.4.1 Distribution Calculation

1. Investor Reporting Engine computes distribution amounts per the fund's limited partnership agreement (LPA) or operating agreement waterfall provisions.
2. Waterfall computation is fully documented, showing: (a) available cash for distribution, (b) allocation per waterfall tier (return of capital, preferred return, catch-up, carried interest split), (c) amount per limited partner, (d) general partner share.
3. Calculus Intelligence verifies waterfall computation against LPA terms (automated contract parsing and comparison).
4. Portfolio Manager reviews and verifies the distribution calculation.
5. CFO approves the distribution amount and authorization.

#### 7.4.2 Distribution Notice

1. Distribution notice generated by Investor Reporting Engine, including: distribution date, amount per LP, breakdown by waterfall tier, and cumulative distribution summary.
2. Notice delivered to LPs minimum 5 business days before distribution date.
3. CCO and CFO sign-off required before notice issuance.

### 7.5 Audit Controls and Reconciliation

#### 7.5.1 Internal Controls

1. All investor reports undergo a four-eye review process: (a) Prepared by Investor Reporting Engine, (b) Reviewed by Portfolio Manager, (c) Verified by Finance team (reconciliation to general ledger), (d) Approved by CCO (content) and CFO (financials).
2. Performance calculations are independently verified by Finance team using a separate calculation methodology (spreadsheet-based parallel computation for IRR and multiples).
3. Any variance between Investor Reporting Engine calculations and independent verification exceeding 10 basis points (for IRR) or 0.01x (for multiples) triggers investigation and resolution before report issuance.

#### 7.5.2 External Audit

1. Annual financial statements audited by an independent registered public accounting firm.
2. Auditor has read-only access to the Investor Reporting Engine data and calculation logs for audit testing.
3. All audit adjustments documented, approved by CFO, and reflected in subsequent investor reports.
4. Audit management letter findings tracked to remediation with CCO oversight.

#### 7.5.3 LP Inquiry Handling

1. LP inquiries regarding reports are logged in the investor relations tracking system.
2. Responses prepared by Portfolio Manager, reviewed by CCO, within 5 business days.
3. Inquiries that identify potential errors in published reports are escalated immediately to CFO and CCO.
4. If an error is confirmed, a corrected report is issued within 10 business days with a cover letter explaining the correction.

---

## SECTION VIII: AI GOVERNANCE AND MODEL OVERSIGHT

### 8.1 Purpose

This section establishes the governance framework for all AI and machine learning models operating within the Calculus Research platform. This framework applies to: Calculus Intelligence, Lex Intelligence Ultimate, Forge Intelligence, Lead Ranking Engine, Underwriting Engine, Due Diligence Engine, Demand Letter Engine, Portfolio Monitoring Engine, and Investor Reporting Engine.

### 8.2 Model Validation Procedures (Before Deployment)

#### 8.2.1 Validation Scope

Every model must undergo independent validation before initial production deployment and before any material change deployment (per the Model Change Classification in Section 1.5.2). Validation covers:

1. **Conceptual Soundness:** Review of the theoretical foundation, methodology, and assumptions underlying the model. Is the approach appropriate for its intended use?
2. **Data Quality Assessment:** Evaluation of training data (where applicable), input data sources, data completeness, data accuracy, and representativeness. Are the data inputs sufficient and reliable?
3. **Developmental Evidence:** Review of model development documentation, algorithm selection rationale, feature engineering decisions, and hyperparameter tuning methodology.
4. **Outcome Analysis:** Back-testing against historical data (minimum 24 months), out-of-sample testing, and comparison against benchmark models or industry standards.
5. **Sensitivity Analysis:** Testing model behavior under extreme input conditions, missing data scenarios, and boundary conditions.
6. **Stress Testing:** Evaluating model performance under adverse economic scenarios (recession, rate shock, market dislocation).
7. **Bias Assessment:** Testing for disparate impact across protected classes (where applicable, particularly for scoring models). Statistical tests for bias must be documented.

#### 8.2.2 Validation Standards by Engine

| Engine | Key Validation Metrics | Acceptable Tolerance |
|---|---|---|
| Lead Ranking Engine | Scoring accuracy (Gini coefficient), rank-ordering stability, bias metrics | Gini above 0.40; rank-order stability above 85% across test periods |
| Underwriting Engine | Valuation accuracy (vs. actual outcomes), DSCR prediction accuracy | Mean absolute error below 10% for valuation; DSCR prediction within 5% of actual |
| Due Diligence Engine | False positive rate (litigation, fraud), false negative rate | False positive rate below 15%; false negative rate below 2% |
| Demand Letter Engine / Lex Intelligence Ultimate | Legal accuracy, compliance accuracy, consistency | Zero tolerance for legal errors; compliance accuracy 99%+ |
| Portfolio Monitoring Engine | Alert accuracy (true positive rate), early warning lead time | True positive rate above 90%; false alarm rate below 20% |
| Investor Reporting Engine | Calculation accuracy | Zero tolerance for calculation errors |
| Calculus Intelligence | Cross-reference accuracy, reasoning consistency | Consistency rate above 95% |
| Forge Intelligence | Code quality metrics, security vulnerability rate, test pass rate | Zero critical vulnerabilities; test pass rate above 98% |

#### 8.2.3 Validation Process

1. AI/ML Engineer submits the model package (code, documentation, test results) to the CRO.
2. CRO assigns an independent validator (internal or external, not involved in model development).
3. Validator conducts testing per Section 8.2.1 scope within 15 business days.
4. Validator produces a Validation Report documenting: methodology, findings, identified weaknesses, recommendations, and a validation opinion (Approved, Approved with Conditions, Not Approved).
5. CRO reviews the Validation Report and presents to Model Risk Committee with recommendation.
6. Model Risk Committee renders decision per Section 1.5.1.

### 8.3 Drift Detection Methodology

#### 8.3.1 Monitoring Framework

All production models are subject to continuous drift monitoring. Drift is defined as a statistically significant change in model input distributions, output distributions, or performance metrics relative to validation baselines.

#### 8.3.2 Drift Detection Methods

1. **Input Drift (Data Drift):**
   - Population Stability Index (PSI) computed weekly for all key input features.
   - PSI threshold: below 0.10 = no action; 0.10-0.25 = investigation required; above 0.25 = model review required.
   - Kolmogorov-Smirnov test applied monthly for continuous variables.

2. **Output Drift (Concept Drift):**
   - Model output distribution monitored weekly (score distributions for scoring models; decision distributions for classification models).
   - Significant shift defined as: mean output change exceeding 2 standard deviations from the rolling 90-day mean.
   - Decision boundary stability checked monthly.

3. **Performance Drift:**
   - Back-test model predictions against actual outcomes as outcomes become available (lag varies by engine: Lead Ranking Engine 90-day lag; Underwriting Engine 12-month lag for default prediction).
   - Performance metrics (accuracy, precision, recall, AUC-ROC as applicable) compared against validation baseline.
   - Degradation exceeding 10% from baseline triggers model review.

#### 8.3.3 Drift Response Protocol

| PSI / Performance Change | Classification | Action |
|---|---|---|
| PSI below 0.10; performance within 5% of baseline | Normal | Continue monitoring. No action. |
| PSI 0.10-0.25; or performance 5-10% below baseline | Warning | AI/ML Engineer investigation within 5 business days. Findings reported to CRO. Root cause analysis documented. |
| PSI above 0.25; or performance more than 10% below baseline | Critical | Model placed on enhanced monitoring (daily drift checks). CRO notified within 24 hours. Model Risk Committee emergency review within 5 business days. Model recalibration or retraining initiated. |
| Sustained critical drift for more than 2 consecutive weeks | Emergency | CRO may order model suspension. Fallback procedures activated. Board Risk Committee notified. |

### 8.4 Bias Mitigation Controls

#### 8.4.1 Pre-Deployment Bias Testing

1. All scoring and decision models (Lead Ranking Engine, Underwriting Engine, Due Diligence Engine) are tested for bias before deployment.
2. Testing includes: statistical parity analysis, equalized odds testing, and disparate impact ratio calculation across available demographic dimensions.
3. Disparate impact ratio below 0.80 (the four-fifths rule) for any protected class triggers remediation before deployment.

#### 8.4.2 Ongoing Bias Monitoring

1. Quarterly bias metrics reporting for all scoring models.
2. Annual comprehensive bias audit conducted by independent reviewer (internal or external).
3. Any identified bias pattern triggers: (a) root cause analysis, (b) remediation plan, (c) Model Risk Committee review, (d) documentation in the Model Risk Register.

#### 8.4.3 Remediation Procedures

1. Identified bias addressed through: data augmentation, feature engineering modifications, algorithmic adjustments, or model replacement.
2. Remediated model must pass full validation before redeployment.
3. Remediation actions and outcomes documented in the Model Risk Register.

### 8.5 Version Control and Rollback Procedures

#### 8.5.1 Version Control Standards

1. All engine code and model artifacts stored in the designated version control system (Git-based).
2. Every production deployment tagged with a unique version identifier: [Engine Name]-v[Major].[Minor].[Patch]-[YYYYMMDD].
3. Version history maintained indefinitely. No version may be deleted from the repository.
4. Each version includes: source code, trained model weights (where applicable), configuration files, dependency manifest, validation report reference, and deployment authorization reference.

#### 8.5.2 Deployment Protocol

1. All deployments follow the staged deployment process defined in Section 1.5.1 (shadow environment, then production).
2. Deployment executed by AI/ML Engineer with CTO authorization.
3. CRO authorization required for any model logic changes (in addition to CTO).
4. Deployment log records: version deployed, deploying engineer, authorizing officer(s), timestamp, environment, and rollback version (the immediately prior production version).

#### 8.5.3 Rollback Procedures

1. Every production deployment maintains a tested rollback package (the prior production version, confirmed operational).
2. Rollback can be initiated by:
   - CRO (unilateral authority) upon model performance emergency.
   - CTO upon infrastructure emergency.
   - Model Risk Committee resolution.
3. Rollback execution:
   - AI/ML Engineer executes rollback within 2 hours of authorization.
   - Rollback deployment uses the same staged deployment pipeline (but shadow period is waived in emergency).
   - Post-rollback verification: confirm prior version is operational, confirm current outputs match expected behavior.
4. Rollback is a temporary measure. Within 10 business days, the Model Risk Committee must determine: (a) root cause of the issue that triggered rollback, (b) remediation plan for the failed version, (c) timeline for re-deployment or permanent reversion.

### 8.6 Incident Response Protocol for Model Failures

#### 8.6.1 Incident Classification

| Severity | Definition | Examples |
|---|---|---|
| P1 -- Critical | Model is producing materially incorrect outputs that could result in financial loss, legal liability, or regulatory violation | Underwriting Engine approving loans outside policy limits; Due Diligence Engine missing known sanctions hits; Demand Letter Engine generating non-compliant notices |
| P2 -- High | Model is degraded but not producing dangerous outputs; outputs require enhanced human review | Scoring model drift exceeding thresholds; calculation errors in non-critical metrics; intermittent processing failures |
| P3 -- Medium | Model issue identified but not impacting current outputs; latent risk | Bias detection threshold approached but not breached; performance degradation trending toward threshold; data quality issue in non-production pipeline |
| P4 -- Low | Minor issue with no current or near-term risk | Documentation gap; non-critical logging failure; cosmetic output formatting issue |

#### 8.6.2 Incident Response Steps

**P1 -- Critical:**
1. Discovery: Any personnel identifying a potential P1 incident reports immediately to CRO and CTO.
2. Containment (within 1 hour): CRO orders model suspension or output quarantine. All outputs generated during the suspected failure window are flagged for review.
3. Assessment (within 4 hours): AI/ML Engineer conducts root cause analysis. CRO assesses scope of impact (number of deals affected, financial exposure).
4. Remediation (within 24 hours): Rollback to last known good version (if applicable), or manual override procedures activated with enhanced human review for all affected outputs.
5. Communication (within 24 hours): CRO notifies Board Risk Committee. Affected deal teams notified. External parties (borrowers, investors) notified if their interests are impacted.
6. Post-Incident Review (within 5 business days): Full incident report documenting: timeline, root cause, scope of impact, remediation actions, and preventive measures. Presented to Model Risk Committee.

**P2 -- High:**
1. Report to CRO and CTO within 4 hours.
2. Enhanced human review of all affected engine outputs immediately.
3. Root cause analysis within 3 business days.
4. Remediation plan approved by CRO within 5 business days.
5. Incident report filed in Model Risk Register.

**P3 -- Medium:**
1. Report to CTO within 1 business day.
2. Root cause analysis within 10 business days.
3. Remediation plan in next Model Risk Committee meeting agenda.
4. Documented in Model Risk Register.

**P4 -- Low:**
1. Logged in engineering issue tracker.
2. Addressed in normal development cycle.
3. Documented in Model Risk Register (summary only).

---

## SECTION IX: DATA SECURITY AND COMPLIANCE

### 9.1 Purpose

This section establishes the data security standards and compliance requirements for the Calculus Research platform, covering access control, encryption, logging, monitoring, and business continuity.

### 9.2 Access Control Hierarchy

#### 9.2.1 Role-Based Access Control (RBAC)

Access to the Calculus Research platform is governed by the principle of least privilege. Each role is granted the minimum access necessary to perform assigned duties.

| Role | Platform Access Level | Data Access | Engine Access | Administrative Access |
|---|---|---|---|---|
| Board Risk Committee Member | Read-only dashboards and reports | Aggregated portfolio data, committee materials | No direct engine access | None |
| CEO | Read-only dashboards and reports; approval workflows | All non-PII aggregated data | No direct engine access | User provisioning approval |
| CCO | Full read access; credit approval workflows | All deal-level data including PII | Underwriting Engine (review), Portfolio Monitoring Engine (review) | None |
| CRO | Full read access; model oversight workflows | All data including model internals | All engines (review and override authority) | Model deployment approval |
| CTO | Infrastructure and system administration | System logs, configuration data, model code | All engines (technical administration) | Full system administration |
| Head of Legal | Legal module full access; read access to deal data | Deal-level data, legal documents, compliance data | Demand Letter Engine (review), Lex Intelligence Ultimate (review) | None |
| Senior Underwriter | Underwriting module full access | Assigned deal data, portfolio reports | Underwriting Engine (review), Lead Ranking Engine (review) | None |
| Credit Analyst | Data entry and preparation access | Assigned deal data only | Underwriting Engine (data input only) | None |
| Due Diligence Analyst | Due diligence module access | Assigned investigation data | Due Diligence Engine (review) | None |
| Portfolio Manager | Portfolio monitoring full access | All active loan performance data | Portfolio Monitoring Engine (review), Investor Reporting Engine (review) | None |
| AI/ML Engineer | Development and deployment access | Model code, training data, performance logs | All engines (development and testing environments); production (read-only unless deploying with authorization) | Deployment execution (with authorization) |
| External Auditor | Read-only audit access (time-limited) | Scoped to audit engagement | No direct engine access | None |

#### 9.2.2 Access Provisioning and Review

1. **New Access Requests:** Submitted via formal request form, approved by the requestor's manager and the system administrator (CTO or designee). Access granted within 2 business days of approval.
2. **Role Changes:** When an employee changes roles, access is reviewed and adjusted within 1 business day. Previous role access is revoked before new role access is granted.
3. **Termination:** Upon employee termination (voluntary or involuntary), all platform access is revoked within 4 hours. For involuntary termination, access is revoked immediately upon notification.
4. **Quarterly Access Review:** CTO conducts a quarterly review of all active access grants. Each manager certifies the continued appropriateness of their team members' access. Discrepancies remediated within 5 business days.
5. **Annual Privileged Access Audit:** CRO and CTO jointly review all privileged access (system administration, model deployment, data export) annually. Results reported to Board Risk Committee.

#### 9.2.3 Multi-Factor Authentication (MFA)

- MFA required for all platform access (no exceptions).
- MFA required for VPN access to the platform network.
- Privileged accounts (CTO, AI/ML Engineers, system administrators) require hardware-based MFA tokens.
- MFA bypass requests require CTO and CRO joint approval (documented, time-limited, maximum 24 hours).

### 9.3 Encryption Standards

#### 9.3.1 Data at Rest

- All data stored within the platform is encrypted using AES-256.
- Encryption keys managed through a dedicated key management system (KMS).
- Key rotation: Annually, or immediately upon suspected compromise.
- Database-level encryption (Transparent Data Encryption) applied to all database instances.
- File-level encryption applied to all stored documents.
- Backup data encrypted using the same standards as production data.

#### 9.3.2 Data in Transit

- All data transmitted within the platform infrastructure uses TLS 1.3 (minimum TLS 1.2; TLS 1.0 and 1.1 are disabled).
- All external API communications use TLS 1.3.
- Internal service-to-service communication uses mutual TLS (mTLS) authentication.
- Certificate management: Automated certificate renewal; certificates with validity not exceeding 13 months.

#### 9.3.3 Data in Processing

- Sensitive computations (PII processing, credit scoring) executed within encrypted memory enclaves where available.
- No sensitive data written to unencrypted temporary storage.
- Log redaction: PII elements (SSN, account numbers) are masked in all logs (show last 4 digits only).

### 9.4 Logging and Monitoring Requirements

#### 9.4.1 Mandatory Logging Events

The following events must be logged with immutable audit trail:

| Event Category | Specific Events | Retention |
|---|---|---|
| Authentication | Login (success/failure), logout, MFA challenge, password change | 3 years |
| Authorization | Access grant, access revocation, role change, privilege escalation | 7 years |
| Data Access | Record view, record edit, record delete, data export, report generation | 7 years |
| Engine Operations | Engine invocation, input data hash, output data hash, model version, processing time | 7 years |
| Credit Decisions | Approval, denial, condition, exception, override (with full context) | Life of loan + 7 years |
| System Administration | Configuration change, deployment, rollback, backup, restore | 7 years |
| Security Events | Intrusion detection alert, vulnerability scan results, incident response actions | 7 years |

#### 9.4.2 Log Integrity

- All logs written to append-only storage (write-once, read-many).
- Log entries include: timestamp (UTC), user ID, source IP, action, target resource, outcome, and a cryptographic hash chaining to the previous entry.
- Log tampering detection: Automated daily integrity verification using hash chain validation.
- Logs are not editable by any user, including system administrators. Log redaction (e.g., for legal hold purposes) requires CRO and Head of Legal joint authorization.

#### 9.4.3 Monitoring and Alerting

- Real-time monitoring dashboards for: system availability, engine processing volumes, error rates, authentication failures, and security events.
- Automated alerting thresholds:
  - Five or more failed login attempts from a single account within 10 minutes (account lockout triggered, security team notified).
  - Any access attempt from an unrecognized device or location (require re-authentication, security team notified).
  - Any data export exceeding 1,000 records (CTO notified).
  - Any configuration change to production engines (CRO and CTO notified).
  - System availability dropping below 99.5% (CTO and engineering team notified immediately).

### 9.5 Disaster Recovery and Business Continuity

#### 9.5.1 Recovery Objectives

| System Component | Recovery Time Objective (RTO) | Recovery Point Objective (RPO) |
|---|---|---|
| Core Platform (Calculus Intelligence, all engines) | 4 hours | 1 hour |
| Document Management System | 8 hours | 1 hour |
| Investor Reporting Engine | 24 hours | 4 hours |
| Email and Communication Systems | 4 hours | 1 hour |
| Development and Testing Environments | 48 hours | 24 hours |

#### 9.5.2 Backup Procedures

1. **Database Backups:** Continuous replication to geographically separate secondary site. Full backup daily at 03:00 UTC. Incremental backups every 15 minutes.
2. **Document Storage Backups:** Synchronized to secondary site in near-real-time (maximum 15-minute lag). Daily full backup to tertiary cold storage.
3. **Model Artifact Backups:** Version control repository replicated to secondary site. Model weights and configurations backed up daily.
4. **Configuration Backups:** Infrastructure-as-code repository replicated continuously. All configuration changes captured in version control.

#### 9.5.3 Disaster Recovery Testing

1. **Tabletop Exercise:** Quarterly. Simulate disaster scenarios with key personnel. Document response decisions and identify gaps.
2. **Partial Failover Test:** Semi-annually. Failover non-critical systems to secondary site and verify functionality.
3. **Full Failover Test:** Annually. Complete failover of all systems to secondary site. Verify all engines operational, data integrity confirmed, and recovery objectives met.
4. **Test Results:** Documented by CTO, reviewed by Board Risk Committee, remediation plan for any identified gaps with deadlines.

#### 9.5.4 Business Continuity Procedures

1. If the primary platform is unavailable, the following manual procedures are activated:
   - Credit decisions: Manual underwriting using standardized spreadsheet templates. CCO approval required for all manual underwriting. Maximum exposure for manually underwritten deals: $2,500,000.
   - Due diligence: Manual screening using direct database access to third-party providers. CRO approval required.
   - Portfolio monitoring: Manual covenant testing using borrower-submitted financials. Monthly frequency only (no weekly alerts).
   - Investor reporting: Delayed until platform is restored. LPs notified of expected delay.
2. Manual procedures may operate for a maximum of 30 calendar days. If platform recovery exceeds 30 days, Board Risk Committee must approve extended manual operations or alternative arrangements.

---

## SECTION X: INCIDENT AND RISK MANAGEMENT

### 10.1 Purpose

This section establishes the procedures for responding to credit defaults, data breaches, regulatory inquiries, and model malfunctions.

### 10.2 Credit Default Response Procedures

#### 10.2.1 Default Classification

| Default Type | Definition | Initial Response Time |
|---|---|---|
| Payment Default | Payment not received within the contractual grace period | Within 2 business days of grace period expiration |
| Covenant Default | Failure to meet any financial or non-financial covenant | Within 5 business days of confirmed covenant failure |
| Technical Default | Failure to provide required financial reporting, insurance lapse, or other non-payment/non-covenant breach | Within 10 business days of confirmed default |
| Maturity Default | Failure to repay at loan maturity | Within 1 business day of maturity date |
| Cross-Default | Default under another obligation that triggers a default under the subject loan | Within 2 business days of notification |

#### 10.2.2 Default Response Workflow

1. **Detection:** Portfolio Monitoring Engine detects default condition (automated) or Portfolio Manager identifies default (manual). All defaults are logged in the Default Tracking System with a unique Default ID.
2. **Classification and Notification (Day 0-1):**
   - Portfolio Manager classifies the default type and assigns initial severity.
   - Notification chain activated per Section 6.3 alert thresholds.
   - CCO notified of all defaults on the same business day.
3. **Initial Assessment (Day 1-5):**
   - Portfolio Manager conducts initial assessment: (a) cause of default, (b) borrower's capacity to cure, (c) current collateral value estimate, (d) guarantor financial capacity.
   - Due Diligence Engine performs updated screening on borrower and guarantor (litigation, financial condition changes).
   - Portfolio Manager recommends initial action: (a) forbearance/workout discussion, (b) formal notice of default, (c) acceleration and enforcement.
4. **CCO Decision (Day 5-10):**
   - CCO reviews assessment and recommendation.
   - CCO determines course of action and resource allocation.
   - For exposures exceeding $5,000,000 or any anticipated litigation, CRO is engaged.
5. **Execution:**
   - Demand Letter Engine generates appropriate notice per Legal SOP (Section V).
   - If workout: Portfolio Manager leads borrower negotiations; proposed workout terms presented to Credit Committee for approval.
   - If enforcement: Head of Legal engages external counsel; foreclosure or other enforcement proceedings initiated per applicable law.
6. **Ongoing Monitoring:**
   - Defaulted loans receive weekly status updates to CCO.
   - Monthly reporting to Board Risk Committee for all defaults with exposure exceeding $2,500,000.
   - Loss reserve updated quarterly (at minimum) based on current recovery assessment.

#### 10.2.3 Loss Mitigation Strategies

The following strategies are considered in order of preference:

1. **Borrower Cash Cure:** Borrower injects additional equity or reserves to cure the default. Preferred outcome. Timeline: within 30 days.
2. **Loan Modification:** Restructure loan terms to create a path to performance. Requires Credit Committee approval (or higher, per Decision Authority Matrix). Must include enhanced covenants and reporting.
3. **Partial Paydown:** Borrower pays down principal to bring metrics into compliance. Credit Committee approval required.
4. **Discounted Payoff (DPO):** Accept less than full balance for immediate resolution. Requires Board Risk Committee approval for any DPO below 90% of outstanding balance.
5. **Deed-in-Lieu of Foreclosure:** Accept property in full or partial satisfaction. Head of Legal and CCO joint approval. Environmental review updated before acceptance.
6. **Foreclosure:** Judicial or non-judicial per applicable state law. Last resort. Board Risk Committee notification required. External counsel mandatory.
7. **Note Sale:** Sell the defaulted loan to a third party. Board Risk Committee approval required. Minimum two bids obtained.

### 10.3 Data Breach Protocol

#### 10.3.1 Breach Detection

1. Security monitoring systems (SIEM, intrusion detection, anomaly detection) provide continuous monitoring.
2. Any employee who suspects a data breach reports immediately to: CTO, CISO (Chief Information Security Officer), and CRO.
3. Third-party vendors who detect a breach involving Calculus Research data must notify the company within 24 hours per contractual requirements.

#### 10.3.2 Breach Response (Following NIST Framework)

**Phase 1: Identification and Containment (0-4 hours)**

1. CTO/CISO activates the Incident Response Team (IRT): CTO, CISO, CRO, Head of Legal, and designated AI/ML Engineer.
2. IRT assesses: (a) nature of the breach (unauthorized access, data exfiltration, ransomware, etc.), (b) scope (systems affected, data types compromised), (c) active or contained.
3. Immediate containment actions: isolate affected systems, revoke compromised credentials, block suspicious network traffic, preserve forensic evidence.
4. No affected system is restored or cleaned until forensic evidence is preserved.

**Phase 2: Assessment (4-48 hours)**

1. Forensic analysis conducted (internal or external forensic team) to determine: root cause, entry vector, data compromised (types and volume), duration of unauthorized access.
2. CRO assesses regulatory notification obligations: (a) state data breach notification laws (varies by state; some require notification within 30 days), (b) federal regulatory requirements, (c) contractual notification obligations to investors and counterparties.
3. Head of Legal prepares notification timeline and content requirements.

**Phase 3: Notification (Per regulatory requirements, typically 30-72 hours)**

1. If personal information of individuals is compromised: notification to affected individuals per applicable state law.
2. If investor data is compromised: notification to affected investors within 48 hours.
3. Regulatory notifications filed per applicable requirements.
4. Board Risk Committee notified within 24 hours of confirmed breach.
5. All notifications reviewed and approved by Head of Legal before issuance.

**Phase 4: Remediation (Ongoing)**

1. Root cause remediation: patch vulnerabilities, strengthen access controls, update security configurations.
2. Enhanced monitoring of affected systems for 90 days post-incident.
3. Post-incident review conducted within 30 days: (a) timeline of events, (b) effectiveness of response, (c) lessons learned, (d) process improvements.
4. Post-incident report presented to Board Risk Committee.

#### 10.3.3 Breach Severity Classification

| Severity | Criteria | Response Level |
|---|---|---|
| Critical | PII of more than 1,000 individuals, or any financial account data, or any regulatory data | Full IRT activation; external forensics; Board notification within 24 hours |
| High | PII of 100-1,000 individuals, or sensitive business data (deal terms, model parameters) | IRT activation; CTO-led response; Board notification within 48 hours |
| Medium | PII of fewer than 100 individuals, or internal non-sensitive data | CTO and CISO response; Board notification at next scheduled meeting |
| Low | No PII; non-sensitive system data; contained immediately | CTO documentation; no Board notification required |

### 10.4 Regulatory Inquiry Handling

#### 10.4.1 Inquiry Receipt Protocol

1. Any employee receiving a regulatory inquiry, subpoena, or examination notice must immediately (within 2 hours) notify the Head of Legal. No substantive response may be made without Head of Legal authorization.
2. Head of Legal logs the inquiry in the Regulatory Tracking System with: (a) regulatory body, (b) nature of inquiry, (c) scope (specific deal, portfolio-wide, operational), (d) response deadline, (e) assigned internal lead.
3. Head of Legal notifies CEO, CRO, and CCO within 4 hours of receiving the inquiry.
4. Board Risk Committee notified at the next scheduled meeting, or within 48 hours if the inquiry is classified as material (as determined by Head of Legal).

#### 10.4.2 Response Preparation

1. Head of Legal assembles a response team: relevant subject matter experts, IT personnel for data retrieval, and external counsel (if warranted).
2. Document preservation notice issued immediately: all documents and data potentially relevant to the inquiry are preserved. Normal retention/destruction schedules suspended for relevant materials.
3. Response is prepared, reviewed by Head of Legal and external counsel (if engaged), and approved by CEO before submission.
4. All communications with regulators are conducted through or with the knowledge of Head of Legal. No employee may independently communicate with regulators regarding the inquiry.
5. Response submitted within the required deadline (typically 30 days, or as specified by the regulatory body).

#### 10.4.3 Examination Support

1. If the inquiry escalates to an on-site examination:
   - Head of Legal designates an examination coordinator.
   - A dedicated examination workspace is prepared with controlled access.
   - All documents provided to examiners are logged.
   - Daily debriefs conducted with Head of Legal and CEO.
2. Examination findings and recommendations tracked to remediation.
3. Remediation status reported to Board Risk Committee quarterly until all findings are resolved.

### 10.5 Model Malfunction Escalation Path

#### 10.5.1 Identification

Model malfunctions may be identified through:

1. Automated drift detection and performance monitoring (Section 8.3).
2. Human review of engine outputs (anomalous results observed by analysts or underwriters).
3. Reconciliation failures between engine outputs and independent verification.
4. User-reported issues (via the platform's issue reporting function).

#### 10.5.2 Escalation Matrix

| Discovery Source | First Responder | Escalation Path | Containment Authority |
|---|---|---|---|
| Automated monitoring alert | AI/ML Engineer on call | CTO (within 1 hour) then CRO (within 2 hours) | CTO: technical isolation; CRO: output quarantine |
| Human reviewer observation | Reporting analyst's supervisor | Senior Underwriter/Portfolio Manager to CTO (within 4 hours) | CTO after confirmation |
| Reconciliation failure | Finance team member | CFO to CTO (within 4 hours) | CTO after confirmation |
| User-reported issue | Help desk | CTO (within 2 hours) | CTO after confirmation |

#### 10.5.3 Investigation and Resolution

1. CTO assigns AI/ML Engineer to investigate. Investigation target: root cause identified within 24 hours (P1-P2) or 5 business days (P3-P4).
2. During investigation: affected engine outputs are flagged. All flagged outputs require manual human review before being acted upon.
3. CRO determines whether any previously generated outputs (before the malfunction was detected) need to be reviewed retroactively. If yes, CRO defines the review scope and assigns resources.
4. Resolution follows the Version Control and Rollback Procedures in Section 8.5.
5. Post-resolution: enhanced monitoring for 30 days; incident report filed per Section 8.6.

---

## APPENDIX A: GLOSSARY OF TERMS

| Term | Definition |
|---|---|
| AES-256 | Advanced Encryption Standard with 256-bit key length |
| AUC-ROC | Area Under the Receiver Operating Characteristic Curve |
| CCO | Chief Credit Officer |
| CLS | Composite Lead Score |
| CRE | Commercial Real Estate |
| CRO | Chief Risk Officer |
| CTO | Chief Technology Officer |
| CISO | Chief Information Security Officer |
| DPI | Distributed to Paid-In capital ratio |
| DSCR | Debt Service Coverage Ratio |
| EIN | Employer Identification Number |
| FDCPA | Fair Debt Collection Practices Act |
| GIPS | Global Investment Performance Standards |
| IC Memo | Investment Committee Memorandum |
| IRR | Internal Rate of Return |
| IRT | Incident Response Team |
| KMS | Key Management System |
| LPA | Limited Partnership Agreement |
| LP | Limited Partner |
| LTV | Loan-to-Value Ratio |
| MAI | Member of the Appraisal Institute |
| MFA | Multi-Factor Authentication |
| MOIC | Multiple on Invested Capital |
| mTLS | Mutual Transport Layer Security |
| NOI | Net Operating Income |
| OFAC SDN | Office of Foreign Assets Control Specially Designated Nationals list |
| PEP | Politically Exposed Person |
| PII | Personally Identifiable Information |
| PSI | Population Stability Index |
| RACI | Responsible, Accountable, Consulted, Informed |
| RBAC | Role-Based Access Control |
| REO | Real Estate Owned |
| RPO | Recovery Point Objective |
| RTO | Recovery Time Objective |
| RVPI | Residual Value to Paid-In capital ratio |
| SAR | Suspicious Activity Report |
| SIEM | Security Information and Event Management |
| TLS | Transport Layer Security |
| TVPI | Total Value to Paid-In capital ratio |
| UCC | Uniform Commercial Code |

---

## APPENDIX B: ENGINE REFERENCE ARCHITECTURE

### Intelligence Core

| Engine | Function | Decision Authority | Human Oversight Level |
|---|---|---|---|
| Calculus Intelligence | Master Reasoning Engine: workflow orchestration, cross-engine validation, data normalization, trend analysis, narrative generation | Coordinating -- no independent credit authority | Output review by relevant analyst per stage |
| Lex Intelligence Ultimate | Legal meta-analysis: statute interpretation, compliance validation, legal risk assessment, contract parsing | Advisory -- no independent legal authority | All outputs reviewed by Head of Legal or counsel |
| Forge Intelligence | Code generation: engine development, testing automation, deployment pipeline management | Technical -- no credit or legal authority | All code reviewed by AI/ML Engineer peer; production deployment requires CTO authorization |

### Origination Engines

| Engine | Function | Decision Authority | Human Oversight Level |
|---|---|---|---|
| Lead Ranking Engine | Composite lead scoring, AI risk analysis, tier classification | Tier 1-2 auto-routing; Tier 3-4 require human review | Senior Underwriter reviews Tier 3; override authority for Tier 4 |
| Skip Trace Engine | Contact information discovery, enrichment, confidence scoring | No decision authority -- data enrichment only | Credit Analyst validates enrichment quality |
| Shovels Engine | Building permit data ingestion, lead identification, initial scoring | No decision authority -- data ingestion only | Credit Analyst validates ingested data |

### Credit and Underwriting Engines

| Engine | Function | Decision Authority | Human Oversight Level |
|---|---|---|---|
| Underwriting Engine | Property valuation, cash flow modeling, risk scoring, loan structuring, IC memo generation | Recommends -- no independent approval authority | Credit Analyst (data), Senior Underwriter (analysis), CCO (escalated) |
| Due Diligence Engine | Entity investigation, litigation scanning, financial verification, fraud detection, risk reporting | Flags and recommends -- no independent clearance authority | Due Diligence Analyst (all outputs), CRO (escalated flags) |

### Legal and Execution Engines

| Engine | Function | Decision Authority | Human Oversight Level |
|---|---|---|---|
| Demand Letter Engine | Legal document generation, notice drafting, template selection | Generates drafts -- no dispatch authority | Head of Legal approval required for all dispatches |

### Portfolio and Surveillance Engines

| Engine | Function | Decision Authority | Human Oversight Level |
|---|---|---|---|
| Portfolio Monitoring Engine | Covenant compliance testing, alert generation, watchlist management, performance tracking | Generates alerts and reports -- no remediation authority | Portfolio Manager reviews all alerts; CCO for escalated actions |

### Capital Markets Engines

| Engine | Function | Decision Authority | Human Oversight Level |
|---|---|---|---|
| Investor Reporting Engine | Performance calculation, data aggregation, report generation, distribution computation | Computes and generates -- no distribution authority | Portfolio Manager review; CFO and CCO approval for distribution and reports |

---

## APPENDIX C: APPROVAL AUTHORITY MATRIX (SUMMARY)

### Credit Approvals

| Exposure Band | Approver | Secondary Approval | Board Notification |
|---|---|---|---|
| Up to $1,000,000 | Senior Underwriter | None | No |
| $1,000,001 - $2,500,000 | Senior Underwriter | Peer review | No |
| $2,500,001 - $5,000,000 | Credit Committee | CCO certification of IC Memo | No |
| $5,000,001 - $10,000,000 | Credit Committee + CCO | CRO review | Quarterly summary |
| Over $10,000,000 | Board Risk Committee | Full committee vote | Direct |

### Exceptions to Policy

| Exception Type | Approver (one level above standard) | Documentation |
|---|---|---|
| LTV up to 5% above limit | Next authority level per exposure band | Written justification, compensating factors |
| DSCR up to 0.10x below limit | Next authority level per exposure band | Written justification, compensating factors |
| Appraisal age extension (up to 60 days) | CCO | Written justification |
| Financial statement age extension | Senior Underwriter | Written justification |
| Below-minimum debt yield | Credit Committee (regardless of size) | Full stress analysis |

### Model and Technology Approvals

| Action | Approver | Secondary |
|---|---|---|
| New engine deployment | Model Risk Committee (CRO + CTO unanimous) | Board Risk Committee notification |
| Model parameter change | CRO | Model Risk Committee review |
| Emergency model suspension | CRO (unilateral) | Board notification within 24 hours |
| Production infrastructure change | CTO | CRO notification |
| Data source addition/change | CRO + CTO | Model Risk Committee review |

---

## APPENDIX D: REVISION HISTORY

| Version | Date | Author | Description of Changes | Approved By |
|---|---|---|---|---|
| 1.0 | March 3, 2026 | Calculus Research Operations | Initial publication | Board Risk Committee |

---

**END OF DOCUMENT**

*This document is the property of Calculus Research. Unauthorized reproduction or distribution is prohibited. This document must be reviewed and recertified annually by the Board Risk Committee. All personnel are responsible for understanding and complying with the procedures relevant to their role. Questions regarding interpretation should be directed to the Chief Risk Officer.*
