#!/usr/bin/env python3
"""
PROP FIRM INTELLIGENCE SYSTEM — Main entry point

Usage:
  python run.py pipeline <firm_id>          # Full pipeline for one firm
  python run.py update <firm_id>            # Re-research + re-extract (no discovery)
  python run.py sweep                       # Monitor all firms for changes
  python run.py snapshot <firm_id>          # Save memory snapshot for one firm
  python run.py snapshot --all              # Snapshot all active firms
  python run.py dashboard <firm_id>         # Sync one firm to dashboard
  python run.py dashboard --all             # Sync all to dashboard
  python run.py discover <firm_id>          # Run discovery only
  python run.py research <firm_id>          # Run research only
  python run.py extract <firm_id>           # Run extraction only
  python run.py validate <firm_id>          # Run validation only
  python run.py firms                       # List all tracked firms
  python run.py new-firms                   # Scan for new firms to add
"""
import sys
import io
import json
from pathlib import Path
from dotenv import load_dotenv

# Force UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

load_dotenv(".env.local")

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from agents import (
    OrchestratorAgent,
    DiscoveryAgent,
    ResearchAgent,
    ExtractionAgent,
    ValidationAgent,
    MonitoringAgent,
    DashboardAgent,
)


def print_header():
    print("""
╔═══════════════════════════════════════════════════════╗
║  🤖  PROP FIRM INTELLIGENCE SYSTEM  v2.0             ║
╚═══════════════════════════════════════════════════════╝""")


def list_firms():
    cfg = json.loads((ROOT / "config" / "firms.json").read_text(encoding="utf-8"))
    print(f"\n{'ID':<20} {'NAME':<30} {'ACTIVE':<8} {'LAST CHECKED'}")
    print("─" * 80)
    for f in cfg["firms"]:
        print(f"  {f['id']:<18} {f['name']:<30} {'✅' if f.get('active') else '❌':<8} "
              f"{f.get('last_checked', 'never')[:19] if f.get('last_checked') else 'never'}")
    print()


def main():
    print_header()

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd  = sys.argv[1]
    arg  = sys.argv[2] if len(sys.argv) > 2 else None

    # ── Routing ────────────────────────────────────────────────────────

    if cmd == "pipeline" and arg:
        ok = OrchestratorAgent().run_full_pipeline(arg)
        sys.exit(0 if ok else 1)

    elif cmd == "update" and arg:
        ok = OrchestratorAgent().run_update_only(arg)
        sys.exit(0 if ok else 1)

    elif cmd == "sweep":
        results = OrchestratorAgent().run_monitoring_sweep()
        print(json.dumps(results, indent=2))

    elif cmd == "snapshot":
        monitor = MonitoringAgent()
        if arg == "--all":
            cfg = json.loads((ROOT / "config" / "firms.json").read_text(encoding="utf-8"))
            for f in cfg["firms"]:
                if f.get("active"):
                    monitor.record_snapshot(f["id"])
        elif arg:
            monitor.record_snapshot(arg)
        else:
            print("Usage: python run.py snapshot <firm_id|--all>")

    elif cmd == "dashboard":
        agent = DashboardAgent()
        if arg == "--all":
            results = agent.sync_all()
            print(json.dumps(results, indent=2))
        elif arg:
            ok = agent.sync_firm(arg)
            sys.exit(0 if ok else 1)
        else:
            print("Usage: python run.py dashboard <firm_id|--all>")

    elif cmd == "discover" and arg:
        result = DiscoveryAgent().discover_firm(arg)
        print(json.dumps(result, indent=2) if result else "Discovery failed")

    elif cmd == "research" and arg:
        result = ResearchAgent().research_firm(arg)
        print(json.dumps(result, indent=2) if result else "Research failed")

    elif cmd == "extract" and arg:
        result = ExtractionAgent().extract_firm(arg)
        print(json.dumps(result, indent=2) if result else "Extraction failed")

    elif cmd == "validate" and arg:
        report = ValidationAgent().validate_firm(arg)
        print(json.dumps(report, indent=2) if report else "Validation failed")

    elif cmd == "firms":
        list_firms()

    elif cmd == "new-firms":
        results = DiscoveryAgent().discover_new_firms()
        print(json.dumps(results, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
