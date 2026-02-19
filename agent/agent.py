"""
Cognizance Chatbot Agent using the new Google GenAI SDK (google.genai).
Handles user queries about the festival and provides support.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)

from config import settings
from data import get_cognizance_context


class CognizanceAgent:
    """
    Main agent class for handling Cognizance-related queries
    using the new Google GenAI SDK (google.genai).
    """

    def __init__(self):
        """Initialize the agent with Gemini model and tools."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables")

        self.client = genai.Client(api_key=settings.google_api_key)

        self.cognizance_context = get_cognizance_context()
        self.system_prompt = self._create_system_prompt()

        self.generation_config = types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            temperature=settings.llm_temperature,
            max_output_tokens=settings.max_tokens,
        )

        # Primary + fallback model names
        self.model_names = [settings.google_model] + settings.fallback_models_list

        # Retry settings
        self.max_retries = 3
        self.base_retry_delay = 1  # seconds

    # ------------------------------------------------------------------
    # Prompt
    # ------------------------------------------------------------------
    def _create_system_prompt(self) -> str:
        """Create the system prompt with Cognizance context."""
        return f"""You are an intelligent AI assistant for Cognizance 2026, the annual technical festival of IIT Roorkee.

Your role is to:
1. Help users learn about Cognizance festival, its events, workshops, and activities
2. Answer questions about registration, dates, prizes, and participation
3. Provide information about past performances, workshops, and festival highlights
4. Guide users to the right resources and contacts
5. Help users file queries or issues when they need support

Guidelines:
- Be friendly, helpful, and enthusiastic about Cognizance
- Provide accurate information based on the festival data
- If you don't know something, be honest and suggest the user reach out to the dev team
- Encourage participation and highlight the exciting aspects of the festival

RESPONSE STYLE:
- Keep responses SHORT. Aim for 2 to 3 sentences max for simple questions, 4 to 5 sentences for detailed ones. Never exceed a small paragraph.
- Be conversational and simple, like chatting with a friend
- Do NOT use markdown formatting such as bold, italics, headers, bullet lists, or code blocks
- Do NOT use unnecessary punctuation like dashes, asterisks, or special characters
- Write in plain, natural sentences. No walls of text.
- Use emojis very sparingly, only when it genuinely adds warmth, not in every message
- If asked about multiple things, give a brief answer for each rather than long paragraphs
- Do NOT over-explain or repeat yourself. One clear answer is enough.

ISSUE / TROUBLESHOOTING FLOW:
- When a user reports an issue or faces a problem, propose one practical, actionable fix at a time (short and clear).
- After suggesting a fix, ask the user to try it and confirm whether it resolved the problem before offering the next suggestion.
- Repeat this cycle, offering up to 3–4 fixes as needed. Keep each suggestion concise and easy to follow.
- If the issue is not resolved or the user requests escalation, provide the dev team contact: no-reply.cognizance@iitr.ac.in and offer to summarize the attempted fixes for the team.

Festival Information:
{self.cognizance_context}

Current Date: February 2026 (Festival dates: 13th-15th March 2026)

Remember: You represent Cognizance and IIT Roorkee. Be professional, accurate, and helpful!"""

    # ------------------------------------------------------------------
    # History helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _build_history(
        chat_history: Optional[List[Dict[str, str]]],
    ) -> List[types.Content]:
        """Convert simple role/content dicts to google.genai Content objects."""
        contents: List[types.Content] = []
        if not chat_history:
            return contents
        for msg in chat_history:
            # Normalize and preserve common roles. Map unknown roles to 'model'.
            raw_role = (msg.get("role") or "").lower()
            if raw_role == "user":
                role = "user"
            elif raw_role == "assistant":
                # Map 'assistant' to 'model' as required by the new Google GenAI SDK
                role = "model"
            elif raw_role == "system":
                role = "system"
            else:
                role = "model"

            contents.append(
                types.Content(
                    role=role, parts=[types.Part.from_text(text=msg.get("content", ""))]
                )
            )
        return contents

    # ------------------------------------------------------------------
    # Main query processing
    # ------------------------------------------------------------------
    async def process_query(
        self,
        user_input: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        preferred_model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Process a user query and return the response.

        Args:
            user_input: The user's question or message
            chat_history: Optional list of previous messages

        Returns:
            dict with keys: success, response, model_used, (optional) pending_draft_id, error
        """
        history = self._build_history(chat_history)
        last_error: Optional[Exception] = None

        # Determine model candidates: use preferred_model first if provided,
        # otherwise use the configured primary + fallbacks.
        model_candidates = [preferred_model] if preferred_model else self.model_names

        # Build generation config; allow overrides for background/summarization calls
        if temperature is not None or max_output_tokens is not None:
            gen_temp = (
                temperature if temperature is not None else settings.llm_temperature
            )
            gen_max = (
                max_output_tokens
                if max_output_tokens is not None
                else settings.max_tokens
            )
            generation_config = types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                temperature=gen_temp,
                max_output_tokens=gen_max,
            )
        else:
            generation_config = self.generation_config

        for model_name in model_candidates:
            for attempt in range(self.max_retries):
                try:
                    # Build contents: history + current user message
                    contents = list(history) + [
                        types.Content(
                            role="user", parts=[types.Part.from_text(text=user_input)]
                        )
                    ]

                    if not model_name:
                        # Skip if preferred_model was None
                        continue

                    response = await self.client.aio.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=generation_config,
                    )

                    answer = response.text

                    if model_name != self.model_names[0]:
                        logger.info(f"Responded using fallback model: {model_name}")

                    return {
                        "success": True,
                        "response": answer,
                        "model_used": model_name,
                    }

                except (
                    google_exceptions.ResourceExhausted,
                    google_exceptions.TooManyRequests,
                    google_exceptions.ServiceUnavailable,
                ) as e:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        delay = self.base_retry_delay * (2**attempt)
                        logger.warning(
                            f"Model {model_name} rate-limited (attempt {attempt + 1}/{self.max_retries}). "
                            f"Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.warning(
                            f"Model {model_name} exhausted after {self.max_retries} retries: {e}. "
                            "Moving to next fallback model..."
                        )
                        break  # break retry loop, move to next model

                except Exception as e:
                    error_message = (
                        "I apologize, but I encountered an error processing your request. "
                        "Please try again or contact our support team.\n\n"
                        f"Error: {str(e)}"
                    )
                    return {
                        "success": False,
                        "response": error_message,
                        "error": str(e),
                    }

        # All models exhausted
        error_message = (
            "All available models have hit their quota limits right now. "
            "Please try again in a few minutes."
        )
        logger.error(f"All models exhausted. Last error: {last_error}")
        return {
            "success": False,
            "response": error_message,
            "error": str(last_error) if last_error else "Quota exceeded on all models",
        }

    # ------------------------------------------------------------------
    # Quick info
    # ------------------------------------------------------------------
    def get_quick_info(self) -> Dict[str, Any]:
        """Get quick festival information."""
        from data import get_structured_data

        return get_structured_data()


# ------------------------------------------------------------------
# Singleton
# ------------------------------------------------------------------
_agent_instance: Optional[CognizanceAgent] = None


def get_agent() -> CognizanceAgent:
    """Get or create the global agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CognizanceAgent()
    return _agent_instance
