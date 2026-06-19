import json
from pathlib import Path

RULES_PATH = Path(__file__).parent.parent / "rules" / "tax_year_2026_27.json"
RULES = json.loads(RULES_PATH.read_text())
