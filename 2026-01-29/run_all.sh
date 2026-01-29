#!/bin/bash
cd /home/swind/Program/reddit-explorer/2026-01-29

echo "=== Step 1: Fetching HN data ==="
python3 fetch_data.py > prism_output.json 2>&1
if [ $? -ne 0 ]; then
    echo "Fetch failed, trying with simpler script..."
    python3 -c "
import json, urllib.request, sys
story_id = 46783752
story = json.loads(urllib.request.urlopen(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json', timeout=20).read().decode())
comments = []
for cid in story.get('kids', [])[:50]:
    try:
        c = json.loads(urllib.request.urlopen(f'https://hacker-news.firebaseio.com/v0/item/{cid}.json', timeout=10).read().decode())
        comments.append(c)
    except: pass
result = {'story': story, 'comments': comments}
with open('prism_data.json', 'w') as f: json.dump(result, f)
print(json.dumps(result, indent=2))
" > prism_output.json 2>&1
fi

echo ""
echo "=== Step 2: Analyzing data ==="
python3 analyze.py
