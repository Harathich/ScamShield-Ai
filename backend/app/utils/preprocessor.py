"""
Content Preprocessor & Input Normalizer for ScamShield AI.

Takes messy, unstructured, or obfuscated input and converts it into
a standardized NormalizedContent object.

Capabilities:
1. Flexible payload normalization (handles various key names or raw text)
2. Noise stripping (WhatsApp timestamps, forwarded message prefixes, email headers)
3. Zero-width character & obfuscation removal
4. Automatic entity extraction (URLs, email addresses, phone numbers)
5. Format detection (email, chat_message, url_only, plain_text)
"""

import re
from typing import List, Optional
from pydantic import BaseModel, Field


class NormalizedContent(BaseModel):
    """Standardized representation of user-submitted content."""
    clean_text: str
    raw_text: str
    extracted_urls: List[str] = Field(default_factory=list)
    extracted_emails: List[str] = Field(default_factory=list)
    extracted_phones: List[str] = Field(default_factory=list)
    detected_format: str = "plain_text"  # email | chat_message | url_only | plain_text


class ContentPreprocessor:
    """Cleans and extracts entities from unstructured digital communications."""

    # Regex patterns for entity extraction
    URL_REGEX = re.compile(
        r'(?:https?://|www\.)[a-zA-Z0-9.\-_~:/?#[\]@!$&\'()*+,;=%]+',
        re.IGNORECASE
    )
    EMAIL_REGEX = re.compile(
        r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
        re.IGNORECASE
    )
    PHONE_REGEX = re.compile(
        r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,13}'
    )

    # Patterns for chat and email noise
    WHATSAPP_TIMESTAMP_REGEX = re.compile(
        r'\[?\d{1,2}[/-]\d{1,2}[/-]\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:[APap][Mm])?\]?\s*(?:-\s*)?[^:]*:\s*'
    )
    FORWARDED_LABEL_REGEX = re.compile(
        r'\[?Forwarded(?:\s+message)?\]?\s*:?',
        re.IGNORECASE
    )

    @classmethod
    def process(cls, raw_input: str, explicit_url: Optional[str] = None) -> NormalizedContent:
        """
        Main entry point: cleans input text and extracts all entities.
        """
        if not raw_input:
            raw_input = ""

        raw_text = str(raw_input)

        # 1. Strip zero-width spaces and invisible formatting characters
        cleaned = re.sub(r'[\u200B-\u200D\uFEFF\u200E\u200F]', '', raw_text)

        # 2. Strip chat / messaging metadata
        cleaned = cls.WHATSAPP_TIMESTAMP_REGEX.sub('', cleaned)
        cleaned = cls.FORWARDED_LABEL_REGEX.sub('', cleaned)

        # 3. Collapse multiple whitespace and newlines
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned).strip()

        # 4. Extract Entities
        extracted_urls = cls.URL_REGEX.findall(raw_text)
        # Normalize extracted URLs
        formatted_urls = []
        for u in extracted_urls:
            u_clean = u.rstrip('.,;!?:')
            if not u_clean.startswith(('http://', 'https://')):
                u_clean = 'https://' + u_clean
            if u_clean not in formatted_urls:
                formatted_urls.append(u_clean)

        # Add explicit URL if provided and not already present
        if explicit_url:
            exp = explicit_url.strip()
            if not exp.startswith(('http://', 'https://')):
                exp = 'https://' + exp
            if exp not in formatted_urls:
                formatted_urls.insert(0, exp)

        extracted_emails = list(dict.fromkeys(cls.EMAIL_REGEX.findall(raw_text)))
        extracted_phones = list(dict.fromkeys(cls.PHONE_REGEX.findall(raw_text)))

        # 5. Format Detection
        if re.search(r'^(?:From:|Subject:|To:|Date:)', raw_text, re.MULTILINE | re.IGNORECASE):
            detected_format = "email"
        elif cls.WHATSAPP_TIMESTAMP_REGEX.search(raw_text) or cls.FORWARDED_LABEL_REGEX.search(raw_text):
            detected_format = "chat_message"
        elif len(formatted_urls) == 1 and len(cleaned.split()) <= 2:
            detected_format = "url_only"
        else:
            detected_format = "plain_text"

        return NormalizedContent(
            clean_text=cleaned if cleaned else raw_text,
            raw_text=raw_text,
            extracted_urls=formatted_urls,
            extracted_emails=extracted_emails,
            extracted_phones=extracted_phones,
            detected_format=detected_format
        )
