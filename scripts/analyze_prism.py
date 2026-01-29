#!/usr/bin/env python3
"""Analyze OpenAI Prism story from HN."""

import json
import subprocess
import sys

def fetch_story_data(story_id):
    """Fetch story and comments."""
    try:
        result = subprocess.run(
            [sys.executable, "scripts/fetch_story.py", str(story_id)],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error fetching story: {e}", file=sys.stderr)
        return None

def analyze_comments(comments):
    """Analyze comment themes."""
    themes = {
        "privacy": [],
        "capability": [],
        "api": [],
        "pricing": [],
        "comparison": [],
        "skeptical": [],
        "excited": [],
        "technical": []
    }
    
    keywords = {
        "privacy": ["privacy", "data", "security", "surveillance", "tracking", "personal"],
        "capability": ["feature", "capability", "powerful", "impressive", "can do"],
        "api": ["api", "integration", "developer", "sdk", "endpoint"],
        "pricing": ["price", "cost", "expensive", "cheap", "free", "tier"],
        "comparison": ["vs", "versus", "compared", "better", "worse", "alternative", "claude", "anthropic", "google"],
        "skeptical": ["hype", "overrated", "concern", "worry", "problem", "issue"],
        "excited": ["amazing", "great", "love", "finally", "awesome", "wow"],
        "technical": ["architecture", "model", "training", "inference", "latency", "throughput"]
    }
    
    for comment in comments:
        if not comment or "text" not in comment:
            continue
            
        text = comment.get("text", "").lower()
        for theme, words in keywords.items():
            if any(word in text for word in words):
                themes[theme].append({
                    "id": comment.get("id"),
                    "author": comment.get("by"),
                    "text": comment.get("text", "")[:200]
                })
    
    return themes

def main():
    story_id = 46783752
    
    print("Fetching Hacker News story...", file=sys.stderr)
    data = fetch_story_data(story_id)
    
    if not data:
        sys.exit(1)
    
    story = data.get("story", {})
    comments = data.get("comments", [])
    
    print(f"\nStory: {story.get('title', 'N/A')}", file=sys.stderr)
    print(f"URL: {story.get('url', 'N/A')}", file=sys.stderr)
    print(f"Score: {story.get('score', 0)}", file=sys.stderr)
    print(f"Comments fetched: {len(comments)}", file=sys.stderr)
    
    # Output JSON
    output = {
        "story": story,
        "comment_themes": analyze_comments(comments),
        "total_comments_analyzed": len(comments)
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
