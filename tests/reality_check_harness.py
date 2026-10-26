"""Legacy entrypoint that executes the genuine local regression suite."""
import subprocess
import sys
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parents[1]
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "*.py", "-v"]
    return subprocess.run(command, cwd=repo, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
