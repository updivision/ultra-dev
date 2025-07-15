import requests
import json
from .base import BaseProvider

class DeepSeekProvider(BaseProvider):
    """DeepSeek provider using their API."""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.deepseek_api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def review_code(self, message, system_prompt):
        """Review code using DeepSeek API."""
        try:
            payload = {
                "model": "deepseek-reasoner",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "temperature": 0.1,
                "top_p": 0.95,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            response = self._make_api_request(payload)
            
            if response and "choices" in response:
                choices = response["choices"]
                if len(choices) > 0 and "message" in choices[0]:
                    message_content = choices[0]["message"].get("content", "")
                    return self._validate_response(message_content)
            
            return {"summary": None, "comments": []}
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"DeepSeek rate limit exceeded: {e}")
            elif e.response.status_code == 401:
                print(f"DeepSeek authentication error: {e}")
            else:
                print(f"DeepSeek HTTP error: {e}")
            return {"summary": None, "comments": []}
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek request error: {e}")
            return {"summary": None, "comments": []}
        except Exception as e:
            print(f"DeepSeek provider error: {e}")
            return {"summary": None, "comments": []}
    
    def _make_api_request(self, payload):
        """Make API request to DeepSeek."""
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
