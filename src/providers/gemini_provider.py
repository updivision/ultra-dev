import requests
import json
from .base import BaseProvider

class GeminiProvider(BaseProvider):
    """Gemini provider using Google's Generative AI API."""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.gemini_api_key
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def review_code(self, message, system_prompt):
        """Review code using Gemini API."""
        try:
            # Combine system prompt with user message for Gemini
            combined_message = f"{system_prompt}\n\n{message}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": combined_message
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 1,
                    "topP": 1,
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            response = self._make_api_request(payload)
            
            if response and "candidates" in response:
                candidates = response["candidates"]
                if len(candidates) > 0 and "content" in candidates[0]:
                    content = candidates[0]["content"]
                    if "parts" in content and len(content["parts"]) > 0:
                        text_content = content["parts"][0].get("text", "")
                        return self._validate_response(text_content)
            
            return {"summary": None, "comments": []}
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Gemini rate limit exceeded: {e}")
            elif e.response.status_code == 403:
                print(f"Gemini authentication/permission error: {e}")
            else:
                print(f"Gemini HTTP error: {e}")
            return {"summary": None, "comments": []}
        except requests.exceptions.RequestException as e:
            print(f"Gemini request error: {e}")
            return {"summary": None, "comments": []}
        except Exception as e:
            print(f"Gemini provider error: {e}")
            return {"summary": None, "comments": []}
    
    def _make_api_request(self, payload):
        """Make API request to Gemini."""
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
