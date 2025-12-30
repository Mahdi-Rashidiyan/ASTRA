#!/bin/bash

# HPCShell Setup Script
# This script creates the project structure and sets up the environment

echo "╔══════════════════════════════════════════════════════════╗"
echo "║           HPCShell Setup Script                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Create project directories
echo "[1/5] Creating project structure..."

mkdir -p hpcshell/{core,scheduler,monitor,benchmark,parallel,optimization,distributed,visualization,integration,utils}

echo "✓ Directory structure created"

# Create __init__.py files for Python packages
echo "[2/5] Creating Python packages..."

touch hpcshell/__init__.py
touch hpcshell/core/__init__.py
touch hpcshell/scheduler/__init__.py
touch hpcshell/monitor/__init__.py
touch hpcshell/benchmark/__init__.py
touch hpcshell/parallel/__init__.py
touch hpcshell/optimization/__init__.py
touch hpcshell/distributed/__init__.py
touch hpcshell/visualization/__init__.py
touch hpcshell/integration/__init__.py
touch hpcshell/utils/__init__.py

echo "✓ Python packages initialized"

# Create requirements.txt
echo "[3/5] Creating requirements.txt..."

cat > requirements.txt << EOF
# Core dependencies
psutil>=5.9.0

# Optional dependencies for advanced features
# numpy>=1.21.0        # For advanced benchmarking
# matplotlib>=3.5.0    # For visualization
# plotly>=5.0.0        # For interactive graphs
EOF

echo "✓ requirements.txt created"

# Create .gitignore
echo "[4/5] Creating .gitignore..."

cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# HPCShell specific
.hpcshell_history
.hpcshell.log
.hpcshellrc
*.tmp
EOF

echo "✓ .gitignore created"

# Create main executable
echo "[5/5] Creating main executable..."

cat > hpcshell.py << 'EOF'
#!/usr/bin/env python3
"""
HPCShell - High-Performance Computing Shell
Main entry point
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from hpcshell.core.shell import HPCShell
from hpcshell.utils.config import Config
from hpcshell.utils.logger import setup_logger

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
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ██╗  ██╗██████╗  ██████╗███████╗██╗  ██╗███████╗██╗    ║
    ║   ██║  ██║██╔══██╗██╔════╝██╔════╝██║  ██║██╔════╝██║    ║
    ║   ███████║██████╔╝██║     ███████╗███████║█████╗  ██║    ║
    ║   ██╔══██║██╔═══╝ ██║     ╚════██║██╔══██║██╔══╝  ██║    ║
    ║   ██║  ██║██║     ╚██████╗███████║██║  ██║███████╗███████╗║
    ║   ╚═╝  ╚═╝╚═╝      ╚═════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝║
    ║                                                           ║
    ║         High-Performance Computing Shell v1.0            ║
    ║              Optimized for Scientific Computing          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Type 'help' for available commands
    Type 'tutorial' for getting started guide
    Type 'exit' or press Ctrl+D to quit
    
    """
    print(banner)

if __name__ == "__main__":
    main()
EOF

chmod +x hpcshell.py

echo "✓ Main executable created"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Setup Complete!                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Install dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "2. Copy the Python files you received into the appropriate directories:"
echo "   - core/*.py files → hpcshell/core/"
echo "   - scheduler/*.py files → hpcshell/scheduler/"
echo "   - monitor/*.py files → hpcshell/monitor/"
echo "   - benchmark/*.py files → hpcshell/benchmark/"
echo "   - utils/*.py files → hpcshell/utils/"
echo ""
echo "3. Run HPCShell:"
echo "   ./hpcshell.py"
echo ""
echo "Directory structure:"
echo ""
echo "hpcshell/"
echo "├── hpcshell.py              # Main executable"
echo "├── requirements.txt          # Dependencies"
echo "├── README.md                 # Documentation"
echo "└── hpcshell/                 # Package root"
echo "    ├── core/                 # Shell core"
echo "    ├── scheduler/            # Job scheduling"
echo "    ├── monitor/              # Resource monitoring"
echo "    ├── benchmark/            # Benchmarking tools"
echo "    ├── parallel/             # Parallel execution"
echo "    ├── optimization/         # AI optimization"
echo "    ├── distributed/          # Distributed computing"
echo "    ├── visualization/        # Data visualization"
echo "    ├── integration/          # External integrations"
echo "    └── utils/                # Utilities"
echo ""
echo "Happy Computing! 🚀"