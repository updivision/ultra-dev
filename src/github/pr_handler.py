import os
import re
import subprocess
import json
import requests
import base64
from unidiff import PatchSet
from collections import defaultdict
from pathlib import Path

# File extensions to exclude from code review
EXCLUDED_EXTENSIONS = {
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', '.bmp',
    # Data/Config files
    '.json', '.xml', '.yaml', '.yml', '.csv', '.ini', '.toml',
    # Documentation
    '.md', '.txt', '.rst', '.pdf', '.doc', '.docx',
    # Build/Lock files
    '.lock', '.log', '.tmp', '.cache', '.pid',
    # Other binary/non-code files
    '.zip', '.tar', '.gz', '.exe', '.dll', '.so'
}

class PRHandler:
    """Handles GitHub PR operations and diff processing."""
    
    def __init__(self, github_token):
        self.github_token = github_token
        self.event_path = os.environ.get("GITHUB_EVENT_PATH")
        
        with open(self.event_path) as f:
            self.event = json.load(f)
        
        self.pr_number = self.event["number"]
        self.repo = self.event["repository"]["full_name"]
    
    def _should_exclude_file(self, filepath):
        """Check if a file should be excluded from review based on its extension."""
        file_ext = Path(filepath).suffix.lower()
        return file_ext in EXCLUDED_EXTENSIONS
    
    def get_diff(self):
        """Fetch the PR's unified diff via GitHub CLI."""
        res = subprocess.run(
            ["gh", "pr", "diff", str(self.pr_number), "--repo", self.repo, "--color", "never"],
            capture_output=True, text=True, check=True
        )
        return res.stdout
    
    def get_added_lines(self, diff):
        """Get a map of added lines for each file."""
        added_lines = defaultdict(dict)
        
        ps = PatchSet(diff.splitlines(keepends=True))
        
        for pfile in ps:
            if pfile.is_removed_file:
                continue
                
            filepath = pfile.path
            
            for hunk in pfile:
                for line in hunk:
                    if line.is_added and line.target_line_no is not None:
                        added_lines[filepath][line.target_line_no] = line.value.rstrip('\n\r')
        
        return dict(added_lines)
    
    def get_previous_confidence_score(self):
        """Fetch the previous confidence score from the most recent review comment."""
        try:
            res = subprocess.run([
                "gh", "api", 
                f"repos/{self.repo}/pulls/{self.pr_number}/reviews",
                "--jq", ".[0].body // empty"
            ], capture_output=True, text=True, check=False)
            
            if res.returncode == 0 and res.stdout.strip():
                latest_review = res.stdout.strip()
                confidence_match = re.search(r"Merge Confidence:\s*(\d+)%", latest_review)
                if confidence_match:
                    score = int(confidence_match.group(1))
                    print(f"Found previous confidence score: {score}")
                    return score
            
            print("No previous confidence score found")
            return None
            
        except Exception as e:
            print(f"Error fetching previous confidence score: {e}")
            return None
    
    def process_diff_with_enhanced_context(self, diff):
        """Process diff and create structured data with enhanced context."""
        ps = PatchSet(diff.splitlines(keepends=True))
        structured_files = []
        
        for pfile in ps:
            if pfile.is_removed_file:
                continue
                
            filepath = pfile.path
            
            # Skip excluded file types
            if self._should_exclude_file(filepath):
                print(f"Skipping excluded file: {filepath}")
                continue
                
            print(f"Processing file: {filepath}")
            
            # Get current file content for metadata and context
            file_content = self._get_file_content(filepath, diff)
            file_metadata = self._extract_file_metadata(file_content, filepath)
            # Check if we should include full file content (for files < 75,000 characters)
            include_full_file = file_content and len(file_content) < 75000
            
            # Process added lines with exact line numbers
            added_lines = {}
            line_contexts = {}
            
            for hunk in pfile:
                for line in hunk:
                    if line.is_added:
                        line_num = line.target_line_no
                        line_content = line.value.rstrip('\n\r')
                        added_lines[line_num] = line_content
                        
                        # Skip individual line context if we're including full file
                        if not include_full_file:
                            # Use diff-based context for accurate line mapping
                            diff_context = self._get_diff_context(hunk, line_num, context_lines=15)
                            if diff_context:
                                line_contexts[line_num] = diff_context
                            elif file_content:
                                # Fallback to enhanced file-based context (30 lines)
                                line_contexts[line_num] = self._get_surrounding_context(
                                    file_content, line_num, context_lines=30
                                )
            
            if added_lines:  # Only include files with added lines
                file_data = {
                    "file": filepath,
                    "added_lines": added_lines,
                    "line_contexts": line_contexts,
                    "metadata": file_metadata,
                    "total_additions": len(added_lines)
                }
                
                # Add full file content for smaller files
                if include_full_file:
                    file_data["full_file_content"] = file_content
                
                structured_files.append(file_data)
        
        return structured_files
    
    def _get_file_content(self, filepath, diff_content=None):
        """Fetch the current content of a file from the PR's head branch."""
        ref = self.event["pull_request"]["head"]["sha"]
        
        try:
            res = subprocess.run(
                [
                    "gh", "api",
                    f"repos/{self.repo}/contents/{filepath}",
                    "-F", f"ref={ref}",
                    "--jq", ".content"
                ],
                capture_output=True, text=True, check=True
            )

            cleaned = res.stdout.strip().replace('\n', '')
            if cleaned:
                return base64.b64decode(cleaned).decode('utf-8')
            return None
            
        except subprocess.CalledProcessError:
            # File doesn't exist in repository (likely a new file)
            if diff_content:
                return self._reconstruct_file_from_diff(filepath, diff_content)
            return None
    
    def _reconstruct_file_from_diff(self, filepath, diff_content):
        """Reconstruct file content from diff for new files."""
        try:
            file_pattern = rf"^diff --git a/{re.escape(filepath)} b/{re.escape(filepath)}"
            file_match = re.search(file_pattern, diff_content, re.MULTILINE)
            
            if not file_match:
                return None
                
            start_pos = file_match.start()
            next_file_match = re.search(r"^diff --git", diff_content[start_pos + 1:], re.MULTILINE)
            
            if next_file_match:
                file_diff = diff_content[start_pos:start_pos + 1 + next_file_match.start()]
            else:
                file_diff = diff_content[start_pos:]
            
            if "new file mode" in file_diff:
                lines = []
                for line in file_diff.split('\n'):
                    if line.startswith('+') and not line.startswith('+++'):
                        lines.append(line[1:])
                return '\n'.join(lines)
                
            return None
            
        except Exception as e:
            print(f"Warning: Could not reconstruct {filepath} from diff: {e}")
            return None
    
    def _extract_file_metadata(self, content, filepath):
        """Extract enhanced metadata from file content."""
        metadata = {
            "file_type": Path(filepath).suffix or "unknown",
            "imports": [],
            "exports": [],
            "functions": [],
            "classes": [],
            "interfaces": [],
            "line_count": 0
        }
        
        if not content:
            return metadata
        
        metadata["line_count"] = len(content.splitlines())
        lines = content.splitlines()
        
        for line in lines:
            line_stripped = line.strip()
            
            # Imports
            if (line_stripped.startswith('import ') or 
                line_stripped.startswith('from ') or
                line_stripped.startswith('use ') or
                line_stripped.startswith('require(')):
                metadata["imports"].append(line_stripped[:150])
            
            # Exports
            elif line_stripped.startswith('export '):
                metadata["exports"].append(line_stripped[:150])
            
            # Functions
            elif (re.match(r'^\s*(function|const|let|var)\s+\w+.*[=\(]', line) or
                  re.match(r'^\s*(public|private|protected)?\s*function\s+\w+', line) or
                  re.match(r'^\s*def\s+\w+', line) or
                  re.match(r'^\s*\w+\s*:\s*\([^)]*\)\s*=>', line)):
                metadata["functions"].append(line.strip()[:120])
            
            # Classes
            elif re.match(r'^\s*(export\s+)?(abstract\s+)?class\s+\w+', line):
                metadata["classes"].append(line.strip()[:120])
            
            # Interfaces/Types
            elif (re.match(r'^\s*(export\s+)?interface\s+\w+', line) or
                  re.match(r'^\s*(export\s+)?type\s+\w+', line)):
                metadata["interfaces"].append(line.strip()[:120])
        
        return metadata
    
    def _get_surrounding_context(self, content, line_number, context_lines=30):
        """Get surrounding lines of context around a specific line number."""
        if not content:
            return ""
        
        lines = content.splitlines()
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        context_with_numbers = []
        for i in range(start, end):
            prefix = ">>> " if i == line_number - 1 else "    "
            context_with_numbers.append(f"{prefix}{i+1:4d}: {lines[i]}")
        
        return "\n".join(context_with_numbers)
    
    def _get_diff_context(self, hunk, target_line, context_lines=10):
        """Get context lines from the diff hunk itself for accurate line mapping."""
        context = []
        
        target_lines = []
        for line in hunk:
            if not line.is_removed:
                target_lines.append((line.target_line_no, line.value.rstrip('\n\r'), line.is_added))
        
        target_lines.sort(key=lambda x: x[0] if x[0] is not None else 0)
        
        target_idx = None
        for i, (line_no, content, is_added) in enumerate(target_lines):
            if line_no == target_line:
                target_idx = i
                break
        
        if target_idx is not None:
            start = max(0, target_idx - context_lines)
            end = min(len(target_lines), target_idx + context_lines + 1)
            
            for i in range(start, end):
                line_no, content, is_added = target_lines[i]
                if line_no is not None:
                    prefix = ">>> " if line_no == target_line else "    "
                    context.append(f"{prefix}{line_no:4d}: {content}")
        
        return "\n".join(context)
    
    def parse_comments(self, comments_array, added_lines):
        """Turn the AI comments array into GitHub review-comments using line-based approach."""
        comments = []
        skipped_comments = 0
        
        for item in comments_array:
            path = item.get("file")
            line = item.get("line")
            body = item.get("comment", "").strip()
            
            if not (path and line and body):
                print(f"Skipping invalid comment: missing path, line, or body")
                skipped_comments += 1
                continue
                
            try:
                line = int(line)
            except (ValueError, TypeError):
                print(f"Skipping comment with invalid line number: {line}")
                skipped_comments += 1
                continue
            
            if path in added_lines and line in added_lines[path]:
                comments.append({
                    "path": path,
                    "line": line,
                    "body": body,
                    "side": "RIGHT"
                })
                print(f"Added line-based comment for {path}:{line}")
            else:
                print(f"Skipping comment for {path}:{line} - not an added line")
                skipped_comments += 1
        
        print(f"Valid comments: {len(comments)}, Skipped comments: {skipped_comments}")
        return comments
    
    def create_summary_text(self, summary):
        """Create a formatted summary text with merge confidence."""
        if not summary:
            return "Automated code review"
        
        confidence = summary.get("confidence", 0)
        risk_level = summary.get("risk_level", "Unknown risk")
        reasoning = summary.get("reasoning", "No reasoning provided")
        
        if confidence >= 80:
            emoji = "🟢"
        elif confidence >= 50:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        return f"{emoji} Merge Confidence: {confidence}% — {risk_level}\n{reasoning}"
    
    def post_review_comments(self, comments, summary_text):
        """Submit the assembled comments as a PR review on GitHub."""
        if not comments and summary_text == "Automated code review":
            print("No comments or summary to post.")
            return

        payload = {
            "body": summary_text,
            "event": "COMMENT",
            "comments": comments
        }
        url = f"https://api.github.com/repos/{self.repo}/pulls/{self.pr_number}/reviews"
        hdrs = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        res = requests.post(url, headers=hdrs, json=payload)
        if not res.ok:
            print("Failed to post review comments:", res.text)
        else:
            print("Review posted successfully.")
