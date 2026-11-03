# -*- coding: utf-8 -*-
"""Python 3.13 언어 레퍼런스 종합 학습 모듈 앱
실행: streamlit run python_app.py
"""
import contextlib
import io
import json
import os
import re
from pathlib import Path

import streamlit as st

# ==========================================
# 1. Python 3.13 레퍼런스 전체 커리큘럼 데이터
# ==========================================
MODULES = [
    {
        "title": "2. 어휘 분석 (Lexical Analysis)",
        "ref_name": "어휘 분석",
        "ref_url": "https://docs.python.org/ko/3.13/reference/lexical_analysis.html",
        "lessons": [
            {
                "title": "2.1. 줄 구조 (Line structure)",
                "body": "파이썬 소스 코드는 물리적 줄과 논리적 줄로 구성됩니다. 들여쓰기(Indentation)는 공백 4칸을 권장하며 코드 블록을 결정합니다. 역슬래시(\\ )로 물리적 줄을 이어 붙일 수 있습니다.",
                "code": "total = 1 + 2 + \\\n        3 + 4\nprint(total)  # 10",
                "tip": "괄호 `()`, `[]`, `{}` 안에서는 백슬래시 없이도 줄바꿈이 자유롭습니다.",
                "quiz": {
                    "q": "물리적 줄을 논리적 줄 하나로 이어 붙일 때 사용하는 기호는?",
                    "options": ["백슬래시 (\\)", "세미콜론 (;)", "밑줄 (_)"],
                    "answer": 0,
                    "why": "줄 끝에 백슬래시를 쓰면 다음 줄까지 이어집니다."
                }
            },
            {
                "title": "2.2. 다른 토큰들 (Other tokens)",
                "body": "주석(Comment), 연산자, 구분자 등 소스 코드를 이루는 최소 단위인 토큰들을 다룹니다. `#` 기호 뒤의 텍스트는 인터프리터가 무시합니다.",
                "code": "# 이것은 주석입니다.\nx = 10  # 변수 할당 토큰",
                "tip": "코드의 의도를 명확히 하려면 적절한 주석이 필수적입니다.",
                "quiz": {
                    "q": "파이썬에서 주석을 시작할 때 사용하는 기호는?",
                    "options": ["//", "#", "/*"],
                    "answer": 1,
                    "why": "파이썬은 # 이후부터 줄 끝까지를 주석으로 처리합니다."
                }
            },
            {
                "title": "2.3. 식별자와 키워드",
                "body": "변수, 함수, 클래스 등의 이름을 <b>식별자(Identifier)</b>라 합니다. 알파벳, 숫자, 밑줄(_)로 구성되며 숫자로 시작할 수 없습니다. <code>if</code>, <code>for</code> 같은 키워드는 이름으로 쓸 수 없습니다.",
                "code": "my_var = 100\n# 99variable = 1  # 오류 (숫자 시작 불가)\nimport keyword\nprint(keyword.kwlist[:5])  ...",
                "tip": "대소문자를 엄격히 구분하므로 `Var`와 `var`는 다른 이름입니다.",
                "quiz": {
                    "q": "다음 중 올바른 식별자 규칙이 아닌 것은?",
                    "options": ["숫자로 시작할 수 있다", "밑줄(_)을 포함할 수 있다", "대소문자를 구분한다"],
                    "answer": 0,
                    "why": "식별자는 숫자로 시작할 수 없습니다."
                }
            },
            {
                "title": "2.4. 리터럴 (Literals)",
                "body": "코드에 직접 기록된 고정된 값입니다. 정수 리터럴, 부동소수점 리터럴, 문자열 리터럴 등이 있으며, <code>1_000_000</code>처럼 가독성을 위해 언더스코어를 포함할 수 있습니다.",
                "code": "binary = 0b1010\nhex_val = 0xFF\ntext = 'Hello'\nprint(binary, hex_val, text)",
                "tip": "다양한 진법(2진수, 8진수, 16진수) 표현 리터럴을 지원합니다.",
                "quiz": {
                    "q": "숫자 리터럴 사이에 들어가는 밑줄(_)의 용도는?",
                    "options": ["값의 단위를 곱함", "가독성을 높이기 위한 구분자", "음수 표현"],
                    "answer": 1,
                    "why": "밑줄은 값에 영향을 주지 않고 가독성만 높여줍니다."
                }
            },
            {
                "title": "2.5. 연산자 (Operators)",
                "body": "값들을 계산하거나 비교하는 기호들입니다. 산술 연산자(`+`, `-`, `*`, `/`), 비교 연산자(`==`, `<`, `>`), 비트 연산자 등이 포함됩니다.",
                "code": "print(10 + 5)\nprint(10 > 5)\nprint(5 & 3)",
                "tip": "연산자마다 고유한 우선순위 규칙이 존재합니다.",
                "quiz": {
                    "q": "동등 비교를 수행하는 연산자는?",
                    "options": ["=", "==", "==="],
                    "answer": 1,
                    "why": "==는 값이 같은지 비교하는 연산자입니다."
                }
            },
            {
                "title": "2.6. 구분자 (Delimiters)",
                "body": "구문 구조를 나누거나 그룹화하는 기호들입니다. 괄호 `()`, 대괄호 `[]`, 중괄호 `{}`, 쉼표 `,`, 콜론 `:`, 세미콜론 `;` 등이 있습니다.",
                "code": "my_list = [1, 2, 3]\nmy_dict = {'a': 1}",
                "tip": "코드의 블록과 데이터 구조를 정의하는 핵심 뼈대입니다.",
                "quiz": {
                    "q": "딕셔너리를 감싸는 데 사용하는 구분자는?",
                    "options": ["()", "[]", "{}"],
                    "answer": 2,
                    "why": "딕셔너리는 중괄호 {}로 정의합니다."
                }
            }
        ]
    },
    {
        "title": "3. 데이터 모델 (Data Model)",
        "ref_name": "데이터 모델",
        "ref_url": "https://docs.python.org/ko/3.13/reference/datamodel.html",
        "lessons": [
            {
                "title": "3.1. 객체, 값, 형",
                "body": "파이썬의 모든 데이터는 <b>객체(Object)</b>입니다. 모든 객체는 고유한 정체성(Identity, `id()`), 값(Value, `print()`), 그리고 형(Type, `type()`)을 갖습니다.",
                "code": "x = 42\nprint(id(x))\nprint(type(x))",
                "tip": "변수는 객체를 담는 상자가 아니라 객체를 가리키는 이름표입니다.",
                "quiz": {
                    "q": "객체의 고유 정체성(메모리 주소 등)을 확인하는 함수는?",
                    "options": ["type()", "id()", "val()"],
                    "answer": 1,
                    "why": "id() 함수는 객체의 고유한 식별값을 반환합니다."
                }
            },
            {
                "title": "3.2. 표준형 계층 (The standard type hierarchy)",
                "body": "숫자형, 시퀀스형(문자열, 리스트, 튜플), 매핑형(딕셔너리), 집합형, 모듈, 클래스 등 파이썬 내장 타입들의 거대한 계층 구조를 의미합니다.",
                "code": "print(isinstance(10, int))\nprint(isinstance([1, 2], list))",
                "tip": "isinstance()를 통해 객체가 특정 타입 계층에 속하는지 확인할 수 있습니다.",
                "quiz": {
                    "q": "키와 값의 쌍으로 데이터를 관리하는 표준 매핑 타입은?",
                    "options": ["list", "tuple", "dict"],
                    "answer": 2,
                    "why": "딕셔너리(dict)가 대표적인 매핑 타입입니다."
                }
            },
            {
                "title": "3.3. 특수 메서드 이름들 (Dunder methods)",
                "body": "밑줄 두 개로 시작하고 끝나는 메서드(`__init__`, `__str__`, `__len__` 등)로, 파이썬의 내장 연산자나 함수가 사용자 정의 객체와 상호작용하도록 정의합니다.",
                "code": "class Book:\n    def __len__(self):\n    ...         return 100\nb = Book()\nprint(len(b))  # 100",
                "tip": "던더(Dunder) 메서드를 통해 객체 지향 프로그래밍의 연산자 오버로딩을 구현합니다.",
                "quiz": {
                    "q": "객체의 길이를 반환할 때 호출되는 특수 메서드는?",
                    "options": ["__init__", "__len__", "__str__"],
                    "answer": 1,
                    "why": "len() 함수는 내부적으로 __len__ 특수 메서드를 호출합니다."
                }
            },
            {
                "title": "3.4. 코루틴 (Coroutines)",
                "body": "비동기 프로그래밍을 위한 핵심 객체로, 실행을 중단(await)하고 나중에 재개할 수 있는 함수 및 객체 구조입니다. <code>async def</code>로 정의됩니다.",
                "code": "import asyncio\nasync def main():\n    print('Hello')\n# asyncio.run(main())",
                "tip": "I/O bound 작업에서 블로킹을 방지하고 고성능 비동기 처리를 가능하게 합니다.",
                "quiz": {
                    "q": "코루틴 함수를 정의할 때 사용하는 키워드는?",
                    "options": ["async def", "def sync", "routine def"],
                    "answer": 0,
                    "why": "async def로 정의된 함수는 코루틴 객체를 반환합니다."
                }
            }
        ]
    },
    {
        "title": "4. 실행 모델 (Execution Model)",
        "ref_name": "실행 모델",
        "ref_url": "https://docs.python.org/ko/3.13/reference/executionmodel.html",
        "lessons": [
            {
                "title": "4.1. 프로그램의 구조",
                "body": "파이썬 프로그램은 모듈, 클래스, 함수 등 코드 블록들의 중첩 구조로 실행됩니다. 최상위(Top-level) 스크립트 실행 환경을 이해하는 것이 중요합니다.",
                "code": "if __name__ == '__main__':\n    print('직접 실행됨')",
                "tip": "코드 블록은 실행 컨텍스트와 네임스페이스의 단위가 됩니다.",
                "quiz": {
                    "q": "현재 모듈이 직접 실행될 때 __name__에 할당되는 값은?",
                    "options": ["__main__", "root", "script"],
                    "answer": 0,
                    "why": "직접 실행 시 __name__은 '__main__'이 됩니다."
                }
            },
            {
                "title": "4.2. 이름과 연결 (Naming and binding)",
                "body": "이름(변수)이 객체에 바인딩되는 규칙과 스코프(Scope - 지역, 전역, 빌트인)를 다룹니다. 함수 안에서 전역 변수를 수정하려면 <code>global</code> 선언이 필요합니다.",
                "code": "x = 10\ndef modify():\n    global x\n    x = 20\nmodify()\nprint(x)  # 20",
                "tip": "LEGB 규칙(Local -> Enclosing -> Global -> Built-in)에 따라 이름을 탐색합니다.",
                "quiz": {
                    "q": "함수 내부에서 전역 변수의 값을 변경하기 위해 사용하는 키워드는?",
                    "options": ["local", "global", "nonlocal"],
                    "answer": 1,
                    "why": "global 키워드로 전역 변수 바인딩을 명시합니다."
                }
            },
            {
                "title": "4.3. 예외 (Exceptions)",
                "body": "런타임 에러 발생 시 프로그램이 비정상 종료되지 않고 흐름을 제어할 수 있도록 예외 객체가 생성되고 전파(Propagation)되는 메커니즘입니다.",
                "code": "try:\n    1 / 0\nexcept ZeroDivisionError:\n    print('0으로 나눌 수 없음')",
                "tip": "구체적인 예외 클래스를 명시하여 처리하는 것이 안전합니다.",
                "quiz": {
                    "q": "0으로 나누었을 때 발생하는 대표적인 예외 클래스는?",
                    "options": ["ValueError", "ZeroDivisionError", "TypeError"],
                    "answer": 1,
                    "why": "수학적 0 나누기 오류는 ZeroDivisionError입니다."
                }
            },
            {
                "title": "4.4. Runtime Components",
                "body": "파이썬 바이트코드를 실행하는 가상 머신(CPython VM)과 프레임(Frame) 객체 등 프로그램 실행을 뒷받침하는 저수준 런타임 요소들입니다.",
                "code": "import sys\nprint(sys._getframe().f_code.co_name)",
                "tip": "디버깅 도구들이나 내부 프로파일러가 이 런타임 컴포넌트들을 활용합니다.",
                "quiz": {
                    "q": "파이썬 코드가 실행되는 대표적인 표준 인터프리터 구현체는?",
                    "options": ["CPython", "JPython", "IronPython"],
                    "answer": 0,
                    "why": "가장 표준적이고 널리 쓰이는 구현체는 CPython입니다."
                }
            }
        ]
    },
    {
        "title": "5. 임포트 시스템 (The Import System)",
        "ref_name": "임포트 시스템",
        "ref_url": "https://docs.python.org/ko/3.13/reference/import.html",
        "lessons": [
            {
                "title": "5.1. importlib",
                "body": "파이썬의 임포트 시스템을 프로그래밍 방식으로 조작하고 제어할 수 있는 표준 라이브러리 모듈입니다.",
                "code": "import importlib\nmath_mod = importlib.import_module('math')\nprint(math_mod.sqrt(9))",
                "tip": "동적으로 모듈을 로드해야 할 때 매우 유용하게 쓰입니다.",
                "quiz": {
                    "q": "문자열 이름으로 모듈을 동적 임포트할 때 사용하는 표준 라이브러리는?",
                    "options": ["syslib", "importlib", "loadlib"],
                    "answer": 1,
                    "why": "importlib.import_module()을 사용합니다."
                }
            },
            {
                "title": "5.2. 패키지 (Package)",
                "body": "여러 모듈을 디렉토리 구조로 그룹화한 것입니다. __init__.py 파일(또는 네임스페이스 패키지)을 통해 계층적인 모듈 관리를 제공합니다.",
                "code": "# my_package/\n#   __init__.py\n#   module.py",
                "tip": "점(.) 표기법을 사용하여 패키지 내부의 모듈을 임포트합니다.",
                "quiz": {
                    "q": "모듈들을 계층적으로 묶은 디렉토리 구조를 무엇이라 하는가?",
                    "options": ["패키지 (Package)", "클래스 (Class)", "함수 (Function)"],
                    "answer": 0,
                    "why": "모듈들의 집합인 디렉토리를 패키지라 합니다."
                }
            },
            {
                "title": "5.3. 검색 (Searching) & 5.4. 로딩 (Loading)",
                "body": "임포트할 때 파이썬은 먼저 sys.path를 검색(Searching)하여 모듈 위치를 찾고, 발견된 코드를 메모리에 적재 및 초기화하는 로딩(Loading) 단계를 거칩니다.",
                "code": "import sys\nprint(len(sys.path))",
                "tip": "sys.path에 경로를 추가하면 새로운 위치에서도 모듈을 검색할 수 있습니다.",
                "quiz": {
                    "q": "모듈을 찾기 위해 탐색하는 경로 목록이 담긴 곳은?",
                    "options": ["sys.path", "os.path", "env.path"],
                    "answer": 0,
                    "why": "파이썬은 sys.path의 디렉토리들을 차례대로 검색합니다."
                }
            },
            {
                "title": "5.5. 경로 기반 파인더 ~ 5.10. 참고문헌",
                "body": "파이썬의 커스텀 임포트 로직을 구현하는 Path-based finders, 표준 시스템 교체 메커니즘, 패키지 상대 임포트(<code>from . import x</code>), 그리고 <code>__main__</code> 모듈 특수 취급 규칙입니다.",
                "code": "from . import local_module  # 상대 임포트 예시",
                "tip": "패키지 내부 부모/자식 간 상대 참조 시 점(.) 기호를 사용합니다.",
                "quiz": {
                    "q": "현재 패키지 기준 상대 임포트 시 사용하는 기호는?",
                    "options": ["점 (.)", "골뱅이 (@)", "슬래시 (/)"],
                    "answer": 0,
                    "why": "상대 임포트는 . 또는 .. 등의 점 기호를 이용합니다."
                }
            }
        ]
    },
    {
        "title": "6. 표현식 (Expressions)",
        "ref_name": "표현식",
        "ref_url": "https://docs.python.org/ko/3.13/reference/expressions.html",
        "lessons": [
            {
                "title": "6.1. 산술 변환 ~ 6.3. 프라이머리",
                "body": "서로 다른 숫자 타입 간 암시적 형변환(Arithmetic conversions), 가장 기본 단위인 아톰(Atoms), 속성 참조 및 함수 호출 등의 프라이머리(Primaries) 연산입니다.",
                "code": "print(1 + 2.5)  # 3.5 (정수가 실수로 변환)",
                "tip": "데이터 손실이 최소화되는 방향으로 자동 형변환이 일어납니다.",
                "quiz": {
                    "q": "정수와 실수를 더했을 때 결과 타입은?",
                    "options": ["정수 (int)", "실수 (float)", "문자열 (str)"],
                    "answer": 1,
                    "why": "정수와 실수가 연산되면 실수형으로 자동 변환됩니다."
                }
            },
            {
                "title": "6.4. 어웨이트 ~ 6.9. 이항 비트 연산",
                "body": "어웨이트(`await`), 거듭제곱(`**`), 단항/이항 산술 연산, 비트 시프트(`<<`, `>>`), 비트 논리 연산(`&`, `^`, `|`) 등 각종 연산자 식입니다.",
                "code": "print(2 ** 3)     # 8\nprint(8 >> 1)     # 4",
                "tip": "비트 연산자는 정수 단위의 저수준 데이터 조작에 사용됩니다.",
                "quiz": {
                    "q": "거듭제곱을 계산할 때 사용하는 연산자는?",
                    "options": ["^", "**", "//"],
                    "answer": 1,
                    "why": "** 연산자는 거듭제곱을 수행합니다."
                }
            },
            {
                "title": "6.10. 비교 ~ 6.13. 조건 표현식",
                "body": "연쇄 비교(`1 < x < 5`), 논리 연산(`and`, `or`, `not`), 바다코끼리 대입 표현식(`:=`), 삼항 조건 표현식(`A if condition else B`)입니다.",
                "code": "status = 'Adult' if 20 >= 19 else 'Minor'\nprint(status)",
                "tip": "조건 표현식은 값의 선택적 할당에 매우 간결합니다.",
                "quiz": {
                    "q": "값 대입과 평가를 동시에 수행하는 바다코끼리 연산자는?",
                    "options": [":=", "==", "->"],
                    "answer": 0,
                    "why": ":= 대입 표현식(Walrus operator)을 의미합니다."
                }
            },
            {
                "title": "6.14. 람다 ~ 6.17. 연산자 우선순위",
                "body": "익명 함수 람다(Lambdas), 표현식 목록(튜플 생성 등), 표현식 평가 순서(좌측에서 우측), 그리고 <code>**</code>부터 <code>or</code>까지의 연산자 우선순위 표입니다.",
                "code": "f = lambda x: x * 2\nprint(f(5))  # 10",
                "tip": "우선순위가 헷갈릴 때는 괄호 <code>()</code>를 사용해 명시하세요.",
                "quiz": {
                    "q": "이름 없는 한 줄짜리 함수를 만드는 키워드는?",
                    "options": ["def", "lambda", "func"],
                    "answer": 1,
                    "why": "lambda 키워드로 익명 함수를 정의합니다."
                }
            }
        ]
    },
    {
        "title": "7. 단순문 (Simple Statements)",
        "ref_name": "단순문",
        "ref_url": "https://docs.python.org/ko/3.13/reference/simple_stmts.html",
        "lessons": [
            {
                "title": "7.1. 표현식 문 ~ 7.5. del 문",
                "body": "단독으로 실행되는 표현식 문, 대입문(`=`, 복합 대입), 조건 검증용 <code>assert</code>, 빈 문장 <code>pass</code>, 객체 바인딩을 해제하는 <code>del</code> 문입니다.",
                "code": "x = [1, 2, 3]\ndel x[0]\npass",
                "tip": "pass는 문법적으로 문장이필요하지만 실행할 내용이 없을 때 사용합니다.",
                "quiz": {
                    "q": "객체나 변수와의 연결을 끊고 삭제할 때 쓰는 문장은?",
                    "options": ["remove", "del", "clear"],
                    "answer": 1,
                    "why": "del 문을 사용하여 객체 참조를 삭제합니다."
                }
            },
            {
                "title": "7.6. return ~ 7.14. type 문",
                "body": "값 반환 <code>return</code>, 제너레이터 <code>yield</code>, 예외 발생 <code>raise</code>, 반복 제어 <code>break</code>/<code>continue</code>, 모듈 임포트 <code>import</code>, 스코프 확장 <code>global</code>/<code>nonlocal</code>, 그리고 타입 별칭 정의용 <code>type</code> 문입니다.",
                "code": "type Point = tuple[float, float]  # Python 3.12+ 타입 문",
                "tip": "Python 3.12부터 도입된 type 문을 통해 우아하게 타입 별칭을 선언할 수 있습니다.",
                "quiz": {
                    "q": "함수에서 실행을 멈추고 값을 제너레이터 형태로 내보내는 문장은?",
                    "options": ["return", "yield", "emit"],
                    "answer": 1,
                    "why": "yield 문은 제너레이터 함수에서 값을 생성해 반환합니다."
                }
            }
        ]
    },
    {
        "title": "8. 복합문 (Compound Statements)",
        "ref_name": "복합문",
        "ref_url": "https://docs.python.org/ko/3.13/reference/compound_stmts.html",
        "lessons": [
            {
                "title": "8.1. if ~ 8.5. with 문",
                "body": "조건 분기 <code>if</code>, 반복문 <code>while</code>과 <code>for</code>, 예외 처리 블록 <code>try...except...finally</code>, 자원 안전 관리 <code>with</code> 문입니다.",
                "code": "with open('test.txt', 'w', encoding='utf-8') as f:\n    f.write('Hello')",
                "tip": "with 문을 사용하면 파일 등의 자원이 예외 발생 시에도 안전하게 해제됩니다.",
                "quiz": {
                    "q": "컨텍스트 관리자와 함께 쓰여 자원을 자동으로 정리해 주는 문장은?",
                    "options": ["with", "using", "manage"],
                    "answer": 0,
                    "why": "with 문은 블록 진입과 퇴출 시 자원 정리를 보장합니다."
                }
            },
            {
                "title": "8.6. match ~ 8.10. Type parameter lists",
                "body": "구조적 패턴 매칭 <code>match/case</code>, 함수 및 클래스 정의(<code>def</code>, <code>class</code>), 비동기 코루틴, 그리고 제네릭을 위한 타입 매개변수 리스트(Type parameter lists)입니다.",
                "code": "def process(item):\n    match item:\n        case 0:\n            return 'Zero'\n        case _: \n            return 'Other'",
                "tip": "match 문은 다중 조건 분기를 훨씬 직관적이고 가독성 높게 만들어 줍니다.",
                "quiz": {
                    "q": "Python 3.10에 도입된 패턴 매칭 제어 문장은?",
                    "options": ["switch", "match", "select"],
                    "answer": 1,
                    "why": "match 문을 통해 패턴 매칭을 수행합니다."
                }
            }
        ]
    },
    {
        "title": "9. 최상위 요소들 (Top-level Components)",
        "ref_name": "최상위 요소들",
        "ref_url": "https://docs.python.org/ko/3.13/reference/top_level.html",
        "lessons": [
            {
                "title": "9.1. 완전한 프로그램 ~ 9.4. 표현식 입력",
                "body": "독립된 파일 스크립트 형태의 완전한 프로그램, 파일 입력, REPL 대화형 콘솔 입력, 그리고 단일 표현식 입력 모드의 동작 규격입니다.",
                "code": "# 대화형 REPL 환경 및 파일 실행 모드",
                "tip": "파이썬 코드가 실행되는 환경(파일, 인터프리터 콘솔 등)에 따른 차이를 정의합니다.",
                "quiz": {
                    "q": "터미널 등에서 대화형으로 파이썬 코드를 입력받아 실행하는 환경을 뜻하는 용어는?",
                    "options": ["REPL", "Compiler", "Debugger"],
                    "answer": 0,
                    "why": "Read-Eval-Print Loop (REPL) 환경을 의미합니다."
                }
            }
        ]
    },
    {
        "title": "10. 전체 문법 규격 (Full Grammar)",
        "ref_name": "전체 문법 규격",
        "ref_url": "https://docs.python.org/ko/3.13/reference/grammar.html",
        "lessons": [
            {
                "title": "10.1. 파이썬 EBNF 문법 명세",
                "body": "파이썬 언어 전체의 구문 구조를 정의하는 Extended Backus-Naur Form(EBNF) 규격 요약입니다. 파서(Parser)가 코드를 어떻게 해석하는지 근간을 보여줍니다.",
                "code": "# grammar.txt: 파이썬 파서가 사용하는 공식 문법 규칙",
                "tip": "파이썬 문법의 가장 엄밀하고 공식적인 정의입니다.",
                "quiz": {
                    "q": "파이썬 언어의 구문을 정의하기 위해 사용하는 표기법 형식은?",
                    "options": ["EBNF", "JSON", "YAML"],
                    "answer": 0,
                    "why": "Extended Backus-Naur Form (EBNF) 형식으로 문법을 규정합니다."
                }
            }
        ]
    }
]

# ==========================================
# 2. 애플리케이션 UI 및 제어 로직 설정
# ==========================================
PROGRESS_FILE = Path(__file__).with_name("progress.json")
ALLOW_RUN = os.getenv("ENABLE_CODE_RUN") == "1"
MARKS = "①②③"

st.set_page_config(page_title="Python 3.13 레퍼런스 학습", page_icon="🐍", layout="centered")

def load_done():
    try:
        return set(json.loads(PROGRESS_FILE.read_text(encoding="utf-8")).get("done", []))
    except Exception:
        return set()

def save_done():
    try:
        PROGRESS_FILE.write_text(json.dumps({"done": sorted(list(st.session_state.done))}, ensure_ascii=False), encoding="utf-8")
    except Exception:
        st.warning("진도를 파일에 저장하지 못했습니다.")

if "done" not in st.session_state:
    st.session_state.done = load_done()
DONE = st.session_state.done

def esc(text):
    return re.sub(r"([_*`$~])", r"\\\1", text)

def run_code(src):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            exec(compile(src, "<lesson>", "exec"), {"__name__": "__main__"})
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
    return buf.getvalue() or "(출력 없음)"

# 사이드바 구성
total = sum(len(m["lessons"]) for m in MODULES)
st.sidebar.title("🐍 Python 3.13 Reference")
st.sidebar.progress(len(DONE) / total if total > 0 else 0, text=f"전체 진도 {len(DONE)} / {total} 레슨")

mi = st.sidebar.selectbox("모듈 선택", range(len(MODULES)), format_func=lambda i: MODULES[i]["title"])
module = MODULES[mi]
li = st.sidebar.selectbox(
    "레슨 선택", range(len(module["lessons"])),
    format_func=lambda j: ("✓ " if f"{mi}-{j}" in DONE else "") + module["lessons"][j]["title"],
    key=f"lesson-{mi}",
)
lesson = module["lessons"][li]
lid = f"{mi}-{li}"

if st.sidebar.button("전체 진도 초기화"):
    DONE.clear()
    save_done()
    st.rerun()

# 레슨 본문 출력
st.caption(f"공식 문서 레퍼런스: [{module['ref_name']} ↗]({module['ref_url']})")
st.header(lesson["title"])
st.html(f"<div style='line-height:1.8'>{lesson['body']}</div>")

st.subheader("예제 코드")
st.code(lesson["code"], language="python")
st.html(f"<div style='background:rgba(55,118,171,.14);padding:10px 14px;border-radius:8px'>💡 {lesson['tip']}</div>")

if ALLOW_RUN:
    with st.expander("▶ 직접 코드 실행해 보기"):
        src = st.text_area("코드를 수정하고 실행해 보세요", lesson["code"], height=200, key=f"src-{lid}")
        if st.button("실행", key=f"run-{lid}"):
            st.code(run_code(src), language="text")

# 확인 문제 섹션
st.subheader("확인 문제")
quiz = lesson["quiz"]
with st.form(f"quiz-{lid}"):
    choice = st.radio(
        esc(quiz["q"]), range(len(quiz["options"])), index=None,
        format_func=lambda k: f"{MARKS[k]} {esc(quiz['options'][k])}",
        key=f"radio-{lid}",
    )
    submitted = st.form_submit_button("정답 확인", type="primary")

if submitted:
    if choice is None:
        st.warning("답을 선택해 주세요.")
    elif choice == quiz["answer"]:
        st.success(f"정답입니다! {quiz['why']}")
        if lid not in DONE:
            DONE.add(lid)
            save_done()
            st.balloons()
    else:
        st.error("아쉬워요, 다시 골라 보세요.")
elif lid in DONE:
    st.success("✓ 이미 완료한 레슨입니다.")

st.divider()
st.caption("이 콘텐츠는 Python 3.13 언어 레퍼런스(Official Documentation)를 바탕으로 재구성되었습니다. Python 문서 © Python Software Foundation (PSF License v2).")
