#!/usr/bin/env python3
"""Fetch Hacker News story data directly."""

import json
import urllib.request
import urllib.error
import sys

def fetch_item(item_id):
    """Fetch an item from HN API."""
    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching item {item_id}: {e}", file=sys.stderr)
        return None

def fetch_top_comments(story, limit=50):
    """Fetch top-level comments from a story."""
    comments = []
    if 'kids' not in story:
        return comments
    
    for comment_id in story['kids'][:limit]:
        comment = fetch_item(comment_id)
        if comment:
            comments.append(comment)
            # Also fetch some replies
            if 'kids' in comment and len(comment['kids']) > 0:
                comment['replies'] = []
                for reply_id in comment['kids'][:3]:
                    reply = fetch_item(reply_id)
                    if reply:
                        comment['replies'].append(reply)
    
    return comments

def main():
    story_id = 46783752
    
    print("Fetching story...", file=sys.stderr)
    story = fetch_item(story_id)
    
    if not story:
        print("Failed to fetch story", file=sys.stderr)
        sys.exit(1)
    
    print(f"Title: {story.get('title', 'N/A')}", file=sys.stderr)
    print(f"URL: {story.get('url', 'N/A')}", file=sys.stderr)
    print(f"Score: {story.get('score', 0)}", file=sys.stderr)
    
    print("\nFetching comments...", file=sys.stderr)
    comments = fetch_top_comments(story, limit=100)
    print(f"Fetched {len(comments)} comments", file=sys.stderr)
    
    result = {
        "story": story,
        "comments": comments
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
