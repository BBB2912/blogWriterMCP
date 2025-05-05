from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

# Declare globals
agent = None
client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent, client
    print("Starting up...")

    config_file = "newsCrawler.json"
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

    yield  # app is ready

    print("Shutting down...")
    if client and client.sessions:
        await client.close_all_sessions()

app = FastAPI(lifespan=lifespan)


@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_input = data.get("message")

    if not user_input:
        return JSONResponse(content={"error": "No message provided"}, status_code=400)

    try:
        response = await agent.run(user_input)
        return JSONResponse(content={"response": response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/clear")
async def clear_endpoint():
    agent.clear_conversation_history()
    return JSONResponse(content={"message": "Conversation history cleared"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastAPI:app", host="0.0.0.0", port=8000, reload=True)
