from typing import Optional

from pydantic import BaseModel, Field

from test_system.common.enumerations import SolutionTypes


class TestCaseInfo(BaseModel):
    test_id: int = Field(gt=0)
    input: str
    output: str
    expected: str


class TaskSolutionInfo(BaseModel):
    task_name: str
    progress: float = Field(ge=0, le=1)
    solution_type: str = SolutionTypes.NOT_SOLVED.value
    tests_passed: Optional[list[int]] = None
    tests_failed: Optional[list[int]] = None
    tests_info: Optional[list[TestCaseInfo]] = None


class SolutionInfo(BaseModel):
    tested_file: str
    solutions_info: list[TaskSolutionInfo]
