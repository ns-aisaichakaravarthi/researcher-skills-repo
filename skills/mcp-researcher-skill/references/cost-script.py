"""
Cost file generator for MCP research reports.
Referenced by SKILL.md Step 8.1 — run after CSV is saved.

Required variables (set before calling):
  RESEARCH_START  — ISO 8601 timestamp captured before Thread 1
  RESEARCH_END    — ISO 8601 timestamp captured after Gate 4
  SERVER_NAME     — kebab-case server name (e.g. "abacatepay-mcp")
"""
import json, os, glob
from datetime import datetime

# Pricing rates (claude-sonnet-4-6)
PRICE_INPUT      = 3.00 / 1_000_000
PRICE_OUTPUT     = 15.00 / 1_000_000
PRICE_CACHE_READ = 0.30 / 1_000_000

# Auto-detect project dir from current working directory
cwd = os.getcwd().replace("/", "-").lstrip("-")
project_dir = os.path.expanduser(f"~/.claude/projects/-{cwd}")
if not os.path.isdir(project_dir):
    all_dirs = sorted(glob.glob(os.path.expanduser("~/.claude/projects/*")), key=os.path.getmtime, reverse=True)
    project_dir = all_dirs[0] if all_dirs else ""
jsonl_files = sorted(glob.glob(f"{project_dir}/*.jsonl"), key=os.path.getmtime, reverse=True)
session_file = jsonl_files[0]

# Read all entries within the research window
input_tokens = output_tokens = cache_read = 0
with open(session_file) as f:
    for line in f:
        try:
            entry = json.loads(line)
            ts = entry.get("timestamp", "")
            if ts >= RESEARCH_START and ts <= RESEARCH_END:
                usage = entry.get("message", {}).get("usage", {})
                input_tokens  += usage.get("input_tokens", 0)
                output_tokens += usage.get("output_tokens", 0)
                cache_read    += usage.get("cache_read_input_tokens", 0)
        except Exception:
            pass

cost_input  = input_tokens  * PRICE_INPUT
cost_output = output_tokens * PRICE_OUTPUT
cost_cache  = cache_read    * PRICE_CACHE_READ
total_cost  = cost_input + cost_output + cost_cache

report_path = os.path.expanduser(f"~/Documents/mcp-reports/{SERVER_NAME}-cost.txt")
with open(report_path, "w") as f:
    f.write(f"MCP Server     : {SERVER_NAME}\n")
    f.write(f"Date           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Model          : claude-sonnet-4-6\n\n")
    f.write(f"Token Usage\n")
    f.write(f"  Input        : {input_tokens:,}\n")
    f.write(f"  Output       : {output_tokens:,}\n")
    f.write(f"  Cache Read   : {cache_read:,}\n\n")
    f.write(f"Cost\n")
    f.write(f"  Input        : ${cost_input:.4f}  ({input_tokens:,} x $3.00/1M)\n")
    f.write(f"  Output       : ${cost_output:.4f}  ({output_tokens:,} x $15.00/1M)\n")
    f.write(f"  Cache Read   : ${cost_cache:.4f}  ({cache_read:,} x $0.30/1M)\n")
    f.write(f"  Total        : ${total_cost:.4f}\n")

print(f"Cost file saved: {report_path}")
