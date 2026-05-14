from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.tools.code_executor import execute_python_code
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)

ANALYST_SYSTEM = """You are a statistical analysis agent. Given a CSV file path and a data profile, generate Python code that performs deep analysis.

Your code MUST:
1. Load the CSV with pandas
2. Perform and print:
   - Correlation matrix for numeric columns (highlight strong correlations > 0.5 or < -0.5)
   - Top 5 key insights about the data (patterns, outliers, relationships)
   - Group-by summaries for categorical columns (mean of numeric columns per group)
   - Outlier detection using IQR method for numeric columns
   - Distribution analysis (skewness, kurtosis) for numeric columns
3. End with a section called "KEY FINDINGS" that lists the top 5 findings as numbered points

Rules:
- Output ONLY the Python code, no explanations, no markdown backticks
- Use only pandas, numpy, scipy (already installed)
- Print everything to stdout with clear section headers
- Handle errors gracefully with try/except
- If a column has too few values for a test, skip it gracefully"""


def run_analyst(csv_path: str, profile: str, max_retries: int = 3) -> str:
    """Generate and execute analysis code for the given CSV."""

    prompt = f"""Analyze this CSV file: {csv_path}

Here is the data profile for context:
{profile[:2000]}

Generate Python code to perform deep statistical analysis."""

    for attempt in range(max_retries):
        response = llm.invoke([
            SystemMessage(content=ANALYST_SYSTEM),
            HumanMessage(content=prompt),
        ])

        code = response.content.strip()
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

    return f"Analysis failed after {max_retries} attempts. Last error: {result['stderr']}"


if __name__ == "__main__":
    import tempfile, os

    sample = """name,age,salary,department,rating,years_exp
Alice,30,70000,Engineering,4.5,5
Bob,25,50000,Marketing,3.8,2
Charlie,35,90000,Engineering,4.2,10
Diana,29,65000,Sales,4.0,4
Eve,28,55000,Marketing,3.5,3
Frank,40,95000,Engineering,4.7,15
Grace,33,72000,Sales,3.9,8
Henry,27,48000,Marketing,3.6,1
Ivy,31,78000,Engineering,4.4,6
Jack,36,88000,Sales,4.1,11
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample)
        tmp = f.name

    print("Running analyst agent...")
    analysis = run_analyst(tmp, "10 rows, 6 columns, numeric: age, salary, rating, years_exp")
    print(analysis)
    os.unlink(tmp)