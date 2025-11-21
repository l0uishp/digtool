import sys
import argparse
from rich.console import Console
from digtool.core import DigToolCore
from digtool.config import Config
from digtool.logger import setup_logger

console = Console()

LOGO = """
╔═══════════════════════════════════════╗
║                                       ║
║         ██████╗ ██╗ ██████╗           ║
║         ██╔══██╗██║██╔════╝           ║
║         ██║  ██║██║██║  ███╗          ║
║         ██║  ██║██║██║   ██║          ║
║         ██████╔╝██║╚██████╔╝          ║
║         ╚═════╝ ╚═╝ ╚═════╝           ║
║                                       ║
║         TOOL - OSINT Scanner          ║
║            Version 1.0.0              ║
║                                       ║
╚═══════════════════════════════════════╝
"""

def main():
    console.print(LOGO, style="bold cyan")
    
    parser = argparse.ArgumentParser(
        description="DigTool - OSINT Email Verification Tool"
    )
    parser.add_argument("email", help="Email address to check")
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to configuration file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-m", "--modules",
        nargs="+",
        help="Specific modules to run"
    )
    
    args = parser.parse_args()
    
    try:
        config = Config(args.config)
        if args.verbose:
            config.data["verbose"] = True
        if args.modules:
            config.data["modules"] = args.modules
            
        logger = setup_logger(config.data.get("verbose", False))
        
        digtool = DigToolCore(config, logger)
        results = digtool.scan(args.email)
        
        console.print("\n[bold yellow]═══ Results ═══[/bold yellow]\n")
        
        for module_name, result in results.items():
            if result["found"]:
                console.print(f"[green]✓[/green] {module_name}: Found")
                if result.get("data"):
                    for key, value in result["data"].items():
                        console.print(f"  • {key}: {value}")
            else:
                console.print(f"[red]✗[/red] {module_name}: Not found")
            
            if result.get("error"):
                console.print(f"  [red]Error: {result['error']}[/red]")
        
        console.print("\n[bold green]Scan completed![/bold green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
