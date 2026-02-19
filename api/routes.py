"""
FastAPI routes for Cognizance chatbot API.
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Request, status, BackgroundTasks
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from agent import get_agent
from config import settings

limiter = Limiter(key_func=get_remote_address)

# History management
# If a conversation grows too large, keep only the last `KEEP_LAST` turns
# and optionally summarize the earlier part to preserve context while
# reducing token usage.
MAX_TURNS = 15
KEEP_LAST = 8

# In-memory summary cache (conversation_id -> summary).
import time
import asyncio

# Summary cache stores dicts: { conversation_id: {"summary": str, "expires_at": float} }
SUMMARY_CACHE: Dict[str, Dict[str, object]] = {}
# TTL for cached summaries (seconds) — 6 hours
SUMMARY_TTL_SECONDS = 6 * 3600


async def _cleanup_summary_cache_loop(interval_seconds: int = 6000):
    """Periodically remove expired summaries from SUMMARY_CACHE.

    Runs forever; intended to be scheduled as a background task from the
    application startup lifecycle. Default interval: 6000s (100 minutes).
    """
    while True:
        try:
            now = time.time()
            to_delete = [
                k for k, v in SUMMARY_CACHE.items() if v.get("expires_at", 0) <= now
            ]
            for k in to_delete:
                del SUMMARY_CACHE[k]
        except Exception:
            # never let cleanup crash the loop
            pass
        await asyncio.sleep(interval_seconds)


def start_summary_cache_cleanup(interval_seconds: int = 6000):
    """Schedule the summary cache cleanup loop as a background task.

    Call this from an async startup context (e.g., FastAPI lifespan).
    """
    try:
        asyncio.create_task(_cleanup_summary_cache_loop(interval_seconds))
    except RuntimeError:
        # If no running loop is available, ignore — caller should be in async context.
        return


# Request/Response Models
class Message(BaseModel):
    """Individual message in chat history."""

    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., min_length=1, description="User's message")
    chat_history: Optional[List[Message]] = Field(
        default=None, description="Previous conversation history"
    )
    conversation_id: Optional[str] = Field(
        default=None, description="Optional ID to cache conversation summaries"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is Cognizance?",
                "chat_history": [
                    {"role": "user", "content": "Hello"},
                    {
                        "role": "assistant",
                        "content": "Hi! How can I help you with Cognizance?",
                    },
                ],
                "conversation_id": "query-123"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    success: bool = Field(..., description="Whether the request was successful")
    response: str = Field(..., description="AI assistant's response")
    error: Optional[str] = Field(None, description="Error message if any")


class FestivalInfoResponse(BaseModel):
    """Response model for festival info endpoint."""

    festival_name: str
    edition: str
    dates: str
    institution: str
    prize_pool: str
    theme: str
    website: str
    registration_url: str


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    service: str
    version: str


# Create router
router = APIRouter(prefix="/api/v1", tags=["chatbot"])


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("15/minute")
async def chat(
    request: Request, chat_request: ChatRequest, background_tasks: BackgroundTasks
):
    """
    Process a chat message and return AI response.

    This endpoint handles user queries about Cognizance festival,
    events, registration, and provides support through an AI agent.
    """
    try:
        agent = get_agent()

        # Convert chat history to dict format
        history = None
        if chat_request.chat_history:
            full_history = [msg.dict() for msg in chat_request.chat_history]

            # If the conversation is large, do not block the request with
            # summarization. Use recent turns for the immediate response and
            # schedule background summarization (which will cache the result
            # if `conversation_id` is provided).
            if len(full_history) > MAX_TURNS:
                older = full_history[: len(full_history) - KEEP_LAST]
                recent = full_history[len(full_history) - KEEP_LAST :]

                # If a cached summary exists for this conversation and is fresh, use it.
                if (
                    chat_request.conversation_id
                    and chat_request.conversation_id in SUMMARY_CACHE
                ):
                    entry = SUMMARY_CACHE[chat_request.conversation_id]
                    if entry.get("expires_at", 0) > time.time():
                        summary_text = entry.get("summary", "")
                        history = [
                            {"role": "assistant", "content": summary_text}
                        ] + recent
                    else:
                        # expired
                        del SUMMARY_CACHE[chat_request.conversation_id]
                        history = recent
                else:
                    # Immediate path: reply using recent turns only to avoid latency
                    history = recent

                    # Schedule background summarization. Use a synchronous helper
                    # that schedules the async worker to avoid blocking FastAPI.
                    def _schedule_summarization(
                        conv_id: Optional[str], older_turns: list
                    ):
                        async def _do():
                            try:
                                summary_prompt = (
                                    "Please summarize the preceding conversation into 2-3 short "
                                    "sentences focusing on user goals, important facts, and any "
                                    "unresolved issues. Keep the summary concise."
                                )
                                # Use a cheaper fallback model for summarization to save quota
                                cheaper_model = (
                                    settings.fallback_models_list[-1]
                                    if settings.fallback_models_list
                                    else settings.google_model
                                )
                                summary_result = await agent.process_query(
                                    user_input=summary_prompt,
                                    chat_history=older_turns,
                                    preferred_model=cheaper_model,
                                    temperature=0.2,
                                    max_output_tokens=200,
                                )
                                if summary_result.get("success") and summary_result.get(
                                    "response"
                                ):
                                    summary_text = summary_result["response"].strip()
                                    if conv_id:
                                        SUMMARY_CACHE[conv_id] = {
                                            "summary": summary_text,
                                            "expires_at": time.time()
                                            + SUMMARY_TTL_SECONDS,
                                        }
                            except Exception:
                                return

                        try:
                            asyncio.create_task(_do())
                        except Exception:
                            # If scheduling fails, ignore — summarization is optional
                            return

                    background_tasks.add_task(
                        _schedule_summarization, chat_request.conversation_id, older
                    )
            else:
                history = full_history

        # Process the query using the (possibly summarized) history
        result = await agent.process_query(
            user_input=chat_request.message, chat_history=history
        )

        return ChatResponse(
            success=result["success"],
            response=result["response"],
            error=result.get("error"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.get("/info", response_model=FestivalInfoResponse)
async def get_festival_info():
    """
    Get quick information about Cognizance festival.

    Returns basic festival details without requiring a chat interaction.
    """
    try:
        agent = get_agent()
        info = agent.get_quick_info()
        return FestivalInfoResponse(**info)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch festival info: {str(e)}",
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns the service status and version information.
    """
    return HealthResponse(
        status="healthy", service="Cognizance AI Assistant", version="1.0.0"
    )
