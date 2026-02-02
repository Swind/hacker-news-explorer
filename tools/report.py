# tools/report.py
"""Report CRUD tools for managing story analysis reports."""
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from .base import BaseTool


def sanitize_filename(title: str) -> str:
    """Sanitize title for use as filename."""
    # Remove or replace characters that are problematic in filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', '', title)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Limit length
    return sanitized[:100]


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content."""
    lines = content.split('\n')
    if not lines or not lines[0].startswith('---'):
        return {}

    frontmatter_lines = []
    for i, line in enumerate(lines[1:], 1):
        if line.startswith('---'):
            break
        frontmatter_lines.append(line)

    metadata = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip().strip('"')

    return metadata


class CreateReportTool(BaseTool):
    """Tool for creating a new story analysis report."""

    @classmethod
    def get_name(cls) -> str:
        return "create_report"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "create_report",
            "description": "Create a new story analysis report with frontmatter metadata.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "story_id": {
                        "type": "integer",
                        "description": "Hacker News story ID"
                    },
                    "hn_url": {
                        "type": "string",
                        "description": "URL to the HN story"
                    },
                    "title": {
                        "type": "string",
                        "description": "Story title"
                    },
                    "verdict": {
                        "type": "string",
                        "enum": ["interesting", "not_interesting", "controversial", "technical"],
                        "description": "Analysis verdict"
                    },
                    "content": {
                        "type": "string",
                        "description": "Markdown content of the analysis"
                    }
                },
                "required": ["story_id", "hn_url", "title", "verdict", "content"]
            }
        }

    def _execute(self, story_id: int, hn_url: str, title: str, verdict: str, content: str) -> str:
        """Create a report file with frontmatter."""
        workdir = self.context.get("workdir", Path.cwd())
        report_dir = workdir / "report"

        # Check if a report with this story_id already exists (across all dates)
        if report_dir.exists():
            for md_file in report_dir.rglob("*.md"):
                try:
                    existing_content = md_file.read_text()
                    metadata = parse_frontmatter(existing_content)
                    if metadata.get("story_id") == str(story_id):
                        relative_path = md_file.relative_to(workdir)
                        return (f"Error: Report for story_id {story_id} already exists at {relative_path}. "
                                f"Use append_report to add updates instead.")
                except Exception:
                    continue

        # Create date-based subdirectory
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_dir = report_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Create filename from sanitized title
        filename = sanitize_filename(title)
        file_path = date_dir / f"{filename}.md"

        # Double-check (shouldn't happen given above check, but safety first)
        if file_path.exists():
            return f"Error: Report file already exists at {file_path.relative_to(workdir)}"

        # Create frontmatter
        created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        frontmatter = f"""---
story_id: {story_id}
hn_url: {hn_url}
title: "{title}"
verdict: {verdict}
created_at: {created_at}
---

"""

        # Write file
        try:
            full_content = frontmatter + content
            file_path.write_text(full_content)
            return f"Created report at {file_path.relative_to(workdir)}"
        except Exception as e:
            return f"Error creating report: {e}"


class ReadReportTool(BaseTool):
    """Tool for reading a story analysis report."""

    @classmethod
    def get_name(cls) -> str:
        return "read_report"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "read_report",
            "description": "Read a story analysis report by story_id. Returns metadata and content.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "story_id": {
                        "type": "integer",
                        "description": "Hacker News story ID"
                    },
                    "metadata_only": {
                        "type": "boolean",
                        "description": "If true, only return frontmatter metadata"
                    }
                },
                "required": ["story_id"]
            }
        }

    def _execute(self, story_id: int, metadata_only: bool = False) -> str:
        """Read a report by story_id."""
        workdir = self.context.get("workdir", Path.cwd())
        report_dir = workdir / "report"

        if not report_dir.exists():
            return f"Error: Report directory not found"

        # Search for the report file
        report_file = None
        for md_file in report_dir.rglob("*.md"):
            try:
                content = md_file.read_text()
                metadata = parse_frontmatter(content)
                if metadata.get("story_id") == str(story_id):
                    report_file = md_file
                    break
            except Exception:
                continue

        if not report_file:
            return f"Error: No report found for story_id {story_id}"

        try:
            content = report_file.read_text()

            if metadata_only:
                metadata = parse_frontmatter(content)
                metadata_lines = ["---"]
                for key, value in metadata.items():
                    metadata_lines.append(f"{key}: {value}")
                metadata_lines.append("---")
                return "\n".join(metadata_lines)

            return content
        except Exception as e:
            return f"Error reading report: {e}"


class ListReportsTool(BaseTool):
    """Tool for listing all reports with optional filters."""

    @classmethod
    def get_name(cls) -> str:
        return "list_reports"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "list_reports",
            "description": "List all reports with optional filters by verdict or date.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "verdict": {
                        "type": "string",
                        "enum": ["interesting", "not_interesting", "controversial", "technical"],
                        "description": "Filter by verdict"
                    },
                    "date": {
                        "type": "string",
                        "description": "Filter by date (YYYY-MM-DD format)"
                    }
                }
            }
        }

    def _execute(self, verdict: Optional[str] = None, date: Optional[str] = None) -> str:
        """List reports with optional filters."""
        workdir = self.context.get("workdir", Path.cwd())
        report_dir = workdir / "report"

        if not report_dir.exists():
            return "No reports found (report directory does not exist)"

        reports = []

        # Determine search path
        if date:
            search_path = report_dir / date
            if not search_path.exists():
                return f"No reports found for date {date}"
        else:
            search_path = report_dir

        # Search for report files
        for md_file in search_path.rglob("*.md"):
            try:
                content = md_file.read_text()
                metadata = parse_frontmatter(content)

                # Apply verdict filter
                if verdict and metadata.get("verdict") != verdict:
                    continue

                # Format report info
                relative_path = md_file.relative_to(workdir)
                report_info = {
                    "path": str(relative_path),
                    "story_id": metadata.get("story_id", "N/A"),
                    "title": metadata.get("title", "N/A"),
                    "verdict": metadata.get("verdict", "N/A"),
                    "created_at": metadata.get("created_at", "N/A"),
                    "hn_url": metadata.get("hn_url", "N/A")
                }
                reports.append(report_info)
            except Exception:
                continue

        if not reports:
            return "No reports found matching criteria"

        # Format output
        lines = [f"Found {len(reports)} report(s):\n"]
        for r in reports:
            lines.append(f"  Story ID: {r['story_id']}")
            lines.append(f"  Title: {r['title']}")
            lines.append(f"  Verdict: {r['verdict']}")
            lines.append(f"  Created: {r['created_at']}")
            lines.append(f"  Path: {r['path']}")
            lines.append(f"  HN URL: {r['hn_url']}")
            lines.append("")

        return "\n".join(lines)


class SearchReportByIdTool(BaseTool):
    """Tool for checking if a report exists for a story_id."""

    @classmethod
    def get_name(cls) -> str:
        return "search_report_by_id"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "search_report_by_id",
            "description": "Check if a report exists for a given story_id. Returns the file path if found.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "story_id": {
                        "type": "integer",
                        "description": "Hacker News story ID"
                    }
                },
                "required": ["story_id"]
            }
        }

    def _execute(self, story_id: int) -> str:
        """Search for report by story_id."""
        workdir = self.context.get("workdir", Path.cwd())
        report_dir = workdir / "report"

        if not report_dir.exists():
            return f"No report found for story_id {story_id} (report directory does not exist)"

        # Search for the report file
        for md_file in report_dir.rglob("*.md"):
            try:
                content = md_file.read_text()
                metadata = parse_frontmatter(content)
                if metadata.get("story_id") == str(story_id):
                    relative_path = md_file.relative_to(workdir)
                    return f"Report found at: {relative_path}"
            except Exception:
                continue

        return f"No report found for story_id {story_id}"


class AppendReportTool(BaseTool):
    """Tool for appending content to an existing story analysis report."""

    @classmethod
    def get_name(cls) -> str:
        return "append_report"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "append_report",
            "description": "Append markdown content to an existing report. Updates the updated_at timestamp in frontmatter.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "story_id": {
                        "type": "integer",
                        "description": "Hacker News story ID"
                    },
                    "content": {
                        "type": "string",
                        "description": "Markdown content to append to the report"
                    }
                },
                "required": ["story_id", "content"]
            }
        }

    def _execute(self, story_id: int, content: str) -> str:
        """Append content to an existing report."""
        workdir = self.context.get("workdir", Path.cwd())
        report_dir = workdir / "report"

        if not report_dir.exists():
            return f"Error: Report directory not found"

        # Search for the report file
        report_file = None
        for md_file in report_dir.rglob("*.md"):
            try:
                file_content = md_file.read_text()
                metadata = parse_frontmatter(file_content)
                if metadata.get("story_id") == str(story_id):
                    report_file = md_file
                    break
            except Exception:
                continue

        if not report_file:
            return f"Error: No report found for story_id {story_id}. Use create_report for new reports."

        try:
            # Read existing content
            existing_content = report_file.read_text()
            lines = existing_content.split('\n')

            # Find the end of frontmatter (second ---)
            frontmatter_end = 0
            dash_count = 0
            for i, line in enumerate(lines):
                if line.strip() == '---':
                    dash_count += 1
                    if dash_count == 2:
                        frontmatter_end = i
                        break

            # Extract frontmatter lines
            frontmatter_lines = lines[:frontmatter_end + 1]
            content_lines = lines[frontmatter_end + 1:]

            # Update or add updated_at timestamp
            updated_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            updated_at_added = False
            new_frontmatter_lines = []

            for line in frontmatter_lines:
                if line.startswith('updated_at:'):
                    new_frontmatter_lines.append(f'updated_at: {updated_at}')
                    updated_at_added = True
                elif line.strip() == '---' and not updated_at_added and len(new_frontmatter_lines) > 1:
                    # Add updated_at before the closing ---
                    new_frontmatter_lines.append(f'updated_at: {updated_at}')
                    new_frontmatter_lines.append(line)
                    updated_at_added = True
                else:
                    new_frontmatter_lines.append(line)

            # If updated_at still wasn't added (edge case), add it before the last ---
            if not updated_at_added:
                final_lines = []
                for i, line in enumerate(new_frontmatter_lines):
                    if line.strip() == '---' and i > 0:
                        final_lines.append(f'updated_at: {updated_at}')
                    final_lines.append(line)
                new_frontmatter_lines = final_lines

            # Combine: frontmatter + original content + new content
            new_content = '\n'.join(new_frontmatter_lines) + '\n\n'
            if content_lines:
                # Keep original content
                new_content += '\n'.join(content_lines).rstrip()
                if content_lines and not content_lines[-1].strip() == '':
                    new_content += '\n'
            # Append new content
            new_content += '\n' + content

            # Write back to file
            report_file.write_text(new_content)
            relative_path = report_file.relative_to(workdir)
            return f"Appended to report at {relative_path} (updated_at: {updated_at})"

        except Exception as e:
            return f"Error appending to report: {e}"
