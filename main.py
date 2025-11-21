# main.py
import argparse
import importlib
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from utils.requester import Requester

# Optional rich imports (fall back gracefully if not installed)
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
    console = Console()
except Exception:
    RICH_AVAILABLE = False
    console = None

logger = logging.getLogger("digtool")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

ASCII_LOGO = r"""
 ____  _ _  _____           _
|  _ \(_) ||  ___|_ _  ___| |_ ___
| | | | | || |_ / _` |/ __| __/ __|
| |_| | | ||  _| (_| | (__| |_\__ \
|____/|_|_||_|  \__,_|\___|\__|___/

 DigTool — OSINT email presence checker
"""

def print_logo():
    if RICH_AVAILABLE:
        console.print(Panel.fit(ASCII_LOGO, title="[bold]DigTool[/bold]", subtitle="v1.0"))
    else:
        print(ASCII_LOGO)

def load_config(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_modules(names: List[str]):
    modules = []
    for name in names:
        try:
            mod = importlib.import_module(f"modules.{name}")
            if not hasattr(mod, "check"):
                logger.warning("Module %s has no check() function, skipping", name)
                continue
            modules.append((name, mod))
            logger.debug("Loaded module: %s", name)
        except Exception as e:
            logger.exception("Failed to import module %s: %s", name, e)
    return modules

def _run_module_check(name, mod, email, requester):
    try:
        result = mod.check(email, requester)
        if isinstance(result, dict):
            result.setdefault("site", name)
            return result
        else:
            return {"site": name, "found": None, "evidence": "invalid_module_response", "raw": {"value": str(result)}}
    except Exception as e:
        logger.exception("Error while checking module %s: %s", name, e)
        return {"site": name, "found": None, "evidence": "exception", "raw": {"error": str(e)}}

def run_checks_concurrent(email: str, modules, requester: Requester, max_workers: int = 4, use_progress: bool = True):
    results = []
    if RICH_AVAILABLE and use_progress:
        progress = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"))
    else:
        progress = None

    if progress:
        progress.start()
        task = progress.add_task("Checking modules...", total=len(modules))

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_run_module_check, name, mod, email, requester): name for name, mod in modules}
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            if progress:
                progress.advance(task)
    if progress:
        progress.stop()
    return results

def pretty_print(results):
    if RICH_AVAILABLE:
        table = Table(title="DigTool Results", show_lines=False)
        table.add_column("Site", style="cyan", no_wrap=True)
        table.add_column("Found", style="magenta")
        table.add_column("Evidence", style="green")
        table.add_column("Raw (snippet)", style="white")
        for r in results:
            raw = r.get("raw", {})
            raw_snip = ""
            try:
                raw_snip = json.dumps(raw, ensure_ascii=False)[:180]
            except Exception:
                raw_snip = str(raw)[:180]
            table.add_row(r.get("site", "?"), str(r.get("found")), r.get("evidence", ""), raw_snip)
        console.print(table)
    else:
        for r in results:
            print(f"[{r.get('site')}] found={r.get('found')} evidence={r.get('evidence')}")
        print("\n--- JSON ---")
        print(json.dumps(results, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(prog="digtool", description="DigTool - OSINT email presence checker")
    parser.add_argument("email", help="Email address to check")
    parser.add_argument("--config", "-c", default="config.json", help="Path to config.json")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--verbose", action="store_true", help="Verbose logs")
    parser.add_argument("--no-rich", action="store_true", help="Disable rich even if installed")
    args = parser.parse_args()

    cfg = load_config(args.config)

    if args.verbose or cfg.get("verbose", False):
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

    # If user requested to disable rich, pretend it's not available
    if args.no_rich:
        global RICH_AVAILABLE, console
        RICH_AVAILABLE = False
        console = None

    print_logo()

    requester = Requester(
        user_agent=cfg.get("user_agent", "DigTool/1.0"),
        timeout=cfg.get("timeout_seconds", 10),
        rate_limit=cfg.get("rate_limit_seconds", 1.0)
    )

    modules = load_modules(cfg.get("modules", []))
    if not modules:
        logger.error("No modules loaded. Check config.json")
        sys.exit(1)

    max_workers = cfg.get("max_workers", 4)
    results = run_checks_concurrent(args.email, modules, requester, max_workers=max_workers, use_progress=RICH_AVAILABLE and not args.no_rich)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        pretty_print(results)

if __name__ == "__main__":
    main()
