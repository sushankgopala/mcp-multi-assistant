# MCP Multi-Tool AI Assistant

A beginner-friendly Model Context Protocol (MCP) project built using Python and Ollama. The assistant connects to multiple independent MCP servers and uses their tools through a local language model.

## Features

- **Task Manager MCP Server:** Create, list, and complete tasks using SQLite.
- **Notes MCP Server:** Save and search notes using JSON storage.
- **Calculator MCP Server:** Perform arithmetic operations.
- **Multi-Server MCP Client:** Discover tools dynamically and route calls to the correct server.
- **Local AI Integration:** Use Ollama without a paid LLM API.
- **MCP Resources and Prompts:** Expose saved notes and reusable prompt templates.

## Architecture

The Python client connects to three MCP servers over stdio. It discovers their tools, supplies the tool definitions to Ollama, executes requested calls through the appropriate MCP connection, and returns results to the model.

## Tech Stack

- Python
- Model Context Protocol (MCP)
- Ollama
- SQLite
- JSON

## Setup

1. Install Python 3.12, Conda, and Ollama.
2. Download a compatible local model:

   `ollama pull qwen3:4b`

3. Create and activate a Conda environment:

   `conda create -n mcp-multi python=3.12 -y`

   `conda activate mcp-multi`

4. Install dependencies:

   `python -m pip install -r requirements.txt`

5. Run the assistant:

   `python client.py`

## Project Structure

- `task_server.py` — task management tools
- `notes_server.py` — notes tools, resource, and prompt
- `math_server.py` — calculator tools
- `client.py` — multi-server client and Ollama orchestration

## Learning Objectives

This project explores MCP servers and clients, tool discovery, tool execution, stdio transport, resources, prompts, and multi-server orchestration.

## Notes

Local task data and notes are stored on your machine. The project uses Ollama for local model inference, although model performance depends on your hardware and configuration.