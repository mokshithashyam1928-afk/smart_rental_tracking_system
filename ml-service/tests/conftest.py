import sys
from pathlib import Path

# Add ml-service root to sys.path so tests can import modules directly
ml_root = Path(__file__).resolve().parent.parent
if str(ml_root) not in sys.path:
    sys.path.insert(0, str(ml_root))
