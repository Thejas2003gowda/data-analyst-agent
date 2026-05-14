from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents.profiler import run_profiler
from src.agents.analyst import run_analyst
from src.agents.visualizer import run_visualizer
from src.agents.reporter import run_reporter
from langchain_core.messages import HumanMessage
import os


def profile_node(state: AgentState) -> dict:
    """Run the profiler agent."""
    csv_path = state["csv_path"]
    try:
        profile = run_profiler(csv_path)
        return {
            "data_profile": profile,
            "current_agent": "profiler",
            "messages": [HumanMessage(content=f"Profiling complete.")],
        }
    except Exception as e:
        return {
            "data_profile": f"Profiling failed: {str(e)}",
            "current_agent": "profiler",
            "error": str(e),
            "messages": [HumanMessage(content=f"Profiling error: {str(e)}")],
        }


def analyst_node(state: AgentState) -> dict:
    """Run the analyst agent."""
    csv_path = state["csv_path"]
    profile = state.get("data_profile", "")
    try:
        analysis = run_analyst(csv_path, profile)
        return {
            "analysis": analysis,
            "current_agent": "analyst",
            "messages": [HumanMessage(content=f"Analysis complete.")],
        }
    except Exception as e:
        return {
            "analysis": f"Analysis failed: {str(e)}",
            "current_agent": "analyst",
            "error": str(e),
            "messages": [HumanMessage(content=f"Analysis error: {str(e)}")],
        }


def visualizer_node(state: AgentState) -> dict:
    """Run the visualizer agent."""
    csv_path = state["csv_path"]
    analysis = state.get("analysis", "")
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    try:
        chart_paths = run_visualizer(csv_path, analysis, output_dir)
        return {
            "chart_paths": chart_paths,
            "current_agent": "visualizer",
            "messages": [HumanMessage(content=f"Generated {len(chart_paths)} charts.")],
        }
    except Exception as e:
        return {
            "chart_paths": [],
            "current_agent": "visualizer",
            "error": str(e),
            "messages": [HumanMessage(content=f"Visualization error: {str(e)}")],
        }


def reporter_node(state: AgentState) -> dict:
    """Run the reporter agent."""
    profile = state.get("data_profile", "")
    analysis = state.get("analysis", "")
    chart_paths = state.get("chart_paths", [])
    try:
        report = run_reporter(profile, analysis, chart_paths)
        return {
            "report": report,
            "current_agent": "reporter",
            "messages": [HumanMessage(content="Report complete.")],
        }
    except Exception as e:
        return {
            "report": f"Report generation failed: {str(e)}",
            "current_agent": "reporter",
            "error": str(e),
            "messages": [HumanMessage(content=f"Report error: {str(e)}")],
        }


def build_graph():
    """Build the LangGraph agent workflow."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("profiler", profile_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("visualizer", visualizer_node)
    workflow.add_node("reporter", reporter_node)

    # Define edges: profiler -> analyst -> visualizer -> reporter -> END
    workflow.set_entry_point("profiler")
    workflow.add_edge("profiler", "analyst")
    workflow.add_edge("analyst", "visualizer")
    workflow.add_edge("visualizer", "reporter")
    workflow.add_edge("reporter", END)

    return workflow.compile()


def run_pipeline(csv_path: str) -> dict:
    """Run the full analysis pipeline on a CSV file."""
    graph = build_graph()

    initial_state = {
        "messages": [HumanMessage(content=f"Analyze this dataset: {csv_path}")],
        "csv_path": csv_path,
        "data_profile": "",
        "analysis": "",
        "chart_paths": [],
        "report": "",
        "current_agent": "",
        "error": "",
    }

    final_state = graph.invoke(initial_state)
    return final_state


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

    print("Running full pipeline...")
    print("=" * 60)
    result = run_pipeline(tmp)

    print("\n\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result["report"])
    print(f"\nCharts: {result['chart_paths']}")

    os.unlink(tmp)