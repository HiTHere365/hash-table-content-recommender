# hash_table.py
# Core hash table implementation with double hashing collision resolution

from typing import Optional, List, Tuple, Any

class UserPreferenceHashTable:
    """
    Hash table implementation for storing user preferences with double hashing
    for collision resolution. Supports dynamic resizing to maintain performance.

    Time Complexity:
        - Average case: O(1) for insert, search, delete
        - Worst case: O(n) when table is nearly full
        - Resize operation: O(n) but amortized to O(1)
    """

    def __init__(self, initial_size: int = 101):
        """Initialize hash table with given size."""
        self.size = initial_size
        self.count = 0
        self.table = [None] * self.size
        self.load_factor_threshold = 0.7
        self.collision_count = 0  # Track collisions for analysis

    def _hash1(self, key: str) -> int:
        """Primary hash function using polynomial rolling hash."""
        hash_value = 0
        for char in key:
            hash_value = (hash_value * 31 + ord(char)) % self.size
        return hash_value

    def _hash2(self, key: str) -> int:
        """Secondary hash function for double hashing with different prime multiplier."""
        hash_value = 0
        for char in key:
            hash_value = (hash_value * 37 + ord(char)) % (self.size - 1)
        return hash_value + 1  # Ensure non-zero step

    def _resize(self):
        """Resize hash table when load factor exceeds threshold."""
        old_table = self.table

        self.size = self.size * 2
        self.table = [None] * self.size
        self.count = 0
        self.collision_count = 0

        for item in old_table:
            if item is not None and item != "DELETED":
                self.insert(item[0], item[1])

    def insert(self, key: str, value: float):
        if self.count / self.size >= self.load_factor_threshold:
            self._resize()

        index = self._hash1(key)
        step = self._hash2(key)
        original_index = index
        probes = 0

        while self.table[index] is not None and self.table[index] != "DELETED":
            if self.table[index][0] == key:
                self.table[index] = (key, value)
                return
            if probes == 0:
                self.collision_count += 1
            index = (index + step) % self.size
            probes += 1
            if index == original_index:
                self._resize()
                return self.insert(key, value)

        self.table[index] = (key, value)
        self.count += 1

    def search(self, key: str) -> Optional[float]:
        index = self._hash1(key)
        step = self._hash2(key)
        original_index = index

        while self.table[index] is not None:
            if self.table[index] != "DELETED" and self.table[index][0] == key:
                return self.table[index][1]
            index = (index + step) % self.size
            if index == original_index:
                break
        return None

    def delete(self, key: str) -> bool:
        index = self._hash1(key)
        step = self._hash2(key)
        original_index = index

        while self.table[index] is not None:
            if self.table[index] != "DELETED" and self.table[index][0] == key:
                self.table[index] = "DELETED"
                self.count -= 1
                return True
            index = (index + step) % self.size
            if index == original_index:
                break
        return False

    def get_top_n(self, n: int) -> List[Tuple[str, float]]:
        items = [item for item in self.table if item is not None and item != "DELETED"]
        items.sort(key=lambda x: x[1], reverse=True)
        return items[:n]

    def get_all_items(self) -> List[Tuple[str, float]]:
        return [item for item in self.table if item is not None and item != "DELETED"]

    def get_statistics(self) -> dict:
        return {
            "size": self.size,
            "count": self.count,
            "load_factor": self.count / self.size if self.size > 0 else 0,
            "collision_count": self.collision_count,
            "empty_slots": self.size - self.count
        }

    def __len__(self) -> int:
        return self.count

    def __contains__(self, key: str) -> bool:
        return self.search(key) is not None

    def __repr__(self) -> str:
        return f"UserPreferenceHashTable(size={self.size}, count={self.count}, load_factor={self.count/self.size:.2f})"
