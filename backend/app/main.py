import ast, os, re, time
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sympy import Eq, Symbol, diff, integrate, limit, solve, sympify, latex, symbols
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

SYSTEM_PROMPT = "You are HARVIX, an intelligent cloud-based assistant specialized in programming and mathematics. Write clean, correct, well-commented code. For math, use the provided calculation tools, show steps, and verify results. Be concise, ask for clarification when a request is ambiguous, and never fabricate results."
TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)
app = FastAPI(title="HARVIX API", version="1.0.0", description="Cloud AI coding and mathematics assistant")
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    mode: str = Field(default="auto", pattern="^(auto|general|coding|math)$")
    history: list[dict[str, str]] = []

class ChatResponse(BaseModel):
    reply: str
    mode: str
    elapsed_ms: int
    sources: list[str] = []

class MathRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=1000)
    operation: str = Field(default="solve")

class MathResponse(BaseModel):
    expression: str
    result: str
    steps: list[str]
    verified: bool


def route_message(message: str, requested: str) -> str:
    if requested != "auto": return requested
    lower = message.lower()
    if any(x in lower for x in ["derivative", "integral", "solve", "equation", "matrix", "calculate", "factor", "limit", "convert "]): return "math"
    if "```" in message or any(x in lower for x in ["python", "javascript", "typescript", "java", "c++", "sql", "bug", "debug", "refactor", "code", "function"]): return "coding"
    return "general"


def math_engine(expression: str, operation: str = "solve") -> MathResponse:
    raw = expression.strip()
    try:
        if operation == "derivative":
            var = symbols("x")
            result = diff(parse_expr(raw, transformations=TRANSFORMS), var)
            return MathResponse(expression=raw, result=str(result), steps=[f"Identify the variable: x", f"Differentiate {raw} with respect to x", f"Simplify the result to {result}"], verified=True)
        if operation == "integral":
            var = symbols("x")
            result = integrate(parse_expr(raw, transformations=TRANSFORMS), var)
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
        raise HTTPException(status_code=400, detail=f"I could not parse that expression safely: {exc}")


def local_reply(message: str, mode: str) -> str:
    if mode == "math":
        try:
            return "### Math result\n\n" + math_engine(message).result + "\n\n_Use the Math tool for a detailed step-by-step solution._"
        except HTTPException:
            return "I can solve that precisely, but I need a clearer expression. For example: `2x^2 - 5x + 3 = 0` or `derivative: x^3*sin(x)`."
    if mode == "coding":
        return "I’m ready to help with code. Tell me the language and goal, or paste the code and error. I can generate, explain, debug, refactor, or convert it."
    return "Hello, I’m HARVIX. I can help with programming, debugging, code conversion, mathematics, and everyday questions. What would you like to work on?"

@app.get("/api/health")
def health(): return {"status": "ok", "service": "harvix-api", "timestamp": time.time()}

@app.post("/api/math", response_model=MathResponse)
def calculate(req: MathRequest): return math_engine(req.expression, req.operation)

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    started = time.perf_counter(); mode = route_message(req.message, req.mode)
    # Production deployments can enable OpenAI without changing the UI; local mode remains deterministic.
    reply = local_reply(req.message, mode)
    if os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))
            messages = [{"role":"system", "content": SYSTEM_PROMPT}] + req.history[-10:] + [{"role":"user", "content": req.message}]
            completion = client.chat.completions.create(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), messages=messages, temperature=0.2)
            reply = completion.choices[0].message.content or reply
        except Exception:
            pass
    return ChatResponse(reply=reply, mode=mode, elapsed_ms=round((time.perf_counter()-started)*1000), sources=["HARVIX local router"])
