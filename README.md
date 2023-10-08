# Система автоматического тестирования

## Как использовать

В данном разделе описан алгоритм использования системы автоматического тестирования

**Шаги:**

- Создаем папку, и помещаем туда все файлы с решениями, которые необходимо проверить; 

    **Важно**:  файлы должны иметь расширение `.py`;

    **Желательно**: поместить все решения одного человека в один файл; в таком случае отчет о тестировании будет удобнее читать; 
- Создаем файл `testcases.py`, содержимое которого должно выглядить следующим образом: 
    ```python
    testcases = {
        "task1": [
            {
                "input": [
                    "arg1_val1", "arg2_val1"
                ],
                "output": "correct result"
            },
            {
                "input": [
                    "arg1_val2", "arg2_val2"
                ],
                "output": "correct result"
            }
        ],
        "task2": [
            {
                "input": [
                    ["list", "of", "args"]
                ],
                "output": "correct result"
            }
        ]
    }
    ```
    **Важно**: testcases - словарь; ключи - имена функций, которые будут тестироваться; значения - список testcase-словарей; testcase словарь состоит из поля `input` - **списка** значений аргументов функции, и из поля `output` - правильного ответа;  

- Получаем **абсолютный** путь до папки с решениями;  
- Создаем скрипт тестирования со следующим содержанием:  
    ```Python
    from test_system.testers.tester import Tester
    from testcases import testcases


    if __name__ == '__main__':
        tester = Tester()
        tester.get_report('path/to/submissions/', testcases)
    ```
- Выполняем скрипт; В дефолтной конфигурации `Tester` создаст папку `reports/` в той же директории, в которой был вызван скрип, и поместит туда отчет - json-файл следующего вида:
    ```json
    [
        {
            "answer file": "/path/to/answer1.py",
            "tests info": [
                {
                    "task name": "task1",
                    "solution type": "correct solution",
                    "test passed": [
                        1,
                        2
                    ],
                    "test cases info": [
                        {
                            "test id": 1,
                            "input": "arg1_val1, arg2_val1",
                            "output": "correct result",
                            "expected": "correct result"
                        },
                        {
                            "test id": 2,
                            "input": "arg1_val2, arg2_val2",
                            "output": "correct result",
                            "expected": "correct result"
                        }
                    ],
                    "success factor": 1.0
                },
                {
                    "task name": "task2",
                    "solution type": "not solved"
                }
            ]
        }
    ]
    ```