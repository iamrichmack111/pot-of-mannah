from pot_of_mannah.data import MannahStore

def test_dataset_counts_are_realistic():
    stats = MannahStore().stats()
    assert stats["foods"] > 7000
    assert stats["exercises"] > 600

def test_food_search_returns_macros():
    rows = MannahStore().search_foods("chicken", limit=10)
    assert rows
    assert any(row.protein > 0 for row in rows)

def test_exercise_import_is_aligned():
    rows = MannahStore().search_exercises("Neck", limit=10)
    assert rows
    assert any(row.main_muscle == "Neck" for row in rows)
    assert all(row.difficulty is None or isinstance(row.difficulty, int) for row in rows)
