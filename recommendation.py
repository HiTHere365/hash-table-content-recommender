# recommendation.py
# Core recommendation system using hash tables and interaction history

from typing import List, Dict, Tuple, Optional
import random

from hash_table import UserPreferenceHashTable
from content_model import ContentItem, ContentType, ContentDatabase
from compression import InteractionHistory

class RecommendationSystem:
    """
    Social media content recommendation system using hash tables.
    Manages user preferences across multiple content categories with RLE compression.
    """

    def __init__(self, content_db: ContentDatabase, user_id: str = "default_user"):
        self.user_id = user_id
        self.content_db = content_db
        self.music_preferences = UserPreferenceHashTable(initial_size=53)
        self.music_video_preferences = UserPreferenceHashTable(initial_size=53)
        self.informational_preferences = UserPreferenceHashTable(initial_size=53)
        self.interaction_histories: Dict[str, InteractionHistory] = {}

        self._type_to_table = {
            ContentType.MUSIC: self.music_preferences,
            ContentType.MUSIC_VIDEO: self.music_video_preferences,
            ContentType.INFORMATIONAL: self.informational_preferences
        }

    def record_interaction(self, content_id: str, weight: float, update_history: bool = True):
        if not 0.0 <= weight <= 1.0:
            raise ValueError(f"Weight must be between 0.0 and 1.0, got {weight}")

        content = self.content_db.get_by_id(content_id)
        if not content:
            raise ValueError(f"Content ID {content_id} not found in database")

        hash_table = self._type_to_table[content.content_type]
        hash_table.insert(content_id, weight)

        if update_history:
            if content_id not in self.interaction_histories:
                self.interaction_histories[content_id] = InteractionHistory(content_id)
            self.interaction_histories[content_id].add_interaction(weight)

    def get_preference_weight(self, content_id: str) -> Optional[float]:
        content = self.content_db.get_by_id(content_id)
        if not content:
            return None
        hash_table = self._type_to_table[content.content_type]
        return hash_table.search(content_id)

    def get_interaction_history(self, content_id: str) -> Optional[InteractionHistory]:
        return self.interaction_histories.get(content_id)

    def get_recommendations(self, top_n: int = 5, diversify: bool = True) -> Dict[str, List[Tuple[ContentItem, float]]]:
        recommendations = {}
        for content_type, hash_table in self._type_to_table.items():
            top_items = hash_table.get_top_n(top_n)
            content_recs = []
            for content_id, weight in top_items:
                content = self.content_db.get_by_id(content_id)
                if content:
                    content_recs.append((content, weight))
            if diversify and len(content_recs) > 1:
                content_recs = self._weighted_shuffle(content_recs)
            recommendations[content_type.value] = content_recs
        return recommendations

    def _weighted_shuffle(self, items: List[Tuple[ContentItem, float]]) -> List[Tuple[ContentItem, float]]:
        if not items:
            return items
        weighted_items = items.copy()
        result = []
        while weighted_items:
            total_weight = sum(weight for _, weight in weighted_items)
            if total_weight == 0:
                result.extend(weighted_items)
                break
            rand = random.uniform(0, total_weight)
            cumulative = 0
            for i, (content, weight) in enumerate(weighted_items):
                cumulative += weight
                if rand <= cumulative:
                    result.append((content, weight))
                    weighted_items.pop(i)
                    break
        return result

    def get_cold_start_recommendations(self, content_type: ContentType, n: int = 5) -> List[ContentItem]:
        all_content = self.content_db.get_by_type(content_type)
        if len(all_content) <= n:
            return all_content
        return random.sample(all_content, n)

    def analyze_user_preferences(self) -> Dict[str, any]:
        analysis = {
            "user_id": self.user_id,
            "total_interactions": sum(len(table) for table in self._type_to_table.values()),
            "by_category": {},
            "top_genres": [],
            "interaction_trends": {}
        }
        for content_type, hash_table in self._type_to_table.items():
            stats = hash_table.get_statistics()
            analysis["by_category"][content_type.value] = {
                "count": stats["count"],
                "avg_weight": sum(w for _, w in hash_table.get_all_items()) / stats["count"] if stats["count"] > 0 else 0,
                "collision_count": stats["collision_count"]
            }
        for content_id, history in self.interaction_histories.items():
            stats = history.get_statistics()
            if stats["count"] >= 3:
                analysis["interaction_trends"][content_id] = {
                    "trend": stats["trend"],
                    "average": stats["average"],
                    "compression_ratio": stats["compression_ratio"]
                }
        return analysis

    def get_system_statistics(self) -> Dict[str, any]:
        stats = {
            "user_id": self.user_id,
            "content_database_size": len(self.content_db),
            "hash_tables": {},
            "compression_stats": {
                "total_histories": len(self.interaction_histories),
                "total_interactions": 0,
                "avg_compression_ratio": 0.0
            }
        }
        for content_type, hash_table in self._type_to_table.items():
            stats["hash_tables"][content_type.value] = hash_table.get_statistics()
        if self.interaction_histories:
            total_interactions = 0
            total_compression = 0.0
            for history in self.interaction_histories.values():
                history_stats = history.get_statistics()
                total_interactions += history_stats["count"]
                total_compression += history_stats["compression_ratio"]
            stats["compression_stats"]["total_interactions"] = total_interactions
            stats["compression_stats"]["avg_compression_ratio"] = total_compression / len(self.interaction_histories)
        return stats

    def __repr__(self) -> str:
        total_prefs = sum(len(table) for table in self._type_to_table.values())
        return f"RecommendationSystem(user={self.user_id}, preferences={total_prefs}, histories={len(self.interaction_histories)})"
