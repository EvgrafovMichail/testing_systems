from enum import Enum


class SolutionTypes(Enum):
    NOT_SOLVED = 'not solved'
    CORRECT_SOLUTION = 'correct solution'
    INCORRECT_SOLUTION = 'incorrect solution'


class TestFields(Enum):
    INPUT = 'input'
    OUTPUT = 'output'


class AnswerFields(Enum):
    ANSWER_FILE = 'answer file'
    TESTS_INFO = 'tests info'


class SolutionInfoFields(Enum):
    TASK_NAME = 'task name'
    SOLUTION_TYPE = 'solution type'
    TEST_PASSED = 'test passed'
    TEST_FAILED = 'test failed'
    SUCCESS_FACTOR = 'success factor'
