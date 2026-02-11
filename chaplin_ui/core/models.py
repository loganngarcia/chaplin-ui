"""
Shared data models for Chaplin-UI.

This module defines Pydantic models used across the application for
type safety and validation.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChaplinOutput(BaseModel):
    """Output model for LLM-corrected transcription text.
    
    Attributes:
        list_of_changes: Description of changes made during correction.
        corrected_text: The final corrected and formatted text.
    """
    
    list_of_changes: str = Field(
        default="",
        description="Description of changes made during LLM correction"
    )
    corrected_text: str = Field(
        ...,
        description="The corrected and properly formatted transcription text"
    )
    
    class Config:
        """Pydantic configuration."""
        frozen = True  # Immutable after creation
        json_schema_extra = {
            "example": {
                "list_of_changes": "Converted ALL CAPS to sentence case, added punctuation",
                "corrected_text": "Hello world. How are you?"
            }
        }
