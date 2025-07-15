import requests
import time
import json
from .base import BaseProvider

class OpenAIProvider(BaseProvider):
    """OpenAI provider using the existing Assistant API logic."""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.openai_api_key
        self.assistant_id = config.openai_assistant_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "assistants=v2"
        }
        self.max_chars = 250_000
    
    def review_code(self, message, system_prompt):
        """Review code using OpenAI Assistant API."""
        try:
            # Combine system prompt with message for Assistant API
            combined_message = f"{system_prompt}\n\n{message}"
            
            # Create thread and add message (using existing logic)
            thread_id = self._create_thread_and_add_message(combined_message)
            
            # Run assistant
            self._run_assistant(thread_id)
            
            # Get review output
            return self._get_review_output(thread_id)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"OpenAI rate limit exceeded: {e}")
            elif e.response.status_code == 401:
                print(f"OpenAI authentication error: {e}")
            else:
                print(f"OpenAI HTTP error: {e}")
            return {"summary": None, "comments": []}
        except requests.exceptions.RequestException as e:
            print(f"OpenAI request error: {e}")
            return {"summary": None, "comments": []}
        except Exception as e:
            print(f"OpenAI provider error: {e}")
            return {"summary": None, "comments": []}
    
    def _create_thread_and_add_message(self, message):
        """Create thread and send message to the assistant."""
        thread_res = requests.post(
            "https://api.openai.com/v1/threads",
            headers=self.headers
        )
        thread_res.raise_for_status()
        thread_id = thread_res.json()["id"]
        
        # Split into chunks if needed (using existing logic)
        messages = self._chunk_messages([message], self.max_chars)
        
        for part in messages:
            resp = requests.post(
                f"https://api.openai.com/v1/threads/{thread_id}/messages",
                headers=self.headers,
                json={"role": "user", "content": part}
            )
            resp.raise_for_status()
        
        return thread_id
    
    def _run_assistant(self, thread_id):
        """Kick off and poll the assistant run until completion."""
        run_res = requests.post(
            f"https://api.openai.com/v1/threads/{thread_id}/runs",
            headers=self.headers,
            json={"assistant_id": self.assistant_id}
        )
        run_res.raise_for_status()
        run_id = run_res.json()["id"]
        
        while True:
            status_res = requests.get(
                f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
                headers=self.headers
            )
            status_res.raise_for_status()
            status = status_res.json()["status"]
            
            if status == "completed":
                return
            if status == "failed":
                raise Exception("Assistant run failed.")
            time.sleep(3)
    
    def _get_review_output(self, thread_id):
        """Fetch the assistant's final message."""
        res = requests.get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=self.headers
        )
        res.raise_for_status()
        messages = res.json()["data"]
        
        for msg in reversed(messages):
            if msg.get("role") != "assistant":
                continue
            
            raw = ""
            for block in msg.get("content", []):
                if block.get("type") == "text":
                    txt = block.get("text")
                    raw += txt if isinstance(txt, str) else txt.get("value", "")
            
            if raw.strip():
                return self._validate_response(raw.strip())
        
        print("No assistant response found, returning empty structure")
        return {"summary": None, "comments": []}
    
    def _chunk_messages(self, sections, max_chars):
        """Split sections into message chunks ≤ max_chars (existing logic)."""
        import textwrap
        import re
        
        all_chunks = []
        
        for section in sections:
            if len(section) <= max_chars:
                all_chunks.append(section)
            else:
                # For large sections, split intelligently by file boundaries
                lines = section.splitlines(keepends=True)
                temp_chunks = []
                buf = ""
                current_file = "unknown"
                
                # Reserve space for continuation headers
                RESERVED_LEN = 500
                
                for line in lines:
                    # Track current file being processed
                    file_match = re.search(r"^### File: ([^\n]+)", line)
                    if file_match:
                        current_file = file_match.group(1).strip()
                    
                    # Check if adding this line would exceed the limit
                    if len(buf) + len(line) > (max_chars - RESERVED_LEN):
                        if buf.strip():  # Only add non-empty chunks
                            temp_chunks.append((buf, current_file))
                        buf = ""
                    
                    buf += line
                
                # Add the final chunk if it has content
                if buf.strip():
                    temp_chunks.append((buf, current_file))
                
                # Create numbered chunks with appropriate headers
                total = len(temp_chunks)
                for i, (chunk, filename) in enumerate(temp_chunks, start=1):
                    if total > 1:
                        header = textwrap.dedent(f"""\
                            # Code Review Request (Part {i}/{total})
                            
                            ⚠️ This review has been split into multiple parts due to size.
                            Current section: {filename}
                            
                        """)
                        all_chunks.append(header + chunk)
                    else:
                        all_chunks.append(chunk)
        
        return all_chunks
    
    def _make_api_request(self, payload):
        """Make API request to OpenAI (not used in Assistant API flow)."""
        pass
