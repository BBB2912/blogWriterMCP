# server.py
import requests
import wikipedia
from bs4 import BeautifulSoup
from loguru import logger
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv
from exa_py import Exa
import os

load_dotenv()
exa = Exa(os.getenv('EXA_API_KEY'))

# Create an MCP server
mcp = FastMCP("Web Tools MCP")

@mcp.tool(
    name="exa_search_tool",
    description="Performs a search using the Exa API and returns recent results with text and highlights.",
)
def exa_search_tool(topic: str, num_results: int = 5) -> str:
    """
    Perform a Google-like search using the Exa API and return the top search results with text and highlights.
    Filters results to the last 10 days.
    """
    logger.info(f"Searching Exa API for topic: {topic} (top {num_results} results)")
    try:
        results = exa.search_and_contents(
            topic,
            text=True,
            highlights=True,
            start_published_date=(datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            num_results=num_results
        )
        return results
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(
    name="webpage_scraper",
    description="Scrapes and returns visible text content from the given webpage URL.",
)
def webpage_scraper(url: str) -> str:
    """Scrape visible text from a webpage URL."""
    logger.info(f"Scraping webpage: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = [p.text for p in soup.find_all('p')]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    logger.info("Starting server...")
    mcp.run(transport="stdio")
