import importlib.util
import contextlib
import json
import sys
import os

from typing import Any
from datetime import datetime
from types import ModuleType

from test_system.common.log import EventLogger

from test_system.common.enumerations import (
    SolutionTypes as st,
    TestFields as tf
)
from test_system.common.models import (
    TestCaseInfo,
    TaskSolutionInfo,
    SolutionInfo,
)


class Tester:
    _path_to_reports: str
    _logger: EventLogger

    def __init__(self, path_to_report: str = '') -> None:
        self._logger = EventLogger()

        if path_to_report:
            self._path_to_reports = str(path_to_report)

        else:
            self._path_to_reports = os.path.join('.', 'reports')
        
        self._logger.info(
            f'use next folder for report saving: {self._path_to_reports}'
        )

        if not os.path.exists(self._path_to_reports):
            os.makedirs(self._path_to_reports)

    def get_report(
        self, path_to_answers: str, testcases: dict[str, list[Any]]
    ) -> None:
        if not os.path.exists(path_to_answers):
            error_msg = (
                f'path to answers: {path_to_answers}'
                'doesn\'t exist'
            )

            self._logger.error(error_msg)
            raise RuntimeError(error_msg)

        if not isinstance(testcases, dict):
            error_msg = (
                f'invalid testcases type: {type(testcases).__name__}; '
                'dict type was expected; '
            )

            self._logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        self._logger.info(
            f'use next folder as answers source: {path_to_answers}'
        )

        report_id = self._get_report_id()
        path_to_report = os.path.join(
            self._path_to_reports, f'{report_id}.json'
        )

        self._logger.info('start report assembling')

        reports = self._get_reports(path_to_answers, testcases)

        self._logger.info(f'save report into: {path_to_report}')
        with open(path_to_report, 'w') as file:
            json.dump(reports, file, indent=4)

    def _get_reports(
        self, path_to_answers: str, testcases: dict[str, list[Any]]
    ) -> list[dict]:
        extension = '.py'

        pathes = [
            os.path.abspath(os.path.join(path_to_answers, filename))
            for filename in os.listdir(path_to_answers)
            if os.path.splitext(filename)[-1] == extension
        ]
        reports = []

        for path in pathes:
            answer_name = os.path.split(path)[-1].replace(extension, '')

            with self._silence_mode():
                spec = importlib.util.spec_from_file_location(answer_name, path)
                answer = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(answer)

            report = self._get_solution_info(path, answer, testcases)
            reports.append(report.model_dump(exclude_none=True))

        return reports

    def _get_solution_info(
        self, path_to_answer: str, answer: ModuleType,
        testcases: dict[str, list[Any]]
    ) -> SolutionInfo:
        self._logger.info(f'get info for {os.path.split(path_to_answer)[-1]}')
        solutions_info = []

        for task_name in testcases:
            solution_info = self._get_task_solution_info(
                task_name, answer, testcases[task_name]
            )
            solutions_info.append(solution_info)

        return SolutionInfo(
            tested_file=os.path.split(path_to_answer)[-1],
            solutions_info=solutions_info
        )

    def _get_task_solution_info(
        self, task_name: str, answer: ModuleType,
        testcases: list[Any]
    ) -> TaskSolutionInfo:
        solution = answer.__dict__.get(task_name)
        solution_type = st.NOT_SOLVED.value
        progress = 0

        if not solution:
            self._logger.warning(
                f'there is no solution for task {task_name}'
            )

            return TaskSolutionInfo(
                task_name=task_name,
                progress=progress,
                solution_type=solution_type
            )
        
        tests_passed, tests_failed = None, None
        tests_info = None

        for i, test in enumerate(testcases, start=1):
            try:
                with self._silence_mode():
                    output = solution(*test[tf.INPUT.value])

            except:
                self._logger.warning(
                    f'exception in solution for {task_name}'
                )
                solution_type = st.ERROR.value
                break

            if output == test[tf.OUTPUT.value]:
                tests_passed = [] if not tests_passed else tests_passed
                tests_passed.append(i)

            else:
                tests_failed = [] if not tests_failed else tests_failed
                tests_info = [] if not tests_info else tests_info

                tests_failed.append(i)
                tests_info.append(
                    TestCaseInfo(
                        test_id=i,
                        input=', '.join(map(str, test[tf.INPUT.value])),
                        output=str(output),
                        expected=str(test[tf.OUTPUT.value])
                    )
                )

        if tests_failed:
            solution_type = st.INCORRECT_SOLUTION.value

        if tests_passed:
            progress = round(len(tests_passed) / len(testcases), 2)

        if progress == 1:
            solution_type = st.CORRECT_SOLUTION.value

        return TaskSolutionInfo(
            task_name=task_name,
            progress=progress,
            solution_type=solution_type,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            tests_info=tests_info
        )
    
    @contextlib.contextmanager
    def _silence_mode(self):
        stdout, sys.stdout = sys.stdout, None

        try:
            yield

        finally:
            sys.stdout = stdout

    @staticmethod
    def _get_report_id() -> str:
        date_now = datetime.now()
        report_id = (
            f"{date_now.year}{date_now.month}{date_now.day}"
            f"{date_now.hour}{date_now.minute}{date_now.second}"
            f"{date_now.microsecond}"
        )

        return report_id
