# tests/test_recommender.py
# pytest suite for the hash table, RLE compression, and recommendation modules.
# Run from the repository root: pytest -q

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hash_table import UserPreferenceHashTable  # noqa: E402
from compression import (  # noqa: E402
    run_length_encode,
    run_length_decode,
    compression_ratio,
    InteractionHistory,
)
from content_model import ContentType, create_sample_database  # noqa: E402
from recommendation import RecommendationSystem  # noqa: E402


def colliding_keys(table, how_many):
    """Return `how_many` distinct keys that share one primary hash index."""
    target = table._hash1("anchor")
    keys = ["anchor"]
    i = 0
    while len(keys) < how_many:
        candidate = f"probe{i}"
        if table._hash1(candidate) == target:
            keys.append(candidate)
        i += 1
    return keys


def fixed_table(size=7):
    """Small table with resizing disabled so probe behaviour is deterministic."""
    table = UserPreferenceHashTable(initial_size=size)
    table.load_factor_threshold = 2.0
    return table


# Hash table


def test_insert_lookup_round_trip():
    table = UserPreferenceHashTable(initial_size=7)
    table.insert("a", 0.1)
    table.insert("b", 0.2)
    table.insert("c", 0.3)
    assert table.search("a") == 0.1
    assert table.search("b") == 0.2
    assert table.search("c") == 0.3
    assert table.search("missing") is None
    assert len(table) == 3
    assert "a" in table and "missing" not in table


def test_insert_existing_key_updates_in_place():
    table = UserPreferenceHashTable(initial_size=7)
    table.insert("a", 0.1)
    table.insert("a", 0.9)
    assert table.search("a") == 0.9
    assert len(table) == 1


def test_forced_collision_resolution():
    table = fixed_table()
    keys = colliding_keys(table, 4)
    for n, key in enumerate(keys):
        table.insert(key, n / 10)
    assert table.size == 7
    assert table.get_statistics()["collision_count"] == 3
    for n, key in enumerate(keys):
        assert table.search(key) == n / 10


def test_key_inserted_after_collision_is_retrievable_and_updatable():
    table = fixed_table()
    first, second = colliding_keys(table, 2)
    table.insert(first, 0.5)
    table.insert(second, 0.6)
    assert table.search(second) == 0.6
    table.insert(second, 0.7)
    assert table.search(second) == 0.7
    assert len(table) == 2


def test_delete_then_lookup_misses():
    table = UserPreferenceHashTable(initial_size=7)
    table.insert("a", 0.1)
    table.insert("b", 0.2)
    assert table.delete("a") is True
    assert table.search("a") is None
    assert table.delete("a") is False
    assert table.search("b") == 0.2
    assert len(table) == 1


def test_delete_in_probe_chain_keeps_later_keys_reachable():
    table = fixed_table()
    first, second, third = colliding_keys(table, 3)
    for n, key in enumerate((first, second, third)):
        table.insert(key, n / 10)
    assert table.delete(first) is True
    assert table.search(second) == 0.1
    assert table.search(third) == 0.2


def test_reinsert_past_tombstone_does_not_duplicate():
    table = fixed_table()
    first, second = colliding_keys(table, 2)
    table.insert(first, 0.1)
    table.insert(second, 0.2)
    table.delete(first)
    table.insert(second, 0.3)
    assert len(table) == 1
    assert table.get_all_items() == [(second, 0.3)]
    table.insert(first, 0.4)
    assert len(table) == 2
    assert sorted(table.get_all_items()) == sorted([(first, 0.4), (second, 0.3)])


def test_resize_preserves_entries_and_counts_collisions_cumulatively():
    table = UserPreferenceHashTable(initial_size=7)
    for i in range(20):
        table.insert(f"resize_{i}", i / 100)
    assert table.size > 7
    for i in range(20):
        assert table.search(f"resize_{i}") == i / 100
    assert len(table) == 20
    # Force collisions on a fixed table and confirm a resize does not reset
    # the counter.
    small = fixed_table()
    keys = colliding_keys(small, 3)
    for key in keys:
        small.insert(key, 0.5)
    before = small.get_statistics()["collision_count"]
    assert before == 2
    small._resize()
    assert small.get_statistics()["collision_count"] >= before
    for key in keys:
        assert small.search(key) == 0.5


def test_get_top_n_sorted_by_score_descending():
    table = UserPreferenceHashTable(initial_size=53)
    scores = {"a": 0.3, "b": 0.9, "c": 0.1, "d": 0.7, "e": 0.5}
    for key, score in scores.items():
        table.insert(key, score)
    top = table.get_top_n(3)
    assert [k for k, _ in top] == ["b", "d", "e"]
    assert [s for _, s in top] == sorted((s for _, s in top), reverse=True)
    assert len(table.get_top_n(100)) == 5


# RLE compression


@pytest.mark.parametrize(
    "history",
    [
        [],
        [0.5],
        [0.8, 0.8, 0.8, 0.9, 0.9, 0.7, 0.7, 0.7, 0.7],
        [0.1, 0.2, 0.3, 0.4, 0.5],
        [1.0, 1.0, 1.0, 1.0],
        [0.0, 1.0, 0.0, 1.0],
    ],
)
def test_rle_round_trip(history):
    encoded = run_length_encode(history)
    assert run_length_decode(encoded) == history
    assert len(encoded) <= len(history)


def test_rle_empty_and_single():
    assert run_length_encode([]) == []
    assert run_length_decode([]) == []
    assert run_length_encode([0.5]) == [(0.5, 1)]
    assert compression_ratio([], []) == 0.0
    assert compression_ratio([0.5], [(0.5, 1)]) == 1.0


def test_rle_runs_and_ratio():
    history = [0.8, 0.8, 0.8, 0.9, 0.9, 0.7, 0.7, 0.7, 0.7]
    encoded = run_length_encode(history)
    assert encoded == [(0.8, 3), (0.9, 2), (0.7, 4)]
    assert compression_ratio(history, encoded) == 3.0


def test_interaction_history_statistics():
    history = InteractionHistory("x", max_history=5)
    for w in [0.1, 0.1, 0.2, 0.9, 0.9, 0.9]:
        history.add_interaction(w)
    stats = history.get_statistics()
    assert stats["count"] == 5  # oldest entry dropped at max_history
    assert stats["min"] == 0.1 and stats["max"] == 0.9
    assert stats["trend"] == "increasing"
    assert run_length_decode(history.get_compressed()) == [0.1, 0.2, 0.9, 0.9, 0.9]


# Recommendation system


def test_record_and_read_back_weight():
    db = create_sample_database()
    rec = RecommendationSystem(db, user_id="u")
    rec.record_interaction("m1", 0.8)
    assert rec.get_preference_weight("m1") == 0.8
    assert rec.get_preference_weight("m2") is None
    assert rec.get_preference_weight("does_not_exist") is None


def test_weight_validation():
    rec = RecommendationSystem(create_sample_database())
    with pytest.raises(ValueError):
        rec.record_interaction("m1", -0.1)
    with pytest.raises(ValueError):
        rec.record_interaction("m1", 1.1)
    with pytest.raises(ValueError):
        rec.record_interaction("nope", 0.5)


def test_top_n_recommendations_sorted_by_score():
    db = create_sample_database()
    rec = RecommendationSystem(db, user_id="u")
    weights = {"m1": 0.2, "m2": 0.9, "m3": 0.5, "m4": 0.7, "m5": 0.1}
    for cid, w in weights.items():
        rec.record_interaction(cid, w)
    recs = rec.get_recommendations(top_n=3, diversify=False)
    music = recs[ContentType.MUSIC.value]
    assert [c.content_id for c, _ in music] == ["m2", "m4", "m3"]
    assert [w for _, w in music] == sorted((w for _, w in music), reverse=True)
    # With diversify=True the same top-N set is returned, order may vary.
    shuffled = rec.get_recommendations(top_n=3, diversify=True)
    assert {c.content_id for c, _ in shuffled[ContentType.MUSIC.value]} == {"m2", "m4", "m3"}


def test_cold_start_returns_requested_type():
    rec = RecommendationSystem(create_sample_database(), user_id="new")
    items = rec.get_cold_start_recommendations(ContentType.MUSIC_VIDEO, n=3)
    assert len(items) == 3
    assert all(i.content_type == ContentType.MUSIC_VIDEO for i in items)
    everything = rec.get_cold_start_recommendations(ContentType.MUSIC_VIDEO, n=50)
    assert len(everything) == 5
