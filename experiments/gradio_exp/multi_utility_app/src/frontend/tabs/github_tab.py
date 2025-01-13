import gradio as gr
from ...backend.services.github_service import GitHubService

def create_github_tab():
    """Create the GitHub ingestion tab"""
    
    with gr.Column():
        gr.Markdown("## GitHub Repository Ingestion")
        gr.Markdown("Enter a GitHub repository URL to analyze and create a text digest.")
        
        with gr.Row():
            input_url = gr.Textbox(
                label="GitHub Repository URL",
                placeholder="https://github.com/username/repo",
                scale=4
            )
            analyze_btn = gr.Button("Analyze", scale=1)
        
        with gr.Column():
            with gr.Accordion("Advanced Options", open=False):
                output_format = gr.Radio(
                    choices=["summary", "tree", "content", "all"],
                    value="all",
                    label="Output Format",
                    info="Choose what information to include in the digest"
                )
        
        with gr.Column():
            with gr.Row():
                download_btn = gr.Button("📥 Download as Markdown")
                markdown_path = gr.Textbox(visible=False)
            
            with gr.Column():
                with gr.Row():
                    output_summary = gr.Textbox(
                        label="Repository Summary",
                        interactive=False,
                        lines=3,
                        show_copy_button=True
                    )
                
                with gr.Row():
                    output_tree = gr.Textbox(
                        label="Directory Tree",
                        interactive=False,
                        lines=10,
                        show_copy_button=True
                    )
                
                with gr.Row():
                    output_content = gr.Textbox(
                        label="Content Digest",
                        interactive=False,
                        lines=15,
                        show_copy_button=True
                    )
        
        analyze_btn.click(
            fn=GitHubService.analyze_repository,
            inputs=[input_url, output_format],
            outputs=[output_summary, output_tree, output_content, markdown_path]
        )
        
        def download_markdown(path):
            if path:
                return path
            return None
        
        download_btn.click(
            fn=download_markdown,
            inputs=[markdown_path],
            outputs=[gr.File(label="Analysis Report")]
        )
        
        gr.Markdown("""
        ### Features:
        - Analyze any GitHub repository
        - Get repository structure and content summary
        - Generate LLM-friendly text digest
        - Export analysis as Markdown
        - Copy results to clipboard
        """) 