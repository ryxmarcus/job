# Three-node knowledge synchronization

The Windows `local` node is the coordinator and canonical conflict authority. Enabled SSH workers are read from `nodes.json`; no hostnames, users, workspace paths, or key paths are duplicated in the scripts.

The mesh synchronizes only these retrieval sources:

- `knowledge-base/KNOWLEDGE-BASE.md`
- `infrastructure/activity-log.md`
- `infrastructure/environment-summaries.md`

Secrets, SSH keys, environment files, generated vector indexes, repositories, and application source are outside the synchronization scope.

Run a preview:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync-knowledge-mesh.ps1
```

Merge into the master and distribute the result to both workers:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync-knowledge-mesh.ps1 -Apply -Push
```

Install the coordinator as a Windows task running every 15 minutes:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-knowledge-mesh-schedule.ps1
```

Each run pulls all three files before writing anything. Top-level Markdown sections are merged by their exact `##` heading. A section found only on a worker is appended to the canonical master. When the same heading has different content, the master version remains canonical and the worker version is retained beneath `.tmp/knowledge-mesh/<run>/conflicts/` for review. The master files and both worker copies are backed up before replacement.

Every run writes `.tmp/knowledge-mesh/latest-manifest.json` with source nodes, merge counts, conflicts, output hashes, and push results. The exclusive lock `.tmp/knowledge-mesh/sync.lock` prevents overlapping scheduled runs.

Scheduled runs use `scripts/run-knowledge-mesh-scheduled.ps1` and append output or errors to `.tmp/knowledge-mesh/logs/YYYYMMDD.log`.
The Windows task is allowed to start and continue on battery power, does not require idle state, and ignores overlapping triggers.
