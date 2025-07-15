from .base_prompt import BasePrompt

class ReactPrompt(BasePrompt):
    """React/Next.js-specific prompt for code reviews."""
    
    framework = "React/Next.js"
    language_ext = "tsx"
    
    def get_system_prompt(self):
        """Get the React/Next.js-specific system prompt."""
        return f"""You are a senior React/Next.js engineer reviewing code changes.

Focus on:
- React hooks best practices and dependencies
- Next.js optimizations and features
- Component architecture and performance
- TypeScript integration and type safety
- Modern JavaScript/ES6+ patterns

{self.get_confidence_guidelines()}

Return JSON format:
{self.get_base_json_format()}

{self.get_base_rules()}"""
