from tools.policies import search_policy


def test_search_returns_knee_section():
    hits = search_policy("knee MRI", "meniscal tear with mechanical symptoms", k=5)
    assert hits
    assert any(hit["section_id"] == "POL-KNEE-MRI-1.1" for hit in hits)
    assert all(hit["procedure"] == "knee MRI" for hit in hits)


def test_unknown_procedure_is_empty():
    assert search_policy("tattoo removal", "coverage criteria") == []


def test_blank_query_is_empty():
    assert search_policy("CPAP", "   ") == []
