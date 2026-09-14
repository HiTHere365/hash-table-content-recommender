# Design Approach

## The Problem

Social media platforms need to retrieve personalized content preferences for millions of users in real time. The core constraint is speed at lookup: a data structure that degrades as the user's interaction history grows will not scale. The design decision was which structure to build the preference layer around.

## Why Hash Tables

Arrays require O(n) linear scans to find a preference by content ID. Binary search trees give O(log n) but add pointer indirection that hurts cache locality. A hash table with a well-distributed hash function gives O(1) average-case insert, search, and delete with a flat memory layout that stays cache-friendly.

This is also how production recommendation serving layers are built. Redis, Memcached, and the in-process preference caches inside platforms like YouTube and Spotify are all hash tables at their core. The theoretical and practical cases point to the same answer.

The system uses separate hash tables per content category (music, music videos, informational). This keeps each table small, avoids cross-category interference during retrieval, and makes it straightforward to tune load factor and initial size per category based on observed interaction velocity.

## Collision Resolution: Double Hashing

Three standard open-addressing strategies exist:

| Strategy | Problem |
|---|---|
| Linear probing | Primary clustering: consecutive occupied slots form runs that degrade search |
| Quadratic probing | Secondary clustering; can fail to find empty slots if table size is not prime |
| Double hashing | Generates a unique step size per key, producing pseudo-random probe sequences |

Linear probing is the simplest but degrades badly once the table is more than half full. Quadratic probing reduces clustering but can cycle without finding an open slot in a non-prime-sized table. Double hashing computes a second hash of the key to determine the probe step, so two keys that collide at the same initial position will follow different probe sequences. Collisions still resolve in expected O(1) time under a uniform hash, and clustering is far less likely under high load.

The two hash functions here use polynomial rolling hashes with different multipliers (31 and 37). The secondary function is shifted by +1 to guarantee a non-zero step size, which is required for double hashing to cover the full table.

## Load Factor and Resizing

The load factor threshold is 0.7. Below that, probe chains stay short and average lookup stays close to O(1). Above 0.7 the expected probe length grows sharply.

When the threshold is crossed, the table doubles in size and all live entries are rehashed. Doubling keeps the amortized cost of insert at O(1): each element is rehashed at most once per doubling cycle, so the O(n) resize cost spreads across n insertions.

Initial table size for each category is 53 (prime). With a prime size every secondary step is coprime to the table, so a probe sequence visits every slot. Resizing doubles the size, so later sizes (106, 212, ...) are not prime and a step that shares a factor with the size covers only part of the table. The insert path handles this: if a probe sequence returns to its starting index without finding a slot, the table grows again and the insert is retried. Deletions leave tombstones; insert skips over them while probing so that an existing key further along the sequence is updated rather than duplicated, and reuses the first tombstone when the key is new.

## Preference Weights

Preference weights are stored as floats in [0.0, 1.0] rather than integers. This is the standard range in machine learning systems and makes weights directly comparable across content types without normalization. Watch time, repeat views, and explicit interactions all map naturally to fractions of maximum engagement.

## RLE Compression for Interaction Histories

User interaction sequences frequently contain runs of repeated values. Run-Length Encoding collapses `[0.8, 0.8, 0.8, 0.9, 0.9]` into `[(0.8, 3), (0.9, 2)]`, reducing memory proportionally to the run length. The compressed form is computed lazily and cached; the raw history is retained (capped at 100 entries) and is what the statistics and trend detection read. Trend detection compares the average weight in the first third of the history against the last third to produce an increasing, stable, or decreasing signal.

## Cold-Start Strategy

New users have no interaction history, so preference tables are empty. Rather than returning nothing, the system falls back to a random sample from the content database filtered by content type. This provides immediate utility and begins accumulating signal from the first interaction.

As users interact, individual preference tables populate with personalized weights and the system transitions from broad sampling toward tailored retrieval. The separation between the cold-start path (`get_cold_start_recommendations`) and the preference-based path (`get_recommendations`) keeps both logic flows clean and independently extensible.

## Real-World Performance Considerations

Several factors affect practical performance beyond asymptotic complexity:

- **Cache locality**: a hash table that fits in L2/L3 cache outperforms a pointer-linked structure even when both are O(1), because memory access latency dominates at small n
- **Hash function quality**: poor key distribution creates hot slots and pushes average-case lookup toward O(n) regardless of the collision resolution strategy
- **Network latency**: in distributed systems, preference data stored remotely adds round-trip cost that dwarfs algorithmic differences; production systems cache preference scores in-process to eliminate this
- **Resize timing**: in always-on systems, resize operations block concurrent access momentarily; adaptive initial sizing based on early interaction velocity reduces resize frequency for high-traffic users
