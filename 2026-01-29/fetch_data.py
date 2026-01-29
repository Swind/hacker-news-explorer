#!/usr/bin/env python3
import json
import urllib.request
import urllib.error
import sys
from datetime import datetime

def fetch_item(item_id, timeout=15):
    """Fetch a single HN item."""
    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except urllib.error.URLError as e:
        print(f"URL Error for item {item_id}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error fetching item {item_id}: {e}", file=sys.stderr)
        return None

def main():
    story_id = 46783752

    print(f"Fetching HN story {story_id}...", file=sys.stderr)

    # Fetch the main story
    story = fetch_item(story_id)
    if not story:
        print("Failed to fetch story", file=sys.stderr)
        sys.exit(1)

    print(f"Title: {story.get('title')}", file=sys.stderr)
    print(f"URL: {story.get('url')}", file=sys.stderr)
    print(f"Score: {story.get('score')}", file=sys.stderr)
    print(f"Descendants: {story.get('descendants')}", file=sys.stderr)

    # Determine if it's a URL post or Ask HN/Show HN with text
    is_text_post = bool(story.get('text'))

    # Fetch comments
    comments = []
    comment_ids = story.get('kids', [])
    print(f"Fetching {len(comment_ids)} comment IDs...", file=sys.stderr)

    # Fetch first 100 top-level comments
    for i, cid in enumerate(comment_ids[:100]):
        comment = fetch_item(cid, timeout=10)
        if comment:
            comments.append(comment)
        if (i + 1) % 20 == 0:
            print(f"  Fetched {i+1} comments...", file=sys.stderr)

    print(f"Total comments fetched: {len(comments)}", file=sys.stderr)

    # Output
    output = {
        "story": {
            "id": story.get("id"),
            "title": story.get("title"),
            "url": story.get("url"),
            "score": story.get("score"),
            "by": story.get("by"),
            "time": story.get("time"),
            "descendants": story.get("descendants"),
            "text": story.get("text"),
            "is_text_post": is_text_post
        },
        "comments_fetched": len(comments),
        "total_comments": len(comment_ids),
        "comments": comments
    }

    # Save to file
    with open("2026-01-29/prism_data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
