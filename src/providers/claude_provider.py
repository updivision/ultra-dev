import requests
import json
from .base import BaseProvider

class ClaudeProvider(BaseProvider):
    """Claude provider using Anthropic's Messages API."""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.claude_api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        self.max_tokens = 64000
    
    def review_code(self, message, system_prompt):
        """Review code using Claude API."""
        try:
            payload = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": self.max_tokens,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "temperature": 0.1
            }
            
            response = self._make_api_request(payload)
            
            if response and "content" in response:
                content = response["content"]
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].get("text", "")
                    return self._validate_response(text_content)
            
            return {"summary": None, "comments": []}
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Claude rate limit exceeded: {e}")
            elif e.response.status_code == 401:
                print(f"Claude authentication error: {e}")
            else:
                print(f"Claude HTTP error: {e}")
            return {"summary": None, "comments": []}
        except requests.exceptions.RequestException as e:
            print(f"Claude request error: {e}")
            return {"summary": None, "comments": []}
        except Exception as e:
            print(f"Claude provider error: {e}")
            return {"summary": None, "comments": []}
    
    def _make_api_request(self, payload):
        """Make API request to Claude."""
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
