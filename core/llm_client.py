import os
import json
import re

class LLMClient:
    """Unified LLM Client supporting Google Gemini API & local offline SDET fallback."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
    def generate_json(self, prompt: str, schema_class=None) -> dict:
        """Executes LLM request and enforces clean JSON response."""
        if self.api_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                text = response.text
                return self._clean_and_parse_json(text)
            except Exception as e:
                print(f"[LLM WARNING] Gemini API call failed ({e}). Falling back to local AI engine.")
                
        # Local offline deterministic fallback
        return self._offline_generator(prompt)

    def _clean_and_parse_json(self, text: str) -> dict:
        clean_text = re.sub(r"```json\s*", "", text)
        clean_text = re.sub(r"```\s*", "", clean_text).strip()
        match = re.search(r"\{.*\}", clean_text, re.DOTALL)
        if match:
            clean_text = match.group(0)
        return json.loads(clean_text)

    def _offline_generator(self, prompt: str) -> dict:
        """Deterministic local SDET engine for test case generation & self-healing."""
        if "SELF_HEALING" in prompt or "FAILED SELECTOR" in prompt or "TimeoutError" in prompt:
            # Analyze failed selector from prompt
            failed = "#calc-submit-btn-legacy"
            if "[FAILED SELECTOR]:" in prompt:
                failed_match = re.search(r"\[FAILED SELECTOR\]:\s*([^\n]+)", prompt)
                if failed_match:
                    failed = failed_match.group(1).strip()
            
            # Infer robust alternative from DOM snippet if present
            new_selector = "[data-testid='calculate-policy-btn']"
            if "id=\"calc-submit-v2\"" in prompt:
                new_selector = "#calc-submit-v2"
            elif "data-testid" in prompt:
                new_selector = "[data-testid='calculate-policy-btn']"

            return {
                "test_id": "TC-INS-101-01",
                "failing_selector": failed,
                "suggested_selector": new_selector,
                "confidence_score": 0.98,
                "reasoning": f"DOM structure updated selector from legacy ID '{failed}' to modern semantic attribute '{new_selector}'.",
                "patched_code_snippet": f"await page.locator('{new_selector}').click();"
            }
        else:
            # Test Case Generation fallback
            story_id = "US-INS-101"
            if "US-INS-102" in prompt or "US-FG-102" in prompt:
                story_id = "US-INS-102"
                return {
                    "id": "TC-INS-102-01",
                    "story_id": story_id,
                    "title": "Validate Annuity Policy Issuance Eligibility & Underwriting Rules",
                    "description": "Verify applicant age, state licensing, and suitability score automated approval status.",
                    "priority": "P0_CRITICAL",
                    "test_type": "UI_FUNCTIONAL",
                    "steps": [
                        {"step_number": 1, "action": "fill", "selector": "#applicant-age", "input_data": "45", "expected_behavior": "Age set to 45"},
                        {"step_number": 2, "action": "select", "selector": "#applicant-state", "input_data": "IA", "expected_behavior": "State selected as IA"},
                        {"step_number": 3, "action": "fill", "selector": "#suitability-score", "input_data": "85", "expected_behavior": "Score set to 85"},
                        {"step_number": 4, "action": "click", "selector": "[data-testid='submit-eligibility']", "input_data": None, "expected_behavior": "Evaluation triggered"}
                    ],
                    "assertions": [
                        {"target_element": "#status-badge", "operator": "equals", "expected_value": "APPROVED"}
                    ]
                }

            return {
                "id": "TC-INS-101-01",
                "story_id": story_id,
                "title": "Validate Fixed Index Annuity Base Premium & GLWB Rider Calculation",
                "description": "Calculate Year 1 accumulation value with 5% GLWB bonus for initial premium >= $10,000.",
                "priority": "P0_CRITICAL",
                "test_type": "UI_FUNCTIONAL",
                "steps": [
                    {"step_number": 1, "action": "fill", "selector": "#premium-amount", "input_data": "15000", "expected_behavior": "Premium set to 15000"},
                    {"step_number": 2, "action": "fill", "selector": "#applicant-age", "input_data": "55", "expected_behavior": "Age set to 55"},
                    {"step_number": 3, "action": "select", "selector": "#rider-type", "input_data": "GLWB_PLUS", "expected_behavior": "Rider set to GLWB_PLUS"},
                    {"step_number": 4, "action": "click", "selector": "[data-testid='calculate-policy-btn']", "input_data": None, "expected_behavior": "Calculate quote"}
                ],
                "assertions": [
                    {"target_element": "#tier-bonus-result", "operator": "contains", "expected_value": "5%"},
                    {"target_element": "#rider-fee-result", "operator": "contains", "expected_value": "$142.50"},
                    {"target_element": "#accum-value-result", "operator": "contains", "expected_value": "$16,282.50"}
                ]
            }
