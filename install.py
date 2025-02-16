# install_packages.py
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None):
    """Run a command and check for errors"""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout


def install_packages():
    root_dir = Path(__file__).parent
    
    # Clean existing installations
    print("\nCleaning existing installations...")
    run_command([
        sys.executable, "-m", "pip", "uninstall", 
        "-y", "backend", "agent"
    ])
    
    # Install backend with all dependencies
    print("\nInstalling backend package...")
    backend_dir = root_dir / "backend"
    run_command([
        sys.executable, "-m", "pip", "install", "-e", ".",
        "--no-cache-dir"  # Force reinstall
    ], cwd=str(backend_dir))
    
    # Install agent with all dependencies
    print("\nInstalling agent package...")
    agent_dir = root_dir / "agent"
    run_command([
        sys.executable, "-m", "pip", "install", "-e", ".",
        "--no-cache-dir"  # Force reinstall
    ], cwd=str(agent_dir))
    
    # Verify installations
    print("\nInstalled packages:")
    run_command([sys.executable, "-m", "pip", "list"])


def verify_dependencies():
    """Verify all required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'python-dotenv',
        'httpx',
        'annotated-types',
        'anyio',
        'click',
        'h11',
        'idna',
        'sniffio',
        'starlette',
        'typing_extensions'
    ]
    
    print("\nVerifying dependencies...")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            return False
    return True


if __name__ == "__main__":
    install_packages()
    if verify_dependencies():
        print("\nAll dependencies successfully installed!")
    else:
        print("\nSome dependencies are missing. Please check the output above.")