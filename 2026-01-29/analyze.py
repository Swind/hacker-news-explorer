#!/usr/bin/env python3
import json
import sys
from collections import Counter
from datetime import datetime

# Load data
with open("2026-01-29/prism_data.json", "r") as f:
    data = json.load(f)

story = data["story"]
comments = data["comments"]

# Analyze themes
themes = {
    "privacy": ["privacy", "data", "security", "surveillance", "personal", "tracking"],
    "capability": ["feature", "capable", "impressive", "can do", "ability", "powerful", "useful"],
    "api_integration": ["api", "integration", "sdk", "endpoint", "developer", "implement", "code"],
    "pricing": ["price", "cost", "expensive", "cheap", "free", "tier", "$", "subscription"],
    "comparison": ["vs", "versus", "claude", "anthropic", "google", "gemini", "compare", "alternative"],
    "skeptical": ["concern", "worry", "problem", "issue", "hype", "skeptical", "doubt", "bad", "waste"],
    "excited": ["amazing", "great", "finally", "awesome", "excited", "love", "cool", "wow"],
    "business_model": ["business", "monetization", "revenue", "freemium", "enterprise"],
    "technical": ["architecture", "model", "latency", "inference", "technical", "how", "works"],
    "ux": ["interface", "ui", "ux", "easy", "intuitive", "user", "experience"]
}

theme_counts = {theme: 0 for theme in themes}
theme_comments = {theme: [] for theme in themes}

for comment in comments:
    if not comment or "text" not in comment:
        continue
    text = comment.get("text", "").lower()
    for theme, keywords in themes.items():
        if any(word in text for word in keywords):
            theme_counts[theme] += 1
            theme_comments[theme].append({
                "id": comment.get("id"),
                "by": comment.get("by"),
                "text": comment.get("text", "")[:200]
            })

# Generate report
lines = []
lines.append("# Analysis: OpenAI Prism (HN Story #46783752)")
lines.append("")
lines.append(f"**Date Analyzed:** {datetime.now().strftime('%Y-%m-%d')}")
lines.append(f"**Story Score:** {story.get('score', 0)} points")
lines.append(f"**Total Comments:** {story.get('descendants', 0)}")
lines.append(f"**Comments Analyzed:** {len(comments)}")
lines.append("")
lines.append("---")
lines.append("")

# Story Details
lines.append("## Story Details")
lines.append("")
lines.append(f"- **Title:** {story.get('title', 'N/A')}")
lines.append(f"- **URL:** {story.get('url', 'N/A')}")
lines.append(f"- **Submitted by:** {story.get('by', 'N/A')}")
lines.append("")
if story.get('text'):
    lines.append("### Story Text")
    lines.append("")
    text = story.get('text', '')
    lines.append(f"{text[:800]}")
    if len(text) > 800:
        lines.append("...")
    lines.append("")

# What is Prism
lines.append("## What is Prism?")
lines.append("")
if story.get('url'):
    lines.append(f"[Prism]({story.get('url')}) is a new product announcement from OpenAI.")
    lines.append("")
    lines.append("Based on the HN discussion, key points include:")
    lines.append("")

lines.append("## Comment Themes Analysis")
lines.append("")
lines.append("| Theme | Mentions | % of Analyzed |")
lines.append("|-------|----------|---------------|")
total = len(comments)
for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
    pct = (count / total * 100) if total > 0 else 0
    lines.append(f"| {theme} | {count} | {pct:.1f}% |")
lines.append("")

# Top comments for each major theme
lines.append("## Top Comments by Theme")
lines.append("")
major_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]
for theme, count in major_themes:
    if count > 0:
        lines.append(f"### {theme.replace('_', ' ').title()} ({count} mentions)")
        lines.append("")
        for c in theme_comments[theme][:3]:
            lines.append(f"**@{c['by']}**:")
            lines.append(f"> {c['text'][:150]}...")
            lines.append("")

# Sentiment
lines.append("## Sentiment Analysis")
lines.append("")
lines.append(f"- **Skeptical/Concerned:** {theme_counts['skeptical']} mentions")
lines.append(f"- **Excited/Positive:** {theme_counts['excited']} mentions")
lines.append("")
if theme_counts['excited'] > theme_counts['skeptical']:
    lines.append("**Overall sentiment:** Leans positive")
elif theme_counts['skeptical'] > theme_counts['excited']:
    lines.append("**Overall sentiment:** Leans skeptical")
else:
    lines.append("**Overall sentiment:** Mixed/Neutral")
lines.append("")

lines.append("## Key Discussion Points")
lines.append("")
lines.append("### Privacy & Data")
if theme_counts['privacy'] > 0:
    lines.append(f"- {theme_counts['privacy']} comments discussing privacy concerns")
    lines.append("- Topics: data collection, storage, retention policies")
else:
    lines.append("- Minimal discussion of privacy")
lines.append("")

lines.append("### Capabilities")
if theme_counts['capability'] > 0:
    lines.append(f"- {theme_counts['capability']} comments discussing features")
else:
    lines.append("- Limited discussion of capabilities")
lines.append("")

lines.append("### Pricing & Business Model")
if theme_counts['pricing'] > 0 or theme_counts['business_model'] > 0:
    lines.append(f"- {theme_counts['pricing'] + theme_counts['business_model']} comments about pricing/business")
else:
    lines.append("- Limited discussion of pricing")
lines.append("")

lines.append("### Technical Discussion")
if theme_counts['technical'] > 0 or theme_counts['api_integration'] > 0:
    lines.append(f"- {theme_counts['technical'] + theme_counts['api_integration']} technical comments")
else:
    lines.append("- Limited technical discussion")
lines.append("")

# Top commenters
lines.append("## Most Active Commenters")
lines.append("")
commenters = Counter([c.get('by') for c in comments if c.get('by')])
for user, count in commenters.most_common(10):
    lines.append(f"- **@{user}**: {count} comments")
lines.append("")

# Write report
with open("2026-01-29/openai-prism.md", "w") as f:
    f.write("\n".join(lines))

print("Report written to 2026-01-29/openai-prism.md")
print("\n".join(lines))
