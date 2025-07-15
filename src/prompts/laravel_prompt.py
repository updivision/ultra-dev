from .base_prompt import BasePrompt

class LaravelPrompt(BasePrompt):
    """Laravel-specific prompt for code reviews."""
    
    framework = "Laravel"
    language_ext = "php"
    
    def get_system_prompt(self):
        """Get the Laravel-specific system prompt."""
        return f"""You are a senior Laravel engineer reviewing code changes.

Focus on:
- Laravel best practices and conventions
- Eloquent ORM usage and relationships
- Security considerations (validation, authorization)
- Performance optimizations
- Code structure and maintainability

{self.get_confidence_guidelines()}

Return JSON format:
{self.get_base_json_format()}

{self.get_base_rules()}"""
