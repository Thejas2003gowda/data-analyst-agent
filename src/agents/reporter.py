from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)

REPORTER_SYSTEM = """You are a data reporting agent. Given a data profile, statistical analysis, and chart descriptions, write a clear, professional summary report.

Your report MUST include:
1. Executive Summary (2-3 sentences)
2. Data Overview (what the dataset contains)
3. Key Findings (top 5 insights from the analysis, numbered)
4. Recommendations (what actions should be taken based on the findings)

Rules:
- Write in clear, professional language
- Be specific with numbers and statistics
- Keep it concise (under 500 words)
- Format with clear section headers"""


def run_reporter(profile: str, analysis: str, chart_paths: list) -> str:
    """Generate a summary report from all agent outputs."""

    chart_desc = "\n".join([f"- Chart: {p}" for p in chart_paths]) if chart_paths else "No charts generated."

    prompt = f"""Write a professional data analysis report based on the following:

DATA PROFILE:
{profile[:3000]}

STATISTICAL ANALYSIS:
{analysis[:3000]}

CHARTS GENERATED:
{chart_desc}

Write the summary report now."""

    response = llm.invoke([
        SystemMessage(content=REPORTER_SYSTEM),
        HumanMessage(content=prompt),
    ])

    return response.content


if __name__ == "__main__":
    profile = "10 rows, 6 columns. Columns: name, age, salary, department, rating, years_exp. Missing: 0."
    analysis = "Strong correlation: age vs years_exp (0.987). Engineering has highest avg salary ($83,250). Marketing has lowest ($51,000). No outliers detected."
    charts = ["outputs/distribution.png", "outputs/correlation.png"]

    print("Running reporter agent...")
    report = run_reporter(profile, analysis, charts)
    print(report)