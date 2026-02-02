---
name: incremental-update
description: Incremental update workflow for existing reports. Use when analyzing stories that already have reports or need updates.
---

# Incremental Update Workflow

## When to Use
- The story you're analyzing already has a report
- You need to update an existing analysis
- Comment count has increased significantly

## Workflow

### Step 1: Check if Report Exists

Before starting any analysis, you MUST check:

```python
search_report_by_id(story_id=XXXXX)
```

### Step 2: Decide Next Action Based on Result

**Case A: Report doesn't exist**
→ Perform full analysis, use `create_report()` to create new report

**Case B: Report exists**
→ Continue to Step 3

### Step 3: Read Existing Report

```python
read_report(story_id=XXXXX, metadata_only=true)
```

Check the existing report for:
- Created date
- Verdict
- Comment count at time of analysis

### Step 4: Determine if Update is Needed

Compare comment count change:

| Comment Growth | Action |
|----------------|--------|
| < 10% | Skip update, reply "No significant new discussion" |
| 10-30% | Optional update, decide based on content |
| > 30% | **Must update** |

### Step 5: Update the Report

Use `append_report()` to add new content:

```markdown
## Update [YYYY-MM-DD]

**New comments:** +X comments (Y total)

### New Discussion Highlights
[Summary of new comments and discussions]

### Updated Verdict (if changed)
[Explain why your assessment changed]
```

## Important Principles

1. **Always check first**: Never assume a report doesn't exist
2. **Avoid duplicates**: Don't create multiple reports for the same story
3. **Append, don't replace**: Use `append_report` rather than recreating
4. **Timestamp updates**: Update content must be dated
5. **Explain changes**: Clearly explain why an update is needed

## Error Handling

If `create_report()` returns "report already exists" error:
→ Use `append_report()` to add content
→ Or use `read_report()` to view existing content

## Example

**Scenario: Analyzing a story from 3 days ago**

1. `search_report_by_id(12345)` → Report exists
2. `read_report(12345, metadata_only=true)` → Old report shows 50 comments
3. Check HN → Now has 80 comments (+60%)
4. Read new comments, analyze new discussion
5. `append_report(12345, "## Update [2026-02-02]\n\n**New comments:** +30...")`
