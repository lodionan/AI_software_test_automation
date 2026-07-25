from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class TestCaseStep(BaseModel):
    step_number: int = Field(..., description="1-based index of the test step")
    action: str = Field(..., description="Action to perform (e.g. click, fill, select, assert)")
    selector: Optional[str] = Field(None, description="CSS or ARIA selector for UI element")
    input_data: Optional[str] = Field(None, description="Value or data to enter")
    expected_behavior: str = Field(..., description="Expected visual or state outcome of the step")

class AssertionRule(BaseModel):
    target_element: str = Field(..., description="Element or response property to evaluate")
    operator: Literal["equals", "contains", "greater_than_or_equal", "is_visible", "is_disabled"] = Field(...)
    expected_value: str = Field(..., description="Target value for assertion match")

class TestCase(BaseModel):
    id: str = Field(..., description="Unique Test Case Identifier e.g. TC-INS-101-01")
    story_id: str = Field(..., description="Associated Jira User Story ID")
    title: str = Field(..., description="Descriptive title of test case")
    description: str = Field(..., description="Objective and scope of the test case")
    priority: Literal["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM"] = Field("P1_HIGH")
    test_type: Literal["UI_FUNCTIONAL", "API_CONTRACT", "E2E_INTEGRATION"] = Field("UI_FUNCTIONAL")
    steps: List[TestCaseStep] = Field(..., description="Ordered list of execution steps")
    assertions: List[AssertionRule] = Field(..., description="Validation rules for test pass criteria")

class TestSuite(BaseModel):
    suite_name: str = Field("Enterprise Insurance Core Automation Matrix")
    domain: str = Field("Fixed & Guaranteed Life & Annuities")
    version: str = Field("1.0.0")
    test_cases: List[TestCase] = Field(...)

class SelfHealProposal(BaseModel):
    test_id: str = Field(..., description="Failing Test Case ID")
    failing_selector: str = Field(..., description="Selector that timed out or failed")
    suggested_selector: str = Field(..., description="Robust self-healed selector proposed by AI")
    confidence_score: float = Field(..., description="Confidence score from 0.0 to 1.0")
    reasoning: str = Field(..., description="Analysis of structural DOM change and locator repair strategy")
    patched_code_snippet: str = Field(..., description="Patched Playwright TypeScript code segment")

class GovernancePR(BaseModel):
    branch_name: str = Field(...)
    pr_title: str = Field(...)
    pr_description: str = Field(...)
    commit_message: str = Field(...)
    modified_files: List[str] = Field(...)
    status: Literal["PENDING_HUMAN_APPROVAL", "APPROVED", "REJECTED"] = Field("PENDING_HUMAN_APPROVAL")
