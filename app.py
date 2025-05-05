import gradio as gr
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

# System prompt
system_prompt = """
You are an AI research assistant and professional blog writer. Your task is to create high-quality, well-researched, original blog posts in **HTML format with embedded CSS styling**.

You have access to the following tools:

1. `scrape_wikipedia(topic: str)`  
   → Use this tool to retrieve a summary, full content, and URL from Wikipedia for the given topic.

2. `exa_search(query: str, num_results: int)`  
   → Use this tool to search the web and retrieve the latest, most relevant URLs related to the topic.

3. `scrape_webpage(url: str)`  
   → Use this tool to scrape the main content of a webpage, including the title, article body, and image URLs.

Use these tools strategically to gather reliable information and enrich the blog content.

Your output must follow these guidelines:
1. Use semantic HTML tags: <h1>, <h2>, <p>, <img>, etc.
2. Add **inline CSS styling** inside a <style> block in <head> to control layout, typography, image sizes (max-width: 100%; height: auto), padding, and margins.
3. Include **at least 2 relevant images** using <img src="image_url">, choosing the best images from scraped content.
4. Follow blogging best practices: clear introduction, logical subheadings, short paragraphs, good readability, conclusion.
5. Ensure valid HTML structure.

👉 Example output structure:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Blog Title</title>
  <style>
     body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: auto; padding: 20px; }}
     img {{ max-width: 100%; height: auto; display: block; margin: 20px 0; }}
     h1, h2 {{ color: #333; }}
     p {{ color: #555; }}
  </style>
</head>
<body>
  <h1>Blog Title</h1>
  <p>Introduction paragraph...</p>
  <h2>Subheading 1</h2>
  <p>Content paragraph...</p>
  <img src="image_url_1">
  <h2>Subheading 2</h2>
  <p>More content...</p>
  <img src="image_url_2">
  <p>Conclusion paragraph...</p>
</body>
</html>
"""

# Initialize MCP client and agent globally
config_file = "newsCrawler.json"
client = MCPClient.from_config_file(config_file)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")
agent = MCPAgent(
    llm=llm,
    client=client,
    system_prompt=system_prompt,
    max_steps=15,
    memory_enabled=True,
    verbose=True
)

# Store logs globally
terminal_logs = []

async def get_response(user_input):
    """Async function to get agent's response."""
    response = await agent.run(user_input)
    return response

def handle_input(user_input, chat_history):
    """Handles user input from sidebar textbox."""
    if user_input.strip().lower() in ["exit", "quit"]:
        terminal_logs.append("Session ended by user.")
        return chat_history + [("You: " + user_input, "Session ended.")], "", "\n".join(terminal_logs)

    if user_input.strip().lower() == "clear":
        agent.clear_conversation_history()
        terminal_logs.append("Conversation history cleared.")
        return [], "", "\n".join(terminal_logs)

    terminal_logs.append(f"Running agent for input: {user_input}")

    # Handle asyncio event loop safely
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Inside running loop (e.g., Jupyter, Gradio async backend)
            response = asyncio.ensure_future(get_response(user_input))
            response = loop.run_until_complete(response)
        else:
            # Normal script
            response = loop.run_until_complete(get_response(user_input))
    except RuntimeError:
        # No loop exists yet
        response = asyncio.run(get_response(user_input))
    except Exception as e:
        response = f"Error: {str(e)}"
        terminal_logs.append(response)
        return chat_history + [("You: " + user_input, "Assistant: Error")], "", "\n".join(terminal_logs[-20:])

    terminal_logs.append("Agent responded successfully.")

    chat_history.append(("You: " + user_input, "Assistant: [Response generated]"))
    return chat_history, response, "\n".join(terminal_logs[-20:])  # show last 20 logs

# Gradio Blocks UI
with gr.Blocks(title="AI Blog Writer with Sidebar") as app:
    with gr.Row():
        # Sidebar (left)
        with gr.Column(scale=1, min_width=300, elem_id="left-sidebar"):
            gr.Markdown("## 📝 Chat History")
            chat_view = gr.Chatbot(height=300)

            gr.Markdown("## 🖥️ Terminal Logs")
            terminal_output = gr.Textbox(lines=15, interactive=False, show_copy_button=True, label="Logs")

            user_input = gr.Textbox(placeholder="Type your prompt here...", label="💬 Enter prompt")
            send_button = gr.Button("Generate Blog")

        # Main output area (right)
        with gr.Column(scale=3, elem_id="right-column"):
            gr.Markdown("## 📰 Generated Blog Preview")
            html_output = gr.HTML(label="Blog Preview")

    # Button event
    send_button.click(
        fn=handle_input,
        inputs=[user_input, chat_view],
        outputs=[chat_view, html_output, terminal_output]
    )

    # Apply custom CSS styling
    app.css = """
        /* Apply background color to the left sidebar */
        #left-sidebar {
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
        }

        /* Style the right column (blog preview) */
        #right-column {
            padding: 20px;
            background-color: #ffffff;
            border-radius: 10px;
        }

        /* Adjust width and margins for better responsiveness */
        .gradio-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }

        .gradio-column {
            padding: 15px;
        }

        /* Set width constraints for responsive design */
        .gradio-column#right-column {
            max-width: 800px;
        }

        /* Styling for images in the blog preview */
        #right-column img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px 0;
        }

        /* Add margins for cleaner UI */
        .gradio-textbox {
            margin-bottom: 20px;
        }

        /* Style the Markdown headers */
        h1, h2 {
            color: #333;
        }

        p {
            color: #555;
        }
    """

app.launch()
