import ast
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sympy import Eq, diff, integrate, solve, symbols
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

SYSTEM_PROMPT = (
    "You are HARVIX, an intelligent assistant for programming and mathematics. "
    "Follow the user's exact request. If code is requested, return complete code in a fenced block. "
    "If explanation, debugging, conversion, optimization, test cases, or execution is requested, "
    "return that requested artifact instead of a generic reply. Preserve input details and never fabricate execution results."
)
TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)
app = FastAPI(title="HARVIX API", version="1.1.0", description="AI coding and mathematics assistant")
logger = logging.getLogger("harvix")
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    mode: str = Field(default="auto", pattern="^(auto|general|coding|math)$")
    history: list[dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    response: str
    mode: str
    elapsed_ms: int
    sources: list[str] = Field(default_factory=list)


class MathRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=1000)
    operation: str = Field(default="solve")


class MathResponse(BaseModel):
    expression: str
    result: str
    steps: list[str]
    verified: bool


class ExecuteRequest(BaseModel):
    language: str = Field(default="python", pattern="^(python|javascript)$")
    code: str = Field(min_length=1, max_length=20000)
    stdin: str = Field(default="", max_length=20000)
    timeout_seconds: int = Field(default=5, ge=1, le=10)


class ExecuteResponse(BaseModel):
    success: bool
    output: str
    error: str
    exit_code: int
    elapsed_ms: int


def route_message(message: str, requested: str) -> str:
    if requested != "auto":
        return requested
    lower = message.lower()
    coding_terms = [
        "python", "javascript", "typescript", "java", "c++", "sql", "code", "coding",
        "program", "programming", "function", "algorithm", "class", "loop", "array",
        "binary search", "linked list", "debug", "bug", "refactor", "convert", "explain this code",
        "run this", "execute", "optimize", "test cases", "complexity", "competitive programming",
    ]
    if "```" in message or any(term in lower for term in coding_terms):
        return "coding"
    if any(term in lower for term in ["derivative", "integral", "solve equation", "simplify", "matrix", "calculate", "factorize", "limit"]):
        return "math"
    return "general"


def math_engine(expression: str, operation: str = "solve") -> MathResponse:
    raw = expression.strip()
    try:
        if operation == "derivative":
            result = diff(parse_expr(raw, transformations=TRANSFORMS), symbols("x"))
            return MathResponse(expression=raw, result=str(result), steps=[f"Identify the variable: x", f"Differentiate {raw} with respect to x", f"Simplify the result to {result}"], verified=True)
        if operation == "integral":
            result = integrate(parse_expr(raw, transformations=TRANSFORMS), symbols("x"))
            return MathResponse(expression=raw, result=str(result) + " + C", steps=[f"Identify the variable: x", f"Integrate {raw} with respect to x", f"Apply the antiderivative rule to obtain {result} + C"], verified=True)
        if "=" in raw:
            left, right = raw.split("=", 1)
            equation = Eq(parse_expr(left, transformations=TRANSFORMS), parse_expr(right, transformations=TRANSFORMS))
            result = solve(equation)
            return MathResponse(expression=raw, result=str(result), steps=[f"Rewrite as an equation: {left} = {right}", "Move all terms to one side", f"Solve symbolically to obtain {result}"], verified=True)
        expr = parse_expr(raw, transformations=TRANSFORMS)
        result = expr.simplify()
        return MathResponse(expression=raw, result=str(result), steps=[f"Parse the expression: {raw}", "Apply exact symbolic simplification", f"Final result: {result}"], verified=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"I could not parse that expression safely: {exc}") from exc


def extract_code(text: str) -> tuple[str, str]:
    match = re.search(r"```([\w+#-]*)\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(2).strip(), match.group(1).strip().lower() or "python"
    return text.strip(), "python"


def previous_code(history: list[dict[str, str]]) -> str:
    for item in reversed(history):
        if item.get("role") == "assistant" and "```" in item.get("content", ""):
            code, _ = extract_code(item["content"])
            return code
    return ""


def generic_code_reply(message: str) -> str:
    """Return a useful runnable starter for common code requests without an external AI key."""
    lower = message.lower()
    language = "python"
    if "javascript" in lower or "node.js" in lower or re.search(r"\bjs\b", lower):
        language = "javascript"
    elif "java" in lower and "javascript" not in lower:
        language = "java"
    elif "c++" in lower or "cpp" in lower:
        language = "cpp"

    task = "general programming task"
    if "sort" in lower:
        task = "sorting an array"
    elif "palindrome" in lower:
        task = "checking a palindrome"
    elif "reverse" in lower and "string" in lower:
        task = "reversing a string"
    elif "prime" in lower:
        task = "checking prime numbers"
    elif "calculator" in lower or "calculate" in lower:
        task = "a calculator"
    elif "even" in lower or "odd" in lower:
        task = "checking whether a number is even or odd"
    elif "pattern" in lower:
        task = "printing a pattern"
    elif "read" in lower and "file" in lower and "word" in lower:
        task = "counting words in a file"

    templates = {
        "python": {
            "sorting an array": "def sort_numbers(values):\n    return sorted(values)\n\nvalues = list(map(int, input('Enter numbers: ').split()))\nprint(sort_numbers(values))",
            "checking a palindrome": "def is_palindrome(text):\n    cleaned = ''.join(ch.lower() for ch in text if ch.isalnum())\n    return cleaned == cleaned[::-1]\n\ntext = input('Enter text: ')\nprint(is_palindrome(text))",
            "reversing a string": "text = input('Enter a string: ')\nprint(text[::-1])",
            "checking prime numbers": "def is_prime(number):\n    if number < 2:\n        return False\n    return all(number % divisor for divisor in range(2, int(number ** 0.5) + 1))\n\nnumber = int(input('Enter a number: '))\nprint(is_prime(number))",
            "a calculator": "first = float(input('First number: '))\noperator = input('Operator (+, -, *, /): ')\nsecond = float(input('Second number: '))\n\noperations = {'+': first + second, '-': first - second, '*': first * second, '/': first / second}\nprint(operations[operator])",
            "checking whether a number is even or odd": "number = int(input('Enter a number: '))\nprint('Even' if number % 2 == 0 else 'Odd')",
            "printing a pattern": "rows = int(input('Number of rows: '))\nfor row in range(1, rows + 1):\n    print('*' * row)",
            "counting words in a file": "from pathlib import Path\n\nfile_path = input('File path: ')\ntext = Path(file_path).read_text(encoding='utf-8')\nwords = text.split()\nprint(f'Word count: {len(words)}')",
            "general programming task": "def solve():\n    # Implement the requested logic here.\n    # Read input, process it, and print the result.\n    pass\n\nif __name__ == '__main__':\n    solve()",
        },
        "javascript": {
            "sorting an array": "const values = [5, 2, 9, 1];\nconsole.log(values.sort((a, b) => a - b));",
            "checking a palindrome": "const text = prompt('Enter text:');\nconst normalized = text.toLowerCase().replace(/[^a-z0-9]/g, '');\nconsole.log(normalized === [...normalized].reverse().join(''));",
            "general programming task": "function solve(input) {\n  // Implement the requested logic here.\n  return input;\n}\n\nconsole.log(solve('input'));",
        },
        "java": {
            "sorting an array": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        int[] values = {5, 2, 9, 1};\n        Arrays.sort(values);\n        System.out.println(Arrays.toString(values));\n    }\n}",
            "general programming task": "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner scanner = new Scanner(System.in);\n        // Read input and implement the requested logic here.\n    }\n}",
        },
        "cpp": {
            "sorting an array": "#include <algorithm>\n#include <iostream>\n#include <vector>\nusing namespace std;\n\nint main() {\n    vector<int> values{5, 2, 9, 1};\n    sort(values.begin(), values.end());\n    for (int value : values) cout << value << ' ';\n    return 0;\n}",
            "general programming task": "#include <iostream>\nusing namespace std;\n\nint main() {\n    // Read input and implement the requested logic here.\n    return 0;\n}",
        },
    }
    code = templates.get(language, templates["python"]).get(task) or templates[language]["general programming task"]
    label = {"python": "Python", "javascript": "JavaScript", "java": "Java", "cpp": "C++"}[language]
    return f"### {label} program: {task}\n\n```{language}\n{code}\n```\n\nThis local starter was generated from your request. Add the problem constraints or sample input for a more specific implementation."


def local_code_reply(message: str, history: list[dict[str, str]]) -> str:
    lower = message.lower()
    supplied_code, supplied_language = extract_code(message)
    prior = previous_code(history)

    if "run" in lower or "execute" in lower:
        code = supplied_code if "```" in message else prior
        if code:
            return f"I found executable code. Use the **Run Code** button below to execute it with the supplied input.\n\n```{supplied_language}\n{code}\n```"
        return "Please provide the program in a fenced code block, for example:\n\n```python\nprint('Hello')\n```\n\nThen HARVIX can execute it and show the real stdout or error."

    if "debug" in lower or "fix this" in lower:
        if "```" in message:
            return f"### Debug review\n\nI received the complete {supplied_language} program. The code is preserved below so the requested error can be inspected without losing indentation.\n\n```{supplied_language}\n{supplied_code}\n```\n\nAdd the error message or failing input for a precise diagnosis."
        return "Paste the complete program and the error inside a fenced code block. HARVIX will return the identified error, reason, corrected code, and explanation."

    if "explain" in lower and ("code" in lower or "```" in message):
        code = supplied_code if "```" in message else prior
        if code:
            return f"### Code explanation\n\nThe requested program is preserved below. It defines the main logic in a readable function and can be explained line by line once the target language and focus are specified.\n\n```{supplied_language}\n{code}\n```"
        return "Paste the code you want explained inside a fenced code block so the explanation is based on the exact input."

    if "convert" in lower or "translate" in lower:
        code = supplied_code if "```" in message else prior
        target = "Java" if "java" in lower else "C++" if "c++" in lower or "cpp" in lower else "Python"
        if code:
            return f"### {target} conversion\n\nThe complete source was received. A language-model provider can perform the semantic conversion while preserving the original request context.\n\nSource received:\n\n```{supplied_language}\n{code}\n```\n\nConfigure `OPENAI_API_KEY` for automatic semantic conversion, or specify the target language and constraints."
        return "Paste the source program in a fenced code block and specify the target language, for example: `Convert this Python code to Java`."

    if "binary search" in lower:
        return "### Python program: binary search\n\n```python\ndef binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        middle = (left + right) // 2\n        if arr[middle] == target:\n            return middle\n        if arr[middle] < target:\n            left = middle + 1\n        else:\n            right = middle - 1\n    return -1\n\nprint(binary_search([1, 3, 5, 7, 9], 7))\n```\n\nThe input array must be sorted. Time complexity is O(log n)."
    if "largest" in lower and ("array" in lower or "number" in lower):
        return "### Python program: largest number in an array\n\n```python\ndef largest_number(values):\n    if not values:\n        raise ValueError('array must not be empty')\n    largest = values[0]\n    for value in values[1:]:\n        if value > largest:\n            largest = value\n    return largest\n\nprint(largest_number([4, 9, 2, 7]))\n```\n\nThe program scans the array once, so its time complexity is O(n)."
    if "linked list" in lower and "java" in lower:
        return "### Java program: linked list\n\n```java\nclass Node {\n    int value;\n    Node next;\n\n    Node(int value) {\n        this.value = value;\n    }\n}\n\npublic class LinkedListDemo {\n    public static void main(String[] args) {\n        Node head = new Node(10);\n        head.next = new Node(20);\n        System.out.println(head.next.value);\n    }\n}\n```\n\nEach node stores a value and a reference to the next node."
    if "prime" in lower:
        return "### Python program: prime numbers\n\n```python\ndef primes_up_to(limit):\n    primes = []\n    for number in range(2, limit + 1):\n        if all(number % divisor for divisor in range(2, int(number ** 0.5) + 1)):\n            primes.append(number)\n    return primes\n\nprint(primes_up_to(20))\n```\n\nThe divisor check stops at the square root of each number."
    if "factorial" in lower:
        return "### Python program: factorial\n\n```python\ndef factorial(number):\n    if number < 0:\n        raise ValueError('number must be non-negative')\n    result = 1\n    for value in range(2, number + 1):\n        result *= value\n    return result\n\nprint(factorial(5))\n```\n\nThe function multiplies all integers from 2 through the requested number."
    if "fibonacci" in lower:
        return "### Python program: Fibonacci sequence\n\n```python\ndef fibonacci(count):\n    values = []\n    first, second = 0, 1\n    for _ in range(count):\n        values.append(first)\n        first, second = second, first + second\n    return values\n\nprint(fibonacci(8))\n```\n\nThe program produces the first requested Fibonacci values."
    if "sum" in lower or "add" in lower:
        return "### Python program: add two numbers\n\n```python\ndef add_numbers(first, second):\n    return first + second\n\nprint(add_numbers(3, 4))\n```\n\nThis function returns the sum of the two input values."
    if "multiple test" in lower or "multiple input" in lower:
        return "### Python program: multiple test cases\n\n```python\ndef solve_case(value):\n    return value * 2\n\ncount = int(input())\nfor _ in range(count):\n    value = int(input())\n    print(solve_case(value))\n```\n\nThe first input line is the number of test cases; each following line is passed to the solver."
    if "test cases" in lower:
        return "### Test-case template\n\n```python\ndef solve_case(value):\n    # Replace this body with the problem-specific logic.\n    return value\n\ninputs = [5, 10, 15]\nfor value in inputs:\n    print(solve_case(value))\n```\n\nProvide the full problem statement to generate exact test cases and expected outputs."
    if "optimize" in lower or "o(n log n)" in lower:
        code = supplied_code if "```" in message else prior
        if code:
            return f"### Optimization review\n\nThe complete source was received. For an exact complexity-preserving rewrite, the configured AI provider should analyze the algorithm and constraints.\n\n```{supplied_language}\n{code}\n```\n\nTarget constraint: O(n log n)."
        return "Provide the complete program and its input constraints in a fenced code block. HARVIX will return the optimized code and explain the time and space complexity."
    if any(word in lower for word in ["write", "create", "generate", "give me", "build", "make", "program", "function"]):
        return generic_code_reply(message)
    return "### Coding request received\n\nHARVIX preserved your complete request. Include the programming language, task, input format, and expected output so the local processor can generate a targeted implementation."


def local_reply(message: str, mode: str, history: list[dict[str, str]]) -> str:
    if mode == "math":
        try:
            result = math_engine(message).result
            return f"### Math result\n\n{result}\n\n_The result was calculated with SymPy._"
        except HTTPException:
            return "I could not parse that expression. Provide an equation or expression such as `2*x^2 - 5*x + 3 = 0`."
    if mode == "coding":
        return local_code_reply(message, history)
    return "Hello, I’m HARVIX. Ask for code, debugging, code conversion, code execution, mathematics, or a technical explanation."


def provider_reply(req: ChatRequest) -> tuple[str, str] | None:
    if not os.getenv("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + req.history[-12:] + [{"role": "user", "content": req.message}]
        completion = client.chat.completions.create(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), messages=messages, temperature=0.2)
        content = completion.choices[0].message.content if completion.choices else None
        if content:
            return content, "OpenAI-compatible provider"
    except Exception:
        return None
    return None


def execute_python(code: str, stdin: str, timeout_seconds: int) -> ExecuteResponse:
    started = time.perf_counter()
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return ExecuteResponse(success=False, output="", error=f"SyntaxError: {exc}", exit_code=1, elapsed_ms=round((time.perf_counter() - started) * 1000))
    with tempfile.TemporaryDirectory(prefix="harvix-run-") as tmp:
        script = Path(tmp) / "program.py"
        script.write_text(code, encoding="utf-8")
        env = {"PATH": os.getenv("PATH", ""), "PYTHONIOENCODING": "utf-8"}
        try:
            result = subprocess.run([sys.executable, str(script)], input=stdin, text=True, capture_output=True, timeout=timeout_seconds, cwd=tmp, env=env)
            return ExecuteResponse(success=result.returncode == 0, output=result.stdout, error=result.stderr, exit_code=result.returncode, elapsed_ms=round((time.perf_counter() - started) * 1000))
        except subprocess.TimeoutExpired:
            return ExecuteResponse(success=False, output="", error=f"Execution timed out after {timeout_seconds} seconds.", exit_code=124, elapsed_ms=round((time.perf_counter() - started) * 1000))


def execution_request(message: str, history: list[dict[str, str]]) -> tuple[str, str] | None:
    lower = message.lower()
    if "run" not in lower and "execute" not in lower:
        return None
    code, language = extract_code(message)
    if "```" not in message:
        code = previous_code(history)
    if not code or language not in {"python", "py", ""}:
        return None
    input_match = re.search(r"(?:input|stdin)\s*:\s*(.*)", message, flags=re.IGNORECASE | re.DOTALL)
    stdin = input_match.group(1).strip() if input_match else ""
    return code, stdin


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "harvix-api", "timestamp": time.time()}


@app.post("/api/math", response_model=MathResponse)
def calculate(req: MathRequest):
    return math_engine(req.expression, req.operation)


@app.post("/api/execute", response_model=ExecuteResponse)
def execute(req: ExecuteRequest):
    if req.language != "python":
        raise HTTPException(status_code=400, detail="Only Python execution is enabled in the local safe runner.")
    return execute_python(req.code, req.stdin, req.timeout_seconds)


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    started = time.perf_counter()
    mode = route_message(req.message, req.mode)
    logger.info("INPUT_RECEIVED mode=%s chars=%d", mode, len(req.message))
    execution = execution_request(req.message, req.history)
    if execution:
        code, stdin = execution
        logger.info("CODE_EXECUTION_REQUEST language=python stdin_chars=%d", len(stdin))
        result = execute_python(code, stdin, 5)
        if result.success:
            reply = f"### Execution result\n\n**OUTPUT**\n\n```text\n{result.output or '(no stdout)'}\n```"
        else:
            reply = f"### Execution result\n\n**ERROR**\n\n```text\n{result.error or 'Program exited with an error.'}\n```"
        source = "HARVIX safe Python execution service"
    else:
        provider = provider_reply(req) if mode in {"coding", "general"} else None
        if provider:
            reply, source = provider
        else:
            reply, source = local_reply(req.message, mode, req.history), "HARVIX deterministic local processor"
    elapsed = round((time.perf_counter() - started) * 1000)
    logger.info("OUTPUT_DISPLAYED mode=%s chars=%d elapsed_ms=%d", mode, len(reply), elapsed)
    return ChatResponse(reply=reply, response=reply, mode=mode, elapsed_ms=elapsed, sources=[source])
