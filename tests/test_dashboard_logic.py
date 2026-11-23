import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dashboard import RESCUE_RULES, get_rescue_query, clean_records, breed_figure, map_layers


def test_rescue_queries():
    assert get_rescue_query("reset") == {}
    assert get_rescue_query("water")["sex_upon_outcome"] == "Intact Female"
    assert get_rescue_query("mountain")["age_upon_outcome_in_weeks"] == {"$gte": 26, "$lte": 156}
    assert get_rescue_query("tracking")["age_upon_outcome_in_weeks"] == {"$gte": 20, "$lte": 300}
    for category, rule in RESCUE_RULES.items():
        assert all(breed in get_rescue_query(category)["breed"]["$regex"] for breed in rule["breeds"])


def test_clean_records():
    assert clean_records([{"_id": "123", "name": "Gunther"}]) == [{"name": "Gunther"}]
    assert clean_records([]) == []


def test_figure_and_map():
    rows = [
        {"name": "A", "breed": "German Shepherd", "location_lat": 30.7, "location_long": -97.5},
        {"name": "B", "breed": "German Shepherd", "location_lat": None, "location_long": -97.3},
    ]
    figure = breed_figure(rows)
    assert "German Shepherd" in list(figure.data[0].labels)
    assert len(map_layers(rows, [0])) == 2
    assert len(map_layers(rows, [1])) == 1
    assert len(map_layers([], [])) == 1
