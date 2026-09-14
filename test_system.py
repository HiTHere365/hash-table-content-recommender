# test_system.py
# Unit tests for the recommendation system components

from hash_table import UserPreferenceHashTable
from compression import run_length_encode, run_length_decode, compression_ratio, InteractionHistory
from content_model import ContentItem, ContentType, ContentDatabase, create_sample_database
from recommendation import RecommendationSystem

def test_hash_table_basic_operations():
    print("Testing Hash Table Basic Operations…")
    hash_table = UserPreferenceHashTable(initial_size=7)
    hash_table.insert("content1", 0.8)
    hash_table.insert("content2", 0.6)
    hash_table.insert("content3", 0.9)
    assert hash_table.search("content1") == 0.8, "Search failed for content1"
    assert hash_table.search("content2") == 0.6, "Search failed for content2"
    assert hash_table.search("content3") == 0.9, "Search failed for content3"
    assert hash_table.search("nonexistent") is None, "Search should return None for missing key"
    hash_table.insert("content1", 0.95)
    assert hash_table.search("content1") == 0.95, "Update failed"
    result = hash_table.delete("content2")
    assert result is True, "Delete should return True for existing key"
    assert hash_table.search("content2") is None, "Deleted item should not be found"
    stats = hash_table.get_statistics()
    assert stats["count"] == 2, f"Count should be 2, got {stats['count']}"
    print("  ✓ All basic operations tests passed")

def test_hash_table_collision_handling():
    print("Testing Hash Table Collision Handling…")
    # Keys like item0, item1, ... hash to consecutive slots under the
    # polynomial hash and never collide, and the table resizes at 0.7 load.
    # To force collisions deterministically: disable resizing and pick keys
    # that share the same primary hash index.
    hash_table = UserPreferenceHashTable(initial_size=7)
    hash_table.load_factor_threshold = 2.0  # never resize during this test
    target = hash_table._hash1("anchor")
    keys = ["anchor"]
    i = 0
    while len(keys) < 4:
        candidate = f"probe{i}"
        if hash_table._hash1(candidate) == target:
            keys.append(candidate)
        i += 1
    for n, key in enumerate(keys):
        hash_table.insert(key, float(n) / 10)
    for n, key in enumerate(keys):
        value = hash_table.search(key)
        expected = float(n) / 10
        assert value == expected, f"Failed to retrieve {key}, expected {expected}, got {value}"
    assert hash_table.size == 7, "Table must not have resized"
    stats = hash_table.get_statistics()
    assert stats["collision_count"] == len(keys) - 1, (
        f"Expected {len(keys) - 1} collisions, got {stats['collision_count']}")
    print(f"  ✓ Handled {stats['collision_count']} collisions successfully")

def test_hash_table_dynamic_resizing():
    print("Testing Hash Table Dynamic Resizing…")
    hash_table = UserPreferenceHashTable(initial_size=7)
    initial_size = hash_table.size
    for i in range(10):
        hash_table.insert(f"resize_test_{i}", float(i) / 10)
    assert hash_table.size > initial_size, "Table should have resized"
    for i in range(10):
        value = hash_table.search(f"resize_test_{i}")
        expected = float(i) / 10
        assert value == expected, f"Item lost during resize: resize_test_{i}"
    print(f"  ✓ Resized from {initial_size} to {hash_table.size}")

def test_rle_compression():
    print("Testing RLE Compression…")
    weights = [0.8, 0.8, 0.8, 0.9, 0.9, 0.7, 0.7, 0.7, 0.7]
    encoded = run_length_encode(weights)
    decoded = run_length_decode(encoded)
    assert decoded == weights, "Decode should return original sequence"
    assert len(encoded) < len(weights), "Encoded should be smaller"
    ratio = compression_ratio(weights, encoded)
    assert ratio > 1.0, "Compression ratio should be > 1 for repeated values"
    unique_weights = [0.1, 0.2, 0.3, 0.4, 0.5]
    encoded_unique = run_length_encode(unique_weights)
    assert len(encoded_unique) == len(unique_weights), "No compression for unique values"
    print(f"  ✓ Achieved {ratio:.2f}x compression ratio")

def test_interaction_history():
    print("Testing Interaction History…")
    history = InteractionHistory("test_content")
    interactions = [0.5, 0.5, 0.6, 0.6, 0.6, 0.7, 0.8, 0.8, 0.9, 0.9, 0.9, 0.9]
    for weight in interactions:
        history.add_interaction(weight)
    stats = history.get_statistics()
    assert stats["count"] == len(interactions), "Should track all interactions"
    assert 0.0 <= stats["average"] <= 1.0, "Average should be in valid range"
    assert stats["trend"] in ["increasing", "decreasing", "stable"], "Should have valid trend"
    compressed = history.get_compressed()
    assert len(compressed) < len(interactions), "Compressed should be smaller"
    print(f"  ✓ Tracked {stats['count']} interactions with {stats['trend']} trend")

def test_content_database():
    print("Testing Content Database…")
    db = create_sample_database()
    music = db.get_by_type(ContentType.MUSIC)
    videos = db.get_by_type(ContentType.MUSIC_VIDEO)
    info = db.get_by_type(ContentType.INFORMATIONAL)
    assert len(music) > 0, "Should have music content"
    assert len(videos) > 0, "Should have video content"
    assert len(info) > 0, "Should have informational content"
    first_music = music[0]
    retrieved = db.get_by_id(first_music.content_id)
    assert retrieved == first_music, "Should retrieve same content by ID"
    jazz_content = db.search_by_tags(["jazz"])
    assert len(jazz_content) > 0, "Should find jazz content"
    print(f"  ✓ Database contains {len(db)} items across {len(ContentType)} categories")

def test_recommendation_system():
    print("Testing Recommendation System…")
    db = create_sample_database()
    rec_system = RecommendationSystem(db, user_id="test_user")
    music_items = db.get_by_type(ContentType.MUSIC)
    for item in music_items[:3]:
        rec_system.record_interaction(item.content_id, 0.8)
    weight = rec_system.get_preference_weight(music_items[0].content_id)
    assert weight == 0.8, f"Should retrieve correct weight, got {weight}"
    recommendations = rec_system.get_recommendations(top_n=3)
    assert ContentType.MUSIC.value in recommendations, "Should have music recommendations"
    assert len(recommendations[ContentType.MUSIC.value]) > 0, "Should return recommendations"
    stats = rec_system.get_system_statistics()
    assert stats["user_id"] == "test_user", "Should track user ID"
    assert stats["content_database_size"] > 0, "Should reference database"
    print(f"  ✓ Generated recommendations for {len(recommendations)} categories")

def test_float_weight_validation():
    print("Testing Weight Validation…")
    db = create_sample_database()
    rec_system = RecommendationSystem(db)
    music_items = db.get_by_type(ContentType.MUSIC)
    content_id = music_items[0].content_id
    rec_system.record_interaction(content_id, 0.0)
    rec_system.record_interaction(content_id, 0.5)
    rec_system.record_interaction(content_id, 1.0)
    try:
        rec_system.record_interaction(content_id, -0.1)
        assert False, "Should reject negative weights"
    except ValueError:
        pass
    try:
        rec_system.record_interaction(content_id, 1.1)
        assert False, "Should reject weights > 1.0"
    except ValueError:
        pass
    print("  ✓ Weight validation working correctly")

def test_cold_start_recommendations():
    print("Testing Cold Start Recommendations…")
    db = create_sample_database()
    rec_system = RecommendationSystem(db, user_id="new_user")
    cold_start = rec_system.get_cold_start_recommendations(ContentType.MUSIC, n=5)
    assert len(cold_start) > 0, "Should provide cold start recommendations"
    assert all(isinstance(item, ContentItem) for item in cold_start), "Should return ContentItem objects"
    assert all(item.content_type == ContentType.MUSIC for item in cold_start), "Should match requested type"
    print(f"  ✓ Generated {len(cold_start)} cold start recommendations")

def run_all_tests():
    print("\n" + "=" * 70)
    print("  RUNNING UNIT TESTS")
    print("=" * 70 + "\n")
    tests = [
        test_hash_table_basic_operations,
        test_hash_table_collision_handling,
        test_hash_table_dynamic_resizing,
        test_rle_compression,
        test_interaction_history,
        test_content_database,
        test_recommendation_system,
        test_float_weight_validation,
        test_cold_start_recommendations,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            failed += 1
        print()
    print("=" * 70)
    print(f"  TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")
    if failed == 0:
        print(" All tests passed! The system is working correctly.\n")
    else:
        print(f"  {failed} test(s) failed. Review the output above.\n")

if __name__ == "__main__":
    run_all_tests()
