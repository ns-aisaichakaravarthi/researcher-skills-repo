<!-- SKILL_VERSION: 3.0.5 — must match SKILL.md version -->
# Multi-Server Parallel Research

🔒 **SKILL MODIFICATION POLICY — ABSOLUTE ENFORCEMENT**

When modifying ANY part of this file (format, rule, instruction, workflow step, output template):

1. **Read the full context first** — understand how the existing instruction works before changing it
2. **Change only what was asked** — never silently remove working logic, calculation methods, enforcement rules, or checklists
3. **Preserve the working method** — if changing a format or presentation, keep the underlying rules and instructions intact
4. **No collateral removal** — dropping an instruction while reformatting its container is a violation

---

🚫 **ZERO-ASSUMPTION POLICY applies to EVERY server in the batch.**

🔒 **MANDATORY before any batch research:**
> 1. Follow SKILL.md Gates 1-3 (Evidence Ledger, Connection Verification, Learning Gate)
> 2. All learnings (L1–L10) are embedded in SKILL.md Step 5.1–5.13 — follow each section's rules directly
> 3. Each Layer 1 agent MUST build its own Evidence Ledger (internal only — do NOT output in agent response) — no attribute without source proof
> 4. If an agent cannot verify an attribute → return `"No"` and flag, never `"UNVERIFIED"` or `"unknown"`
> SKILL.md is the single source of truth — rules are not duplicated here.

## Workflow

1. **Detect** — Step 0-M identifies 2+ servers in input
2. **Parse & Classify** — Step M1: resolve all server names to GitHub URLs
3. **Confirm** — show list to user, allow adjustment before proceeding
3.5. **Auth Pre-Scan** — quick-scan ALL servers for auth signals (README text via Detection Patterns, API Token, PAT, Bearer, env TOKEN/KEY/SECRET); README is a PRIMARY scan source for STDIO/GitHub repo servers; show summary table (AUTH REQUIRED / No auth needed per server); collect 3-option decisions before any dispatch; proceed immediately with no-auth servers
4. **Dispatch** — Step M2: launch one Layer 1 Research Agent per server in parallel (only after all auth decisions collected from step 3.5)
5. **Collect** — wait for all agents to return JSON results
6. **Finalize** — Step M3: render individual CSVs + comparison table
7. **Prompt** — offer: set up locally / view full report / re-sort / done

---

**Trigger:** Auto-detected via Step 0-M (see below). No explicit command needed.

**Architecture:** 2-layer sub-agent system. Token-bounded. Parallel per server. No scoring.

---

## Step 0-M — Multi-Server Detection

Before any research begins, check if input contains multiple servers.

**Detection patterns (any match → enter Multi-Server mode):**

| Pattern | Example |
|---------|---------|
| Comma-separated | "GitHub MCP, Slack MCP, Notion MCP" |
| "and"-separated | "GitHub MCP and Slack MCP and Notion MCP" |
| Numbered list | "1. GitHub MCP\n2. Slack MCP" |
| JSON array | `["github-mcp", "slack-mcp"]` |
| Explicit keyword | "research X, Y, Z in parallel" |

**If 1 server detected** → continue with standard single-server workflow (Step 0 onward).
**If 2+ servers detected** → enter Multi-Server mode (Steps M1–M3 below).

---

## Layer 0 — Coordinator

**Step M1: Parse & Classify**
Extract all server identifiers. Classify each (name / GitHub URL / endpoint).
Resolve names to GitHub URLs before dispatching using SKILL.md Step 4 Resolution Order (STEP 1–4):
- STEP 1: Check `modelcontextprotocol/servers` reference repo (Source of Truth)
- STEP 2: GitHub topic search — `topic:mcp-server+{name}` (Wide Net)
- STEP 3: Git Trees API — monorepo subdirectory discovery (Deep Dive)
- STEP 4: Keyword pattern fallback — `{vendor}-mcp-server OR mcp-{vendor}` (Last Resort)

Confirm list before proceeding:
```
Found [N] servers to research:
1. GitHub MCP → github.com/github/github-mcp-server
2. Slack MCP  → github.com/slack/slack-mcp-server

Accuracy estimate:
  ≤ 3 servers → 100% parity with single-server research (recommended)
  4–5 servers → ⚠️  best-effort (~90–95%) — L9 source verification may compress on complex servers
  > 5 servers → blocked (split into batches of ≤5)

[ 1 ] Proceed
[ 2 ] Adjust list
```

Limit: 5 servers max per batch. If more → ask user to split into batches of ≤5.
🔒 3 servers is the recommended batch size for 100% accuracy parity with single-server research.

**Step M2: Dispatch Layer 1 Agents (parallel)**
Launch one Research Agent per server simultaneously.
Pass each agent: server URL + attribute schema + JSON output format.
Do NOT wait for one to finish before starting others.

**Step M3: Finalize**
Once ALL Layer 1 results received → render individual CSVs + comparison table.

---

## Layer 1 — Research Agent (per server, token budget: ~5,000)

**Budget breakdown (per agent):**
```
Input  (README + server.py + lock file + config files)  : ~8,000–20,000 tokens
Output (full JSON including capabilities_detail)         : ~1,000–5,000 tokens
Total per agent                                          : ~9,000–25,000 tokens
```
At 3 servers: ~27,000–75,000 total — well within context limits, full accuracy guaranteed.
At 4–5 servers: ~36,000–125,000 total — manageable, minor compression risk on complex servers.

Each agent runs the **Step 0.5 parallel search workflow** (5 concurrent threads) for its assigned server. Thread 1 uses SKILL.md Step 4 Resolution Order (STEP 1–4) when resolving a server name to a GitHub URL. Then returns ONLY this JSON structure (no prose):

```json
{
  "server": "GitHub MCP",
  "repo": "github.com/github/github-mcp-server",
  "attributes": {
    "name": "GitHub MCP Server",
    "description": "...",   // 3–4 sentences, single continuous line — NO embedded newlines (Pattern #9/#12)
    "version": "v1.2.3",   // "No" if no Releases or Tags found — package.json is NOT a valid version source (Pattern #10)
    "category": "Developer Tools",
    "distribution": "Official",
    "protocol_version": "2025-06-18",
    "framework": "mcp 1.15",
    "pricing": "Free",
    "hosting": "GitHub",
    "auth": "Personal Access Token",
    "tls": "STDIO N/A",
    "transport": "STDIO",
    "tools_ops": "R+Update+Delete",
    "deployment": "Local",
    "remote": "No",
    "remote_endpoint": "N/A",
    "capabilities": ["Tools"],
    "capabilities_detail": {
      "tools": "Search & Query Utilities\n  • tool_name – Description of what it does",
      "resources": "None",
      "prompts": "None",
      "sampling": "None",
      "non_readonly": "None"
    }
  },
  "evidence": ["README line 12", "pyproject.toml line 5"],
  "auth_required": true,
  "auth_types_detected": ["API Token", "Bearer Token"],
  "errors": []
}
```

**CSV mapping (Layer 0 → CSV rows):**
```
attributes.name              → MCP Info,Name,<value>
attributes.description       → MCP Info,Description,<value>   // must be 3–4 sentences, single continuous line, NO embedded newlines
attributes.version           → MCP Info,Git Repo Version,<value>
attributes.category          → MCP Info,Category,<value>
attributes.remote_endpoint   → MCP Info,Endpoint URL,<value>
attributes.capabilities_detail.tools       → Capabilities - Tools,detailed_info,<value>
attributes.capabilities_detail.resources   → Capabilities - Resources,detailed_info,<value>
attributes.capabilities_detail.prompts     → Capabilities - Prompts,detailed_info,<value>
attributes.capabilities_detail.sampling    → Capabilities - Sampling,detailed_info,<value>
attributes.capabilities_detail.non_readonly → Non-Read-Only Tools,detailed_info,<value>
```
🔒 `attributes.name` → Status column of `MCP Info,Name` row. Never use `"server"` (top-level) for this row — `"server"` is used only for the comparison table header.
🔒 `capabilities_detail` values follow SKILL.md Step 5.13 format exactly: standard taxonomy titles (L6), "None" fallback (L7), en-dash connector for Tools, colon connector for Non-Read-Only (see SKILL.md Report Format).

**Agent rules:**
- Output JSON only — no explanations, no markdown
- **ZERO-ASSUMPTION:** If data missing → return `"No"` and flag — never `"UNVERIFIED"`, never `"unknown"`, never guess
- **Auth detection:** Apply SKILL.md Step 5.6.B implicit auth scan (README text / headers / env / args) for all 3 input types. **README is a PRIMARY scan source** — apply Detection Patterns against full README text: API Token (`"api key"`, `"api_token"`, `"api_key"`); PAT (`"personal access"`, `"pat"`, `"personal token"`, `"personal access token"`, `"personal_access_token"`); Bearer (`"Authorization: Bearer"`); also scan for `"authentication"`, `"credentials"`, `"token required"`, `"requires auth"`. Additionally scan env/args/headers from config files. Set `auth_required: true` and populate `auth_types_detected` for every matched type — do NOT omit any. If user chose Option 3 (proceed without auth), apply the fallback rule: mark ALL pattern-matched auth types as Yes (evidence = detection pattern match). OAuth 2.1 (Auth Code / Client Creds) = No for STDIO transport (see SKILL.md Step 5.6 STDIO exception).
- If repo inaccessible → set `errors: ["repo not found"]`, return partial data with UNVERIFIED fields
- Do not call other agents or tools outside README + file search + endpoint probe
- **Evidence required:** Every attribute value MUST include source in `"evidence"` array (file + line or URL)
- **Learning gate:** Apply all Learnings from SKILL.md Step 5.1–5.13 (L1→Step 5.3, L3→Step 5.7, L4→Step 5.4, L5→Step 5.9, L6→Step 5.13, L7→Step 5.13, L8→Step 5.1, L9→Step 5.12, L10→Step 5.13). **L3 critical:** Fill Step 5.10 (Deployment) BEFORE Step 5.7 (TLS). Container = Yes → "Lower versions or no encryption" = No always — overrides STDIO logic. Mixed-deployment (STDIO + Container) → all 3 TLS rows = No (Error Pattern #18).
- **SSRF protection:** Validate all probe URLs against SKILL.md Security Mandate blocklist before probing
- **Curl safety:** All probes use `--connect-timeout 5 --max-time 10 --max-redirs 3`
- **Rate limit:** Max 3 attempts per endpoint, 2-second delay between retries

---

## Layer 0 — Comparison Summary Output

Show ALL attributes for each server in a full comparison table:

```
MULTI-SERVER RESEARCH SUMMARY — [date]
════════════════════════════════════════════════════════════════════════════════════════════════════════
Server          | Version | Category         | Protocol    | Hosting  | Auth         | TLS     | Transport    | Tools Ops    | Deployment | Remote | Dist
----------------|---------|------------------|-------------|----------|--------------|---------|--------------|--------------|------------|--------|------
GitHub MCP      | v1.2.3  | Developer Tools  | 2025-06-18  | GitHub   | PAT          | STDIO/NA| STDIO        | R+U+D        | Local      | No     | Official
Slack MCP       | v2.0.1  | Productivity     | 2025-03-26  | SaaS     | OAuth 2.1    | TLS 1.3 | HTTP/SSE     | R+U          | Remote     | Yes    | Official
Linear MCP      | v0.9.0  | Productivity     | 2024-11-05  | GitHub   | API Token    | STDIO/NA| STDIO        | Read-only    | Local      | No     | Community
════════════════════════════════════════════════════════════════════════════════════════════════════════
Default sort: Protocol Version (newest first)
Sort options: protocol / hosting / auth / transport / deployment
Reports saved: ~/Documents/mcp-reports/
```

**All 11 comparison columns:**
1. Version (from GitHub Releases or Tags only — "No" if neither found; package.json is not a valid source per Pattern #10)
2. Category (Developer Tools / Productivity / Data Retrieval / File Management)
3. Protocol (MCP protocol version)
4. Hosting (SaaS / GitHub)
5. Auth (OAuth 2.1 / Bearer / PAT / API Token)
6. TLS (TLS 1.3 / TLS 1.2 / STDIO N/A)
7. Transport (STDIO / HTTP/SSE / StreamableHttp)
8. Tools Ops (Read-only / R+U / R+U+D)
9. Deployment (Local / Container / Remote)
10. Remote (Yes / No)
11. Dist (Official / Community)

After summary, prompt:
```
What next?
[ 1 ] Set up one of these locally
[ 2 ] View full report for a specific server
[ 3 ] Re-sort by different criteria
[ 4 ] Done
```

**Auth handling:** Auth decisions are collected during Step 3.5 (Auth Pre-Scan) BEFORE dispatch — not post-summary. See SKILL.md MULTI-SERVER AUTH PRE-SCAN block for the full workflow. If a server's `auth_required: true` and user chose Option 3, the Option 3 fallback rule applies (mark all pattern-matched auth types as Yes).

---

## Error Handling
- Server unreachable → log error, continue batch, mark as "ERROR" in summary
- Duplicate servers in list → deduplicate silently, note once
- New error patterns found → flag to user for manual review

---

## Key Learnings Reference

> **All Learnings (L1–L10) are embedded in SKILL.md Step 5.1–5.13.** They are the single source of truth.
> Read SKILL.md before starting any multi-server batch research. Do not duplicate rules here.

---

## Final Report Format

> Use the Final Report Format box defined in SKILL.md for all batch research reports.
> Display order: Comparison table → individual Attributes Information or Detected Information → REPORT SUCCESSFULLY GENERATED box (see SKILL.md Final Report Output).
