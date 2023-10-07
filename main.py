from test_system.testers.tester import Tester


if __name__ == '__main__':
    tester = Tester(task_names=['get_answer'])
    tester.get_report('submissions/', 'testcases.json')
