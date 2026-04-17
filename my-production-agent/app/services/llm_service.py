from ..config import settings
from ..utils.mock_llm import ask as mock_ask
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.use_mock = settings.use_mock_llm
        
        if not self.use_mock and settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel(settings.llm_model)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.use_mock = True
        else:
            self.model = None
            logger.info("Running in MOCK mode as requested.")

    def ask(self, question: str, history: list = None) -> str:
        """
        Send a question to LLM. 
        Uses Mock LLM if use_mock_llm is True or if Gemini fails.
        """
        if self.use_mock or not self.model:
            # Sử dụng hàm mock_llm đã có sẵn
            return mock_ask(question, history)

        try:
            # Convert simple history to Gemini format
            chat_history = []
            if history:
                for item in history:
                    chat_history.append({"role": "user", "parts": [item["q"]]})
                    chat_history.append({"role": "model", "parts": [item["a"]]})

            chat = self.model.start_chat(history=chat_history)
            response = chat.send_message(question)
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            # Fallback to mock on error
            return f"[Gemini Error, falling back to Mock] {mock_ask(question, history)}"

# Singleton instance
gemini_service = GeminiService()
