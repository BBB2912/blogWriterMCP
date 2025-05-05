# BlogWriter MCP

BlogWriter MCP is a project designed to streamline the process of writing and managing blogs using APIs and tools like `exa_search`, `gemini`, and the `uv` package manager.

## Features
- Integration with `exa_search` API for content discovery.
- Integration with `gemini` API for advanced text processing.
- Managed dependencies using the `uv` package manager.

## Prerequisites
- `uv` package manager installed globally. / you can use pip as well

## Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd blogWriterMCP
```

### 2. Install Dependencies
```bash
uv install
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and add the following keys:
```
EXA_SEARCH_API_KEY=your_exa_search_api_key
GEMINI_API_KEY=your_gemini_api_key
```

Replace `your_exa_search_api_key` and `your_gemini_api_key` with your actual API keys.

## Commands
create mcp configuration json for your mcp server

```bash
uv run mcp install <server.py> 
```
this will create a json or follow this json for manual.
```bash
{
    "mcpServers": {
      "<serverName>": {
      "<command uv/pip>": "C:/Users/User/.local/bin/uv",
      "args": [
        "--directory",
        "directory path where your server script located",
        "run",
        "<server_script_Name>.py" 
      ]
    }
    }
  }
```

### Start the Project
```bash
uv run mcpClient.py
```



## License
This project is licensed under the MIT License.

## Contributing
Feel free to submit issues or pull requests to improve the project.

## Contact
For any inquiries, please contact [your-email@example.com].