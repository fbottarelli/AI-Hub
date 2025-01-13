import gradio as gr
from ...backend.services.github_service import GitHubService

def create_github_tab():
    """Create the GitHub ingestion tab"""
    
    with gr.Column():
        gr.Markdown("## 📊 GitHub Repository Analyzer")
        
        with gr.Row():
            repo_url = gr.Textbox(
                label="GitHub Repository URL",
                placeholder="Enter GitHub repository URL...",
                scale=4
            )
            output_format = gr.Dropdown(
                choices=["all", "summary", "tree", "content"],
                value="all",
                label="Output Format",
                scale=1
            )

        with gr.Row():
            analyze_btn = gr.Button("🔍 Analyze Repository", variant="primary")
            copy_analysis_btn = gr.Button("📋 Copy Analysis", variant="secondary")
            copy_content_btn = gr.Button("📄 Copy Repository Content", variant="secondary")

        with gr.Column():
            summary_box = gr.Textbox(label="Summary", lines=5, interactive=False)
            tree_box = gr.Textbox(label="Directory Structure", lines=10, interactive=False)
            content_box = gr.Textbox(label="Content Analysis", lines=10, interactive=False)
            raw_content_box = gr.Textbox(label="Raw Content", visible=False)
            markdown_path = gr.Textbox(label="Markdown File Path", visible=False)

        def analyze_repo(url, format_choice):
            summary, tree, content, md_path = GitHubService.analyze_repository(url, format_choice)
            raw_content = GitHubService.get_raw_content(url)
            return summary, tree, content, raw_content, md_path

        analyze_btn.click(
            fn=analyze_repo,
            inputs=[repo_url, output_format],
            outputs=[summary_box, tree_box, content_box, raw_content_box, markdown_path]
        )

        # Add JavaScript for copying analysis
        copy_analysis_js = """
        async function copyToClipboard(summary, tree, content) {
            const text = [
                "Summary:", 
                summary,
                "\nDirectory Structure:",
                tree,
                "\nContent Analysis:",
                content
            ].filter(Boolean).join("\n");
            
            try {
                await navigator.clipboard.writeText(text);
                console.log("Analysis copied to clipboard");
            } catch (err) {
                console.error("Failed to copy analysis: ", err);
            }
        }
        """

        # Add JavaScript for copying raw content
        copy_content_js = """
        async function copyContent(content) {
            try {
                await navigator.clipboard.writeText(content);
                console.log("Repository content copied to clipboard");
            } catch (err) {
                console.error("Failed to copy content: ", err);
            }
        }
        """

        copy_analysis_btn.click(
            fn=lambda x,y,z: None,
            inputs=[summary_box, tree_box, content_box],
            outputs=None,
            js=copy_analysis_js
        )

        copy_content_btn.click(
            fn=lambda x: None,
            inputs=[raw_content_box],
            outputs=None,
            js=copy_content_js
        )
        
        gr.Markdown("""
        ### Features:
        - Analyze any GitHub repository
        - Get repository structure and content summary
        - Generate LLM-friendly text digest
        - Export analysis as Markdown
        - Copy analysis or full repository content to clipboard
        """) 