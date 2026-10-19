# Work evidence and portfolio opportunities

These are artifacts reviewed locally, not a claim that every repository project is known or authored by Rahul. Employer details are deliberately generalised.

| Evidence | Demonstrable theme | Portfolio extension | Measurement to collect |
| --- | --- | --- | --- |
| `../../lambda_function.py` | S3 backup inventory and notification logic | Sanitised backup validator with duplicate/missing/undersized archive cases | Detection accuracy; runtime; known inventory coverage |
| `../../bb-backup-simple.sh`, `../../bb-backup.sh` | Repository backups, locking, AWS storage, notifications | Disposable Git server, test restores, checksums and retention | Restore success; RPO/RTO measured in lab |
| `../../scripts/ebx-auto-healing/README.md` | Recovery state machine with failure thresholds and cooldown | Dummy service failure injector and process-scoped recovery controller | False restarts; recovery time; restart rate |
| `../../core/knowledge_rag.py`, `../../scripts/search_knowledge.py` | Retrieval over operational documents | Synthetic incident knowledge base, citations, retrieval evaluation | Recall@k; citation correctness; response latency |
| `../../core/agent_loop.py`, `../../core/node_manager.py` | Infrastructure agent and node management | Read-only troubleshooting demo with scoped actions and audit log | Task success; denied-action coverage; time saved |
| `../../infrastructure/monitoring/dev/README.md` | Operational dashboard artifacts | Synthetic application dashboard and SLO burn-rate alerts | Alert precision; p95 latency; error budget |

## Recommended flagship: Reliable Operations Lab

Build one small service on a local Kubernetes cluster, deployed through CI. Add Terraform examples, Prometheus/Grafana, backup and restore validation, a guarded recovery controller, and a read-only incident assistant using synthetic runbooks. Keep actual employer code, endpoints, cloud account IDs, screenshots, customer data, and secrets out of the public repository. Reimplement examples using disposable local resources.

SRE story: define an availability SLI and latency SLI, choose lab SLOs, induce failure, measure recovery, write a postmortem.
DevOps story: reproduce deployment from a clean checkout, verify release gates and rollback, record release time.
MLOps extension: deploy a small scikit-learn model, use MLflow registry, add data/schema checks and measured model-quality gates. This is proposed work, not completed experience.
FDE story: write a customer problem brief, record requirements, demonstrate integration, show acceptance criteria and handover. Include a working API and evidence of actual users only when real.

Definition of done: runnable instructions; architecture diagram; dependency versions; CI result; failure demo; restore demo; recorded measurements; short demo video; honest limitations. No numerical improvement claim until measured.
