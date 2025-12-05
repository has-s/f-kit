import pytest
import sys
from pathlib import Path

# Add parent folder to sys.path (if access to speech_censor is needed)
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    # Run all tests in the 'tests/' folder
    # -v: verbose output
    # --tb=short: short traceback for failures
    # -s: allow print() output in the console
    exit_code = pytest.main([
        str(Path(__file__).parent),  # folder containing tests
        "-v",
        "--tb=short",
        "-s"
    ])
    # Exit with pytest return code
    exit(exit_code)