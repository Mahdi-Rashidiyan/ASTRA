#!/usr/bin/env python3
"""
HPCShell - High-Performance Computing Shell
Main entry point for the shell
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.shell import HPCShell
from utils.config import Config
from utils.logger import setup_logger

def main():
    """Main entry point for HPCShell"""
    
    # Setup logging
    logger = setup_logger()
    
    # Load configuration
    config = Config()
    
    # Print banner
    print_banner()
    
    # Create and run shell
    try:
        shell = HPCShell(config)
        shell.run()
    except KeyboardInterrupt:
        print("\n\nExiting HPCShell...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

def print_banner():
    """Print welcome banner"""
    # Allow alternate banner via env var: set BANNER_STYLE=alt
    if os.environ.get('BANNER_STYLE', '').lower() == 'alt':
        print_banner_alt()
        return
    # ANSI color codes
    RED = "\033[31m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"

    # Use a raw formatted string to avoid escape-sequence warnings
    banner = fr"""
{MAGENTA}╔════════════════════════════════════════════════════════════════════════╗{RESET}
{MAGENTA}║{RESET}                                                                        {MAGENTA}║{RESET}
{MAGENTA}║{RESET}  {CYAN} █████╗ ███████╗████████╗██████╗  █████╗ {RESET}             {MAGENTA}║{RESET}
{MAGENTA}║{RESET}  {CYAN}██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗{RESET}             {MAGENTA}║{RESET}
{MAGENTA}║{RESET}  {CYAN}███████║███████╗   ██║   ██████╔╝███████║{RESET}             {MAGENTA}║{RESET}
{MAGENTA}║{RESET}  {CYAN}██╔══██║╚════██║   ██║   ██╔══██╗██╔══██║{RESET}             {MAGENTA}║{RESET}
{MAGENTA}║{RESET}  {CYAN}██║  ██║███████║   ██║   ██║  ██║██║  ██║{RESET}             {MAGENTA}║{RESET}
{MAGENTA}║{RESET}  {CYAN}╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝{RESET}             {MAGENTA}║{RESET}
{MAGENTA}║{RESET}                                                                        {MAGENTA}║{RESET}
{MAGENTA}║{RESET}    {YELLOW}ASTRA — ADVANCED HIGH-PERFORMANCE COMPUTING{RESET}    {MAGENTA}║{RESET}
{MAGENTA}║{RESET}    {GREEN}Optimized for Scientific & HPC Workloads{RESET}    {MAGENTA}║{RESET}
{MAGENTA}║{RESET}                                                                        {MAGENTA}║{RESET}
{MAGENTA}╚════════════════════════════════════════════════════════════════════════╝{RESET}

{CYAN}Type 'help' for available commands{RESET}
{CYAN}Type 'tutorial' for getting started guide{RESET}
{CYAN}Type 'exit' or press Ctrl+D to quit{RESET}

"""

    print(banner)


def print_banner_alt():
    """Alternate banner design for HPCshell"""
    # ANSI color codes
    MAGENTA = "\033[35m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    RESET = "\033[0m"

    banner_alt = fr"""
{MAGENTA}************************************************************{RESET}
{MAGENTA}*{RESET}                                                          {MAGENTA}*{RESET}
{MAGENTA}*{RESET}  {YELLOW} █████╗ ███████╗ █████╗ ████████╗ ██████╗  ██████╗ {RESET}  {MAGENTA}*{RESET}
{MAGENTA}*{RESET}  {YELLOW}██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗{RESET}  {MAGENTA}*{RESET}
{MAGENTA}*{RESET}  {YELLOW}███████║█████╗  ███████║   ██║   ██║   ██║██║   ██║{RESET}  {MAGENTA}*{RESET}
{MAGENTA}*{RESET}  {YELLOW}██╔══██║██╔══╝  ██╔══██║   ██║   ██║   ██║██║   ██║{RESET}  {MAGENTA}*{RESET}
{MAGENTA}*{RESET}  {YELLOW}██║  ██║███████╗██║  ██║   ██║   ╚██████╔╝╚██████╔╝{RESET}  {MAGENTA}*{RESET}
{MAGENTA}*{RESET}  {YELLOW}╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ {RESET}  {MAGENTA}*{RESET}
{MAGENTA}*{RESET}                                                          {MAGENTA}*{RESET}
{MAGENTA}*{RESET}  {CYAN}ASTRA — ADVANCED HIGH-PERFORMANCE COMPUTING{RESET}  {MAGENTA}*{RESET}
{MAGENTA}*{RESET}  {GREEN}Optimized for Scientific & HPC workflows{RESET}  {MAGENTA}*{RESET}
{MAGENTA}*{RESET}                                                          {MAGENTA}*{RESET}
{MAGENTA}************************************************************{RESET}

{CYAN}Type 'help' for available commands{RESET}
{CYAN}Type 'tutorial' for getting started guide{RESET}
{CYAN}Type 'exit' or press Ctrl+D to quit{RESET}

"""

    print(banner_alt)

if __name__ == "__main__":
    main()