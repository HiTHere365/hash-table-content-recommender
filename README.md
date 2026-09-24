# Social Media Content Recommendation System

## Overview

A modular implementation of a content recommendation system using hash tables with double hashing collision resolution and Run-Length Encoding (RLE) compression for user interaction histories.

The point of the exercise is the data structures, not the model: every lookup path is a hand-built hash table with open addressing, interaction histories are stored compressed, and the whole thing runs on the Python standard library with no third-party packages. Run `python demo.py` to see it score and rank content for sample users.

## Installation & Running

### Requirements

- Python 3.7 or higher (the code uses nothing newer than f-strings and insertion-ordered dicts; CI runs 3.11 and 3.13)
- No external dependencies required (uses only the standard library)
- `pytest` is needed only to run the `tests/` suite

### To Run

```
python demo.py
```

### Tests

Two entry points cover the same modules:

```
pytest -q               # tests/test_recommender.py (requires pytest)
python test_system.py   # self-contained runner, no dependencies
```

`test_system.py` was kept so the project stays runnable without pytest; the pytest suite is the one CI reports on.

This will execute a complete demonstration showing:
1. System initialization
2. 50 simulated user interactions
3. Hash table performance metrics
4. Compression statistics
5. Personalized recommendations
6. User preference analysis
7. Time complexity analysis

## Project Structure

```
content-recommendation-engine/
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions: pytest, test_system.py, demo.py on 3.11 and 3.13
├── .gitignore
├── APPROACH.md               # Design rationale and trade-offs
├── LICENSE                   # AGPL v3
├── README.md                 # This file
├── compression.py            # RLE compression utilities and InteractionHistory
├── content_model.py          # Content data models and in-memory database
├── demo.py                   # Demonstration script (RUN THIS)
├── hash_table.py             # Core hash table with double hashing
├── recommendation.py         # Main recommendation system logic
├── requirements.txt          # Stdlib only at runtime; pytest for tests
├── test_system.py            # Self-contained test runner (no pytest needed)
└── tests/
    └── test_recommender.py   # pytest suite
```


## File Descriptions

### `hash_table.py`
Core hash table implementation featuring:
- Double hashing collision resolution
- Dynamic resizing (table doubles) when the load factor reaches 0.7
- Tombstone deletion; re-inserting a key that sits past a tombstone updates it in place instead of duplicating it
- O(1) average-case insert, search, and delete operations
- Statistics tracking: size, count, load factor, cumulative collision count

### `compression.py`
Run-Length Encoding utilities including:
- RLE compression/decompression functions
- `InteractionHistory` class for managing user interaction sequences
- Lazily computed compressed view with ratio analysis (the raw history is kept, capped at 100 entries)
- Trend detection (first third vs last third of the raw history)

### `content_model.py`
Data models and content management:
- `ContentItem` class representing music, videos, and informational content
- `ContentDatabase` for in-memory content storage
- Tag-based search functionality
- Sample data generation

### `recommendation.py`
Main recommendation system featuring:
- Separate hash tables for each content type
- Float-based preference weights (0.0-1.0)
- Integration with RLE compression for histories
- Top-N recommendations per category, sorted by weight; optional weighted shuffle (`diversify=True`, the default) for variety
- Cold-start recommendations (random sample by content type) for new users

### `demo.py`
Comprehensive demonstration script that shows:
- Realistic user interaction simulation
- Hash table performance statistics
- RLE compression analysis
- Personalized recommendations
- Time complexity explanations

## Key Features

### 1. Hash Table with Double Hashing
- Primary hash function: Polynomial rolling hash (multiplier: 31)
- Secondary hash function: Different multiplier (37) for step size
- Collision resolution: double hashing reduces clustering compared with linear probing
- Dynamic resizing: automatic doubling when load factor reaches 0.7; if a probe sequence cycles back to its start without finding a slot (possible once the doubled size is no longer prime), the table grows and retries

### 2. Float-Based Weights
- Preference weights range from 0.0 to 1.0
- More intuitive than integer ranges (0-255)
- Represents percentage of user interest
- Standard approach in ML/recommendation systems

### 3. RLE Compression
- Compresses runs of repeated interaction values
- Produces a compact representation of each history; in this implementation the raw history is retained (capped at 100 entries) so statistics and trends are computed from it
- Example: `[0.8, 0.8, 0.8, 0.9, 0.9]` → `[(0.8, 3), (0.9, 2)]`
- Tracks compression ratios for analysis

### 4. Modular Architecture
- Separation of concerns (hash table, compression, content, recommendations)
- Easy to test individual components
- Extensible for additional features
- Clear interfaces between modules

## Time Complexity Analysis

| Operation    | Average Case | Worst Case |
|--------------|--------------|------------|
| Insert       | O(1)         | O(n)       |
| Search       | O(1)         | O(n)       |
| Delete       | O(1)         | O(n)       |
| Resize       | O(n)         | O(n)       |
| Top-N        | O(m log m)   | O(m log m) |
| RLE Compress | O(n)         | O(n)       |
| RLE Decode   | O(n)         | O(n)       |

**Notes**: n is the table size for hash operations and the history length for RLE. Resize cost is amortized to O(1) per insert because the table doubles, so each entry is rehashed at most once per doubling. Top-N scans the whole table (m = table size) and sorts the live entries; it is not a heap-based partial sort.

## Example Output

When you run `demo.py`, you will see output like the following (values vary because interactions are randomly simulated):

```

======================================================================
SIMULATING USER INTERACTIONS
Recording interactions...
Processed 10/50 interactions...
Processed 20/50 interactions...
...

======================================================================
HASH TABLE PERFORMANCE ANALYSIS
Music Hash Table:
- Size: 106
- Stored preferences: 15
- Load factor: 0.142
- Collisions handled: 0
...
```

## Design Decisions

### Why Double Hashing?
- Superior to linear probing (avoids primary clustering)
- Better than quadratic probing at avoiding secondary clustering; a full probe cycle is guaranteed only when the step is coprime to the table size, so the insert path detects a cycle and resizes
- Provides pseudo-random probe sequences
- Maintains O(1) average case more reliably

### Why Float Weights (0.0-1.0)?
- More intuitive than 0-255 integer range
- Standard in machine learning systems
- Easier to normalize and compare
- Represents percentage naturally

### Why RLE Compression?
- User interactions often have repeated values
- Compact representation for histories with long runs
- Fast compression/decompression (O(n))
- Compression ratio is reported per history as a signal of how repetitive a user's engagement is

### Why Modular Structure?
- Follows Single Responsibility Principle
- Easier to test and maintain
- Demonstrates software engineering best practices
- Allows swapping implementations easily

## Real-World Applications

This system demonstrates techniques used by actual social media platforms:

- YouTube: Video recommendation system
- Spotify: Music preference tracking
- TikTok: Content personalization
- Instagram: Feed ranking algorithms

## Future Enhancements

Potential improvements for production systems:
- Collaborative filtering: Recommend based on similar users
- Content-based filtering: Use content features for recommendations
- A/B testing framework: Test recommendation strategies
- Distributed hash tables: Scale across multiple servers
- Machine learning integration: Deep learning for weight prediction
- Real-time updates: Stream processing for instant recommendations

## License

GNU Affero General Public License v3.0 (AGPL v3). See [LICENSE](LICENSE).

Copyright (C) 2026 William Rogers.

This software is free to use, modify, and distribute under the terms of the AGPL v3. Any service that deploys this software over a network must also release its source code under the same license.

For commercial licensing: volts-beret0t@icloud.com