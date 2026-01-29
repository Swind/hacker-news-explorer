"""
Hacker News API Adapter.

Uses the official HN Firebase API:
https://github.com/HackerNews/API
"""
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional


class HackerNewsAdapter:
    """Adapter for fetching data from Hacker News API."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, timeout: float = 10.0):
        self.client = httpx.Client(timeout=timeout)

    def _fetch(self, endpoint: str) -> Any:
        """Make a GET request to the HN API."""
        response = self.client.get(f"{self.BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()

    def get_story_ids(self, story_type: str, limit: int = 10) -> List[int]:
        """Get list of story IDs for the given type."""
        type_to_endpoint = {
            "top": "topstories",
            "new": "newstories",
            "best": "beststories",
            "ask": "askstories",
            "show": "showstories",
            "job": "jobstories",
        }

        if story_type not in type_to_endpoint:
            raise ValueError(f"Unknown story_type: {story_type}")

        endpoint = type_to_endpoint[story_type]
        all_ids = self._fetch(f"{endpoint}.json")
        return all_ids[:limit]

    def get_item(self, item_id: int) -> Dict[str, Any]:
        """Fetch a single item (story, comment, job, poll)."""
        return self._fetch(f"item/{item_id}.json")

    def get_stories(self, story_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch multiple stories with their full details."""
        story_ids = self.get_story_ids(story_type, limit)
        stories = []

        for story_id in story_ids:
            item = self.get_item(story_id)
            if item and item.get("type") in ("story", "job"):
                stories.append(self._format_story(item))

        return stories

    def get_comments(self, story_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch top-level comments for a story."""
        story = self.get_item(story_id)
        if not story or "kids" not in story:
            return []

        comment_ids = story["kids"][:limit]
        comments = []

        for comment_id in comment_ids:
            item = self.get_item(comment_id)
            if item and item.get("type") == "comment" and not item.get("deleted"):
                comments.append(self._format_comment(item))

        return comments

    def _format_story(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Format a story item for consistent output."""
        return {
            "id": item.get("id"),
            "title": item.get("title"),
            "url": item.get("url"),
            "score": item.get("score", 0),
            "by": item.get("by"),
            "time": item.get("time"),
            "time_iso": datetime.fromtimestamp(item.get("time", 0)).isoformat() if item.get("time") else None,
            "descendants": item.get("descendants", 0),
            "type": item.get("type"),
            "text": item.get("text"),
        }

    def _format_comment(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Format a comment item for consistent output."""
        return {
            "id": item.get("id"),
            "by": item.get("by"),
            "text": item.get("text"),
            "time": item.get("time"),
            "time_iso": datetime.fromtimestamp(item.get("time", 0)).isoformat() if item.get("time") else None,
            "parent": item.get("parent"),
            "kids_count": len(item.get("kids", [])),
        }

    def close(self):
        """Close the HTTP client."""
        self.client.close()
