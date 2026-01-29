#!/usr/bin/env python3
import json
import urllib.request
import sys

# Simple HN fetcher
story_id = 46783752

def fetch(url):
    return urllib.request.urlopen(url, timeout=20).read().decode()

story = json.loads(fetch(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"))

print(f"Story: {story.get('title')}", file=sys.stderr)
print(f"Score: {story.get('score')}", file=sys.stderr)
print(f"Comments: {story.get('descendants')}", file=sys.stderr)

# Get comments
comments = []
for cid in (story.get('kids') or [])[:80]:
    try:
        c = json.loads(fetch(f"https://hacker-news.firebaseio.com/v0/item/{cid}.json"))
        comments.append(c)
        if len(comments) % 10 == 0:
            print(f"Fetched {len(comments)} comments...", file=sys.stderr)
    except Exception as e:
        pass

result = {'story': story, 'comments': comments}
with open('prism_data.json', 'w') as f:
    json.dump(result, f)

print(json.dumps({
    'title': story.get('title'),
    'url': story.get('url'),
    'score': story.get('score'),
    'comments_fetched': len(comments)
}, indent=2))
