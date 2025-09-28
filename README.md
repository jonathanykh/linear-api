# Linear API MCP Server

Extended Linear MCP server for querying initiatives, projects, and documents with full GraphQL support.
Provides comprehensive access to Linear workspace data including initiative hierarchies, project details, and associated documentation.

## Features

- **Initiatives**: List and get detailed information about Linear initiatives
- **Projects**: Query projects with filtering by team or initiative
- **Documents**: Access Linear documents with project/initiative filtering
- Full pagination support for all list operations
- Detailed views including related entities (projects in initiatives, issues in projects, etc.)

## Prerequisites

- Python 3.11+
- Linear API key (get it from [Linear Settings](https://linear.app/settings/api))
- `uv` package manager

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd linear-api
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Set up your Linear API key:
```bash
cp .env.example .env
# Edit .env and add your Linear API key
```

## Usage

### Running the Server

You can run the server in several ways:

#### 1. Direct Python execution:
```bash
uv run python server.py
```

#### 2. Using FastMCP CLI:
```bash
uv run fastmcp run server.py
```

#### 3. For development/testing with FastMCP:
```bash
uv run fastmcp dev server.py
```

### Integrating with Claude Desktop

Add the following to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "linear-api": {
      "command": "uv",
      "args": ["run", "python", "/path/to/linear-api/server.py"],
      "env": {
        "LINEAR_API_KEY": "your-linear-api-key-here"
      }
    }
  }
}
```

### Available Tools

#### Initiative Tools

1. **list_initiatives** - List all initiatives
   - Parameters:
     - `limit` (int): Number of results to return (max 250)
     - `search` (string): Search term for filtering by name
     - `include_archived` (bool): Include archived initiatives
     - `cursor_after` (string): Pagination cursor
     - `cursor_before` (string): Backward pagination cursor

2. **get_initiative** - Get detailed initiative information
   - Parameters:
     - `id` (string): Initiative ID

#### Project Tools

3. **list_projects** - List all projects
   - Parameters:
     - `limit` (int): Number of results to return (max 250)
     - `search` (string): Search term for filtering by name
     - `include_archived` (bool): Include archived projects
     - `team_id` (string): Filter by team ID
     - `initiative_id` (string): Filter by initiative ID
     - `cursor_after` (string): Pagination cursor
     - `cursor_before` (string): Backward pagination cursor

4. **get_project** - Get detailed project information
   - Parameters:
     - `id` (string): Project ID

#### Document Tools

5. **list_documents** - List all documents
   - Parameters:
     - `limit` (int): Number of results to return (max 250)
     - `search` (string): Search term for filtering by title
     - `include_archived` (bool): Include archived documents
     - `project_id` (string): Filter by project ID
     - `initiative_id` (string): Filter by initiative ID
     - `cursor_after` (string): Pagination cursor
     - `cursor_before` (string): Backward pagination cursor

6. **get_document** - Get detailed document information
   - Parameters:
     - `id` (string): Document ID

## Example Usage

Once connected to an MCP client, you can use the tools like this:

```
// List all active initiatives
list_initiatives(limit=10)

// Search for specific projects
list_projects(search="Mobile App", include_archived=false)

// Get detailed information about a specific project
get_project(id="PROJECT_ID_HERE")

// List documents for a specific initiative
list_documents(initiative_id="INITIATIVE_ID", limit=20)
```

## Testing

### Test Your Connection First

Before running any tests, verify your Linear API connection:
```bash
uv run python test_connection.py
```

This will:
- Check if your API key is set correctly
- Verify the API key format
- Test authentication with Linear
- Show your Linear account details if successful

### Direct Testing Without MCP Client

You can test the Linear API functions directly without setting up an MCP client:

#### 1. Automated Test Suite
Run comprehensive tests of all functions:
```bash
uv run python test_api.py
```

#### 2. Interactive Testing
Test specific functions with custom parameters:
```bash
# Interactive menu mode
uv run python interactive_test.py

# Quick test mode (command line)
uv run python interactive_test.py list_initiatives 10
uv run python interactive_test.py get_initiative <INITIATIVE_ID>
uv run python interactive_test.py list_projects 5
uv run python interactive_test.py get_project <PROJECT_ID>
uv run python interactive_test.py list_documents 20
uv run python interactive_test.py get_document <DOCUMENT_ID>
```

## Development

To modify or extend the server:

1. Edit `server.py` to add new tools or modify existing ones
2. Update `linear_client.py` to add new GraphQL queries
3. Test locally using `uv run fastmcp dev server.py`
4. Use `test_api.py` or `interactive_test.py` to test your changes

## License

MIT