import google.generativeai as genai

# NOTE: This engine uses the google-generativeai library.
# Ensure it is installed: pip install google-generativeai

class AIEngine:
    """
    Handles all interactions with the generative AI model.
    """
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key for AI Engine cannot be None or empty.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        self.chat = None # Will hold the stateful chat session

    def start_new_chat(self):
        """Starts a new, stateful chat session."""
        self.chat = self.model.start_chat(history=[])

    def get_chat_response(self, prompt):
        """
        Sends a prompt to the current chat session and gets a response.
        """
        if not self.chat:
            self.start_new_chat()
        try:
            # A simple safety setting to get started.
            # For production, these should be more robust.
            safety_settings = [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
            response = self.chat.send_message(prompt, safety_settings=safety_settings)
            return response.text
        except Exception as e:
            print(f"An error occurred with the AI model: {e}")
            return f"Sorry, I encountered an error: {e}"