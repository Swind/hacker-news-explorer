---
name: hn-analysis
description: Hacker News story analysis techniques. Use when evaluating story interest level, assessing technical value, or identifying controversial topics.
---

# Hacker News Story Analysis Guide

## When to Use
- Evaluating whether a story is worth deep analysis
- Assessing the technical value of an article
- Identifying controversial topics
- Deciding on verdict classification

## Evaluation Dimensions

### 1. Technical Significance

**High technical value indicators:**
- Major tech releases (new languages, frameworks, major version updates)
- Security vulnerabilities or fixes (especially for widely-used software)
- New development methodologies or best practices
- Deep technical articles (not pop-science)
- Open source tool/project releases

**Technical value scoring:**
- ⭐⭐⭐⭐⭐ Major impact (e.g., new CPU architecture, major language release)
- ⭐⭐⭐⭐ Important impact (e.g., useful tool, security fix)
- ⭐⭐⭐ Some value (e.g., technical sharing, experience post)
- ⭐⭐ Lower value (e.g., intro/overview content)
- ⭐ Low technical content

### 2. Engagement Level

**Evaluation metrics:**
| Score | Comment Count | Assessment |
|-------|---------------|------------|
| Very High | > 200 | High community interest |
| High | 100-200 | Worth attention |
| Medium | 50-100 | Some discussion |
| Low | < 50 | Less discussion |

**Note:**
- New articles naturally have fewer comments
- Consider score (points) alongside comment count
- Comment quality matters more than quantity

### 3. Controversy

**Controversy indicators:**
- Polarized opinions in comments
- Discussion touches sensitive topics (politics, social issues)
- Disagreement on technical decisions
- Company/product criticism

**Controversy levels:**
- **High controversy**: Polarized comments, heated debate
- **Medium controversy**: Differing views but rational discussion
- **Low controversy**: More consensus

### 4. Novelty

**Novelty assessment:**
- Is this a completely new concept or technology?
- Unique perspective or insight?
- Different from common discussions?
- Challenges conventional thinking?

## Verdict Decision Tree

```
Start
  │
  ├─ Technical significance ⭐⭐⭐⭐ or ⭐⭐⭐⭐⭐?
  │   └─ YES → technical
  │
  ├─ Controversy High or Medium?
  │   └─ YES → controversial
  │
  ├─ Engagement High or Very High?
  │   └─ YES → interesting
  │
  ├─ Novelty High?
  │   └─ YES → interesting
  │
  └─ Other → not_interesting
```

## Analysis Process

### Step 1: Quick Scan
- Title: What's the topic?
- Score: How many people engaged?
- Comment count: Discussion level?

### Step 2: Deep Dive
- Article content: Technical depth?
- Comment sample: Community reaction?
- Source: Credible?

### Step 3: Synthesis
- Combine all dimensions
- Consider target audience
- Decide verdict

## Special Cases

### Show HN Posts
- Prioritize independent developers
- Assess project utility
- Consider innovation

### Controversial Topics
- Stay neutral
- Report both perspectives
- Avoid taking sides

### Recurring Topics
- Common HN cycles
- Assess if there's a new angle
- Avoid overcoverage

## Common Pitfalls

❌ **Only looking at score**: High score ≠ high value
❌ **Ignoring comment quality**: Toxic comments don't make it worth analyzing
❌ **Personal bias**: Don't let personal likes/dislikes affect judgment
❌ **Chasing trends**: Not all hot topics deserve deep analysis

✅ **Holistic assessment**: Consider multiple dimensions
✅ **Objective neutrality**: Base judgments on facts
✅ **Long-term value**: Will this content still be valuable a week from now?
