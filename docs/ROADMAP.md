# AutoQ Roadmap

v1 is the **spine**: one thin pass through every idea (see SPEC.md). Everything else is designed in and scheduled here.

## v1 — the spine
- Tiny world model and three SAP-style sims (vendors, POs, invoices), one price driver, the "spend" conflict
- Question cascade (exec → VP → analyst leaf) with Question Governance acceptance
- One mission through all six steps, one thin agent per step
- Need Spec, resolve-before-create, Contract, Postgres catalogue, OpenLineage events
- One meaning mission: "spend" ratified by the Meaning Authority (authority commit only)
- Claim-graph answer; claim-routed domain review; counter-claim accept/reject; no provisional release
- Typed handoff records for all agent and human actions
- Builder: retrospective, one change type (skills and checks), eval gate (Dev and Promotion), hypotheses, rollback, ledger
- Four compounding metrics from handoff records
- Operator: spend caps, kill switch, storage space and cost view, lineage view
- `docker compose up` and one cloud VM (BYO key)

## v1.1 — meaning, data trust and values
- Fourth system: minimal existing lakehouse with trust assessment, reuse verdicts, hierarchies as ontology relations, lake meaning as proposals
- Matching agent with confidence bands and identity links
- Vote and evidence-weighted commit policies
- Default Values Register with story value links and indicators
- Counter-claim triage with test sub-missions
- Remediation rules for factual conflicts
- Sensitivity check and provisional resolution with meaning missions

## v1.2 — depth and autonomy
- Full role sets in each step
- Exploration against local minima: scouts, fresh-eyes rebuilds, plateau detection, diverse eval worlds
- Pattern library and shape evaluation by replay
- Retention-score eviction and consolidation
- Proposals to relax review (human-approved only)
- Purpose partition and Intent Records in the ontology
- Follow-up routing, Dialogue Agent, delegates and timeout escalation
- Sealed audit set run by CI/operator

## v2 — production hardening
- Real connectors and adopting a real existing lake
- OIDC, Helm, multi-tenancy
- Notebook-style visualisation
- Prompt-injection evals and a threat model
- Standard ontology export, snapshot expiry policies
