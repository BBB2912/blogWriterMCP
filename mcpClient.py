import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient
import os
load_dotenv()
os.environ["GOOGLE_API_KEY"]=os.getenv("GEMINI_API_KEY")
async def run_memory_chat():
    """Run a chat using MCPAgent's built-in conversation memory."""

    # Config file path - change this to your config file
    config_file = "newsCrawler.json"

    print("Initializing chat...")
   
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
    # Create MCP client and agent with memory enabled
    client = MCPClient.from_config_file(config_file)
    llm=llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")

    # Create agent with memory_enabled=True
    agent = MCPAgent(
        llm=llm,
        client=client,
        system_prompt=system_prompt,
        max_steps=15,
        memory_enabled=True,  
        verbose=True
    )

    print("\n===== Interactive MCP Chat =====")
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("==================================\n")

    try:
        # Main chat loop
        while True:
            # Get user input
            user_input = input("\nYou: ")
            

            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation...")
                break

            # Check for clear history command
            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Conversation history cleared.")
                continue

            # Get response from agent
            print("\nAssistant: ", end="", flush=True)

            try:
                # Run the agent with the user input (memory handling is automatic)
                response = await agent.run(user_input)
                print(response)

            except Exception as e:
                print(f"\nError: {e}")

    finally:
        # Clean up
        if client and client.sessions:
            await client.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(run_memory_chat())