from enum import Enum


class SolutionTypes(Enum):
    NOT_SOLVED = 'not solved'
    CORRECT_SOLUTION = 'correct solution'
    INCORRECT_SOLUTION = 'incorrect solution'
    ERROR = 'error in code'


class TestFields(Enum):
    INPUT = 'input'
    OUTPUT = 'output'
