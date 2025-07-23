import google.generativeai as genai
import json
import os
import logging

# Set up logging
LOG_DIR = r"C:\Users\gilbe\Documents\GitHub\coddy_v3\coddy_core\log"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "ai_engine.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# NOTE: This engine uses the google-generativeai library.
# Ensure it is installed: pip install google-generativeai

class AIEngine:
    """
    Handles all interactions with the generative AI model.
    """
    def __init__(self, api_key):
        if not api_key:
            logger.error("API key for AI Engine cannot be None or empty.")
            raise ValueError("API key for AI Engine cannot be None or empty.")
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            self.chat = None # Will hold the stateful chat session
            logger.info("AIEngine initialized successfully.")
        except Exception as e:
            logger.exception(f"Failed to initialize AIEngine: {e}")
            raise

    def start_new_chat(self):
        """Starts a new, stateful chat session."""
        system_instruction = """
You are Coddy, a creative and helpful AI coding assistant. Your primary goal is to help the user brainstorm and define a new software project.

Follow these rules:
1.  Be encouraging and ask clarifying questions to understand the project's purpose, features, and target audience.
2.  Do not use the `[READY_TO_GENERATE]` token on your first turn; you must ask questions first and wait for the user's response.
3.  Only after the user has provided sufficient answers should you determine if you are ready to proceed.
4.  When you feel you have enough information to create a detailed README.md file, you MUST end your response with the exact token: `[READY_TO_GENERATE]`.
5.  Keep your responses concise and friendly.
"""
        try:
            self.chat = self.model.start_chat(history=[{'role': 'user', 'parts': [system_instruction]},
                                                       {'role': 'model', 'parts': ["Hello! I'm Coddy. What brilliant idea are we working on today?"]}])
            logger.info("Started a new chat session.")
        except Exception as e:
            logger.exception(f"Error starting new chat session: {e}")
            raise

    def get_chat_response(self, prompt):
        """
        Sends a prompt to the current chat session and gets a response.
        """
        if not self.chat:
            self.start_new_chat()
        try:
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
            response = self.chat.send_message(prompt, safety_settings=safety_settings)
            logger.info(f"Chat response received for prompt: {prompt}")
            return response.text
        except Exception as e:
            logger.exception(f"An error occurred with the AI model: {e}")
            return f"Sorry, I encountered an error: {e}"

    def get_code_suggestion(self, user_prompt, code_snippet):
        """
        Generates a code suggestion and a suggested filename based on a user prompt and a code snippet.
        Returns a dictionary: {'filename': 'suggested_name.py', 'code': '...'}
        """
        if not self.model:
            logger.error("AI model is not initialized. Please check your API key.")
            raise ConnectionError("AI model is not initialized. Please check your API key.")

        if not code_snippet.strip():
            system_prompt = f"""
You are an expert software engineering assistant named Coddy.
A user has provided a task to create a new file. Your goal is to:
1. Suggest a concise, standard, snake_case Python filename for this task.
2. Write the initial Python code to implement the task.

You MUST return a JSON object with two keys: "filename" and "code".
The "filename" should be a string (e.g., "weather_api_handler.py").
The "code" should be a string containing the raw Python code.
Do not include any other text or markdown formatting in your response.

User's Task: "{user_prompt}"
"""
        else:
            system_prompt = f"""
You are an expert software engineering assistant named Coddy.
A user has provided a code snippet and a request. Your task is to modify the code as requested.

You MUST return a JSON object with two keys: "filename" and "code".
The "filename" key should be null, as the file already exists.
The "code" key should be a string containing ONLY the raw, modified code block.
Do not include any explanations or conversational text in the code.

Modify the following code:
---
{code_snippet}
---

User's Request: "{user_prompt}"
"""
        try:
            response = self.model.generate_content(system_prompt)
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = "\n".join(cleaned_text.splitlines()[1:-1])
            data = json.loads(cleaned_text)
            logger.info(f"Code suggestion generated for prompt: {user_prompt}")
            return data
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing AI JSON response: {e}\nRaw response: {getattr(response, 'text', '')}")
            return {'filename': None, 'code': getattr(response, 'text', '')}
        except Exception as e:
            logger.exception(f"Error during AI code suggestion generation: {e}")
            raise

    def get_full_refactor(self, code_snippet):
        """
        Generates a full semantic refactor of a given code snippet.
        """
        if not self.model:
            logger.error("AI model is not initialized. Please check your API key.")
            raise ConnectionError("AI model is not initialized. Please check your API key.")

        system_prompt = f"""
You are an expert software architect named Coddy.
Your task is to perform a full, semantic refactoring of the provided code.
Analyze the code for structure, clarity, efficiency, and adherence to best practices.
Improve variable names, function signatures, and overall architecture without altering the public-facing functionality.
Add comments where complex logic requires explanation.

IMPORTANT: You MUST return ONLY the raw, refactored code block. Do NOT include any explanations, conversational text, or markdown formatting like ```python.
Your entire response should be ONLY the code, ready to be pasted directly back into an editor.

Refactor the following code:
---
{code_snippet}
---
"""
        try:
            response = self.model.generate_content(system_prompt)
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```") and cleaned_text.endswith("```"):
                cleaned_text = "\n".join(cleaned_text.splitlines()[1:-1])
            logger.info("Full refactor generated successfully.")
            return cleaned_text
        except Exception as e:
            logger.exception(f"Error during AI full refactor generation: {e}")
            raise

    def get_session_summary(self, roadmap_content):
        """
        Analyzes the project's roadmap and provides a summary of progress.
        """
        if not self.model:
            logger.error("AI model is not initialized. Please check your API key.")
            raise ConnectionError("AI model is not initialized. Please check your API key.")

        system_prompt = f"""
You are an expert project manager named Coddy.
Your task is to analyze the following `roadmap.md` file content.
Pay close attention to tasks marked with `[x]` (completed) versus `[ ]` (pending).
Your tone should be positive and motivational. Provide a brief, insightful summary of the project's status.
Mention what has been accomplished and what the key next steps are.
Format the output as a concise, easy-to-read status report.

Roadmap Content:
---
{roadmap_content}
---
"""
        try:
            response = self.model.generate_content(system_prompt)
            logger.info("Session summary generated successfully.")
            return response.text
        except Exception as e:
            logger.exception(f"Error during AI session summary generation: {e}")
            raise

    def get_auto_planned_roadmap(self, project_goal):
        """
        Generates a new roadmap.md file content from a high-level goal.
        """
        if not self.model:
            logger.error("AI model is not initialized. Please check your API key.")
            raise ConnectionError("AI model is not initialized. Please check your API key.")

        system_prompt = f"""
You are an expert project planner and software architect named Coddy.
Your task is to take a high-level project goal and break it down into a detailed, phase-based roadmap in Markdown format.
The roadmap should be structured with `### Phase X:` headers, followed by a list of tasks using the `- [ ] Task description` format.
The plan should be logical, starting from setup and design, moving through implementation of core features, and ending with polish and deployment.

IMPORTANT: The output MUST be only the raw Markdown content for the `roadmap.md` file. Do not include any other text, conversation, or explanations.

The user's project goal is: "{project_goal}"

Generate the `roadmap.md` content now.
"""
        try:
            response = self.model.generate_content(system_prompt)
            logger.info("Auto-planned roadmap generated successfully.")
            return response.text
        except Exception as e:
            logger.exception(f"Error during AI auto-planning generation: {e}")
            raise