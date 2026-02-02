---
name: web-extraction
description: Web content extraction techniques. Use when reading article pages, extracting key information, or handling special website formats.
---

# Web Content Extraction Guide

## When to Use
- Need to read full article content
- Extracting key information
- Handling special website formats
- Webpage content is too long and needs focus

## Using the read_webpage Tool

```python
read_webpage(url="https://example.com/article")
```

**Note:** The tool automatically extracts main content, removing ads and navigation elements.

## Handling Different Website Types

### 1. Tech Blogs/Articles

**Characteristics:**
- Clear titles
- Publication dates
- Code examples
- Structured content

**Extract:**
- Title and subtitles
- Core arguments
- Code examples
- Conclusions

**Common formats:**
- Medium, Dev.to, personal blogs
- Company tech blogs

### 2. News Sites

**Characteristics:**
- Inverted pyramid structure
- Headline, lead, body
- Possible paywall

**Extract:**
- Headline (<h1>)
- Lead paragraph
- Key facts
- Quotes

### 3. PDF Documents

**When using read_webpage:**
- Tool handles PDF automatically
- May be incomplete, focus on:
  - Title page info
  - Table of contents (understand structure)
  - Abstract/Conclusion

### 4. GitHub README

**Characteristics:**
- Markdown format
- Contains code examples
- Has badges

**Extract:**
- Project description
- Installation instructions
- Usage examples
- Key features list

### 5. Video/Audio Content

**Cannot extract directly, strategies:**
- Read description/transcript text
- Check comment summaries
- Look for transcripts

## Content Extraction Strategies

### When Content is Too Long

**Strategy 1: Segment Reading**
```
Read first 30% → Understand topic
Read middle 40% → Get core arguments
Read last 30% → Check conclusion
```

**Strategy 2: Focus on Structure**
- Heading levels (h1, h2, h3)
- List items
- Bold/italic text
- Quote blocks

**Strategy 3: Keyword Search**
```
Search within content for:
- "conclusion", "summary", "takeaway"
- "however", "therefore", "importantly"
- Keywords from title
```

### When Content is Difficult to Understand

**Check:**
1. Is it a technical paper? → Focus on abstract and conclusion
2. Is it a series? → Look for the first part
3. Does it need background? → Check comments for explanations

### When Webpage Fails to Load

**Possible reasons:**
- Requires login
- Has anti-scraping measures
- Server issues
- Incorrect URL

**Strategies:**
- Check HN comments for summaries
- Look for alternative sources (mirrors, reposts)
- Skip the source, rely on comment discussion

## Key Information Identification

### Tech Article Key Points

**Must extract:**
- What is the core technology/concept?
- What problem does it solve?
- How is it implemented (high-level)?
- What are the limitations or drawbacks?

**Optional extract:**
- Performance data
- Benchmark results
- Comparisons with alternatives

### News Article Key Points

**5W1H:**
- Who: Which organization/person
- What: What happened
- When: When did it happen
- Where: Where did it happen
- Why: Why did it happen
- How: How did it happen

### Comment Content Handling

When using `read_webpage` to read HN comment pages:

**Focus on high-voted comments**
- Usually represent community consensus
- May have technical details
- May have differing opinions

**Identify discussion themes**
- What are the main arguments?
- Is there controversy? What's the debate focus?
- Are experts participating?

**Extract useful information**
- Background context
- Related links
- Experience sharing
- Criticisms

## Error Handling

### Common Errors

```
Error: Unable to fetch webpage
```

**Response:**
1. Verify URL is correct
2. Check if special handling is needed (e.g., PDF)
3. Rely on HN comment summaries
4. Note in report that content was inaccessible

### Content Quality Assessment

**Low quality indicators:**
- Repetitive content
- Too many ads
- Clickbait titles
- No substantive content

**Response:**
- Note in report
- Rely mainly on comment discussion
- Assess whether worth analyzing

## Best Practices

✅ **Check structure first**: Titles, sections, abstracts
✅ **Focus on key points**: Extract core information, don't read word-for-word
✅ **Combine with comments**: HN comments often have supplementary info
✅ **Note sources**: Cite where information came from

❌ **Don't read word-for-word**: Long articles are inefficient
❌ **Don't ignore conclusions**: Conclusions are usually most important
❌ **Don't get lost in details**: Focus on main arguments
