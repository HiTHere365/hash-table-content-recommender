# demo.py
# Main demonstration script for the Social Media Content Recommendation System

import random
from content_model import create_sample_database, ContentType
from recommendation import RecommendationSystem
from compression import run_length_encode, compression_ratio

def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def simulate_realistic_interactions(rec_system: RecommendationSystem, num_interactions: int = 50):
    print_section("SIMULATING USER INTERACTIONS")
    all_content = rec_system.content_db.get_all()
    preferred_genres = ["pop", "jazz", "rock"]
    interaction_count = 0
    print("\nRecording interactions...")
    for i in range(num_interactions):
        if random.random() < 0.7:
            preferred_content = [c for c in all_content if any(genre in c.tags for genre in preferred_genres)]
            content = random.choice(preferred_content) if preferred_content else random.choice(all_content)
        else:
            content = random.choice(all_content)
        if any(genre in content.tags for genre in preferred_genres):
            weight = random.uniform(0.6, 1.0)
        else:
            weight = random.uniform(0.1, 0.5)
        rec_system.record_interaction(content.content_id, weight)
        interaction_count += 1
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{num_interactions} interactions...")
    print(f"\n Completed {interaction_count} user interactions")

def demonstrate_hash_table_performance(rec_system: RecommendationSystem):
    print_section("HASH TABLE PERFORMANCE ANALYSIS")
    stats = rec_system.get_system_statistics()
    print("\n Hash Table Statistics:\n")
    for content_type, table_stats in stats["hash_tables"].items():
        print(f"  {content_type.replace('_', ' ').title()} Hash Table:")
        print(f"    • Size: {table_stats['size']}")
        print(f"    • Stored preferences: {table_stats['count']}")
        print(f"    • Load factor: {table_stats['load_factor']:.3f}")
        print(f"    • Collisions handled: {table_stats['collision_count']}")
        print(f"    • Empty slots: {table_stats['empty_slots']}")
        print()

def demonstrate_compression(rec_system: RecommendationSystem):
    print_section("RLE COMPRESSION ANALYSIS")
    compression_stats = rec_system.get_system_statistics()["compression_stats"]
    print("\n Compression Statistics:\n")
    print(f"  • Total interaction histories: {compression_stats['total_histories']}")
    print(f"  • Total interactions recorded: {compression_stats['total_interactions']}")
    print(f"  • Average compression ratio: {compression_stats['avg_compression_ratio']:.2f}x")
    if rec_system.interaction_histories:
        print("\n  Example - Detailed History for One Item:")
        content_id = list(rec_system.interaction_histories.keys())[0]
        history = rec_system.interaction_histories[content_id]
        stats = history.get_statistics()
        content = rec_system.content_db.get_by_id(content_id)
        print(f"\n    Content: {content.title if content else content_id}")
        print(f"    • Interactions: {stats['count']}")
        print(f"    • Average weight: {stats['average']:.3f}")
        print(f"    • Trend: {stats['trend']}")
        print(f"    • Compression: {stats['count']} → {stats['compressed_size']} entries")
        print(f"    • Compression ratio: {stats['compression_ratio']:.2f}x")
        compressed = history.get_compressed()
        print(f"    • Compressed representation: {compressed[:5]}..." if len(compressed) > 5 else f"    • Compressed representation: {compressed}")

def display_recommendations(rec_system: RecommendationSystem, top_n: int = 5):
    print_section("PERSONALIZED RECOMMENDATIONS")
    recommendations = rec_system.get_recommendations(top_n=top_n)
    print("\n Top Recommendations for User:\n")
    for content_type, items in recommendations.items():
        print(f"  {content_type.replace('_', ' ').title()}:")
        if items:
            for i, (content, weight) in enumerate(items, 1):
                print(f"    {i}. {content.get_display_string()}")
                print(f"       └─ Preference weight: {weight:.3f}")
                history = rec_system.get_interaction_history(content.content_id)
                if history:
                    stats = history.get_statistics()
                    if stats['count'] >= 3:
                        print(f"       └─ Interest trend: {stats['trend']}")
        else:
            print("    No interactions yet - showing cold start recommendations")
            cold_start = rec_system.get_cold_start_recommendations(
                ContentType.from_string(content_type), n=3
            )
            for i, content in enumerate(cold_start, 1):
                print(f"    {i}. {content.get_display_string()} (suggested)")
        print()

def analyze_user_preferences(rec_system: RecommendationSystem):
    print_section("USER PREFERENCE ANALYSIS")
    analysis = rec_system.analyze_user_preferences()
    print("\n Overall User Profile:\n")
    print(f"  • Total tracked preferences: {analysis['total_interactions']}")
    print("\n  By Content Category:")
    for category, stats in analysis["by_category"].items():
        print(f"    {category.replace('_', ' ').title()}:")
        print(f"      - Items interacted with: {stats['count']}")
        print(f"      - Average preference weight: {stats['avg_weight']:.3f}")
        print(f"      - Hash collisions: {stats['collision_count']}")
    if analysis["interaction_trends"]:
        print("\n  Content with Notable Trends:")
        trend_count = 0
        for content_id, trend_info in analysis["interaction_trends"].items():
            if trend_count >= 5:
                break
            content = rec_system.content_db.get_by_id(content_id)
            if content:
                print(f"    • {content.title}: {trend_info['trend']} (avg: {trend_info['average']:.3f})")
                trend_count += 1

def demonstrate_time_complexity():
    print_section("TIME COMPLEXITY ANALYSIS")
    print("""
Hash Table Operations - Time Complexity:

┌─────────────────────┬──────────────┬──────────────┐
│ Operation           │ Average Case │ Worst Case   │
├─────────────────────┼──────────────┼──────────────┤
│ Insert              │ O(1)         │ O(n)         │
│ Search              │ O(1)         │ O(n)         │
│ Delete              │ O(1)         │ O(n)         │
│ Resize (rehash)     │ O(n)         │ O(n)         │
└─────────────────────┴──────────────┴──────────────┘

Key Performance Factors:

 Double Hashing: Minimizes clustering for O(1) average case
 Load Factor < 0.7: Maintains low collision probability
 Dynamic Resizing: Amortizes O(n) rehash across operations
 RLE Compression: Compact view and repetition signal for histories

Real-World Considerations:

• Network Latency: Affects distributed hash table access
• Cache Locality: Important for large tables exceeding CPU cache
• Hash Function Quality: Critical for uniform key distribution
• Concurrent Access: May require locking mechanisms in production
""")

def main():
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  SOCIAL MEDIA CONTENT RECOMMENDATION SYSTEM".center(68) + "█")
    print("█" + "  Using Hash Tables with Double Hashing & RLE Compression".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    print("\n Initializing recommendation system...")
    db = create_sample_database()
    rec_system = RecommendationSystem(db, user_id="demo_user_001")
    print(f" System ready: {rec_system}")
    print(f" Content database: {db}")
    simulate_realistic_interactions(rec_system, num_interactions=50)
    demonstrate_hash_table_performance(rec_system)
    demonstrate_compression(rec_system)
    display_recommendations(rec_system, top_n=5)
    analyze_user_preferences(rec_system)
    demonstrate_time_complexity()
    print_section("DEMONSTRATION COMPLETE")
    print("""
 Successfully demonstrated:
• Hash table implementation with double hashing
• Dynamic resizing with load factor management
• RLE compression for interaction histories
• Real-time personalized recommendations
• Performance analysis and statistics

 Key Achievements:
• O(1) average-case retrieval for recommendations
• Efficient collision resolution with minimal clustering
• Memory optimization through compression
• Scalable architecture for large-scale user data

 This implementation shows how hash tables provide the foundation
for real-time content recommendation systems used by social media
platforms to deliver personalized user experiences.
""")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
