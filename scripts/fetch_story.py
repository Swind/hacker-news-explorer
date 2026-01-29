#!/usr/bin/env python3
"""Fetch a Hacker News story by ID."""

import json
import sys
import urllib.request
import urllib.error

def fetch_story(story_id):
    """Fetch story and comments from HN API."""
    base_url = "https://hacker-news.firebaseio.com/v0"
    
    try:
        # Fetch story
        story_url = f"{base_url}/item/{story_id}.json"
        with urllib.request.urlopen(story_url) as response:
            story = json.loads(response.read().decode())
        
        # Fetch top comments
        comments = []
        if 'kids' in story:
            for comment_id in story['kids'][:100]:  # Limit to first 100
                try:
                    comment_url = f"{base_url}/item/{comment_id}.json"
                    with urllib.request.urlopen(comment_url) as response:
                        comment = json.loads(response.read().decode())
                        comments.append(comment)
                except:
                    pass
        
        return story, comments
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        return None, []
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None, []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fetch_story.py <story_id>", file=sys.stderr)
        sys.exit(1)
    
    story_id = sys.argv[1]
    story, comments = fetch_story(story_id)
    
    if story:
        print(json.dumps({"story": story, "comments": comments}, indent=2))
