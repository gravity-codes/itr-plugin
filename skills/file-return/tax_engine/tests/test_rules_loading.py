import json
from pathlib import Path

RULES_PATH = Path(__file__).parent.parent / "rules" / "tax_year_2026_27.json"


def test_rules_file_loads_and_has_required_keys():
    rules = json.loads(RULES_PATH.read_text())
    assert "new_regime" in rules
    assert "old_regime" in rules
    assert "capital_gains" in rules
    assert rules["new_regime"]["rebate_threshold"] == 1200000
    assert rules["old_regime"]["rebate_threshold"] == 500000


def test_every_regime_section_cites_a_source():
    rules = json.loads(RULES_PATH.read_text())
    assert rules["new_regime"]["source_section"]
    assert rules["old_regime"]["source_section"]
    assert rules["capital_gains"]["source_section"]
