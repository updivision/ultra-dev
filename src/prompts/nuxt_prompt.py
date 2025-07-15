from .base_prompt import BasePrompt

class NuxtPrompt(BasePrompt):
    """Vue/Nuxt-specific prompt for code reviews."""
    
    framework = "Vue/Nuxt"
    language_ext = "vue"
    
    def get_system_prompt(self):
        """Get the Vue/Nuxt-specific system prompt."""
        return f"""You are a senior Vue 3/Nuxt 3 engineer reviewing code changes.

Focus on:
- Vue 3 Composition API best practices
- Nuxt 3 conventions and optimizations
- Component structure and reactivity
- TypeScript integration
- SSR/SSG considerations

{self.get_confidence_guidelines()}

Return JSON format:
{self.get_base_json_format()}

{self.get_base_rules()}"""
