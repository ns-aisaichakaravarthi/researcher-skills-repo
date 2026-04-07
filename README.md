# researcher-skills-repo -- MCP Researcher Skills

All-in-one MCP server research, deployment, error recovery, and project auditing -- unified into a single fast, efficient skill. Security hardened, token-optimized, 4-gate enforcement.

**v3.0 Highlights:** SSRF protection, 4-gate enforcement, SSOT architecture, ~37% fewer tokens, zero duplication, 8 learnings, 6 error patterns documented

---

## Quick Start

```bash
git clone https://github.com/aisaichakaravarthi/researcher-skills-repo.git
cd researcher-skills-repo
```

Then use the unified skill:

```bash
/mcp-researcher-skill "Research the GitHub MCP server"
```

---

## What It Does

| Task | Command |
|------|---------|
| **Research** | `/mcp-researcher-skill "Research the GitHub MCP server"` |
| **Document** | `/mcp-researcher-skill "Document this MCP: https://github.com/org/repo"` |
| **Setup** | `/mcp-researcher-skill "Set up the Slack MCP server locally"` |
| **Fix Errors** | `/mcp-researcher-skill "The MCP server won't connect"` |
| **Audit** | `/mcp-researcher-skill "Review the project"` |
| **Batch** | `/mcp-researcher-skill "Research these MCPs: GitHub, Slack, Linear"` |

---

## Features

- Evidence-backed attribute documentation (Gate 1: Evidence Ledger)
- 4-gate enforcement (no assumptions, no skipped learnings)
- Multi-server parallel research + comparison
- Conditional local setup (clone + install if user wants)
- 7-phase inline error recovery
- SSRF protection, curl timeouts, path validation
- 3 input types: Remote endpoint / GitHub URL / Server name
- 4 connection methods: STDIO / Published Package / Docker / Remote
- Protocol version verification before research
- Security mandate (no credentials in chat, filesystem only)
- CSV report output to `~/Documents/mcp-reports/`
- Self-learning via learned-fixes.md (8 error patterns)

---

## Project Structure (v3.0)

```
researcher-skills-repo/
  CLAUDE.md                              # Project instructions
  README.md                              # This file
  marketplace.json                       # Marketplace config (v3.0.0)
  optimization_guide.md                  # Full optimization reference
  .claude-plugin/
    plugin.json                          # Plugin config (v3.0.0)
  skills/
    README.md                            # Skills overview
    mcp-researcher-skill/               # THE SKILL
      SKILL.md                           # Source of truth (all workflows, rules, gates)
      references/
        learned-fixes.md                 # Error case studies (#1-#4, #7-#8)
        multi-server.md                  # Batch research orchestration
        csv-example.md                   # CSV formatting reference
```

---

## Architecture (SSOT)

```
SKILL.md (source of truth)
  |-- references/multi-server.md (batch orchestration, references SKILL.md)
  |-- references/learned-fixes.md (error case studies, references SKILL.md)
  |-- references/csv-example.md (formatting reference only)
```

Rules are NEVER duplicated across files. Each reference file points to SKILL.md for authoritative rules.

---

## Workflow

```
User Input
  |
  v
/mcp-researcher-skill (Unified Skill)
  |
  +-- Gate 2: Connection Verification (5 concurrent threads)
  +-- Gate 1: Evidence Ledger (every Yes/No has source proof)
  +-- Gate 3: Learning Walkthrough (L1-L8 checked)
  +-- Gate 4: Self-Improvement (new patterns documented)
  |
  v
CSV Report (only after all gates pass)
```

---

## Security

- Never asks for credentials in chat (filesystem only)
- SSRF protection (IP blocklist for private ranges, localhost, metadata)
- Curl safety (`--connect-timeout 5 --max-time 10 --max-redirs 3`)
- Path validation (reject `..`, symlinks, system dirs)
- No hardcoded secrets (placeholder syntax required)
- Git clone depth limited (`--depth 1`)

---

## Documentation

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project instructions and quick start |
| `skills/mcp-researcher-skill/SKILL.md` | Complete skill definition (source of truth) |
| `skills/mcp-researcher-skill/references/learned-fixes.md` | Error case studies |
| `skills/mcp-researcher-skill/references/multi-server.md` | Batch research workflow |
| `skills/mcp-researcher-skill/references/csv-example.md` | CSV formatting reference |
| `optimization_guide.md` | Full v3.0 optimization reference |
| `marketplace.json` | Skills metadata and discovery |

---

Made with Claude Code | Version: 3.0.0 | Last Updated: 2026-03-27 | Status: Production Ready
