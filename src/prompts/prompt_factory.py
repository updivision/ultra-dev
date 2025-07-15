from .laravel_prompt import LaravelPrompt
from .nuxt_prompt import NuxtPrompt
from .react_prompt import ReactPrompt

class PromptFactory:
    """Factory class to create framework-specific prompts."""
    
    @staticmethod
    def create_prompt(framework):
        """
        Create a prompt based on the framework.
        
        Args:
            framework: Framework name (laravel, vue, nuxt, react, nextjs)
            
        Returns:
            Prompt class instance
        """
        prompt_map = {
            "laravel": LaravelPrompt,
            "vue": NuxtPrompt,  # Vue uses same as Nuxt
            "nuxt": NuxtPrompt,
            "react": ReactPrompt,
            "nextjs": ReactPrompt  # Next.js uses same as React
        }
        
        prompt_class = prompt_map.get(framework)
        if not prompt_class:
            raise ValueError(f"Unsupported framework: {framework}")
        
        return prompt_class()
