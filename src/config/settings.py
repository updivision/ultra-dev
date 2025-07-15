import os

class Config:
    """Configuration class to handle all environment variables and validation."""
    
    def __init__(self):
        # Core configuration
        self.ai_provider = os.environ.get("AI_PROVIDER", "").lower()
        self.framework = os.environ.get("FRAMEWORK", "").lower()
        self.github_token = os.environ.get("GITHUB_TOKEN")
        
        # Provider-specific API keys
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.openai_assistant_id = os.environ.get("OPENAI_ASSISTANT_ID")
        self.claude_api_key = os.environ.get("CLAUDE_API_KEY")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        
        # GitHub event data
        self.event_path = os.environ.get("GITHUB_EVENT_PATH")
        
        # Validate configuration
        self._validate()
    
    def _validate(self):
        """Validate the configuration."""
        # Validate AI provider
        valid_providers = ["openai", "claude", "gemini", "deepseek"]
        if self.ai_provider not in valid_providers:
            raise ValueError(f"Invalid AI provider: {self.ai_provider}. Must be one of: {', '.join(valid_providers)}")
        
        # Validate framework
        valid_frameworks = ["laravel", "vue", "nuxt", "react", "nextjs"]
        if self.framework not in valid_frameworks:
            raise ValueError(f"Invalid framework: {self.framework}. Must be one of: {', '.join(valid_frameworks)}")
        
        # Validate required fields
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN is required")
        
        if not self.event_path:
            raise ValueError("GITHUB_EVENT_PATH is required")
        
        # Validate provider-specific requirements
        if self.ai_provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
            if not self.openai_assistant_id:
                raise ValueError("OPENAI_ASSISTANT_ID is required when using OpenAI provider")
        
        elif self.ai_provider == "claude":
            if not self.claude_api_key:
                raise ValueError("CLAUDE_API_KEY is required when using Claude provider")
        
        elif self.ai_provider == "gemini":
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY is required when using Gemini provider")
        
        elif self.ai_provider == "deepseek":
            if not self.deepseek_api_key:
                raise ValueError("DEEPSEEK_API_KEY is required when using DeepSeek provider")
