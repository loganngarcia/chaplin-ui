"""
LLM client wrapper for Chaplin-UI.

This module provides a unified interface for interacting with LLM services
(LM Studio, OpenAI-compatible APIs) for text correction and formatting.
"""

import logging
from typing import Optional
from openai import AsyncOpenAI

from chaplin_ui.core.models import ChaplinOutput
from chaplin_ui.core.constants import (
    LLM_DEFAULT_BASE_URL,
    LLM_DEFAULT_MODEL,
    LLM_FALLBACK_MODEL,
    LLM_API_KEY,
    LLM_TEMPERATURE,
    CHAPLIN_OUTPUT_SCHEMA,
)
from chaplin_ui.core.text_formatter import format_text_locally

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with LLM services for text correction.
    
    This class wraps the OpenAI-compatible API client and provides
    methods for correcting VSR transcription output.
    
    Attributes:
        client: AsyncOpenAI client instance.
        model: Current model name being used.
        base_url: Base URL for the LLM API.
    """
    
    def __init__(
        self,
        base_url: str = LLM_DEFAULT_BASE_URL,
        model: str = LLM_DEFAULT_MODEL,
        api_key: str = LLM_API_KEY,
    ):
        """Initialize LLM client.
        
        Args:
            base_url: Base URL for the LLM API endpoint.
            model: Model name to use (defaults to "local" for LM Studio).
            api_key: API key (not required for LM Studio).
        """
        self.base_url = base_url
        self.model = model
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        logger.info(f"Initialized LLM client: {base_url}, model: {model}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for LLM text correction.
        
        Returns:
            System prompt string describing the correction task.
        """
        return (
            "You are an assistant that corrects and formats text from a lipreading model. "
            "The input text will be in ALL CAPS and may have errors.\n\n"
            "Your tasks:\n"
            "1. Convert ALL CAPS to proper sentence case (first letter capitalized, rest lowercase)\n"
            "2. Fix any obvious transcription errors\n"
            "3. Add proper punctuation:\n"
            "   - Add periods (.) at the end of sentences\n"
            "   - Add commas (,) where natural pauses occur\n"
            "   - Add question marks (?) for questions\n"
            "   - Add exclamation marks (!) for exclamations\n"
            "4. Capitalize the first letter of each sentence\n"
            "5. Keep proper nouns capitalized (names, places, etc.)\n\n"
            "Example:\n"
            "Input: 'I LOVE YOU I LOVE YOU'\n"
            "Output: 'I love you. I love you.'\n\n"
            "Do NOT keep text in all caps. Always convert to proper sentence case.\n"
            "Return the corrected text as JSON with 'list_of_changes' and 'corrected_text' keys."
        )
    
    async def correct_text(
        self,
        raw_text: str,
        use_fallback_model: bool = True,
    ) -> ChaplinOutput:
        """Correct and format raw VSR transcription text.
        
        Args:
            raw_text: Raw transcription text from VSR model (typically ALL CAPS).
            use_fallback_model: Whether to try fallback model if primary fails.
            
        Returns:
            ChaplinOutput with corrected text and change description.
            
        Raises:
            Exception: If LLM correction fails and no fallback is available.
        """
        system_prompt = self._get_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Transcription:\n\n{raw_text}"},
        ]
        
        # Try primary model first
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format=CHAPLIN_OUTPUT_SCHEMA,
                temperature=LLM_TEMPERATURE,
            )
            content = response.choices[0].message.content
            return ChaplinOutput.model_validate_json(content)
            
        except Exception as e:
            logger.warning(f"Primary model '{self.model}' failed: {e}")
            
            # Try fallback model if enabled
            if use_fallback_model and self.model != LLM_FALLBACK_MODEL:
                try:
                    logger.info(f"Attempting fallback model: {LLM_FALLBACK_MODEL}")
                    response = await self.client.chat.completions.create(
                        model=LLM_FALLBACK_MODEL,
                        messages=messages,
                        response_format=CHAPLIN_OUTPUT_SCHEMA,
                        temperature=LLM_TEMPERATURE,
                    )
                    content = response.choices[0].message.content
                    return ChaplinOutput.model_validate_json(content)
                except Exception as fallback_error:
                    logger.error(f"Fallback model also failed: {fallback_error}")
            
            # Try plain text response (no structured output)
            try:
                simple_prompt = (
                    "Convert this ALL CAPS text to proper sentence case with "
                    "periods and commas. Output only the corrected text, nothing else:\n\n"
                )
                response = await self.client.chat.completions.create(
                    model=self.model if self.model != LLM_DEFAULT_MODEL else LLM_FALLBACK_MODEL,
                    messages=[{"role": "user", "content": simple_prompt + raw_text}],
                    temperature=LLM_TEMPERATURE,
                )
                content = response.choices[0].message.content.strip()
                return ChaplinOutput(
                    list_of_changes="",
                    corrected_text=content,
                )
            except Exception as plain_error:
                logger.error(f"Plain text correction also failed: {plain_error}")
                # Final fallback: use local formatting
                logger.info("Using local text formatting as final fallback")
                return ChaplinOutput(
                    list_of_changes="",
                    corrected_text=format_text_locally(raw_text),
                )
    
    async def correct_text_simple(self, raw_text: str) -> str:
        """Correct text and return only the corrected string.
        
        Convenience method that returns just the corrected text string
        instead of the full ChaplinOutput model.
        
        Args:
            raw_text: Raw transcription text from VSR model.
            
        Returns:
            Corrected and formatted text string.
        """
        output = await self.correct_text(raw_text)
        corrected = output.corrected_text.strip()
        
        # Ensure proper formatting
        if (corrected.isupper() and len(corrected) > 1) or not any(
            c in corrected for c in '.!?'
        ):
            corrected = format_text_locally(corrected)
        
        # Ensure sentence ending
        if corrected and corrected[-1] not in ['.', '?', '!']:
            corrected += '.'
        
        return corrected


def create_llm_client(
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> LLMClient:
    """Factory function to create an LLM client with defaults.
    
    Args:
        base_url: Optional base URL override.
        model: Optional model name override.
        
    Returns:
        Configured LLMClient instance.
    """
    return LLMClient(
        base_url=base_url or LLM_DEFAULT_BASE_URL,
        model=model or LLM_DEFAULT_MODEL,
    )
