import importlib.util
import json
import os

from typing import Any
from datetime import datetime
from types import ModuleType

from test_system.common.enumerations import (
    SolutionTypes as st,
    TestFields as tf,
    SolutionInfoFields as sif,
    TestCaseInfo as tci,
    AnswerFields as af,
)


class Tester:
    _path_to_reports: str

    def __init__(self, path_to_report: str = "") -> None:
        if path_to_report:
            self._path_to_reports = str(path_to_report)

        else:
            self._path_to_reports = os.path.join('.', 'reports')

        if not os.path.exists(self._path_to_reports):
            os.makedirs(self._path_to_reports)

    def get_report(
        self, path_to_answers: str, testcases: dict[str, list[Any]]
    ) -> None:
        if not os.path.exists(path_to_answers):
            raise RuntimeError(
                f'path to answers: {path_to_answers} doesn\'t exist'
            )

        if not isinstance(testcases, dict):
            raise RuntimeError(
                f'invalid testcases type: {type(testcases).__name__}; '
                'dict type was expected; '
            )

        report_id = self._get_report_id()
        path_to_report = os.path.join(
            self._path_to_reports, f'{report_id}.json'
        )

        reports = self._get_reports(path_to_answers, testcases)

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

            spec = importlib.util.spec_from_file_location(answer_name, path)
            answer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(answer)

            report = self._get_answer_report(path, answer, testcases)
            reports.append(report)

        return reports

    def _get_answer_report(
        self, path_to_answer: str, answer: ModuleType,
        testcases: dict[str, list[Any]]
    ) -> dict[str, Any]:
        report = {
            af.ANSWER_FILE.value: path_to_answer,
            af.TESTS_INFO.value: []
        }

        for task_name in testcases:
            solution_info = self._get_solution_info(
                task_name, answer, testcases[task_name]
            )
            report[af.TESTS_INFO.value].append(solution_info)

        return report

    def _get_solution_info(
        self, task_name: str, answer: ModuleType,
        testcases: list[Any]
    ) -> dict[str, Any]:
        solution = answer.__dict__.get(task_name)
        info = {
            sif.TASK_NAME.value: task_name,
            sif.SOLUTION_TYPE.value: st.NOT_SOLVED.value
        }

        if not solution:
            return info

        for i, test in enumerate(testcases, start=1):
            output = solution(*test[tf.INPUT.value])

            if output == test[tf.OUTPUT.value]:
                info.setdefault(sif.TEST_PASSED.value, []).append(i)

            else:
                info.setdefault(sif.TEST_FAILED.value, []).append(i)

            info.setdefault(sif.TEST_CASES_INFO.value, []).append({
                tci.TEST_ID.value: i,
                tci.INPUT.value: ', '.join(map(str, test[tf.INPUT.value])),
                tci.OUTPUT.value: str(output),
                tci.EXPECTED.value: str(test[tf.OUTPUT.value])
            })

        success_factor = len(info[sif.TEST_PASSED.value]) / len(testcases)
        info[sif.SUCCESS_FACTOR.value] = success_factor

        if success_factor == 1:
            info[sif.SOLUTION_TYPE.value] = st.CORRECT_SOLUTION.value

        else:
            info[sif.SOLUTION_TYPE.value] = st.INCORRECT_SOLUTION.value

        return info

    @staticmethod
    def _get_report_id() -> str:
        date_now = datetime.now()
        report_id = (
            f"{date_now.year}{date_now.month}{date_now.day}"
            f"{date_now.hour}{date_now.minute}{date_now.second}"
            f"{date_now.microsecond}"
        )

        return report_id
