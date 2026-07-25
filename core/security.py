import re

class PIIMasker:
    """Enterprise-grade local PII & PCI Data Masking guardrail."""
    
    # Regex patterns for Sensitive Data (PII / PCI)
    PATTERNS = {
        "SSN": (r"\b\d{3}-\d{2}-\d{4}\b", "[MASKED_SSN]"),
        "POLICY_NUMBER": (r"\bPOL-\d{6,8}\b", "[MASKED_POLICY_ID]"),
        "CREDIT_CARD": (r"\b(?:\d[ -]*?){13,16}\b", "[MASKED_CARD_NUMBER]"),
        "EMAIL": (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[MASKED_EMAIL]"),
        "PHONE": (r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b", "[MASKED_PHONE]"),
        "DOB": (r"\b(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(19|20)\d{2}\b", "[MASKED_DOB]")
    }

    @classmethod
    def sanitize(cls, text: str) -> str:
        """Masks all sensitive data patterns in text before sending payload to LLM."""
        sanitized = text
        for label, (pattern, replacement) in cls.PATTERNS.items():
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

if __name__ == "__main__":
    sample = "Customer John Doe (SSN: 123-45-6789, Policy POL-987654) email user@fg.com called regarding card 4111-2222-3333-4444."
    masked = PIIMasker.sanitize(sample)
    print("Original:", sample)
    print("Sanitized:", masked)
