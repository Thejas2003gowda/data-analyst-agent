import gradio as gr
import shutil
import os
import sys
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.graph import run_pipeline


def clear_outputs():
    """Clear previous outputs."""
    if os.path.exists("outputs"):
        for f in glob.glob("outputs/*.png"):
            os.remove(f)


def analyze_csv(file):
    """Run the full agent pipeline on an uploaded CSV."""
    if file is None:
        return "Please upload a CSV file.", "", "", []

    clear_outputs()

    # Copy uploaded file to a stable path
    upload_path = "uploads/uploaded_data.csv"
    os.makedirs("uploads", exist_ok=True)
    shutil.copy(file, upload_path)

    try:
        result = run_pipeline(upload_path)

        profile = result.get("data_profile", "No profile generated.")
        analysis = result.get("analysis", "No analysis generated.")
        report = result.get("report", "No report generated.")
        chart_paths = result.get("chart_paths", [])

        # Collect existing chart images
        charts = [p for p in chart_paths if os.path.exists(p)]

        return profile, analysis, report, charts

    except Exception as e:
        return f"Error: {str(e)}", "", "", []


with gr.Blocks(title="AI Data Analyst Agent") as app:

    gr.Markdown(
        """
        # AI Data Analyst Agent
        Upload a CSV file and a team of AI agents will collaboratively analyze your data.

        **Agents**: Profiler → Analyst → Visualizer → Reporter

        Built with LangGraph + Claude + Gradio
        """
    )

    with gr.Row():
        file_input = gr.File(label="Upload CSV", file_types=[".csv"])
        run_btn = gr.Button("Analyze", variant="primary", size="lg")

    gr.Markdown("---")

    with gr.Tabs():
        with gr.Tab("Report"):
            report_output = gr.Markdown(label="Summary Report")

        with gr.Tab("Data Profile"):
            profile_output = gr.Textbox(
                label="Data Profile",
                lines=25,
            )

        with gr.Tab("Statistical Analysis"):
            analysis_output = gr.Textbox(
                label="Statistical Analysis",
                lines=25,
            )

        with gr.Tab("Charts"):
            gallery_output = gr.Gallery(
                label="Generated Charts",
                columns=2,
                height="auto",
            )

    run_btn.click(
        fn=analyze_csv,
        inputs=[file_input],
        outputs=[profile_output, analysis_output, report_output, gallery_output],
    )

if __name__ == "__main__":
    app.launch(server_port=7860)