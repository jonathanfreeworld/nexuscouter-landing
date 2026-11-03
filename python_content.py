# -*- coding: utf-8 -*-
"""파이썬 첫걸음 학습 콘텐츠 (Python 3.13 언어 레퍼런스를 참고해 새로 작성).
body/tip 은 간단한 HTML(<b>, <code>)을 포함합니다.
"""

MODULES = [
 {
  "title": "1. 파이썬 코드의 기본 모양",
  "ref_name": "어휘 분석",
  "ref_url": "https://docs.python.org/ko/3.13/reference/lexical_analysis.html",
  "lessons": [
   {
    "title": "줄과 들여쓰기",
    "body": "파이썬은 <b>들여쓰기</b>로 코드 덩어리(블록)를 구분합니다. 중괄호 대신 공백 4칸이 관례입니다. <code>#</code> 뒤는 주석이라 실행되지 않습니다.",
    "code": "# 인사하기\nif True:\n    print('안녕')   # 들여쓰기 4칸\nprint('끝')",
    "tip": "같은 블록 안의 줄은 들여쓰기 칸 수가 반드시 같아야 합니다.",
    "quiz": {
     "q": "파이썬에서 코드 블록을 구분하는 것은?",
     "options": [
      "중괄호 { }",
      "들여쓰기",
      "세미콜론 ;"
     ],
     "answer": 1,
     "why": "파이썬은 들여쓰기로 블록의 범위를 정합니다."
    }
   },
   {
    "title": "이름(식별자)과 키워드",
    "body": "변수나 함수에 붙이는 이름을 <b>식별자</b>라 합니다. 글자·숫자·밑줄(_)을 쓸 수 있지만 숫자로 시작할 수 없고, <code>if</code>, <code>for</code> 같은 <b>키워드</b>는 이름으로 쓸 수 없습니다. 대소문자는 구분됩니다.",
    "code": "age = 20\nAge = 30      # age와 다른 이름\n# 2nd = 1     # 오류: 숫자로 시작\n# for = 1     # 오류: 키워드",
    "tip": "이름은 <code>user_name</code>처럼 뜻이 보이게 짓는 것이 좋습니다.",
    "quiz": {
     "q": "다음 중 올바른 변수 이름은?",
     "options": [
      "2nd_place",
      "for",
      "my_score"
     ],
     "answer": 2,
     "why": "숫자로 시작하거나 키워드인 이름은 쓸 수 없습니다."
    }
   },
   {
    "title": "숫자·문자열 리터럴",
    "body": "코드에 직접 적은 값을 <b>리터럴</b>이라 합니다. 정수 <code>10</code>, 실수 <code>3.14</code>, 문자열 <code>'a'</code> 또는 <code>\"a\"</code>가 대표적입니다. 여러 줄 문자열은 <code>'''...'''</code>, 큰 수는 <code>1_000_000</code>처럼 밑줄로 읽기 쉽게 적을 수 있습니다.",
    "code": "print(1_000_000)   # 1000000\nprint(0xFF)        # 255 (16진수)\nprint('줄1\\n줄2')   # \\n 은 줄바꿈\nprint('a' 'b')     # ab",
    "tip": "문자열 안에 따옴표가 있으면 다른 종류의 따옴표로 감싸세요.",
    "quiz": {
     "q": "1_000_000 은 어떤 값일까요?",
     "options": [
      "오류",
      "백만 (1000000)",
      "1 과 000000"
     ],
     "answer": 1,
     "why": "숫자 사이의 밑줄은 읽기 편하라고 넣는 구분자일 뿐입니다."
    }
   }
  ]
 },
 {
  "title": "2. 데이터 모델: 값과 형",
  "ref_name": "데이터 모델",
  "ref_url": "https://docs.python.org/ko/3.13/reference/datamodel.html",
  "lessons": [
   {
    "title": "모든 것은 객체",
    "body": "파이썬의 모든 데이터는 <b>객체</b>이고, 객체는 값(value)과 형(type)을 가집니다. <code>type()</code>으로 형을, <code>id()</code>로 객체의 고유 번호를 볼 수 있습니다.",
    "code": "print(type(3))        # <class 'int'>\nprint(type(3.5))      # <class 'float'>\nprint(type('hi'))     # <class 'str'>\nprint(type([1, 2]))   # <class 'list'>",
    "tip": "변수는 상자가 아니라 객체에 붙인 <b>이름표</b>라고 생각하세요.",
    "quiz": {
     "q": "type('hi')의 결과는?",
     "options": [
      "int",
      "str",
      "list"
     ],
     "answer": 1,
     "why": "따옴표로 감싼 값은 문자열(str)입니다."
    }
   },
   {
    "title": "바뀌는 객체와 안 바뀌는 객체",
    "body": "리스트·딕셔너리처럼 내용을 바꿀 수 있는 객체를 <b>가변(mutable)</b>, 숫자·문자열·튜플처럼 바꿀 수 없는 객체를 <b>불변(immutable)</b>이라 합니다. 두 이름이 같은 가변 객체를 가리키면 한쪽을 바꿀 때 다른 쪽도 바뀝니다.",
    "code": "a = [1, 2]\nb = a          # 같은 객체를 가리킴\nb.append(3)\nprint(a)       # [1, 2, 3]\n\ns = 'abc'\n# s[0] = 'x'   # 오류: 문자열은 불변",
    "tip": "복사본이 필요하면 <code>b = a.copy()</code>를 쓰세요.",
    "quiz": {
     "q": "a=[1,2]; b=a; b.append(3) 후 a의 값은?",
     "options": [
      "[1, 2]",
      "[1, 2, 3]",
      "[3]"
     ],
     "answer": 1,
     "why": "a와 b는 같은 리스트 객체를 가리키므로 함께 바뀝니다."
    }
   },
   {
    "title": "리스트·튜플·딕셔너리·집합",
    "body": "데이터를 묶는 기본 그릇 4가지입니다. <b>리스트</b> <code>[ ]</code>는 순서가 있고 변경 가능, <b>튜플</b> <code>( )</code>은 변경 불가, <b>딕셔너리</b> <code>{키: 값}</code>은 키로 값을 찾고, <b>집합</b> <code>{ }</code>은 중복을 자동으로 제거합니다.",
    "code": "scores = [90, 80]\nscores.append(70)\npoint = (3, 4)\nuser = {'name': '민수', 'age': 20}\nprint(user['name'])   # 민수\nprint({1, 2, 2, 3})   # {1, 2, 3}",
    "tip": "순서가 중요하면 리스트, 이름표로 찾으려면 딕셔너리를 쓰세요.",
    "quiz": {
     "q": "user = {'name': '민수'} 에서 '민수'를 꺼내는 방법은?",
     "options": [
      "user['name']",
      "user.name",
      "user(name)"
     ],
     "answer": 0,
     "why": "딕셔너리는 대괄호 안에 키를 넣어 값을 꺼냅니다."
    }
   }
  ]
 },
 {
  "title": "3. 표현식과 연산자",
  "ref_name": "표현식",
  "ref_url": "https://docs.python.org/ko/3.13/reference/expressions.html",
  "lessons": [
   {
    "title": "산술과 비교 연산",
    "body": "<b>표현식</b>은 계산하면 값이 되는 코드입니다. <code>/</code>는 나눗셈(실수), <code>//</code>는 몫, <code>%</code>는 나머지, <code>**</code>는 거듭제곱입니다. 비교 결과는 <code>True</code>/<code>False</code>입니다.",
    "code": "print(7 / 2)    # 3.5\nprint(7 // 2)   # 3\nprint(7 % 2)    # 1\nprint(2 ** 10)  # 1024\nprint(1 < 3 < 5)  # True",
    "tip": "<code>1 &lt; 3 &lt; 5</code>처럼 비교를 이어 쓸 수 있는 것은 파이썬의 특징입니다.",
    "quiz": {
     "q": "17 // 5 의 값은?",
     "options": [
      "3",
      "3.4",
      "2"
     ],
     "answer": 0,
     "why": "// 는 나눗셈의 몫만 구합니다. 17을 5로 나눈 몫은 3입니다."
    }
   },
   {
    "title": "논리 연산과 우선순위",
    "body": "<code>and</code>, <code>or</code>, <code>not</code>으로 조건을 조합합니다. 연산자에는 우선순위가 있어 <code>**</code> → 곱셈·나눗셈 → 덧셈·뺄셈 → 비교 → <code>not</code> → <code>and</code> → <code>or</code> 순으로 계산됩니다. 헷갈리면 괄호를 쓰세요.",
    "code": "print(2 + 3 * 4)     # 14\nprint((2 + 3) * 4)   # 20\nprint(True or False and False)  # True",
    "tip": "가독성을 위해 괄호를 아끼지 마세요.",
    "quiz": {
     "q": "2 + 3 * 4 의 값은?",
     "options": [
      "20",
      "14",
      "24"
     ],
     "answer": 1,
     "why": "곱셈이 덧셈보다 먼저 계산되어 2 + 12 = 14가 됩니다."
    }
   },
   {
    "title": "리스트 컴프리헨션",
    "body": "반복문으로 리스트를 만드는 코드를 한 줄로 줄이는 표현식입니다. 모양은 <code>[식 for 변수 in 시퀀스 if 조건]</code>입니다.",
    "code": "squares = [n * n for n in range(5)]\nprint(squares)   # [0, 1, 4, 9, 16]\nevens = [n for n in range(10) if n % 2 == 0]\nprint(evens)     # [0, 2, 4, 6, 8]",
    "tip": "너무 복잡해지면 일반 for 문으로 풀어 쓰는 편이 읽기 좋습니다.",
    "quiz": {
     "q": "[n * 2 for n in range(3)] 의 결과는?",
     "options": [
      "[0, 2, 4]",
      "[2, 4, 6]",
      "[0, 1, 2]"
     ],
     "answer": 0,
     "why": "n이 0, 1, 2일 때 각각 2배하면 0, 2, 4입니다."
    }
   },
   {
    "title": "호출·인덱싱·슬라이싱",
    "body": "<b>프라이머리</b>는 값 뒤에 붙여 쓰는 기본 연산입니다. 함수 <b>호출</b> <code>f(x)</code>, <b>인덱싱</b> <code>s[0]</code>, <b>슬라이싱</b> <code>s[1:4]</code>, 속성 접근 <code>obj.name</code>이 있습니다. 인덱스는 0부터 시작하고 음수는 뒤에서부터 셉니다. 슬라이스의 끝 값은 포함되지 않습니다.",
    "code": "s = 'python'\nprint(s[0])      # p\nprint(s[-1])     # n\nprint(s[1:4])    # yth\nprint(s[::2])    # pto (2칸씩)\nprint(s[::-1])   # nohtyp (뒤집기)",
    "tip": "리스트와 튜플도 같은 방식으로 자를 수 있습니다.",
    "quiz": {
     "q": "'python'[1:4] 의 결과는?",
     "options": [
      "yth",
      "pyth",
      "ytho"
     ],
     "answer": 0,
     "why": "인덱스 1부터 3까지이며 끝 값 4는 포함되지 않습니다."
    }
   },
   {
    "title": "비트 연산과 시프트",
    "body": "정수를 2진수로 보고 계산하는 연산입니다. <code>&</code>(AND), <code>|</code>(OR), <code>^</code>(XOR), <code>~</code>(반전), <code>&lt;&lt;</code>(왼쪽 시프트), <code>&gt;&gt;</code>(오른쪽 시프트)가 있습니다. 왼쪽으로 1칸 밀면 2배가 됩니다.",
    "code": "print(6 & 3)    # 2  (110 & 011 = 010)\nprint(6 | 3)    # 7\nprint(6 ^ 3)    # 5\nprint(1 << 3)   # 8 (2의 3제곱)\nprint(16 >> 2)  # 4\nprint(~5)       # -6",
    "tip": "권한 플래그나 저수준 데이터를 다룰 때 자주 씁니다.",
    "quiz": {
     "q": "1 << 4 의 값은?",
     "options": [
      "4",
      "16",
      "8"
     ],
     "answer": 1,
     "why": "1을 왼쪽으로 4칸 밀면 2의 4제곱, 즉 16입니다."
    }
   },
   {
    "title": "대입 표현식 (:=)",
    "body": "<b>바다코끼리 연산자</b> <code>:=</code>는 값을 변수에 대입하면서 그 값을 바로 식의 결과로 씁니다. 같은 계산을 두 번 쓰지 않게 해 줍니다(3.8+).",
    "code": "data = [3, 5, 8]\nif (n := len(data)) > 2:\n    print(n, '개라 많음')   # 3 개라 많음\n\nbig = [y for x in data if (y := x * 2) > 8]\nprint(big)   # [10, 16]",
    "tip": "일반 대입(=)과 달리 표현식 안에서 쓰며, 보통 괄호로 감쌉니다.",
    "quiz": {
     "q": "(n := 5) 가 하는 일은?",
     "options": [
      "5를 n에 대입하고 값 5를 결과로 돌려준다",
      "n과 5를 비교한다",
      "항상 오류가 난다"
     ],
     "answer": 0,
     "why": ":= 는 대입과 값 반환을 동시에 합니다."
    }
   },
   {
    "title": "조건 표현식",
    "body": "<code>값1 if 조건 else 값2</code> 형태로, 조건이 참이면 값1, 아니면 값2가 됩니다. 간단한 if/else를 한 줄로 쓸 때 편리합니다.",
    "code": "age = 20\nlabel = '성인' if age >= 19 else '미성년'\nprint(label)   # 성인\nprint('짝' if 4 % 2 == 0 else '홀')   # 짝",
    "tip": "조건 표현식은 값을 만들 때, if 문은 동작을 나눌 때 쓰세요.",
    "quiz": {
     "q": "x = 5 if False else 9 에서 x는?",
     "options": [
      "5",
      "9",
      "오류"
     ],
     "answer": 1,
     "why": "조건이 False이므로 else 쪽 값 9가 됩니다."
    }
   },
   {
    "title": "람다 (lambda)",
    "body": "이름 없는 한 줄짜리 작은 함수를 만듭니다. 형식은 <code>lambda 매개변수: 식</code>이며 식의 결과가 곧 반환값입니다. 정렬 기준처럼 잠깐 쓰는 함수에 알맞습니다.",
    "code": "square = lambda x: x * x\nprint(square(4))   # 16\n\nwords = ['apple', 'fig', 'banana']\nwords.sort(key=lambda w: len(w))\nprint(words)   # ['fig', 'apple', 'banana']",
    "tip": "람다 안에는 문장(if 문, for 문 등)을 쓸 수 없고 식 하나만 쓸 수 있습니다.",
    "quiz": {
     "q": "lambda x: x + 1 과 같은 함수는?",
     "options": [
      "def f(x): return x + 1",
      "def f(x): print(x + 1)",
      "f = x + 1"
     ],
     "answer": 0,
     "why": "람다의 식 결과가 그대로 반환됩니다."
    }
   },
   {
    "title": "표현식 목록과 평가 순서",
    "body": "쉼표로 이어진 값은 <b>튜플</b>이 됩니다. 원소가 하나인 튜플은 쉼표가 꼭 필요합니다. 파이썬은 표현식을 <b>왼쪽에서 오른쪽</b>으로 계산하며, 대입문은 오른쪽을 먼저 계산한 뒤 왼쪽에 넣습니다.",
    "code": "t = 1, 2, 3\nprint(type(t))        # <class 'tuple'>\nprint(type((5,)))     # <class 'tuple'>\nprint(type((5)))      # <class 'int'>\n\ndef f(n):\n    print('f', n)\n    return n\nprint(f(1) + f(2))    # f 1, f 2, 3 순서로 출력",
    "tip": "부수효과(출력 등)가 있는 함수를 한 식에 여러 개 쓰면 순서를 헷갈리기 쉽습니다.",
    "quiz": {
     "q": "(5,) 의 자료형은?",
     "options": [
      "int",
      "tuple",
      "list"
     ],
     "answer": 1,
     "why": "쉼표가 있으면 원소가 하나여도 튜플입니다."
    }
   },
   {
    "title": "형 변환, 단항 연산, 거듭제곱",
    "body": "정수와 실수를 섞어 계산하면 결과는 실수가 됩니다. 단항 연산자는 <code>-x</code>, <code>+x</code>, <code>~x</code>이고, 거듭제곱 <code>**</code>는 오른쪽부터 묶이며 왼쪽의 단항 마이너스보다 먼저 계산됩니다.",
    "code": "print(1 + 2.0)       # 3.0 (int가 float로)\nprint(2 ** 3 ** 2)   # 512 (3**2 먼저)\nprint(-2 ** 2)       # -4\nprint((-2) ** 2)     # 4\nprint(-(-3))         # 3",
    "tip": "음수의 거듭제곱은 괄호를 꼭 쓰세요.",
    "quiz": {
     "q": "-2 ** 2 의 값은?",
     "options": [
      "4",
      "-4",
      "오류"
     ],
     "answer": 1,
     "why": "** 가 먼저 계산되어 -(2 ** 2) = -4가 됩니다."
    }
   }
  ]
 },
 {
  "title": "4. 단순문",
  "ref_name": "단순문",
  "ref_url": "https://docs.python.org/ko/3.13/reference/simple_stmts.html",
  "lessons": [
   {
    "title": "대입문과 del",
    "body": "<code>=</code>는 오른쪽 값을 왼쪽 이름에 연결합니다. 여러 값을 한 번에 풀어 담을 수도 있고, <code>del</code>로 이름을 지울 수 있습니다.",
    "code": "x = 10\na, b = 1, 2\na, b = b, a    # 값 맞바꾸기\nprint(a, b)     # 2 1\ndel x",
    "tip": "파이썬은 임시 변수 없이 <code>a, b = b, a</code>로 값을 맞바꿉니다.",
    "quiz": {
     "q": "a,b=1,2 후 a,b=b,a 를 실행하면 a는?",
     "options": [
      "1",
      "2",
      "오류"
     ],
     "answer": 1,
     "why": "b 값 2가 a에 들어가고, a 값 1이 b에 들어갑니다."
    }
   },
   {
    "title": "assert, pass, return",
    "body": "<code>assert 조건</code>은 조건이 거짓이면 오류를 냅니다(검증용). <code>pass</code>는 아무 일도 안 하는 자리표시자, <code>return</code>은 함수에서 값을 돌려주며 종료합니다.",
    "code": "def half(n):\n    assert n % 2 == 0, '짝수만 가능'\n    return n // 2\n\nprint(half(8))   # 4\ndef todo():\n    pass         # 나중에 작성",
    "tip": "빈 함수나 반복문 본문에는 <code>pass</code>를 써야 문법 오류가 나지 않습니다.",
    "quiz": {
     "q": "함수에서 결과값을 돌려주는 문장은?",
     "options": [
      "pass",
      "assert",
      "return"
     ],
     "answer": 2,
     "why": "return이 값을 반환하고 함수를 끝냅니다."
    }
   }
  ]
 },
 {
  "title": "5. 복합문: 조건, 반복, 함수, 예외",
  "ref_name": "복합문",
  "ref_url": "https://docs.python.org/ko/3.13/reference/compound_stmts.html",
  "lessons": [
   {
    "title": "if 와 for",
    "body": "<code>if / elif / else</code>로 조건에 따라 갈라지고, <code>for</code>는 시퀀스를 하나씩 꺼내며 반복합니다. 줄 끝의 콜론(<code>:</code>)과 들여쓰기를 잊지 마세요.",
    "code": "for n in range(1, 4):\n    if n % 2 == 0:\n        print(n, '짝수')\n    else:\n        print(n, '홀수')",
    "tip": "<code>range(1, 4)</code>는 1, 2, 3입니다. 끝 값은 포함되지 않습니다.",
    "quiz": {
     "q": "range(1, 4)가 만드는 값은?",
     "options": [
      "1, 2, 3, 4",
      "1, 2, 3",
      "0, 1, 2, 3"
     ],
     "answer": 1,
     "why": "끝 값(4)은 포함되지 않습니다."
    }
   },
   {
    "title": "함수 정의",
    "body": "<code>def</code>로 함수를 만들면 같은 코드를 이름 하나로 재사용할 수 있습니다. 괄호 안은 <b>매개변수</b>, 호출 때 넣는 값은 <b>인자</b>입니다. 기본값도 줄 수 있습니다.",
    "code": "def greet(name, greeting='안녕'):\n    return f'{greeting}, {name}!'\n\nprint(greet('민수'))\nprint(greet('지은', '반가워'))",
    "tip": "<code>f'...{변수}'</code>는 문자열 안에 값을 끼워 넣는 f-문자열입니다.",
    "quiz": {
     "q": "greet('민수')의 결과는?",
     "options": [
      "안녕, 민수!",
      "greeting, name!",
      "오류"
     ],
     "answer": 0,
     "why": "greeting에 기본값 '안녕'이 적용됩니다."
    }
   },
   {
    "title": "try / except 예외 처리",
    "body": "실행 중 오류(예외)가 나도 프로그램이 멈추지 않게 <code>try</code>로 감싸고 <code>except</code>에서 대응합니다.",
    "code": "try:\n    n = int('abc')\nexcept ValueError:\n    print('숫자가 아닙니다')\nelse:\n    print('성공', n)\nfinally:\n    print('항상 실행')",
    "tip": "<code>finally</code>는 오류가 있든 없든 마지막에 실행됩니다.",
    "quiz": {
     "q": "오류가 났을 때 실행되는 블록은?",
     "options": [
      "try",
      "except",
      "finally(오류 시에만)"
     ],
     "answer": 1,
     "why": "except 블록이 예외를 받아 처리합니다."
    }
   },
   {
    "title": "클래스 정의",
    "body": "<code>class</code>는 데이터와 동작을 묶는 설계도입니다. <code>__init__</code>은 객체를 만들 때 자동 실행되고, <code>self</code>는 자기 자신을 가리킵니다.",
    "code": "class Dog:\n    def __init__(self, name):\n        self.name = name\n    def bark(self):\n        return self.name + ': 멍멍'\n\nd = Dog('초코')\nprint(d.bark())",
    "tip": "클래스 이름은 관례상 대문자로 시작합니다.",
    "quiz": {
     "q": "객체를 만들 때 자동 실행되는 메서드는?",
     "options": [
      "__init__",
      "bark",
      "self"
     ],
     "answer": 0,
     "why": "__init__이 초기화를 담당합니다."
    }
   },
   {
    "title": "while 과 break / continue",
    "body": "<code>while</code>은 조건이 참인 동안 반복합니다. <code>break</code>는 반복을 즉시 끝내고, <code>continue</code>는 이번 차례만 건너뛰고 다음 반복으로 갑니다.",
    "code": "n = 0\nwhile True:\n    n += 1\n    if n == 2:\n        continue\n    if n > 4:\n        break\n    print(n)   # 1 3 4",
    "tip": "조건이 영원히 참이면 무한 반복되니 종료 조건을 꼭 확인하세요.",
    "quiz": {
     "q": "반복문을 즉시 빠져나오는 문장은?",
     "options": [
      "continue",
      "break",
      "pass"
     ],
     "answer": 1,
     "why": "break는 반복문 전체를 종료합니다."
    }
   },
   {
    "title": "with 문",
    "body": "파일처럼 쓰고 나면 정리해야 하는 자원을 안전하게 다룹니다. <code>with</code> 블록이 끝나면 오류가 나더라도 자동으로 정리됩니다.",
    "code": "with open('memo.txt', 'w', encoding='utf-8') as f:\n    f.write('안녕')\n# 블록이 끝나면 파일이 자동으로 닫힘",
    "tip": "파일을 열 때는 거의 항상 with를 쓰는 것이 좋습니다.",
    "quiz": {
     "q": "with 문을 쓰는 가장 큰 이유는?",
     "options": [
      "자원을 자동으로 정리해 주기 때문",
      "실행이 더 빨라서",
      "변수를 삭제하기 위해"
     ],
     "answer": 0,
     "why": "블록을 벗어날 때 파일 닫기 같은 정리 작업이 자동으로 실행됩니다."
    }
   },
   {
    "title": "match 문 (3.10+)",
    "body": "값의 모양에 따라 갈라지는 <b>구조적 패턴 매칭</b>입니다. 여러 <code>elif</code>를 깔끔하게 대체할 수 있고, <code>|</code>로 여러 값을 묶으며, <code>_</code>는 나머지 모든 경우입니다.",
    "code": "def reply(cmd):\n    match cmd:\n        case 'start':\n            return '시작'\n        case 'stop' | 'quit':\n            return '종료'\n        case _:\n            return '모르는 명령'\nprint(reply('quit'))   # 종료",
    "tip": "<code>case _</code>는 else와 같은 역할이라 맨 마지막에 둡니다.",
    "quiz": {
     "q": "case _ 의 의미는?",
     "options": [
      "나머지 모든 경우",
      "이름이 _ 인 변수",
      "오류"
     ],
     "answer": 0,
     "why": "_ 는 어떤 값과도 일치하는 와일드카드입니다."
    }
   }
  ]
 },
 {
  "title": "6. 이름의 범위와 import",
  "ref_name": "실행 모델",
  "ref_url": "https://docs.python.org/ko/3.13/reference/executionmodel.html",
  "lessons": [
   {
    "title": "지역 변수와 전역 변수",
    "body": "이름은 만들어진 <b>범위(scope)</b> 안에서만 보입니다. 함수 안 변수는 지역이라 밖에서 쓸 수 없습니다. 함수 안에서 전역 변수를 바꾸려면 <code>global</code>을 선언합니다.",
    "code": "count = 0\ndef up():\n    global count\n    count += 1\nup()\nprint(count)   # 1",
    "tip": "가능하면 global 대신 인자와 return을 쓰는 것이 안전합니다.",
    "quiz": {
     "q": "함수 안에서 만든 변수는 어디서 보일까요?",
     "options": [
      "프로그램 전체",
      "그 함수 안에서만",
      "다른 함수에서도"
     ],
     "answer": 1,
     "why": "함수 안에서 만든 변수는 지역 변수입니다."
    }
   },
   {
    "title": "모듈 import",
    "body": "다른 파일이나 표준 라이브러리의 기능은 <code>import</code>로 가져옵니다. 필요한 것만 가져오는 <code>from ... import</code>도 많이 씁니다.",
    "code": "import math\nprint(math.sqrt(16))   # 4.0\n\nfrom random import randint\nprint(randint(1, 6))",
    "tip": "<code>if __name__ == '__main__':</code> 블록은 파일을 직접 실행할 때만 동작합니다.",
    "quiz": {
     "q": "math 모듈의 sqrt만 가져오는 올바른 문장은?",
     "options": [
      "from math import sqrt",
      "import sqrt from math",
      "include math.sqrt"
     ],
     "answer": 0,
     "why": "from 모듈 import 이름 형식을 씁니다."
    }
   },
   {
    "title": "패키지와 모듈 찾기",
    "body": "모듈을 폴더로 묶은 것이 <b>패키지</b>입니다. 폴더 이름과 파일 이름을 점(.)으로 이어 가져오고, 같은 패키지 안에서는 상대 임포트(<code>from . import x</code>)도 쓸 수 있습니다. 파이썬은 <code>sys.path</code>에 담긴 경로를 순서대로 뒤져 모듈을 찾습니다.",
    "code": "# shop/\n#   __init__.py\n#   cart.py\n\nfrom shop.cart import add\n\nimport sys\nprint(sys.path)   # 모듈 검색 경로 목록",
    "tip": "내 파일 이름을 math.py처럼 표준 모듈과 같게 지으면 충돌합니다.",
    "quiz": {
     "q": "모듈 검색 경로 목록이 들어 있는 곳은?",
     "options": [
      "sys.path",
      "math.path",
      "os.module"
     ],
     "answer": 0,
     "why": "sys.path 목록의 앞쪽부터 차례로 모듈을 찾습니다."
    }
   }
  ]
 }
]
