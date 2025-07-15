class BasePrompt:
    """Base prompt class with common functionality."""
    
    framework = None  # Should be overridden by subclasses
    language_ext = None  # Should be overridden by subclasses
    
    def get_system_prompt(self):
        """Get the framework-specific system prompt - should be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement get_system_prompt()")
    
    def get_base_json_format(self):
        """Get the common JSON format structure."""
        return """{
  "summary": {
    "confidence": 85,
    "risk_level": "Low risk",
    "reasoning": "Brief explanation"
  },
  "comments": [
    {
      "file": "path/to/file.ext",
      "line": 42,
      "comment": "Specific issue or suggestion"
    }
  ]
}"""
    
    def get_base_rules(self):
        """Get the common rules for all prompts."""
        return """Rules:
- Only comment on added lines with genuine issues
- Be concise and specific
- Empty comments array [] is acceptable for good code
- Use exact line numbers provided
- Be confident and decisive in your recommendations"""
    
    def get_confidence_guidelines(self):
        """Get confidence scoring and reasoning guidelines."""
        return """Confidence Scoring Guidelines:
- High Confidence (85-100): No critical issues, follows best practices, well-structured
- Medium Confidence (65-84): Minor issues, some improvements needed, generally solid
- Low Confidence (0-64): Major issues, critical bugs, architectural problems, security concerns

Risk Assessment:
- Low risk: Minor improvements, no breaking changes
- Medium risk: Some issues that could affect functionality or maintainability  
- High risk: Critical issues, security vulnerabilities, or major architectural problems"""
    
    def create_enhanced_review_message(self, structured_files, previous_score=None):
        """Create a structured message for code review."""
        message_parts = []
        
        header = f"## {self.framework.upper()} CODE REVIEW\n\nReview the following {self.framework} code changes:"
        
        if previous_score is not None:
            header += f"\n\nPrevious confidence score: {previous_score}%"
        
        message_parts.append(header)
        
        for file_data in structured_files:
            file_section = f"\n\n### File: {file_data['file']}\n"
            file_section += f"Added lines: {file_data['total_additions']}\n\n"
            
            if file_data.get('full_file_content'):
                file_section += f"```{self.language_ext}\n{file_data['full_file_content']}\n```\n\n"
            
            file_section += "**Lines to review:**\n\n"
            
            for line_num, line_content in sorted(file_data['added_lines'].items()):
                file_section += f"Line {line_num}: `{line_content}`\n"
                
                if not file_data.get('full_file_content') and line_num in file_data['line_contexts']:
                    file_section += f"```{self.language_ext}\n{file_data['line_contexts'][line_num]}\n```\n"
                file_section += "\n"
            
            message_parts.append(file_section)
        
        return "\n".join(message_parts)
