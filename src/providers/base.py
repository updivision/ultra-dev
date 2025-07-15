from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config):
        self.config = config
    
    @abstractmethod
    def review_code(self, message, system_prompt):
        """
        Review code using the AI provider.
        
        Args:
            message (str): The formatted review message
            system_prompt (str): Framework-specific system prompt (required)
            
        Returns:
            dict: Review result with summary and comments
        """
        pass
    
    @abstractmethod
    def _make_api_request(self, payload):
        """
        Make API request to the provider.
        
        Args:
            payload (dict): Request payload
            
        Returns:
            dict: API response
        """
        pass
    
    def _validate_response(self, response):
        """
        Validate and parse the AI response.
        
        Args:
            response (str): Raw response from AI
            
        Returns:
            dict: Parsed response with summary and comments
        """
        import json
        import re
        
        try:
            # Clean the response
            cleaned_response = response.strip()
            
            # Check if response is wrapped in markdown code blocks
            if cleaned_response.startswith('```json') and cleaned_response.endswith('```'):
                # Extract JSON content from markdown code blocks
                json_match = re.search(r'```json\s*(.*?)\s*```', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(1).strip()
            elif cleaned_response.startswith('```') and cleaned_response.endswith('```'):
                # Handle generic code blocks (without json specifier)
                json_match = re.search(r'```\s*(.*?)\s*```', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(1).strip()
            
            # Parse the cleaned JSON
            parsed = json.loads(cleaned_response)
            print("Successfully parsed JSON response:")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            return {"summary": None, "comments": []}
        except Exception as e:
            print(f"Response validation error: {e}")
            return {"summary": None, "comments": []}
