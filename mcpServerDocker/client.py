import asyncio
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient
import os
import nest_asyncio
nest_asyncio.apply()
# Load environment variables
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

# Set Streamlit page config
st.set_page_config(layout="wide", page_title="AI Blog Assistant")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'terminal_logs' not in st.session_state:
    st.session_state.terminal_logs = []

if 'generated_html' not in st.session_state:
    st.session_state.generated_html = ""

# Sidebar: Chat history + terminal logs
with st.sidebar:
    st.header("📝 Chat History")
    for entry in st.session_state.chat_history:
        st.markdown(f"**You:** {entry['user']}")
        st.markdown(f"**Assistant:** {entry['assistant']}")
    
    st.divider()
    st.header("🖥️ Terminal Logs")
    for log in st.session_state.terminal_logs[-20:]:  # last 20 logs
        st.text(log)

# Main page: Render generated HTML
st.header("📰 Generated Blog Preview")
if st.session_state.generated_html:
    st.markdown(st.session_state.generated_html, unsafe_allow_html=True)
else:
    st.info("No blog content generated yet. Ask something to start!")

# Text input at bottom
user_input = st.text_input("💬 Type your message here", "")

config_file = "../newsCrawler.json"
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
"""
# Initialize LLM and Agent
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

async def get_response(user_input):
    """Async function to get agent's response."""
    response = await agent.run(user_input)
    return response

def chat(user_input, history):
    """Wrapper function for Gradio to handle async inside worker thread."""
    if user_input.lower() in ["exit", "quit"]:
        return history + [[user_input, "Session ended."]], history
    elif user_input.lower() == "clear":
        agent.clear_conversation_history()
        return history + [[user_input, "Conversation history cleared."]], history

    # 🔥 Create a new event loop inside the thread (fix)

    
    response = asyncio.get_event_loop().run_until_complete(get_response(user_input))

    return response

def run_agent_input(user_input,history):
    
    try:
        st.session_state.terminal_logs.append("Starting agent execution...")

        response = chat(user_input,history)
        st.session_state.terminal_logs.append("Agent response received.")
        
        # Save response
        st.session_state.chat_history.append({"user": user_input, "assistant": response})
        st.session_state.generated_html = response
        
    except Exception as e:
        st.session_state.terminal_logs.append(f"Error: {str(e)}")
    
    finally:
        if client and client.sessions:
             client.close_all_sessions()
        st.session_state.terminal_logs.append("Closed all client sessions.")

# Handle user input
if user_input:
    run_agent_input(user_input,st.session_state.chat_history)
    st.rerun()  # refresh page to show updated chat

