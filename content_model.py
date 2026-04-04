# content_model.py
# Data models for content items and content categories

from typing import List, Optional
from enum import Enum

class ContentType(Enum):
    MUSIC = "music"
    MUSIC_VIDEO = "music_video"
    INFORMATIONAL = "informational"

    @classmethod
    def from_string(cls, value: str) -> 'ContentType':
        for content_type in cls:
            if content_type.value == value:
                return content_type
        raise ValueError(f"Unknown content type: {value}")

class ContentItem:
    def __init__(self, 
                 content_id: str, 
                 content_type: ContentType, 
                 title: str, 
                 tags: List[str],
                 artist: Optional[str] = None,
                 duration_seconds: Optional[int] = None,
                 genre: Optional[str] = None):
        self.content_id = content_id
        self.content_type = content_type if isinstance(content_type, ContentType) else ContentType.from_string(content_type)
        self.title = title
        self.tags = tags
        self.artist = artist
        self.duration_seconds = duration_seconds
        self.genre = genre
        self.view_count = 0
        self.average_rating = 0.0

    def matches_tags(self, search_tags: List[str]) -> bool:
        return any(tag.lower() in [t.lower() for t in self.tags] for tag in search_tags)

    def get_display_string(self) -> str:
        parts = [self.title]
        if self.artist:
            parts.append(f"by {self.artist}")
        if self.duration_seconds:
            minutes = self.duration_seconds // 60
            seconds = self.duration_seconds % 60
            parts.append(f"({minutes}:{seconds:02d})")
        return " ".join(parts)

    def __repr__(self) -> str:
        return f"ContentItem({self.content_type.value}: {self.title})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, ContentItem):
            return False
        return self.content_id == other.content_id

    def __hash__(self) -> int:
        return hash(self.content_id)

class ContentDatabase:
    def __init__(self):
        self._content = {}
        self._by_type = {ct: [] for ct in ContentType}

    def add_content(self, item: ContentItem):
        self._content[item.content_id] = item
        self._by_type[item.content_type].append(item)

    def get_by_id(self, content_id: str) -> Optional[ContentItem]:
        return self._content.get(content_id)

    def get_by_type(self, content_type: ContentType) -> List[ContentItem]:
        return self._by_type[content_type].copy()

    def search_by_tags(self, tags: List[str], content_type: Optional[ContentType] = None) -> List[ContentItem]:
        items = self._content.values()
        if content_type:
            items = [item for item in items if item.content_type == content_type]
        return [item for item in items if item.matches_tags(tags)]

    def get_all(self) -> List[ContentItem]:
        return list(self._content.values())

    def __len__(self) -> int:
        return len(self._content)

    def __repr__(self) -> str:
        counts = {ct: len(items) for ct, items in self._by_type.items()}
        return f"ContentDatabase(total={len(self)}, by_type={counts})"

def create_sample_database() -> ContentDatabase:
    db = ContentDatabase()
    music_items = [
        ContentItem("m1", ContentType.MUSIC, "Summer Vibes", ["pop", "upbeat"], 
                   artist="The Beachside", duration_seconds=215, genre="Pop"),
        ContentItem("m2", ContentType.MUSIC, "Midnight Jazz", ["jazz", "relaxing"], 
                   artist="Jazz Collective", duration_seconds=342, genre="Jazz"),
        ContentItem("m3", ContentType.MUSIC, "Thunder Road", ["rock", "energetic"], 
                   artist="The Rockers", duration_seconds=267, genre="Rock"),
        ContentItem("m4", ContentType.MUSIC, "Symphony No. 5", ["classical", "orchestral"], 
                   artist="Beethoven", duration_seconds=420, genre="Classical"),
        ContentItem("m5", ContentType.MUSIC, "City Lights", ["hiphop", "urban"], 
                   artist="MC Flow", duration_seconds=198, genre="Hip Hop"),
        ContentItem("m6", ContentType.MUSIC, "Country Road", ["country", "folk"], 
                   artist="Nashville Stars", duration_seconds=223, genre="Country"),
        ContentItem("m7", ContentType.MUSIC, "Electronic Dreams", ["electronic", "dance"], 
                   artist="DJ Pulse", duration_seconds=245, genre="Electronic"),
    ]
    video_items = [
        ContentItem("v1", ContentType.MUSIC_VIDEO, "Summer Vibes (Official Video)", ["pop", "concert"], 
                   artist="The Beachside", duration_seconds=230, genre="Pop"),
        ContentItem("v2", ContentType.MUSIC_VIDEO, "Jazz Live at Blue Note", ["jazz", "live"], 
                   artist="Jazz Collective", duration_seconds=360, genre="Jazz"),
        ContentItem("v3", ContentType.MUSIC_VIDEO, "Rock Festival 2024", ["rock", "festival"], 
                   artist="The Rockers", duration_seconds=285, genre="Rock"),
        ContentItem("v4", ContentType.MUSIC_VIDEO, "Orchestra Performance", ["classical", "performance"], 
                   artist="Symphony Orchestra", duration_seconds=450, genre="Classical"),
        ContentItem("v5", ContentType.MUSIC_VIDEO, "City Lights Music Video", ["hiphop", "studio"], 
                   artist="MC Flow", duration_seconds=210, genre="Hip Hop"),
    ]
    info_items = [
        ContentItem("i1", ContentType.INFORMATIONAL, "Music Theory Fundamentals", ["education", "theory"], 
                   duration_seconds=1200),
        ContentItem("i2", ContentType.INFORMATIONAL, "The History of Jazz", ["education", "jazz", "history"], 
                   duration_seconds=1800),
        ContentItem("i3", ContentType.INFORMATIONAL, "Guitar Tutorial for Beginners", ["education", "instrument", "tutorial"], 
                   duration_seconds=2400),
        ContentItem("i4", ContentType.INFORMATIONAL, "Music Production 101", ["education", "production", "tutorial"], 
                   duration_seconds=3600),
        ContentItem("i5", ContentType.INFORMATIONAL, "Understanding Rhythm and Time", ["education", "theory", "rhythm"], 
                   duration_seconds=900),
        ContentItem("i6", ContentType.INFORMATIONAL, "How to Read Sheet Music", ["education", "theory", "tutorial"], 
                   duration_seconds=1500),
    ]
    for item in music_items + video_items + info_items:
        db.add_content(item)
    return db
