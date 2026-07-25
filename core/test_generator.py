import os
import sys
import json
import importlib.util
from pydantic import ValidationError

# Fix python path & Windows console UTF-8 output
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)
sys.stdout.reconfigure(encoding='utf-8')

# Dynamic import of vector-db/retriever.py due to hyphenated folder name
retriever_path = os.path.join(ROOT_DIR, "vector-db", "retriever.py")
spec = importlib.util.spec_from_file_location("retriever", retriever_path)
retriever = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retriever)
get_relevant_stories = retriever.get_relevant_stories

from core.security import PIIMasker
from core.prompts import TEST_GENERATOR_PROMPT_V1
from core.llm_client import LLMClient
from core.schemas import TestCase, TestSuite

DATA_OUTPUT = os.path.join(ROOT_DIR, "tests", "data", "generated_tests.json")
SPEC_OUTPUT = os.path.join(ROOT_DIR, "tests", "e2e", "policy_config.spec.ts")

def generate_test_cases():
    """Generates Pydantic-validated test cases from ChromaDB Jira user stories."""
    print("[AI ORCHESTRATOR] Fetching requirements from ChromaDB...")
    retrieved_stories = get_relevant_stories("annuity premium rider calculation policy issuance", n_results=2)
    
    llm = LLMClient()
    validated_cases = []

    for item in retrieved_stories:
        raw_doc = item["document"]
        story_id = item["id"]
        
        # 1. Sanitize text for PII
        sanitized_doc = PIIMasker.sanitize(raw_doc)
        
        # 2. Format Prompt
        prompt = TEST_GENERATOR_PROMPT_V1.format(
            user_story_text=sanitized_doc,
            story_id=story_id
        )
        
        # 3. Call LLM & Validate against Pydantic Schema
        print(f"[AI ORCHESTRATOR] Generating & validating test contract for {story_id}...")
        raw_json = llm.generate_json(prompt)
        
        try:
            test_case = TestCase.model_validate(raw_json)
            validated_cases.append(test_case.model_dump())
            print(f"  [VALIDATED] {test_case.id}: {test_case.title}")
        except ValidationError as val_err:
            print(f"  [SCHEMA ERROR] Validation failed for {story_id}: {val_err}")

    # Build full TestSuite
    suite = TestSuite(test_cases=[TestCase.model_validate(tc) for tc in validated_cases])
    
    # Save JSON contract
    os.makedirs(os.path.dirname(DATA_OUTPUT), exist_ok=True)
    with open(DATA_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(suite.model_dump(), f, indent=2)
        
    print(f"[SUCCESS] Saved validated test matrix to {DATA_OUTPUT}")
    
    # Generate Playwright TS Spec file
    generate_playwright_spec(suite)
    return suite

def _format_str(val: str) -> str:
    """Escapes string quotes for TypeScript literal code."""
    return json.dumps(val)

def generate_playwright_spec(suite: TestSuite):
    """Compiles Pydantic TestSuite into clean Playwright TypeScript spec code."""
    ts_code = """import { test, expect } from '@playwright/test';
import path from 'path';

const APP_URL = `file://${path.resolve(__dirname, 'app/fg_policy_portal.html')}`;

test.describe('F&G Policy & Annuity Core Automation Suite', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
  });
"""

    for tc in suite.test_cases:
        ts_code += f"\n  test('{tc.id}: {tc.title}', async ({{ page }}) => {{\n"
        for step in tc.steps:
            ts_code += f"    // Step {step.step_number}: {step.action} on {step.selector}\n"
            sel = _format_str(step.selector) if step.selector else '""'
            inp = _format_str(step.input_data) if step.input_data else '""'
            
            if step.action == "fill" and step.selector:
                ts_code += f"    await page.locator({sel}).fill({inp});\n"
            elif step.action == "select" and step.selector:
                ts_code += f"    await page.locator({sel}).selectOption({inp});\n"
            elif step.action == "click" and step.selector:
                ts_code += f"    await page.locator({sel}).click();\n"
                
        for assertion in tc.assertions:
            target = _format_str(assertion.target_element)
            exp_val = _format_str(assertion.expected_value)
            if assertion.operator == "contains":
                ts_code += f"    await expect(page.locator({target})).toContainText({exp_val});\n"
            elif assertion.operator == "equals":
                ts_code += f"    await expect(page.locator({target})).toHaveText({exp_val});\n"
            elif assertion.operator == "is_visible":
                ts_code += f"    await expect(page.locator({target})).toBeVisible();\n"
                
        ts_code += "  });\n"

    ts_code += "});\n"

    os.makedirs(os.path.dirname(SPEC_OUTPUT), exist_ok=True)
    with open(SPEC_OUTPUT, "w", encoding="utf-8") as f:
        f.write(ts_code)
        
    print(f"[SUCCESS] Playwright TypeScript spec generated at {SPEC_OUTPUT}")

if __name__ == "__main__":
    generate_test_cases()
