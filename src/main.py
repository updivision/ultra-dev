#!/usr/bin/env python3
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config.settings import Config
from providers.provider_factory import ProviderFactory
from prompts.prompt_factory import PromptFactory
from github.pr_handler import PRHandler
from utils.helpers import handle_error

def main():
    """Main execution function following the original review.py pattern."""
    try:
        print("1) Loading configuration...")
        config = Config()
        print(f"Using AI provider: {config.ai_provider}")
        print(f"Using framework: {config.framework}")
        
        print("2) Fetching diff...")
        pr_handler = PRHandler(config.github_token)
        diff = pr_handler.get_diff()
        
        print("3) Fetching previous confidence score...")
        previous_score = pr_handler.get_previous_confidence_score()
        
        print("4) Sending files + diffs to AI provider...")
        provider = ProviderFactory.create_provider(config)
        prompt = PromptFactory.create_prompt(config.framework)
        
        # Process diff and create review request
        structured_files = pr_handler.process_diff_with_enhanced_context(diff)
        if not structured_files:
            print("No files with added lines found.")
            return
        
        enhanced_message = prompt.create_enhanced_review_message(structured_files, previous_score)
        system_prompt = prompt.get_system_prompt()
        
        print("5) Waiting for AI response...")
        output = provider.review_code(enhanced_message, system_prompt)
        
        print("6) Getting added lines...")
        added_lines = pr_handler.get_added_lines(diff)
        
        print("7) Processing summary and comments...")
        summary = output.get("summary")
        comments_array = output.get("comments", [])
        
        # Create summary text
        summary_text = pr_handler.create_summary_text(summary)
        
        # Parse line comments using line-based approach
        comments = pr_handler.parse_comments(comments_array, added_lines)
        
        print("8) Posting review to GitHub...")
        pr_handler.post_review_comments(comments, summary_text)
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
