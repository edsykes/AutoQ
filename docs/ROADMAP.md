# AutoQ Roadmap

v1 is the **spine**: one thin pass through every idea (see SPEC.md, draft 4). Everything else is designed in and scheduled here.

## v1 — the spine
- Tiny world model and three SAP-style sims (vendors, POs, invoices) rendered as lossy, convention-skewed views of one world model, with org politics in the department definitions of "spend"
- All four drivers planted; v1 acceptance asserts the price driver and the duplicate-invoice artefact
- Question cascade (exec → VP → analyst leaf) with Question Governance acceptance
- One mission through all six steps, one thin agent per step; data steward duties folded into the Quality Agent
- Need Spec, plain Intent Record, resolve-before-create, Contract, Postgres catalogue, OpenLineage events
- One meaning mission: "spend" ratified by the Meaning Authority (authority commit only)
- Seeded default values and indicators that claims can link to
- Claim-graph answer; claim-routed domain review; counter-claims dispositioned by hand; no provisional release
- Data artefacts detected and flagged, not fixed
- Typed handoff records for all agent and human actions
- Thin Follow-up Agent proposing follow-ups to the asker's own authority
- Timeout handling: reminder, then re-route to the operator; no proxy decisions
- Builder: retrospective, one change type (skills and checks), eval gate (Dev and Promotion), hypotheses, rollback, ledger; Baseline v0 frozen with one seeded deficiency
- Four compounding metrics from handoff records
- Operator: spend caps, kill switch, storage space and cost view, lineage view, approval of stable-core changes
- `docker compose up` and one cloud VM (visitor's own key only on the hosted instance)

## v1.1 — meaning, data trust and values
- Fourth system: minimal existing lakehouse with trust assessment, reuse verdicts, hierarchies as ontology relations, lake meaning as proposals
- Matching agent with confidence bands and identity links
- Vote and evidence-weighted commit policies
- Values Authority commit workflow for changing the Values Register
- FX and mix driver assertions in acceptance
- Counter-claim triage with test sub-missions
- Remediation rules for factual conflicts
- Sensitivity check and provisional resolution with meaning missions

## v1.2 — depth and autonomy
- Full role sets in each step, including separate per-domain data stewards and a meaning steward
- Exploration against local minima: scouts, fresh-eyes rebuilds, plateau detection, diverse eval worlds
- Pattern library and shape evaluation by replay
- Retention-score eviction and consolidation
- Proposals to relax review (human-approved only)
- Purpose partition in the ontology, with Intent Records linked into it
- Follow-up routing to the lowest covering level, Dialogue Agent
- Delegates and the full timeout escalation chain

## v2 — production hardening
- Sealed audit set run by CI/operator, with Promotion-vs-Sealed divergence alerts
- Real connectors and adopting a real existing lake
- OIDC, Helm, multi-tenancy
- Notebook-style visualisation
- Prompt-injection evals and a threat model
- Standard ontology export, snapshot expiry policies
