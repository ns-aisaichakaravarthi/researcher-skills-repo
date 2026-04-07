---
name: mcp-attribute-validator
user-invocable: true
model: opus
description: >
  Self-contained validator for MCP research CSV reports.
  9 rule categories, 6 validation phases. Detects logical conflicts, auto-rule
  violations, placeholder leaks, TLS/STDIO mismatches, hosting inconsistencies,
  non-read-only cross-validation, evidence gaps, and known error patterns.
  All rules, SDK mappings, and error pattern context are inlined.
  Outputs a structured Security Validation Report with false-positive filtering.
---

<!-- SKILL_VERSION: 1.3.0 | Updated: 2026-03-31 -->

# MCP Attribute Validator

**Post-research quality gate:** Audit CSV reports produced by `/mcp-researcher-skill`
for correctness, consistency, and compliance. All validation rules are self-contained in this file.

---

## Usage

**Invoke with:** `/mcp-attribute-validator`

```
/mcp-attribute-validator "<path-to-csv>"
```

If no CSV path is provided, prompt:
```
Which CSV report should be validated?
Enter full path (e.g. ~/Documents/mcp-reports/github-mcp-server.csv):
```

**Supports:** Single-server CSV (3 or 4 columns) and multi-server CSV (N+2 columns).

---

## Validation Strategy

```
Phase 1  Load & Parse       -> Read CSV, detect format (single vs multi), extract servers
Phase 2  Schema Check       -> Row completeness, duplicates, column count, mandatory rows
Phase 3  Rule Engine        -> 9 rule categories applied per server (see Rule Categories)
Phase 4  Cross-Correlation  -> Inter-attribute logic checks, false-positive filtering
Phase 4b Endpoint Verify    -> Fetch source from GitHub repo, verify Endpoint URL + transport
Phase 5  Evidence Scan      -> Vague/placeholder/unverified content detection
Phase 6  Report Generation  -> Structured output with findings, exclusions, recommendations
```

---

## Phase 1 -- Load & Parse

**Detect CSV format:**

| Format | Detection | Columns |
|--------|-----------|---------|
| **Single-server (standard)** | Exactly 3 columns: `Category, Attribute, Status` | 3 |
| **Single-server (with evidence)** | Exactly 4 columns: `Category, Attribute, Status, Evidence` | 4 |
| **Multi-server** | Column 1 = `Category`, Column 2 = `Attribute`, Columns 3..N = server values | N >= 3 |

**Extract server list:**
- Single-server: server name from filename or `MCP Server Name` row
- Multi-server: server names from `MCP Server Name` row (Row 2 in standard format)

**Skip empty server columns** -- columns where ALL data rows are blank.

**Evidence column handling:**
- If 4th column header is "Evidence", treat as single-server with evidence annotations
- Evidence column is informational only -- not validated by rules, but used for context
  when investigating findings

---

## Phase 2 -- Schema Check

**Mandatory rows (Report Format):**

Every server MUST have ALL of these rows. Flag any missing row as `SCHEMA_MISSING`.

```
MANDATORY ROW CHECKLIST (31 category+attribute pairs):

MCP Info
  [] Description
  [] Git Repo Version
  [] Category
  [] GitHub Repository
  [] Endpoint URL

Distribution Type
  [] Official
  [] Community

MCP Protocol Version
  [] 2025-11-25
  [] 2025-06-18
  [] 2025-03-26
  [] 2024-11-05

Pricing
  [] Free
  [] Paid

Hosting Provider
  [] SaaS Vendor
  [] 3rd Party SaaS
  [] GitHub
  [] GitLab
  [] Bitbucket
  [] SourceHut/Gitea/Gogs

Authentication
  [] OAuth 2.1 - Authorization Code Flow
  [] OAuth 2.1 - Client Credentials Flow
  [] Bearer Token
  [] Personal Access Token
  [] API Token

Data Protection
  [] TLS 1.3
  [] TLS 1.2
  [] Lower versions or no encryption

Transport Protocol
  [] STDIO
  [] HTTP/SSE
  [] StreamableHttp
  [] FastAPI

Tools Operations
  [] Read-only operations
  [] Read-only and/or update operations
  [] Read-only update and/or delete operations

Deployment Approach
  [] Local
  [] Container
  [] Remote

Compliance & Certifications
  [] HIPAA
  [] GDPR
  [] SOC 2
  [] FedRAMP

Capabilities
  [] Tools
  [] Resources
  [] Prompts
  [] Sampling

FIVE MANDATORY DETAILED ROWS (Learning 7):
  [] Capabilities - Tools,detailed_info
  [] Capabilities - Resources,detailed_info
  [] Capabilities - Prompts,detailed_info
  [] Capabilities - Sampling,detailed_info
  [] Non-Read-Only Tools,detailed_info
```

**Total attributes per server:** 50 (31 Yes/No rows + 5 text rows + 5 detailed_info rows + 9 info fields)

**Schema violations:**
- Missing mandatory row -> `SCHEMA_MISSING` (HIGH)
- Wrong attribute name for detailed rows (e.g., `No` instead of `detailed_info`) -> `SCHEMA_FORMAT` (HIGH)
- Empty cell where Yes/No expected -> `SCHEMA_BLANK` (HIGH)
- Duplicate Category+Attribute row in same server -> `SCHEMA_DUP` (HIGH)
- No Hosting Provider has Yes -> `SCHEMA_HOST` (MED)

**Duplicate row detection:**
```
FOR each server column:
  seen = {}
  FOR each row:
    key = Category + "|" + Attribute
    IF key IN seen:
      -> VIOLATION SCHEMA_DUP (HIGH) "Duplicate row: [Category],[Attribute] appears at rows [first] and [current]"
    seen[key] = row_number
```

**Hosting minimum check:**
```
hosting_any_yes = SaaS Vendor == "Yes" OR 3rd Party SaaS == "Yes"
                  OR GitHub == "Yes" OR GitLab == "Yes"
                  OR Bitbucket == "Yes" OR SourceHut/Gitea/Gogs == "Yes"

IF NOT hosting_any_yes:
  -> VIOLATION SCHEMA_HOST (MED) "No Hosting Provider marked Yes -- at least one required"
```

---

## Phase 3 -- Rule Engine (9 Categories)

Apply ALL rules to EACH server column independently. Track every violation with:
`{Server, Attribute, Rule ID, Expected, Actual, Risk Level}`.

---

### Rule Category 1: Mutual Exclusion

**Exactly ONE = Yes within each exclusive group. All others = No. No blanks.**

| Rule ID | Group | Options | Reference |
|---------|-------|---------|-----------|
| `MX-01` | Distribution Type | Official / Community | Step 5 |
| `MX-02` | Pricing | Free / Paid | Step 5, L4 |
| `MX-03` | Tools Operations | Read-only / R+Update / R+Update+Delete | Step 5, L5 |
| `MX-04` | MCP Protocol Version | 2025-11-25 / 2025-06-18 / 2025-03-26 / 2024-11-05 | Step 5 |

**Check:**
```
For each MX group:
  count_yes = number of "Yes" values in group
  count_blank = number of blank/empty values in group

  IF count_yes != 1  -> VIOLATION (risk: HIGH)
  IF count_blank > 0 -> VIOLATION (risk: HIGH, ref: Error Pattern #13)
  IF any cell contains text other than "Yes" or "No" -> VIOLATION (risk: MED)
```

---

### Rule Category 2: Transport-to-TLS Auto-Rules (Learning 3)

**STDIO transport -> ALL Data Protection fields = No. No exceptions.**

This includes "Lower versions or no encryption" -- the most commonly mismarked field.
Researchers often set it to Yes for STDIO servers reasoning "there is no encryption."
The correct value is **No** because the entire Data Protection category is not applicable
when there is no network layer. Docker containers may use a reverse proxy for encryption,
but that is a deployment-level concern, not a property of the STDIO transport protocol.

| Rule ID | Condition | Expected | Reference |
|---------|-----------|----------|-----------|
| `TLS-01` | STDIO=Yes AND no remote transport | TLS 1.3=No, TLS 1.2=No, **Lower=No** | L3, Error #7 |
| `TLS-02` | HTTP/SSE=Yes OR StreamableHttp=Yes | At least one TLS field=Yes | L3 |
| `TLS-03` | All transports=No | Flag as `COLLECTION_GAP` -- transport undetermined | Gate 2 |
| `TLS-04` | TLS 1.3=Yes AND Lower=Yes | Contradictory: modern TLS + "lower/no encryption" | Logic |
| `TLS-05` | TLS 1.2=Yes AND TLS 1.3=Yes | Flag: servers typically negotiate highest available | INFO |

**Check:**
```
has_stdio = Transport STDIO == "Yes"
has_remote = Transport HTTP/SSE == "Yes" OR Transport StreamableHttp == "Yes"
tls_13 = TLS 1.3 == "Yes"
tls_12 = TLS 1.2 == "Yes"
tls_lower = Lower versions or no encryption == "Yes"
tls_any_yes = tls_13 OR tls_12 OR tls_lower

IF has_stdio AND NOT has_remote AND tls_any_yes:
  -> VIOLATION TLS-01 (HIGH) "STDIO-only server has Data Protection field marked Yes"
  NOTE: The most common trigger is "Lower versions or no encryption" = Yes.
        Correct value for STDIO is No (no network layer = category not applicable).
        Docker reverse proxies are deployment-level -- they do not change the transport.

IF has_remote AND NOT tls_any_yes:
  -> VIOLATION TLS-02 (HIGH) "Remote transport with no TLS"

IF NOT has_stdio AND NOT has_remote:
  -> VIOLATION TLS-03 (MED) "No transport protocol detected"

IF tls_13 AND tls_lower:
  -> VIOLATION TLS-04 (MED) "TLS 1.3=Yes contradicts Lower/no encryption=Yes"

IF tls_13 AND tls_12:
  -> INFO TLS-05 "Both TLS 1.3 and 1.2 marked Yes -- verify server supports both"
```

---

### Rule Category 3: Transport-to-Deployment Auto-Rules (Step 5)

| Rule ID | Condition | Expected | Reference |
|---------|-----------|----------|-----------|
| `DEP-01` | STDIO=Yes | Local=Yes | Step 5 auto-rule |
| `DEP-02` | HTTP/SSE=Yes OR StreamableHttp=Yes | Remote=Yes | Step 5 auto-rule |
| `DEP-03` | Dockerfile evidence in description/tools | Container=Yes | Step 5.3, Error #4 |
| `DEP-04` | Container=Yes AND Local=No | Container implies local run capability | Logic |
| `DEP-05` | All Deployment=No | No deployment approach identified | Gate 2 |

**Check:**
```
IF Transport STDIO == "Yes" AND Deployment Local != "Yes":
  -> VIOLATION DEP-01 (HIGH) "STDIO=Yes requires Local=Yes"

IF (Transport HTTP/SSE == "Yes" OR Transport StreamableHttp == "Yes")
   AND Deployment Remote != "Yes":
  -> VIOLATION DEP-02 (HIGH) "Remote transport requires Remote=Yes"

IF Deployment Container == "Yes" AND Deployment Local != "Yes":
  -> VIOLATION DEP-04 (LOW) "Container=Yes typically implies Local=Yes (containers run locally)"

IF Deployment Local != "Yes" AND Deployment Container != "Yes" AND Deployment Remote != "Yes":
  -> VIOLATION DEP-05 (MED) "No deployment approach marked Yes"
```

---

### Rule Category 4: Authentication Co-Occurrence (Auth Detection Rules)

| Rule ID | Condition | Expected | Reference |
|---------|-----------|----------|-----------|
| `AUTH-01` | OAuth 2.1 Auth Code=Yes | Bearer Token=Yes | Auth Rules |
| `AUTH-02` | OAuth 2.1 Client Creds=Yes | Bearer Token=Yes | Auth Rules |
| `AUTH-03` | PAT=Yes | Bearer Token=Yes | Auth Rules |
| `AUTH-04` | Bearer Token=Yes AND all credential types=No | Flag: Bearer without underlying type | Auth Rule 1 |
| `AUTH-05` | STDIO-only AND OAuth(any)=Yes | OAuth requires HTTP endpoint; invalid for STDIO | Transport logic |
| `AUTH-06` | Remote transport AND all Auth=No | Remote server with no auth is suspicious | Security |

**Check:**
```
IF OAuth AuthCode == "Yes" AND Bearer Token != "Yes":
  -> VIOLATION AUTH-01 (HIGH) "OAuth token delivered via Bearer -- Bearer must be Yes"

IF OAuth ClientCreds == "Yes" AND Bearer Token != "Yes":
  -> VIOLATION AUTH-02 (HIGH) "OAuth token delivered via Bearer -- Bearer must be Yes"

IF PAT == "Yes" AND Bearer Token != "Yes":
  -> VIOLATION AUTH-03 (HIGH) "PAT delivered via Bearer header -- Bearer must be Yes"

IF Bearer Token == "Yes" AND PAT != "Yes" AND API Token != "Yes"
   AND OAuth AuthCode != "Yes" AND OAuth ClientCreds != "Yes":
  -> VIOLATION AUTH-04 (MED) "Bearer Token without underlying credential type identified"

has_stdio = Transport STDIO == "Yes"
has_remote = Transport HTTP/SSE == "Yes" OR Transport StreamableHttp == "Yes"

IF has_stdio AND NOT has_remote:
  IF OAuth AuthCode == "Yes" OR OAuth ClientCreds == "Yes":
    -> VIOLATION AUTH-05 (HIGH) "OAuth requires HTTP endpoint -- invalid for STDIO-only server"

IF has_remote:
  all_auth_no = OAuth AuthCode == "No" AND OAuth ClientCreds == "No"
                AND Bearer == "No" AND PAT == "No" AND API Token == "No"
  IF all_auth_no:
    -> VIOLATION AUTH-06 (MED) "Remote server with no authentication -- verify this is intentional"
```

---

### Rule Category 5: Placeholder & Format Detection (Learnings 8-9)

| Rule ID | Pattern | Cells to Check | Reference |
|---------|---------|----------------|-----------|
| `FMT-01` | `{servername}_`, `{prefix}_`, `{name}_` | Capabilities-Tools, Capabilities-Resources, Non-Read-Only Tools | L9, Error #16 |
| `FMT-02` | `{mcpScheme}`, `{tablePath}`, `{tableName}` | Capabilities-Resources | L9 |
| `FMT-03` | **Unquoted** embedded newlines in Description that break CSV row structure | MCP Info,Description | L8, Error #9, #12 |
| `FMT-04` | Git Repo Version = "UNVERIFIED" or SNAPSHOT | Git Repo Version | Error #10 |
| `FMT-06` | Invented category titles (not in standard taxonomy) | Capabilities-Tools, Non-Read-Only Tools | L6, Error #12 (ThingsBoard) |
| `FMT-07` | Git Repo Version inconsistency: "No" vs "NA" within same report | Git Repo Version across servers | Error #10 |
| `FMT-08` | Endpoint URL format invalid (not "N/A" and not a valid URL) | MCP Info,Endpoint URL | Format |
| `FMT-09` | GitHub Repository format invalid (not a valid GitHub URL) | MCP Info,GitHub Repository | Format |

**Standard Taxonomy -- Capabilities-Tools (L6):**
```
ALLOWED TITLES (Capabilities - Tools):
  "Search & Query Utilities"
  "Project Management"
  "Issue Management"
  "Team & Workspace Metadata"
  "Admin & Miscellaneous"
  "Other"

ALLOWED TITLES (Non-Read-Only Tools):
  "Import/Export Tools"
  "Content Management"
  "Configuration Tools"
  "Other Write Operations"
```

**Check:**
```
FOR each detailed_info cell:
  IF regex matches \{[a-zA-Z_]+\}_ or \{[a-zA-Z_]+\}:// or \{[a-zA-Z_]+\}/:
    -> VIOLATION FMT-01 or FMT-02 (HIGH)

  Extract all category header lines (lines without leading spaces or bullets)
  FOR each header:
    IF header NOT IN allowed_titles:
      -> VIOLATION FMT-06 (HIGH) "Invented category title: [header]"

FOR Description cell:
  IF contains newlines AND cell is NOT properly double-quoted:
    -> VIOLATION FMT-03 (HIGH) "Unquoted newline breaks CSV row structure"
  NOTE: Newlines inside properly quoted cells (RFC 4180) are valid CSV -- do NOT flag

FOR Git Repo Version:
  IF value == "UNVERIFIED" -> VIOLATION FMT-04 (MED)
  IF value matches /SNAPSHOT|alpha|beta|rc\d|dev/ -> VIOLATION FMT-04 (MED)

FOR Endpoint URL:
  IF value != "N/A" AND NOT starts with "http://" or "https://":
    -> VIOLATION FMT-08 (MED) "Endpoint URL is not N/A and not a valid URL"

FOR GitHub Repository:
  IF value does NOT match https://github.com/* pattern:
    -> VIOLATION FMT-09 (LOW) "GitHub Repository URL format unexpected"
```

**Git Repo Version consistency check (multi-server only):**
```
values = [Git Repo Version for all servers in report]
has_no = "No" in values
has_na = "NA" in values
IF has_no AND has_na:
  -> VIOLATION FMT-07 (MED) "Mixed 'No' and 'NA' fallback format"
```

---

### Rule Category 6: Evidence Quality (Gate 1 Compliance)

| Rule ID | Pattern | Risk | Reference |
|---------|---------|------|-----------|
| `EVD-01` | Capabilities-Tools cell contains only vague text, no tool names | HIGH | Gate 1 |
| `EVD-02` | Capabilities-Resources cell is vague (no URIs or names) | MED | Gate 1, L8 |
| `EVD-03` | Capabilities-Tools has "(+ N additional tools...)" without source | LOW | Gate 1 |
| `EVD-04` | Non-Read-Only Tools cell is vague (no tool names with bullets) | HIGH | Gate 1 |
| `EVD-05` | Description is empty or trivially short (< 50 chars) | MED | Completeness |

**Check:**
```
FOR Capabilities-Tools detailed_info:
  IF cell does NOT contain any bullet points (  * ):
    IF cell != "None":
      -> VIOLATION EVD-01 (HIGH) "No tool names listed -- evidence missing"

FOR Capabilities-Resources detailed_info:
  IF cell != "None" AND cell does NOT contain any bullet points:
    -> VIOLATION EVD-02 (MED) "No resource names listed -- evidence missing"

FOR Non-Read-Only Tools detailed_info:
  IF cell != "None" AND cell does NOT contain any bullet points:
    -> VIOLATION EVD-04 (HIGH) "Non-Read-Only Tools has content but no tool names listed"

FOR Description:
  IF cell is empty OR length < 50:
    -> VIOLATION EVD-05 (MED) "Description is missing or trivially short"
```

---

### Rule Category 7: Capability Consistency

| Rule ID | Condition | Expected | Reference |
|---------|-----------|----------|-----------|
| `CAP-01` | Capabilities,Tools=Yes | Capabilities-Tools,detailed_info != "None" | L7 |
| `CAP-02` | Capabilities,Tools=No | Capabilities-Tools,detailed_info = "None" | L7 |
| `CAP-03` | Capabilities,Resources=Yes | Capabilities-Resources,detailed_info != "None" | L7 |
| `CAP-04` | Capabilities,Resources=No | Capabilities-Resources,detailed_info = "None" | L7 |
| `CAP-05` | Capabilities,Prompts=Yes | Capabilities-Prompts,detailed_info != "None" | L7 |
| `CAP-06` | Capabilities,Prompts=No | Capabilities-Prompts,detailed_info = "None" | L7 |
| `CAP-07` | Capabilities,Sampling=Yes | Capabilities-Sampling,detailed_info != "None" | L7 |
| `CAP-08` | Capabilities,Sampling=No | Capabilities-Sampling,detailed_info = "None" | L7 |
| `CAP-09` | Tools Ops = R+Update or R+U+Delete | Non-Read-Only Tools != "None" | L7 |
| `CAP-10` | Tools Ops = Read-only | Non-Read-Only Tools = "None" | L7 |

**Check:**
```
IF Capabilities,Tools == "Yes" AND Capabilities-Tools cell == "None":
  -> VIOLATION CAP-01 (HIGH) "Tools=Yes but no tools listed"

IF Capabilities,Tools == "No" AND Capabilities-Tools cell != "None":
  -> VIOLATION CAP-02 (MED) "Tools=No but tools listed -- contradiction"

(same pattern for CAP-03 through CAP-08)

IF Tools Ops highest != "Read-only" AND Non-Read-Only cell == "None":
  -> VIOLATION CAP-09 (HIGH) "Write operations exist but Non-Read-Only Tools is None"

IF Tools Ops == "Read-only" AND Non-Read-Only cell != "None":
  -> VIOLATION CAP-10 (MED) "Read-only ops but Non-Read-Only Tools has content"
```

---

### Rule Category 8: Hosting & Infrastructure Consistency

| Rule ID | Condition | Expected | Reference |
|---------|-----------|----------|-----------|
| `HOST-01` | SaaS Vendor=Yes | Remote=Yes (vendor-hosted implies remote deployment) | Logic |
| `HOST-02` | SaaS Vendor=Yes | Endpoint URL != "N/A" (vendor hosting needs an endpoint) | Logic |
| `HOST-03` | SaaS Vendor=Yes AND STDIO-only | Contradictory: SaaS implies remote, STDIO is local | Logic |
| `HOST-04` | 3rd Party SaaS=Yes | Remote=Yes (third-party hosting implies remote) | Logic |
| `HOST-05` | Endpoint URL != "N/A" | Remote=Yes (endpoint implies remote access) | Cross-check |
| `HOST-06` | Endpoint URL != "N/A" | At least one remote transport=Yes (HTTP/SSE or StreamableHttp) | Cross-check |
| `HOST-07` | Endpoint URL = "N/A" AND Remote=Yes | Endpoint missing for remotely deployed server | Cross-check |
| `HOST-08` | Endpoint URL = "N/A" AND StreamableHttp=Yes | Server supports HTTP but no endpoint documented | Cross-check |
| `HOST-09` | Endpoint URL = "N/A" AND Description mentions managed/hosted service | Researcher may have missed a vendor-hosted endpoint | Evidence gap |
| `HOST-10` | Endpoint URL = "N/A" AND Official=Yes AND STDIO-only | Flag: check if vendor offers a managed/hosted version | Completeness |

**Check:**
```
saas_vendor = Hosting SaaS Vendor == "Yes"
third_party = Hosting 3rd Party SaaS == "Yes"
has_endpoint = Endpoint URL != "N/A"
has_remote_deploy = Deployment Remote == "Yes"
has_remote_transport = Transport HTTP/SSE == "Yes" OR Transport StreamableHttp == "Yes"
has_stdio_only = Transport STDIO == "Yes" AND NOT has_remote_transport

IF saas_vendor AND NOT has_remote_deploy:
  -> VIOLATION HOST-01 (MED) "SaaS Vendor=Yes but Remote=No -- vendor hosting implies remote deployment"

IF saas_vendor AND NOT has_endpoint:
  -> VIOLATION HOST-02 (MED) "SaaS Vendor=Yes but Endpoint URL=N/A -- vendor hosting should have an endpoint"

IF saas_vendor AND has_stdio_only:
  -> VIOLATION HOST-03 (MED) "SaaS Vendor=Yes but server is STDIO-only -- SaaS implies remote access"

IF third_party AND NOT has_remote_deploy:
  -> VIOLATION HOST-04 (MED) "3rd Party SaaS=Yes but Remote=No -- third-party hosting implies remote"

IF has_endpoint AND NOT has_remote_deploy:
  -> VIOLATION HOST-05 (HIGH) "Endpoint URL present but Remote=No"

IF has_endpoint AND NOT has_remote_transport:
  -> VIOLATION HOST-06 (HIGH) "Endpoint URL present but no remote transport (HTTP/SSE or StreamableHttp)"

# --- Endpoint URL = "N/A" checks (missing endpoint detection) ---

no_endpoint = Endpoint URL == "N/A"
is_official = Distribution Type Official == "Yes"
description_lower = lowercase(Description cell)

# Managed/hosted service indicators in Description or Evidence
managed_keywords = [
  "managed", "hosted", "fully managed", "enterprise",
  "cloud-hosted", "serverless", "as a service",
  "managed version", "hosted version", "official endpoint",
  "preview", "marketplace", "agentcore"
]
has_managed_signal = any keyword IN managed_keywords found in description_lower
                     OR in any Evidence cell (case-insensitive)

IF no_endpoint AND has_remote_deploy:
  -> VIOLATION HOST-07 (MED) "Remote=Yes but Endpoint URL=N/A -- remote deployment typically has an endpoint. If self-hosted, document the expected endpoint pattern (e.g., http://localhost:PORT)"

IF no_endpoint AND has_remote_transport:
  -> VIOLATION HOST-08 (MED) "StreamableHttp=Yes or HTTP/SSE=Yes but Endpoint URL=N/A -- server supports HTTP transport but no endpoint documented. Document the default endpoint (e.g., http://127.0.0.1:PORT/mcp)"

IF no_endpoint AND has_managed_signal:
  -> VIOLATION HOST-09 (MED) "Endpoint URL=N/A but Description/Evidence mentions managed or hosted service -- researcher should verify if vendor provides an official hosted endpoint URL"

IF no_endpoint AND is_official AND has_stdio_only:
  -> INFO HOST-10 "Official STDIO-only server with no endpoint -- verify whether the vendor offers a managed/hosted version with a remote endpoint (e.g., AWS managed MCP servers, vendor cloud offerings). If confirmed STDIO-only, this is expected."
```

---

### Rule Category 9: Non-Read-Only Cross-Validation

| Rule ID | Condition | Expected | Reference |
|---------|-----------|----------|-----------|
| `NRO-01` | Tool in Non-Read-Only not in Capabilities-Tools | Every write tool should appear in the main tools list | Completeness |
| `NRO-02` | Non-Read-Only has delete/cancel/remove patterns | Tools Ops should be R+U+Delete (highest level) | MX-03 alignment |
| `NRO-03` | Non-Read-Only has update/create/write patterns but no delete | Tools Ops should be R+Update (middle level) | MX-03 alignment |
| `NRO-04` | Connector style mismatch between Tools and Non-Read-Only | Inconsistent formatting | Style |

**Check:**
```
IF Non-Read-Only Tools != "None":
  nro_tools = extract tool names from Non-Read-Only detailed_info (lines with bullet points)
  cap_tools = extract tool names from Capabilities-Tools detailed_info

  FOR each tool_name IN nro_tools:
    IF tool_name NOT IN cap_tools:
      -> VIOLATION NRO-01 (MED) "Non-Read-Only tool '[tool_name]' not found in Capabilities-Tools list"

  nro_text = Non-Read-Only detailed_info cell text (lowercase)
  has_delete_patterns = regex matches (delete|cancel|remove|destroy|archive|purge|drop)
  has_update_patterns = regex matches (create|update|write|modify|set|configure|edit|push|send|post)

  IF has_delete_patterns AND Tools Ops R+U+Delete != "Yes":
    -> VIOLATION NRO-02 (HIGH) "Non-Read-Only contains delete operations but Tools Ops != R+U+Delete"

  IF has_update_patterns AND NOT has_delete_patterns AND Tools Ops R+Update != "Yes":
    -> VIOLATION NRO-03 (MED) "Non-Read-Only contains write operations but Tools Ops != R+Update"

  cap_connector = detect separator in Capabilities-Tools (en-dash " -- " or colon ": ")
  nro_connector = detect separator in Non-Read-Only (en-dash " -- " or colon ": ")
  IF cap_connector != nro_connector AND both are non-empty:
    -> VIOLATION NRO-04 (LOW) "Connector style mismatch: Tools uses [cap], Non-Read-Only uses [nro]"
```

---

## Phase 4 -- Cross-Correlation & False Positive Filtering

**Purpose:** Prevent flagging logically sound combinations as violations.

### False Positive Filters (apply BEFORE reporting)

| Filter ID | Condition | Action | Reason |
|-----------|-----------|--------|--------|
| `FP-01` | STDIO=Yes AND Auth(any)=Yes AND TLS=No | Suppress TLS-02 | Auth credentials are env vars for downstream services, not network-transmitted |
| `FP-02` | All Compliance=No | Suppress any compliance gap flag | Open-source MCP servers rarely carry certifications |
| `FP-03` | All Auth=No AND Transport=STDIO | Suppress AUTH-06 | STDIO servers commonly run without protocol-level auth |
| `FP-04` | Description mentions "archived" AND some capabilities=No | Suppress capability gap flag | Archived repos may have limited features |
| `FP-05` | Capabilities-Tools cell contains "(+ N additional...)" with a high count | Downgrade EVD-03 to LOW | Acceptable summary when connector count is very high |
| `FP-06` | STDIO=Yes AND API Token=Yes AND Bearer=No | Suppress AUTH-04 | AWS/cloud STDIO servers use env-var credentials (API keys, secrets) not Bearer headers |
| `FP-07` | Container=Yes AND Local=No AND Remote=Yes | Suppress DEP-04 | Container deployed remotely (e.g., Docker on cloud) does not require Local=Yes |

### Cross-Attribute Correlation Checks

| Check | Logic | Risk if violated |
|-------|-------|------------------|
| **Endpoint <-> Remote** | If Endpoint URL != "N/A", Deployment Remote should = Yes | HIGH |
| **Endpoint <-> Transport** | If Endpoint URL != "N/A", at least one remote transport (HTTP/SSE or StreamableHttp) should = Yes | HIGH |
| **SaaS Vendor <-> Remote** | If Hosting SaaS Vendor = Yes, Deployment Remote should = Yes | MED |
| **SaaS Vendor <-> Endpoint** | If Hosting SaaS Vendor = Yes, Endpoint URL should != "N/A" (vendor hosts remotely) | MED |
| **SaaS Vendor <-> Transport** | If Hosting SaaS Vendor = Yes and STDIO-only, flag inconsistency | MED |
| **Container <-> Local** | If Container = Yes, Local should also = Yes (containers run locally too) | LOW |
| **Protocol 2025-03-26 <-> FastMCP** | 2025-03-26 = Yes is ONLY valid for FastMCP 0.3.x; flag if no evidence of FastMCP | MED |
| **Protocol 2025-11-25 <-> SDK** | 2025-11-25 = Yes requires FastMCP >= 3.0 or Go SDK >= 1.12; flag if no evidence | MED |
| **Data Protection contradictions** | TLS 1.3=Yes AND Lower=Yes is contradictory | MED |
| **STDIO <-> OAuth** | STDIO-only AND any OAuth=Yes is contradictory | HIGH |

---

## Phase 4b -- Endpoint URL Source Verification (MANDATORY)

**Purpose:** Verify the Endpoint URL value in the CSV by checking the actual source code
for transport configuration. This catches cases where:
- A remote endpoint exists but was missed (Endpoint URL wrongly set to "N/A")
- A remote endpoint was assumed but doesn't exist (Endpoint URL wrongly set to a URL)
- Transport protocol fields don't match the actual server implementation

**This phase makes network calls to the GitHub repository listed in the CSV.**

### Step 1: Extract GitHub Repository URL

```
github_url = CSV row "MCP Info","GitHub Repository"

IF github_url is blank OR does not match https://github.com/*:
  -> SKIP Phase 4b (no repo to verify against)
  -> Add INFO note: "Endpoint verification skipped -- no valid GitHub Repository URL"

Parse org/repo from github_url:
  - Standard repo: https://github.com/ORG/REPO -> org=ORG, repo=REPO
  - Monorepo subdir: https://github.com/ORG/REPO/tree/BRANCH/path/to/server
    -> org=ORG, repo=REPO, subdir=path/to/server
```

### Step 2: Fetch Entry Point Source

Determine the server's entry point file based on language conventions.
For monorepos, prepend the subdir path.

```
FETCH ORDER (try each, stop at first success):

TypeScript/JavaScript:
  1. curl -sL https://raw.githubusercontent.com/ORG/REPO/main/{subdir}/src/index.ts
  2. curl -sL https://raw.githubusercontent.com/ORG/REPO/main/{subdir}/index.ts
  3. curl -sL https://raw.githubusercontent.com/ORG/REPO/main/{subdir}/src/server.ts
  4. curl -sL https://raw.githubusercontent.com/ORG/REPO/main/{subdir}/src/index.js

Python:
  5. curl -sL https://raw.githubusercontent.com/ORG/REPO/main/{subdir}/src/main.py
  6. curl -sL https://raw.githubusercontent.com/ORG/REPO/main/{subdir}/main.py
  7. curl -sL https://raw.githubusercontent.com/ORG/REPO/main/{subdir}/server.py

Go:
  8. curl -sL https://raw.githubusercontent.com/ORG/REPO/main/{subdir}/main.go
  9. curl -sL https://raw.githubusercontent.com/ORG/REPO/main/{subdir}/cmd/server/main.go

Java:
  10. Find via: curl -sL https://raw.githubusercontent.com/ORG/REPO/main/{subdir}/pom.xml
      then locate src/main/java/**/Application.java or Program.java

Also try "master" branch if "main" returns 404.

IF no entry point found:
  -> Add INFO note: "Endpoint verification: could not locate entry point source"
  -> Continue to Phase 5 (do not block)
```

### Step 3: Detect Transport from Source

Scan the fetched source file for transport-related imports and configuration:

```
TRANSPORT DETECTION PATTERNS:

TypeScript (@modelcontextprotocol/sdk):
  STDIO:          "StdioServerTransport" OR "stdio" in import path
  HTTP/SSE:       "SSEServerTransport" in import path
  StreamableHttp: "StreamableHTTPServerTransport" in import path

Python (mcp / fastmcp):
  STDIO:          "stdio_server" OR "StdioServerTransport" OR "mcp.server.stdio"
  HTTP/SSE:       "sse_server" OR "SseServerTransport" OR "mcp.server.sse"
  StreamableHttp: "StreamableHTTPServerTransport" OR "streamable"
  FastAPI:        "FastMCP" with "host=" or "port=" (indicates HTTP serving)

Go (mcp-go):
  STDIO:          "stdio.NewStdioServer" OR "server.ServeStdio"
  HTTP/SSE:       "sse.NewSSEServer" OR "server.ServeSSE"
  StreamableHttp: "server.ServeHTTP" OR "StreamableHTTP"

Java (io.modelcontextprotocol.sdk):
  STDIO:          "StdioServerTransportProvider" OR "StdioServerTransport"
  HTTP/SSE:       "WebMvcSseServerTransportProvider" OR "SseServerTransport"
  StreamableHttp: "StreamableHttpServerTransportProvider"

Record:
  source_has_stdio = true/false
  source_has_sse = true/false
  source_has_streamable = true/false
  source_has_any_remote = source_has_sse OR source_has_streamable
```

### Step 4: Fetch README for Endpoint Evidence

```
readme = curl -sL https://raw.githubusercontent.com/ORG/REPO/main/{subdir}/README.md
         (fall back to repo root README if subdir README not found)

Scan README for:
  - URL patterns matching endpoint format (https://*.*/mcp, http://localhost:PORT)
  - "endpoint", "remote", "hosted", "cloud", "url" keywords near URL patterns
  - Configuration examples with "url" field (not "command" field)

Record:
  readme_has_endpoint_url = true/false
  readme_endpoint_value = extracted URL or null
```

### Step 5: Cross-Validate Against CSV

```
csv_endpoint = Endpoint URL from CSV ("N/A" or a URL)
csv_stdio = Transport STDIO from CSV
csv_sse = Transport HTTP/SSE from CSV
csv_streamable = Transport StreamableHttp from CSV
csv_remote = Deployment Remote from CSV

# --- Endpoint URL Verification ---

IF csv_endpoint == "N/A":
  IF source_has_any_remote:
    -> FINDING EP-01 (HIGH) "Endpoint URL is N/A but source code imports remote transport
       ([SSEServerTransport|StreamableHTTPServerTransport]). Server likely has a remote
       endpoint that was not documented."

  IF readme_has_endpoint_url:
    -> FINDING EP-02 (MED) "Endpoint URL is N/A but README documents an endpoint URL:
       [readme_endpoint_value]. Verify and update CSV."

IF csv_endpoint != "N/A":
  IF NOT source_has_any_remote AND source_has_stdio:
    -> FINDING EP-03 (HIGH) "Endpoint URL is set to [csv_endpoint] but source code only
       imports StdioServerTransport. Server has no remote transport -- Endpoint URL
       should be N/A."

# --- Transport Field Verification ---

IF source_has_sse AND csv_sse != "Yes":
  -> FINDING EP-04 (HIGH) "Source imports SSE transport but CSV Transport HTTP/SSE = No"

IF source_has_streamable AND csv_streamable != "Yes":
  -> FINDING EP-05 (HIGH) "Source imports StreamableHttp transport but CSV StreamableHttp = No"

IF source_has_stdio AND csv_stdio != "Yes":
  -> FINDING EP-06 (MED) "Source imports STDIO transport but CSV STDIO = No"

IF NOT source_has_stdio AND csv_stdio == "Yes":
  -> FINDING EP-07 (MED) "CSV STDIO = Yes but source does not import STDIO transport"
```

### Step 6: Bonus -- Git Repo Version Verification

While connected to GitHub, also verify Git Repo Version:

```
releases = curl -sL https://api.github.com/repos/ORG/REPO/releases
tags = curl -sL https://api.github.com/repos/ORG/REPO/tags

csv_version = Git Repo Version from CSV

IF releases has entries:
  latest_release = releases[0].tag_name
  IF csv_version == "No" OR csv_version == "NA":
    -> FINDING EP-08 (MED) "Git Repo Version is [csv_version] but GitHub Releases exist.
       Latest release: [latest_release]"
ELSE IF tags has entries:
  latest_tag = tags[0].name
  IF csv_version == "No" OR csv_version == "NA":
    -> FINDING EP-09 (MED) "Git Repo Version is [csv_version] but GitHub Tags exist.
       Latest tag: [latest_tag]"
```

### Timeout & Error Handling

```
All curl calls use: --connect-timeout 5 --max-time 10
IF any curl call fails or times out:
  -> Add INFO note: "Endpoint verification: network request failed for [URL]"
  -> Continue with remaining checks (do not abort Phase 4b)
  -> Do not count network failures as findings

IF GitHub API rate-limited (HTTP 403):
  -> Add INFO note: "Endpoint verification: GitHub API rate limit reached -- skipping
     release/tag checks"
  -> Source file checks (raw.githubusercontent.com) are NOT rate-limited, continue those
```

---

## Phase 5 -- Evidence Scan

Scan all detailed_info cells and description for quality signals:

| Signal | Detection | Severity |
|--------|-----------|----------|
| **Vague tools** | Cell text has no `  * ` bullet lines AND is not "None" | HIGH |
| **Placeholder leak** | `\{[a-z_]+\}` pattern anywhere in detailed cells | HIGH |
| **Connector mismatch** | Capabilities-Tools uses en-dash but Non-Read-Only uses colon, or vice versa | LOW |
| **Duplicate tool** | Same tool name appears in multiple categories within Capabilities-Tools | MED |
| **Description overflow** | Description cell exceeds 500 characters (not a violation, but flag for review) | INFO |
| **Tool count mismatch** | Evidence mentions "N tools confirmed" but bullet count differs | MED |
| **Non-Read-Only orphan** | Tool in Non-Read-Only that does not appear anywhere in Capabilities-Tools | MED |
| **Missing separator** | Bullet line has no separator (no en-dash and no colon) between name and description | LOW |

---

## Phase 6 -- Report Generation

### Output Format

```
# Security Validation Report -- MCP Attribute Audit

**Audit Date:** [current date]
**CSV Audited:** [filename]
**Servers Validated:** [count] ([names])
**Methodology:** mcp-attribute-validator SKILL.md v1.2.0

---

## 1. Execution Summary

| Metric | Value |
|:-------|:------|
| **Total Attributes Scoped** | [count per server] x [servers] = [total] |
| **Data Completeness** | [% non-blank cells] |
| **Validation Findings** | [H] High, [M] Medium, [L] Low = [total] |
| **False Positive Exclusions** | [count] |
| **Confidence Score** | [High / Medium / Low] |

---

## 2. Validation Findings (Filtered for High Relevance)

| # | Server | Attribute | Rule ID | Risk | Finding |
|:--|:-------|:----------|:--------|:-----|:--------|
| 1 | [name] | [attr]    | [ID]    | HIGH | [description] |

---

## 3. False Positive Exclusions

- [Item]: [Why it was excluded -- logical reasoning]

---

## 4. Systemic Patterns

| Pattern | Affected Servers | Root Cause |
|:--------|:----------------|:-----------|
| [name]  | [list]          | [cause]    |

---

## 5. Recommendations

1. [Prioritized action items]
```

### Confidence Score Calculation

```
high_count   = findings with risk HIGH
med_count    = findings with risk MED
total_cells  = attributes_per_server * server_count

error_rate = (high_count * 3 + med_count) / total_cells

IF error_rate == 0     -> "High"    (perfect -- no findings)
IF error_rate < 0.02   -> "High"    (< 2% weighted error)
IF error_rate < 0.06   -> "Medium"  (2-6% weighted error)
IF error_rate >= 0.06  -> "Low"     (>= 6% weighted error)

Qualifier (append to score):
  IF total findings <= 2 AND error_rate < 0.08:
    append "(near-perfect -- [N] minor finding[s])"
```

---

## Validation Execution Order

**MANDATORY -- run phases in order. Do not skip.**

```
1. LOAD CSV
   -> Parse all server columns
   -> Identify format (single vs multi, with or without evidence column)

2. SCHEMA CHECK (Phase 2)
   -> Count mandatory rows per server
   -> Flag missing rows immediately (SCHEMA_MISSING)
   -> Flag blank cells (SCHEMA_BLANK)
   -> Flag duplicate rows (SCHEMA_DUP)
   -> Flag no hosting provider (SCHEMA_HOST)

3. RULE ENGINE (Phase 3) -- run ALL 9 categories per server:
   -> MX-01..04   (mutual exclusion)
   -> TLS-01..05  (transport <-> TLS)
   -> DEP-01..05  (transport <-> deployment)
   -> AUTH-01..06  (auth co-occurrence + transport alignment)
   -> FMT-01..09  (format & placeholders)
   -> EVD-01..05  (evidence quality)
   -> CAP-01..10  (capability consistency)
   -> HOST-01..06 (hosting & infrastructure consistency)
   -> NRO-01..04  (non-read-only cross-validation)

4. CROSS-CORRELATION (Phase 4)
   -> Apply false positive filters FIRST (FP-01..07)
   -> Then run cross-attribute checks
   -> Remove any finding matched by a filter

4b. ENDPOINT SOURCE VERIFICATION (Phase 4b) -- MANDATORY
   -> Extract GitHub Repository URL from CSV
   -> Fetch entry point source (index.ts, main.py, main.go, etc.)
   -> Detect transport imports (STDIO, SSE, StreamableHttp)
   -> Fetch README for endpoint URL evidence
   -> Cross-validate: EP-01..EP-07 (endpoint + transport checks)
   -> Bonus: EP-08..EP-09 (Git Repo Version vs Releases/Tags)
   -> All curl calls use --connect-timeout 5 --max-time 10
   -> Network failures are INFO notes, not findings

5. EVIDENCE SCAN (Phase 5)
   -> Scan detailed_info cells for quality signals

6. GENERATE REPORT (Phase 6)
   -> Compile findings, apply confidence formula
   -> Sort by risk (HIGH first), then by server
   -> Present structured output
```

---

## Known Error Pattern Cross-Reference (Inlined from Learned Fixes)

The validator automatically checks for recurrence of these documented patterns.
All detection logic is embedded in the rule engine above -- this section provides
context for WHY each rule exists.

| Error # | Pattern | Rule IDs | Root Cause Summary |
|---------|---------|----------|--------------------|
| #1 | Protocol version assumed without SDK check | MX-04 | Did not cross-reference SDK version against protocol mapping table. E.g., Go SDK v1.4.1 -> 2025-06-18, not latest |
| #2 | Auth fields all=No when credentials exist | AUTH-01..04 | Searched README only, missed server.json which defines BUILDKITE_API_TOKEN. Bearer/PAT/API Token can all be Yes for same credential |
| #3 | Multiple Tools Ops levels marked Yes | MX-03 | Marked both Read+Update and Read+Update+Delete. Must pick HIGHEST level only. cancel_*/delete_* = delete operations |
| #4 | Container=No when Docker evidence exists | DEP-03 | Missed Dockerfile.local, OCI registry, or server.json docker transport. Deployment is NOT mutually exclusive |
| #7 | TLS=Yes for STDIO server (Bearer confusion) | TLS-01 | Conflated Bearer Token (auth layer) with TLS (transport encryption). STDIO = always TLS No. Auth != Encryption |
| #8 | Git Repo Version wrong source priority | FMT-04 | Priority: 1st Releases -> 2nd Tags -> 3rd package.json. Copy version EXACTLY as shown, no notes/brackets |
| #9 | Description unquoted newlines corrupt CSV | FMT-03 | **Unquoted** newlines in Description break row structure. Properly quoted newlines (RFC 4180) are valid and NOT flagged |
| #10 | Git Repo Version "No" vs "NA" | FMT-07 | Fallback when no version found = "NA" (not "No", not "UNVERIFIED"). SNAPSHOT/alpha/beta/rc/dev = not real versions -> "NA" |
| #11 | Missing capability detailed rows | SCHEMA_MISSING | All 5 detailed rows mandatory even when content is "None". Attribute = always "detailed_info", never "No" |
| #12 | Unquoted description newlines hide Protocol/Pricing | FMT-03 | Cascade from #9: Only applies when newlines are unquoted, breaking row alignment. Properly quoted multiline cells do not cause this |
| #13 | Protocol/Pricing blank Status values | MX-02, MX-04 | All Protocol Version rows (4) and Pricing rows (2) must always be present with explicit Yes/No. No blanks, no commentary |
| #14 | Java SDK missing protocol mapping | MX-04 | Java SDK (io.modelcontextprotocol.sdk:mcp): < 0.13.0 -> 2024-11-05; >= 0.13.0 -> 2025-06-18. Check McpSchema.LATEST_PROTOCOL_VERSION |
| #15 | Capabilities=No without reading source | CAP-01..08 | README alone is never sufficient. Must read entry point source (Program.java, main.py, index.ts) + check tools/resources/prompts subdirs |
| #16 | Placeholder tool names in CSV | FMT-01, FMT-02 | {servername}_, {prefix}_ copied from README docs. Must resolve to actual names before writing CSV |

### Error Pattern Detail: Delete/Cancel Operation Dictionary

For MX-03 (Tools Operations) and NRO-02 detection, these tool name patterns indicate delete operations:
```
cancel_*  -> Delete operation
delete_*  -> Delete operation
remove_*  -> Delete operation
destroy_* -> Delete operation
archive_* -> Delete operation
purge_*   -> Delete operation
drop_*    -> Delete operation
unblock_* -> Write operation (state change, not delete)
```

### Error Pattern Detail: SDK Protocol Version Mappings

For MX-04 (Protocol Version) detection, these mappings are authoritative:
```
TypeScript SDK (@modelcontextprotocol/sdk):
  < 1.0.0    -> 2024-11-05
  1.0.0-1.11 -> 2025-03-26
  >= 1.12    -> 2025-06-18

Python SDK (mcp):
  < 1.0.0   -> 2024-11-05
  1.0.0-1.4 -> 2025-03-26
  1.5-1.14  -> 2025-06-18
  >= 1.15   -> 2025-06-18

Go SDK (github.com/mark3labs/mcp-go):
  < 1.4     -> 2024-11-05
  1.4-1.11  -> 2025-06-18
  >= 1.12   -> 2025-11-25

Java SDK (io.modelcontextprotocol.sdk:mcp):
  < 0.13.0  -> 2024-11-05
  >= 0.13.0 -> 2025-06-18

FastMCP (Python):
  < 0.3.0   -> 2024-11-05
  0.3.x     -> 2025-03-26
  0.4.x-2.x -> 2025-06-18
  >= 3.0    -> 2025-11-25
```

### Error Pattern Detail: Mandatory Detailed Rows Format

For SCHEMA_MISSING (#11) detection:
```
ALWAYS include all five (attribute = "detailed_info"):
  Capabilities - Tools,detailed_info,"<tools OR None>"
  Capabilities - Resources,detailed_info,"<resources OR None>"
  Capabilities - Prompts,detailed_info,"<prompts OR None>"
  Capabilities - Sampling,detailed_info,"<sampling OR None>"
  Non-Read-Only Tools,detailed_info,"<write tools OR None>"

WRONG:
  Capabilities - Sampling,No
  Capabilities - Sampling,No,
```

---

## Integration with Unified MCP Skill

This validator is a **post-research quality gate**. It runs AFTER `/mcp-researcher-skill`
produces a CSV, BEFORE the report is considered final.

**Recommended workflow:**
```
1. /mcp-researcher-skill "Research server X"   -> produces CSV
2. /mcp-attribute-validator "<csv-path>"          -> validates CSV
3. Fix any HIGH findings
4. Re-validate until 0 HIGH findings
5. CSV is production-ready
```

**The validator does NOT:**
- Modify the CSV (read-only audit)
- Re-research ALL attributes (targeted verification only)
- Probe MCP endpoints directly (no MCP protocol calls)
- Overwrite any files

**The validator DOES:**
- Read the CSV file
- Apply all validation rules from this SKILL.md (self-contained)
- **Fetch source code from the GitHub repo** listed in the CSV (Phase 4b) to verify
  Endpoint URL and Transport Protocol accuracy
- **Check GitHub Releases/Tags API** to verify Git Repo Version (Phase 4b bonus)
- Output a validation report to the terminal

---

## Security

- **Read-only operation** -- never writes to CSV or methodology files
- **Targeted network access** -- Phase 4b fetches public source files from GitHub
  (raw.githubusercontent.com) and public GitHub API (api.github.com/repos) only.
  No authenticated requests. No private repo access. All curl calls use
  `--connect-timeout 5 --max-time 10`
- **No credential handling** -- does not process or display any secrets
- **Path validation** -- rejects CSV paths outside user home directory
- **No endpoint probing** -- does NOT call or probe the MCP server endpoint itself

---

**v1.3.0 | Created: 2026-03-28 | Updated: 2026-03-31**
**Status:** Production Ready
**Self-contained:** All validation rules, error patterns, and SDK mappings are inlined in this file.
**Network access:** Phase 4b fetches public GitHub source files and API to verify Endpoint URL and transport accuracy.
