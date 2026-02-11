"""
Text formatting utilities for Chaplin-UI.

This module provides functions for formatting raw VSR output text,
including conversion from ALL CAPS to sentence case and punctuation insertion.
"""

import re
from typing import List


# Common clause starters that should be preceded by a period
CLAUSE_STARTERS: List[str] = [
    "do you",
    "did you",
    "can you",
    "would you",
    "could you",
    "will you",
    "do you want",
]


def format_text_locally(text: str) -> str:
    """Convert ALL CAPS text to sentence case with proper punctuation.
    
    This function provides a local fallback for text formatting when LLM
    correction is unavailable. It performs basic sentence case conversion
    and adds punctuation marks.
    
    Args:
        text: Raw text input, typically in ALL CAPS from VSR model.
        
    Returns:
        Formatted text with proper capitalization and punctuation.
        
    Examples:
        >>> format_text_locally("HELLO WORLD")
        'Hello world.'
        
        >>> format_text_locally("I LOVE YOU DO YOU LOVE ME")
        'I love you. Do you love me.'
    """
    if not text or not text.strip():
        return text
    
    # Normalize whitespace and convert to lowercase
    text = text.strip().lower()
    
    # Add periods before common clause starters
    for starter in CLAUSE_STARTERS:
        pattern = r'(\w)\s+' + re.escape(starter)
        text = re.sub(pattern, r'\1. ' + starter, text)
    
    # Split into sentences and capitalize first letter of each
    sentences = [
        s.strip() 
        for s in re.split(r'[.!?]+', text) 
        if s.strip()
    ]
    
    # Capitalize first letter of each sentence
    formatted_sentences = []
    for sentence in sentences:
        if len(sentence) > 1:
            formatted_sentences.append(sentence[0].upper() + sentence[1:])
        else:
            formatted_sentences.append(sentence.upper())
    
    result = '. '.join(formatted_sentences)
    
    # Ensure sentence ends with punctuation
    if result and result[-1] not in '.!?':
        result += '.'
    
    return result
