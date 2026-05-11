from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.tools.code_executor import execute_python_code
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)

PROFILER_SYSTEM = """You are a data profiling agent. Given a CSV file path, generate Python code that produces a comprehensive data profile.

Your code MUST:
1. Load the CSV with pandas
2. Print the following clearly with labels:
   - Shape (rows, columns)
   - Column names and data types
   - Missing values per column (count and percentage)
   - Descriptive statistics (mean, std, min, max, quartiles) for numeric columns
   - Unique value counts for categorical columns (top 10 values if more than 10)
   - Memory usage

Rules:
- Output ONLY the Python code, no explanations, no markdown backticks
- Use only pandas and numpy (already installed)
- Print everything to stdout with clear section headers
- Handle errors gracefully with try/except"""


def run_profiler(csv_path: str, max_retries: int = 3) -> str:
    """Generate and execute profiling code for the given CSV."""

    prompt = f"Generate Python code to profile this CSV file: {csv_path}"

    for attempt in range(max_retries):
        response = llm.invoke([
            SystemMessage(content=PROFILER_SYSTEM),
            HumanMessage(content=prompt),
        ])

        code = response.content.strip()
        # Clean markdown backticks if present
        if code.startswith("```python"):
            code = code[len("```python"):].strip()
        if code.startswith("```"):
            code = code[len("```"):].strip()
        if code.endswith("```"):
            code = code[:-len("```")].strip()

        result = execute_python_code(code)

        if result["success"]:
            return result["stdout"]
        else:
            prompt = f"""The previous code failed with this error:
{result['stderr']}

Fix the code and try again. CSV path: {csv_path}
Output ONLY the corrected Python code."""

    return f"Profiling failed after {max_retries} attempts. Last error: {result['stderr']}"


if __name__ == "__main__":
    import tempfile, os

    sample = """name,age,salary,department,rating
Alice,30,70000,Engineering,4.5
Bob,25,50000,Marketing,3.8
Charlie,35,90000,Engineering,4.2
Diana,,65000,Sales,4.0
Eve,28,55000,Marketing,
Frank,40,95000,Engineering,4.7
Grace,33,72000,Sales,3.9
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample)
        tmp = f.name

    print("Running profiler agent...")
    profile = run_profiler(tmp)
    print(profile)
    os.unlink(tmp)