from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.tools.code_executor import execute_python_code
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)

VISUALIZER_SYSTEM = """You are a data visualization agent. Given a CSV file path and analysis context, generate Python code that creates insightful charts.

Your code MUST:
1. Load the CSV with pandas
2. Create 4 charts saved as PNG files in the specified output directory:
   - Chart 1: Distribution plot (histogram) for the most interesting numeric column
   - Chart 2: Correlation heatmap for all numeric columns
   - Chart 3: Bar chart showing mean of a numeric column grouped by a categorical column
   - Chart 4: Scatter plot showing the relationship between the two most correlated numeric columns
3. Use matplotlib and seaborn for styling
4. Each chart must have: title, axis labels, clean layout
5. Save each chart with plt.savefig() using tight layout and 150 dpi
6. Print the file paths of all saved charts, one per line, prefixed with "CHART:"

Rules:
- Output ONLY the Python code, no explanations, no markdown backticks
- Use only pandas, numpy, matplotlib, seaborn (already installed)
- Use plt.figure() before each chart and plt.close() after saving to avoid overlap
- Handle errors gracefully with try/except
- If the data has fewer than 2 numeric columns, adapt (skip correlation heatmap, etc.)"""


def run_visualizer(csv_path: str, analysis: str, output_dir: str = "outputs", max_retries: int = 3) -> list:
    """Generate and execute visualization code. Returns list of chart file paths."""

    os.makedirs(output_dir, exist_ok=True)

    prompt = f"""Create visualizations for this CSV file: {csv_path}
Save all charts to this directory: {output_dir}

Here is the analysis context:
{analysis[:2000]}

Generate Python code to create 4 insightful charts."""

    for attempt in range(max_retries):
        response = llm.invoke([
            SystemMessage(content=VISUALIZER_SYSTEM),
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
            # Extract chart paths from output
            chart_paths = []
            for line in result["stdout"].split("\n"):
                if line.startswith("CHART:"):
                    path = line.replace("CHART:", "").strip()
                    if os.path.exists(path):
                        chart_paths.append(path)

            if chart_paths:
                return chart_paths
            else:
                prompt = f"""The code ran but no charts were saved correctly.
stdout: {result['stdout'][:500]}

Make sure to:
1. Use plt.savefig('{output_dir}/chart_name.png', dpi=150, bbox_inches='tight')
2. Print each saved path as CHART:/full/path.png

CSV path: {csv_path}
Output directory: {output_dir}
Generate corrected Python code."""
        else:
            prompt = f"""The previous code failed with this error:
{result['stderr']}

Fix the code and try again. CSV path: {csv_path}
Output directory: {output_dir}
Output ONLY the corrected Python code."""

    return []


if __name__ == "__main__":
    import tempfile

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

    print("Running visualizer agent...")
    charts = run_visualizer(tmp, "numeric cols: age, salary, rating, years_exp. categorical: department. strong correlation: age vs years_exp (0.987)")
    print(f"\nGenerated {len(charts)} charts:")
    for c in charts:
        print(f"  {c}")
    os.unlink(tmp)
    