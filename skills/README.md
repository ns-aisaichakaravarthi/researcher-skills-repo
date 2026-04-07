# Claude Skills -- Unified MCP Skill (v3.0)

> Last updated: 2026-03-27
> **Skill v3.0:** Security hardened, token-optimized, 4-gate enforcement
> Structure: Unified all-in-one workflow (research, setup, error recovery, audit)

---

## The Unified MCP Skill -- `/mcp-researcher-skill`

**All-in-one skill that replaces 4 separate skills:**

```
/mcp-researcher-skill "your request"
```

### What It Does

| Task | Command |
|------|---------|
| **Research** | `/mcp-researcher-skill "Research the GitHub MCP server"` |
| **Document** | `/mcp-researcher-skill "Document this MCP: https://github.com/org/repo"` |
| **Setup** | `/mcp-researcher-skill "Set up the Slack MCP server locally"` |
| **Fix Errors** | `/mcp-researcher-skill "The MCP server won't connect"` |
| **Audit Project** | `/mcp-researcher-skill "Review the project"` |
| **Batch Research** | `/mcp-researcher-skill "Research these MCPs: GitHub, Slack, Linear"` |

### Key Features

- Evidence-backed attribute documentation (Gate 1: Evidence Ledger)
- Multi-server parallel research + comparison
- Protocol version verification
- Conditional local setup (clone + install if user wants)
- 4 connection methods: STDIO, Package, Docker, Remote
- 7-phase inline error recovery
- Project compliance audit
- Self-learning via `learned-fixes.md`
- SSRF protection, curl timeouts, path validation
- 4-gate enforcement (no assumptions, no skipped learnings)
- Token-optimized SSOT architecture (~37% fewer tokens vs v2.0)

---

## Directory Structure (v3.0)

```
skills/
├── mcp-researcher-skill/          <-- THE SKILL
│   ├── SKILL.md                    (all workflows, rules, gates)
│   └── references/
│       ├── learned-fixes.md        (error case studies)
│       ├── multi-server.md         (batch research orchestration)
│       └── csv-example.md          (CSV formatting reference)
│
└── README.md                       <-- This file
```

---

## Architecture (v3.0 SSOT)

```
SKILL.md (source of truth)
  ├── Gates 1-4 (enforcement)
  ├── Steps 0-8 (workflow)
  ├── Learnings 1-8 (attribute rules)
  ├── Auth Detection Rules
  ├── CSV Format + Rules
  └── Error Recovery (7-phase)

references/multi-server.md
  └── References SKILL.md (never duplicates)

references/learned-fixes.md
  └── References SKILL.md (never duplicates)

references/csv-example.md
  └── Formatting reference only
```

---

## Quick Start

```bash
/mcp-researcher-skill "Research the GitHub MCP server"
/mcp-researcher-skill "Set up the Slack MCP server locally"
/mcp-researcher-skill "The MCP server won't connect"
/mcp-researcher-skill "Review the project"
/mcp-researcher-skill "Research these MCPs: GitHub, Slack, Linear"
```

One skill. One command. All functionality.

---

**v3.0.0 | Updated: 2026-03-27**
