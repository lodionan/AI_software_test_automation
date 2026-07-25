import os
import sys
import json
import re
import subprocess
from pydantic import ValidationError

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)
sys.stdout.reconfigure(encoding='utf-8')

from core.llm_client import LLMClient
from core.prompts import SELF_HEALING_PROMPT_V1
from core.schemas import SelfHealProposal

SPEC_PATH = os.path.join(ROOT_DIR, "tests", "e2e", "policy_config.spec.ts")
DOM_PATH = os.path.join(ROOT_DIR, "tests", "e2e", "app", "policy_portal.html")

class SelfHealingEngine:
    """Autonomous Self-Healing Agent for Playwright Test Failures."""

    def __init__(self):
        self.llm = LLMClient()

    def simulate_failure_and_heal(self, force_drift: bool = True):
        """Simulates a selector drift failure, catches timeout, triggers AI repair, patches test file, and re-executes."""
        print("\n========================================================")
        print("🤖 [PHASE 5: AI SELF-HEALING RECOVERY DEMO]")
        print("========================================================")
        
        # 1. Introduce broken selector into test spec file
        failing_selector = "#calc-submit-btn-legacy"
        print(f"⚠️  [FAULT INJECTION] Modifying locator in spec to legacy selector: '{failing_selector}'")
        
        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            spec_content = f.read()
            
        # Replace valid selector with broken selector
        broken_spec = re.sub(
            r"page\.locator\(\"\[data-testid='calculate-policy-btn'\]\"\)",
            f'page.locator("{failing_selector}")',
            spec_content
        )
        
        with open(SPEC_PATH, "w", encoding="utf-8") as f:
            f.write(broken_spec)

        # 2. Run Playwright & catch expected failure
        print("🚀 [PLAYWRIGHT RUN 1] Executing test suite with injected failing selector...")
        cmd = "npx playwright test --config tests/e2e/playwright.config.ts"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT_DIR)

        if res.returncode == 0:
            print("❓ Test unexpectedly passed. No healing required.")
            return True

        error_output = res.stderr or res.stdout
        print("\n❌ [TIMEOUT CAUGHT] Playwright Test Failed as expected!")
        print(f"   Log Snippet: Timeout 5000ms exceeded waiting for locator('{failing_selector}')")

        # 3. Read current HTML DOM snippet
        with open(DOM_PATH, "r", encoding="utf-8") as f:
            dom_content = f.read()

        # 4. Construct AI Self-Healing Prompt
        prompt = SELF_HEALING_PROMPT_V1.format(
            failed_selector=failing_selector,
            error_log=error_output[:800],
            dom_html=dom_content[:1500],
            test_id="TC-INS-101-01"
        )

        print("\n🧠 [AI HEALING AGENT] Analyzing DOM structural changes & proposing locator repair...")
        healing_json = self.llm.generate_json(prompt)

        # 5. Pydantic validation of self-heal proposal
        try:
            proposal = SelfHealProposal.model_validate(healing_json)
            print(f"✅ [PROPOSAL VALIDATED] Confidence: {proposal.confidence_score * 100:.1f}%")
            print(f"   Original Selector:  {proposal.failing_selector}")
            print(f"   Suggested Selector: {proposal.suggested_selector}")
            print(f"   Reasoning: {proposal.reasoning}")
        except ValidationError as e:
            print(f"❌ [PROPOSAL SCHEMA ERROR]: {e}")
            return False

        # 6. Apply patch locally
        print(f"\n🩹 [AUTO-PATCHING] Replacing '{failing_selector}' with '{proposal.suggested_selector}' in {SPEC_PATH}...")
        patched_spec = broken_spec.replace(
            f'page.locator("{failing_selector}")',
            f'page.locator({json.dumps(proposal.suggested_selector)})'
        )
        
        with open(SPEC_PATH, "w", encoding="utf-8") as f:
            f.write(patched_spec)

        # 7. Re-run test to verify recovery
        print("\n🚀 [PLAYWRIGHT RUN 2] Re-executing test suite after AI Self-Healing Patch...")
        res2 = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT_DIR)

        if res2.returncode == 0:
            print("\n🎉 [SELF-HEALING SUCCESS] All Playwright E2E tests passed cleanly after self-repair!")
            return proposal
        else:
            print("❌ Re-execution failed after patch.")
            print(res2.stdout or res2.stderr)
            return False

if __name__ == "__main__":
    engine = SelfHealingEngine()
    engine.simulate_failure_and_heal()
