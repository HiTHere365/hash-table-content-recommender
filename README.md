
# Social Media Content Recommendation System

## Overview

A modular implementation of a content recommendation system using hash tables with double hashing collision resolution and Run-Length Encoding (RLE) compression for user interaction histories.

## Project Structure

recommendation-system/
├── hash_table.py # Core hash table with double hashing
├── compression.py # RLE compression utilities
├── content_model.py # Content data models and database
├── recommendation.py # Main recommendation system logic
├── demo.py # Demonstration script (RUN THIS)
└── README.md # This file


## File Descriptions

### `hash_table.py`
Core hash table implementation featuring:
- Double hashing collision resolution
- Dynamic resizing when load factor exceeds 0.7
- O(1) average-case insert, search, and delete operations
- Comprehensive statistics tracking

### `compression.py`
Run-Length Encoding utilities including:
- RLE compression/decompression functions
- `InteractionHistory` class for managing user interaction sequences
- Automatic compression with ratio analysis
- Trend detection for user interest patterns

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
- Weighted recommendation generation
- Cold-start recommendations for new users

### `demo.py`
Comprehensive demonstration script that shows:
- Realistic user interaction simulation
- Hash table performance statistics
- RLE compression analysis
- Personalized recommendations
- Time complexity explanations

## Installation & Running

### Requirements

- Python 3.7 or higher
- No external dependencies required (uses only standard library)

### To Run

python demo.py



This will execute a complete demonstration showing:
1. System initialization
2. 50 simulated user interactions
3. Hash table performance metrics
4. Compression statistics
5. Personalized recommendations
6. User preference analysis
7. Time complexity analysis

## Key Features

### 1. Hash Table with Double Hashing
- Primary hash function: Polynomial rolling hash (multiplier: 31)
- Secondary hash function: Different multiplier (37) for step size
- Collision resolution: Double hashing minimizes clustering
- Dynamic resizing: Automatic when load factor > 0.7

### 2. Float-Based Weights
- Preference weights range from 0.0 to 1.0
- More intuitive than integer ranges (0-255)
- Represents percentage of user interest
- Standard approach in ML/recommendation systems

### 3. RLE Compression
- Compresses repeated interaction values
- Reduces memory for interaction histories
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
| RLE Compress | O(n)         | O(n)       |

**Note**: Resize operations are amortized to O(1) because they occur infrequently (only when load factor threshold is exceeded).

## Example Output

When you run `demo.py`, you’ll see:

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
- Collisions handled: 3
...



## Design Decisions

### Why Double Hashing?
- Superior to linear probing (avoids primary clustering)
- Better than quadratic probing (guaranteed to find slots)
- Provides pseudo-random probe sequences
- Maintains O(1) average case more reliably

### Why Float Weights (0.0-1.0)?
- More intuitive than 0-255 integer range
- Standard in machine learning systems
- Easier to normalize and compare
- Represents percentage naturally

### Why RLE Compression?
- User interactions often have repeated values
- Significant memory savings for long histories
- Fast compression/decompression (O(n))
- Enables trend analysis on compressed data

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

GNU Affero General Public License v3.0 (AGPL v3)

This software is free to use, modify, and distribute under the terms of the AGPL v3. Any service that deploys this software over a network must also release its source code under the same license.

For commercial licensing: volts-beret0t@icloud.com