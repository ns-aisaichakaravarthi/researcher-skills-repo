# researcher-skills-repo -- MCP Skills Suite v3.1

This project contains MCP skills for research, deployment, error recovery, project auditing, and **post-research validation**. Security hardened, token-optimized, 4-gate enforcement.

## Quick Start

Clone this repo, navigate to the directory, and the unified skill will load automatically:

```bash
git clone https://github.com/aisaichakaravarthi/researcher-skills-repo.git
cd researcher-skills-repo
```

Then invoke skills in Claude Code:
- `/mcp-researcher-skill` — Research, deploy, fix, audit MCP servers
- `/mcp-attribute-validator` — Validate CSV reports for correctness

---

## Skill: `/mcp-researcher-skill`

**The all-in-one MCP skill** -- research and document attributes, conditionally set up locally, diagnose errors inline, run multi-server batch research, and audit projects -- all in one optimized execution path.

**Invocation:** `/mcp-researcher-skill`

Use this skill for any MCP-related task:

| Task | Example |
|------|---------|
| **Research** | "Research the GitHub MCP server" |
| **Attribute Docs** | "Document attributes for this MCP: https://github.com/org/repo" |
| **Local Setup** | "Set up this server locally", "Clone and run the Slack MCP" |
| **Error Recovery** | "The MCP server won't connect" [paste error] |
| **Project Audit** | "Review the project", "Is this ready to commit?" |
| **Batch Research** | "Research these MCPs: GitHub, Slack, Linear", "Compare GitHub and Stripe MCPs" |

**Features:**
- Evidence-backed attribute documentation (Gate 1: Evidence Ledger)
- 4-gate enforcement: Evidence Ledger, Connection Verification, Learning Walkthrough, Self-Improvement
- Multi-server parallel research + comparison
- Conditional local setup (clone + install if user wants)
- 7-phase inline error recovery (auto-diagnosis on connection fail)
- SSRF protection, curl timeouts, path validation
- 3 input types: Remote endpoint / GitHub URL / Server name
- 4 connection methods: STDIO / Published Package / Docker / Remote
- Protocol version verification before research
- Security mandate enforced (no credentials in chat, always via file editing)
- CSV report output
- Token-optimized SSOT architecture (~37% fewer tokens vs v2.0)

---

## Skill: `/mcp-attribute-validator`

**Post-research quality gate** -- validates CSV reports produced by `/mcp-researcher-skill` for correctness, consistency, and compliance.

**Invocation:** `/mcp-attribute-validator "<path-to-csv>"`

| Check Category | What It Catches |
|----------------|-----------------|
| **Mutual Exclusion** | Multiple Yes in exclusive groups (Protocol, Pricing, Tools Ops, Distribution) |
| **Transport-TLS** | STDIO servers with TLS=Yes, remote servers with no TLS |
| **Transport-Deployment** | StreamableHttp=Yes but Remote=No, STDIO=Yes but Local=No |
| **Auth Co-Occurrence** | OAuth=Yes but Bearer=No, PAT=Yes but Bearer=No |
| **Placeholder Leak** | `{servername}_`, `{prefix}_`, `{mcpScheme}` in tool/resource names |
| **Evidence Quality** | Vague tools descriptions, missing bullet points, Gate 1 violations |
| **Capability Consistency** | Tools=Yes but detailed_info="None", or vice versa |

**Output:** Structured Security Validation Report with findings, false-positive exclusions, and confidence score.

---

## Project Structure (v3.1)

```
researcher-skills-repo/
  CLAUDE.md                          <-- This file
  README.md                          <-- Public-facing readme
  marketplace.json                   <-- Marketplace config
  .claude-plugin/
    plugin.json                      <-- Plugin config
  skills/
    README.md                        <-- Skills overview
    mcp-researcher-skill/           <-- Research skill (source of truth)
      SKILL.md                       <-- All workflows, rules, gates
      references/
        cost-script.py               <-- Cost calculator (Step 8.1)
        learned-fixes.md             <-- Error case studies (#1-#18)
        multi-server.md              <-- Batch research orchestration
        csv-example.md               <-- CSV formatting reference
    mcp-attribute-validator/         <-- Validation skill (quality gate)
      SKILL.md                       <-- 9 rule categories, 6 phases
```

---

## Security & Confidentiality

All skills enforce strict security rules:

- **Never ask for credentials in chat** -- credentials are always entered via file editing
- **No hardcoded secrets** -- all config examples use `<PLACEHOLDER>` syntax
- **Credentials routed to local filesystem only** -- never transited through chat
- **Security mandates enforced at every step** -- no exceptions
- **SSRF protection** -- IP blocklist for endpoint probing (private ranges, localhost, metadata)
- **Curl safety** -- `--connect-timeout 5 --max-time 10 --max-redirs 3` on all probes
- **Path validation** -- reject `..`, symlinks, system dirs, other users' homes

---

## SSOT Architecture (v3.1)

```
mcp-researcher-skill/SKILL.md (source of truth -- authoritative for ALL rules)
  |
  +-- references/multi-server.md (batch orchestration ONLY, references SKILL.md)
  |
  +-- references/learned-fixes.md (error case studies ONLY, references SKILL.md)
  |
  +-- references/csv-example.md (formatting reference ONLY)

mcp-attribute-validator/SKILL.md (validation rules -- references unified skill)
  |
  +-- reads mcp-researcher-skill/SKILL.md for methodology
  |
  +-- reads mcp-researcher-skill/references/learned-fixes.md for error patterns
```

**Rules are NEVER duplicated across files.** The validator references the unified skill's SKILL.md as its methodology source.

---

## Workflow: Unified MCP Skill

```
"Research the GitHub MCP server and set it up locally"

  Skill handles:
  1. Research: Fills all attributes with evidence (Gate 1: Evidence Ledger)
  2. Verification: All 5 threads complete (Gate 2: Connection Verification)
  3. Learning check: L1-L8 applied (Gate 3: Learning Walkthrough)
  4. Setup: Asks deployment preference (local/remote/research-only)
  5. Local Setup (if chosen): Clones, installs, configures
  6. Error Recovery (if needed): Diagnoses and fixes connection errors inline
  7. Report: Saves CSV to configured path
  8. Self-Improvement: Records new patterns (Gate 4)
```

**No context-switching.** One skill. One command. Complete workflow.

---

## Team Setup

When team members clone this repo:

1. They get the unified skill automatically (in `skills/mcp-researcher-skill/`)
2. CLAUDE.md loads and shows available skills
3. They can invoke `/mcp-researcher-skill` immediately
4. All functionality consolidated -- no version conflicts

**No additional setup needed.**

---

## References

- **MCP Spec:** https://spec.modelcontextprotocol.io
- **MCP Servers Directory:** https://github.com/modelcontextprotocol/servers
- **Output location:** `~/Documents/mcp-reports/` (configurable)
- **Cloned repos location:** Configurable (asked at clone time, see SKILL.md Step 3)
- **Self-learning:** `skills/mcp-researcher-skill/references/learned-fixes.md`
- **Optimization guide:** `optimization_guide.md` (full v3.0 reference)

---

## Support & Feedback

For issues:
1. Use `/mcp-researcher-skill` with error message to diagnose (built-in error recovery)
2. Check `skills/mcp-researcher-skill/references/learned-fixes.md` for known solutions
3. Run project audit: `/mcp-researcher-skill` -> "Review the project"

For feedback on Claude Code, visit: https://github.com/anthropics/claude-code/issues

---

## Last Updated: 2026-03-28
**Status:** Production Ready | **Version:** 3.1.0 | **SSOT Architecture**
