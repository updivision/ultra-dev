from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .gemini_provider import GeminiProvider
from .deepseek_provider import DeepSeekProvider

class ProviderFactory:
    """Factory class to create AI providers."""
    
    @staticmethod
    def create_provider(config):
        """
        Create an AI provider based on the configuration.
        
        Args:
            config: Configuration object with ai_provider setting
            
        Returns:
            BaseProvider: Instance of the appropriate provider
        """
        provider_map = {
            "openai": OpenAIProvider,
            "claude": ClaudeProvider,
            "gemini": GeminiProvider,
            "deepseek": DeepSeekProvider
        }
        
        provider_class = provider_map.get(config.ai_provider)
        if not provider_class:
            raise ValueError(f"Unsupported AI provider: {config.ai_provider}")
        
        return provider_class(config)
