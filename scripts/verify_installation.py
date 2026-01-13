#!/usr/bin/env python3
"""
Focus Mate - Installation Verification Script

Checks that all components are properly installed and configured.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check_file_exists(path: Path, description: str) -> bool:
    """Check if a file exists."""
    if path.exists():
        print(f"{GREEN}✓{RESET} {description}: {path}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {path} (NOT FOUND)")
        return False


def check_directory_exists(path: Path, description: str) -> bool:
    """Check if a directory exists."""
    if path.is_dir():
        file_count = len(list(path.glob("*")))
        print(f"{GREEN}✓{RESET} {description}: {path} ({file_count} files)")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {path} (NOT FOUND)")
        return False


def check_python_packages() -> bool:
    """Check if required Python packages are installed."""
    required = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "tensorflow",
        "opencv-python",
        "numpy",
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print(f"{GREEN}✓{RESET} Python package: {package}")
        except ImportError:
            print(f"{RED}✗{RESET} Python package: {package} (NOT INSTALLED)")
            missing.append(package)
    
    return len(missing) == 0


def check_node_modules() -> bool:
    """Check if Node modules are installed."""
    frontend_modules = Path("frontend/node_modules")
    if frontend_modules.exists():
        print(f"{GREEN}✓{RESET} Frontend node_modules installed")
        return True
    else:
        print(f"{RED}✗{RESET} Frontend node_modules not installed")
        print(f"  {YELLOW}→{RESET} Run: cd frontend && npm install")
        return False


def main():
    """Run all verification checks."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Focus Mate - Installation Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    checks: List[Tuple[str, bool]] = []
    
    # Check project structure
    print(f"\n{BLUE}[1/7] Checking Project Structure{RESET}")
    checks.append(("Backend directory", check_directory_exists(Path("backend"), "Backend")))
    checks.append(("Frontend directory", check_directory_exists(Path("frontend"), "Frontend")))
    checks.append(("Extension directory", check_directory_exists(Path("extension"), "Extension")))
    checks.append(("ML directory", check_directory_exists(Path("ml"), "ML")))
    checks.append(("Docs directory", check_directory_exists(Path("docs"), "Docs")))
    
    # Check backend files
    print(f"\n{BLUE}[2/7] Checking Backend Files{RESET}")
    checks.append(("Backend main", check_file_exists(Path("backend/app/main.py"), "Main app")))
    checks.append(("Backend config", check_file_exists(Path("backend/app/config.py"), "Config")))
    checks.append(("Requirements", check_file_exists(Path("backend/requirements.txt"), "Requirements")))
    
    # Check frontend files
    print(f"\n{BLUE}[3/7] Checking Frontend Files{RESET}")
    checks.append(("Frontend App", check_file_exists(Path("frontend/src/App.tsx"), "App component")))
    checks.append(("Package.json", check_file_exists(Path("frontend/package.json"), "Package config")))
    checks.append(("Index.html", check_file_exists(Path("frontend/index.html"), "Index HTML")))
    
    # Check extension files
    print(f"\n{BLUE}[4/7] Checking Extension Files{RESET}")
    checks.append(("Manifest", check_file_exists(Path("extension/manifest.json"), "Manifest")))
    checks.append(("Background", check_file_exists(Path("extension/background.js"), "Background worker")))
    checks.append(("Content", check_file_exists(Path("extension/content.js"), "Content script")))
    checks.append(("Popup", check_file_exists(Path("extension/popup.html"), "Popup UI")))
    
    # Check ML files
    print(f"\n{BLUE}[5/7] Checking ML Files{RESET}")
    checks.append(("Model", check_file_exists(Path("ml/model.py"), "Model definition")))
    checks.append(("Training", check_file_exists(Path("ml/train.py"), "Training script")))
    checks.append(("Export", check_file_exists(Path("ml/export_model.py"), "Export script")))
    checks.append(("Data ingest", check_file_exists(Path("ml/data_ingest.py"), "Data ingestion")))
    checks.append(("Labels", check_file_exists(Path("ml/labels.py"), "Label definitions")))
    
    # Check documentation
    print(f"\n{BLUE}[6/7] Checking Documentation{RESET}")
    checks.append(("README", check_file_exists(Path("README.md"), "Main README")))
    checks.append(("Features", check_file_exists(Path("docs/FEATURES.md"), "Features doc")))
    checks.append(("Quick Start", check_file_exists(Path("docs/QUICKSTART.md"), "Quick start")))
    checks.append(("ML README", check_file_exists(Path("ml/README.md"), "ML README")))
    checks.append(("Extension README", check_file_exists(Path("extension/README.md"), "Extension README")))
    checks.append(("Changelog", check_file_exists(Path("CHANGELOG.md"), "Changelog")))
    
    # Check dependencies
    print(f"\n{BLUE}[7/7] Checking Dependencies{RESET}")
    checks.append(("Python packages", check_python_packages()))
    checks.append(("Node modules", check_node_modules()))
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    percentage = (passed / total) * 100
    
    if percentage == 100:
        print(f"{GREEN}✓ All checks passed! ({passed}/{total}){RESET}")
        print(f"\n{GREEN}Focus Mate is ready to use!{RESET}")
        print(f"\nNext steps:")
        print(f"  1. Start backend: cd backend && uvicorn app.main:app --reload")
        print(f"  2. Start frontend: cd frontend && npm run dev")
        print(f"  3. Load extension in Chrome from extension/ folder")
        print(f"  4. See docs/QUICKSTART.md for detailed instructions")
        return 0
    elif percentage >= 80:
        print(f"{YELLOW}⚠ Most checks passed ({passed}/{total} - {percentage:.0f}%){RESET}")
        print(f"\n{YELLOW}Some components may be missing. Review errors above.{RESET}")
        return 1
    else:
        print(f"{RED}✗ Many checks failed ({passed}/{total} - {percentage:.0f}%){RESET}")
        print(f"\n{RED}Installation appears incomplete. Please review errors above.{RESET}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Verification cancelled by user{RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED}Error during verification: {e}{RESET}")
        sys.exit(1)
