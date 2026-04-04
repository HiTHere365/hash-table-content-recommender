# compression.py
# Run-Length Encoding (RLE) utilities for compressing user interaction sequences

from typing import List, Tuple

def run_length_encode(weights: List[float]) -> List[Tuple[float, int]]:
    if not weights:
        return []
    result = []
    prev = weights[0]
    count = 1
    for w in weights[1:]:
        if abs(w - prev) < 1e-9:
            count += 1
        else:
            result.append((prev, count))
            prev = w
            count = 1
    result.append((prev, count))
    return result

def run_length_decode(encoded: List[Tuple[float, int]]) -> List[float]:
    if not encoded:
        return []
    result = []
    for weight, count in encoded:
        result.extend([weight] * count)
    return result

def compression_ratio(original: List[float], encoded: List[Tuple[float, int]]) -> float:
    if not encoded:
        return 0.0
    original_size = len(original)
    compressed_size = len(encoded)
    return original_size / compressed_size if compressed_size > 0 else 0.0

def should_compress(weights: List[float], threshold: float = 2.0) -> bool:
    if len(weights) < 3:
        return False
    encoded = run_length_encode(weights)
    ratio = compression_ratio(weights, encoded)
    return ratio >= threshold

class InteractionHistory:
    def __init__(self, content_id: str, max_history: int = 100):
        self.content_id = content_id
        self.max_history = max_history
        self._raw_history = []
        self._compressed = None
        self._compression_enabled = True

    def add_interaction(self, weight: float):
        self._raw_history.append(weight)
        if len(self._raw_history) > self.max_history:
            self._raw_history.pop(0)
        self._compressed = None

    def get_compressed(self) -> List[Tuple[float, int]]:
        if self._compressed is None:
            self._compressed = run_length_encode(self._raw_history)
        return self._compressed

    def get_average_weight(self) -> float:
        if not self._raw_history:
            return 0.0
        return sum(self._raw_history) / len(self._raw_history)

    def get_latest_weight(self) -> float:
        return self._raw_history[-1] if self._raw_history else 0.0

    def get_trend(self) -> str:
        if len(self._raw_history) < 3:
            return "insufficient_data"
        first_third = self._raw_history[:len(self._raw_history)//3]
        last_third = self._raw_history[-(len(self._raw_history)//3):]
        if not first_third or not last_third:
            return "insufficient_data"
        avg_first = sum(first_third) / len(first_third)
        avg_last = sum(last_third) / len(last_third)
        if avg_last > avg_first * 1.1:
            return "increasing"
        elif avg_last < avg_first * 0.9:
            return "decreasing"
        else:
            return "stable"

    def get_statistics(self) -> dict:
        if not self._raw_history:
            return {
                "count": 0,
                "average": 0.0,
                "min": 0.0,
                "max": 0.0,
                "compression_ratio": 0.0,
                "trend": "no_data"
            }
        compressed = self.get_compressed()
        return {
            "count": len(self._raw_history),
            "average": self.get_average_weight(),
            "min": min(self._raw_history),
            "max": max(self._raw_history),
            "latest": self.get_latest_weight(),
            "compression_ratio": compression_ratio(self._raw_history, compressed),
            "compressed_size": len(compressed),
            "trend": self.get_trend()
        }

    def __repr__(self) -> str:
        stats = self.get_statistics()
        return f"InteractionHistory(content={self.content_id}, count={stats['count']}, avg={stats['average']:.3f})"
