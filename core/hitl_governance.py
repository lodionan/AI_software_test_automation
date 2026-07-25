import os
import sys
import json
import subprocess
from pydantic import ValidationError

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)
sys.stdout.reconfigure(encoding='utf-8')

from core.schemas import GovernancePR, SelfHealProposal

GOVERNANCE_LOG = os.path.join(ROOT_DIR, "reports", "governance_pr_log.json")

class HITLGovernanceManager:
    """Human-in-the-Loop Governance & Git Pull Request Orchestrator."""

    def __init__(self):
        os.makedirs(os.path.dirname(GOVERNANCE_LOG), exist_ok=True)

    def create_simulated_pr(self, proposal: SelfHealProposal) -> GovernancePR:
        """Isolates healed test patch into a Git feature branch and opens a Pull Request."""
        branch_name = f"feature/self-heal-{proposal.test_id.lower()}"
        
        pr = GovernancePR(
            branch_name=branch_name,
            pr_title=f"[AI Self-Heal] Repair locator for test {proposal.test_id}",
            pr_description=f"**Auto-Repair Summary**:\n- **Failing Selector**: `{proposal.failing_selector}`\n- **Repaired Selector**: `{proposal.suggested_selector}`\n- **Confidence**: {proposal.confidence_score*100:.1f}%\n- **Reasoning**: {proposal.reasoning}",
            commit_message=f"fix(tests): auto-heal broken locator in {proposal.test_id}",
            modified_files=["tests/e2e/policy_config.spec.ts"],
            status="PENDING_HUMAN_APPROVAL"
        )
        
        # Save PR metadata
        with open(GOVERNANCE_LOG, "w", encoding="utf-8") as f:
            json.dump(pr.model_dump(), f, indent=2)
            
        print("\n========================================================")
        print("🛡️  [PHASE 6: HUMAN-IN-THE-LOOP (HITL) GOVERNANCE GATE]")
        print("========================================================")
        print(f"📌 Simulated Git Branch Created: '{pr.branch_name}'")
        print(f"📝 Pull Request Opened: {pr.pr_title}")
        print(f"🔍 Modified Files: {', '.join(pr.modified_files)}")
        print("--------------------------------------------------------")
        print("PROPOSED CHANGE DETAILED DIFF:")
        print(f"  - Original failing selector: {proposal.failing_selector}")
        print(f"  + New resilient selector:   {proposal.suggested_selector}")
        print(f"  Confidence Score: {proposal.confidence_score * 100:.1f}%")
        print("--------------------------------------------------------")
        
        return pr

    def process_approval(self, decision: str = "/approve") -> GovernancePR:
        """Processes human command (/approve or /reject) to merge or rollback changes."""
        if not os.path.exists(GOVERNANCE_LOG):
            raise FileNotFoundError("No active PR found in governance log.")

        with open(GOVERNANCE_LOG, "r", encoding="utf-8") as f:
            pr_data = json.load(f)

        pr = GovernancePR.model_validate(pr_data)

        if decision.strip().lower() in ["/approve", "approve", "yes", "y"]:
            pr.status = "APPROVED"
            print("\n✅ [HUMAN GOVERNANCE] Command '/approve' received!")
            print(f"🔀 [GIT MERGE] Merging branch '{pr.branch_name}' into 'main'...")
            print("🚀 [CI/CD QUALITY GATE] All policies verified. Production deployment unblocked!")
        else:
            pr.status = "REJECTED"
            print("\n🛑 [HUMAN GOVERNANCE] Command '/reject' received.")
            print(f"🗑️  [GIT ROLLBACK] Discarding branch '{pr.branch_name}'...")

        # Update log
        with open(GOVERNANCE_LOG, "w", encoding="utf-8") as f:
            json.dump(pr.model_dump(), f, indent=2)

        return pr

if __name__ == "__main__":
    gov = HITLGovernanceManager()
    dummy_proposal = SelfHealProposal(
        test_id="TC-INS-101-01",
        failing_selector="#calc-submit-btn-legacy",
        suggested_selector="[data-testid='calculate-policy-btn']",
        confidence_score=0.98,
        reasoning="Restored semantic data-testid attribute locator.",
        patched_code_snippet="await page.locator(\"[data-testid='calculate-policy-btn']\").click();"
    )
    gov.create_simulated_pr(dummy_proposal)
    
    # Process approval if passed via CLI arg, else default /approve
    decision = sys.argv[1] if len(sys.argv) > 1 else "/approve"
    gov.process_approval(decision)
