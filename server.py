#!/usr/bin/env python3
"""FastMCP server for Linear API - Query initiatives, projects, and documents"""

import os
import json
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
from pydantic import Field
from linear_client import LinearClient
from dotenv import load_dotenv

load_dotenv()

# Create FastMCP server instance
mcp = FastMCP(
    name="linear-initiatives-mcp",
    instructions="Extended Linear MCP server for querying initiatives, projects, and documents with full GraphQL support.\nProvides comprehensive access to Linear workspace data including initiative hierarchies, project details, and associated documentation."
)

# Initialize Linear client
linear_client = LinearClient()


# ============================================================================
# Internal Functions (for direct usage)
# ============================================================================

async def _list_initiatives(
    limit: int = 50,
    search: Optional[str] = None,
    include_archived: bool = False,
    cursor_after: Optional[str] = None,
    cursor_before: Optional[str] = None
) -> Dict[str, Any]:
    """Internal function to list initiatives from Linear workspace"""
    try:
        result = await linear_client.get_initiatives(
            limit=min(limit, 250),
            filter_query=search,
            include_archived=include_archived,
            after=cursor_after,
            before=cursor_before
        )

        initiatives = result.get("initiatives", {})
        nodes = initiatives.get("nodes", [])
        page_info = initiatives.get("pageInfo", {})

        # Format the response
        formatted_initiatives = []
        for initiative in nodes:
            formatted_initiatives.append({
                "id": initiative["id"],
                "name": initiative["name"],
                "description": initiative.get("description"),
                "status": initiative.get("status"),  # status is a string now
                "owner": initiative.get("owner", {}).get("name") if initiative.get("owner") else None,
                "project_count": None,  # Not available in list view
                "target_date": initiative.get("targetDate"),
                "started_at": initiative.get("startedAt"),
                "completed_at": initiative.get("completedAt"),
                "archived_at": initiative.get("archivedAt"),
                "created_at": initiative.get("createdAt"),
                "updated_at": initiative.get("updatedAt"),
                "color": initiative.get("color"),
                "icon": initiative.get("icon")
            })

        return {
            "initiatives": formatted_initiatives,
            "total_count": len(formatted_initiatives),
            "pagination": {
                "has_next_page": page_info.get("hasNextPage", False),
                "has_previous_page": page_info.get("hasPreviousPage", False),
                "end_cursor": page_info.get("endCursor"),
                "start_cursor": page_info.get("startCursor")
            }
        }
    except Exception as e:
        return {"error": str(e)}


async def _get_initiative(id: str) -> Dict[str, Any]:
    """Internal function to get detailed information about a specific initiative"""
    try:
        result = await linear_client.get_initiative(id)
        initiative = result.get("initiative")

        if not initiative:
            return {"error": f"Initiative with ID '{id}' not found"}

        # Format projects
        projects = []
        for project in initiative.get("projects", {}).get("nodes", []):
            projects.append({
                "id": project["id"],
                "name": project["name"],
                "description": project.get("description"),
                "state": project.get("state"),
                "progress": project.get("progress"),
                "target_date": project.get("targetDate")
            })

        # Format documents
        documents = []
        for doc in initiative.get("documents", {}).get("nodes", []):
            documents.append({
                "id": doc["id"],
                "title": doc["title"],
                "created_at": doc.get("createdAt"),
                "updated_at": doc.get("updatedAt")
            })

        return {
            "id": initiative["id"],
            "name": initiative["name"],
            "description": initiative.get("description"),
            "content": initiative.get("content"),
            "status": initiative.get("status"),  # status is a string now
            "owner": {
                "name": initiative.get("owner", {}).get("name"),
                "email": initiative.get("owner", {}).get("email")
            } if initiative.get("owner") else None,
            "project_count": len(projects),  # Count from actual projects array
            "target_date": initiative.get("targetDate"),
            "started_at": initiative.get("startedAt"),
            "completed_at": initiative.get("completedAt"),
            "archived_at": initiative.get("archivedAt"),
            "created_at": initiative.get("createdAt"),
            "updated_at": initiative.get("updatedAt"),
            "color": initiative.get("color"),
            "icon": initiative.get("icon"),
            "projects": projects,
            "documents": documents
        }
    except Exception as e:
        return {"error": str(e)}


async def _list_projects(
    limit: int = 50,
    search: Optional[str] = None,
    include_archived: bool = False,
    team_id: Optional[str] = None,
    initiative_id: Optional[str] = None,
    cursor_after: Optional[str] = None,
    cursor_before: Optional[str] = None
) -> Dict[str, Any]:
    """Internal function to list projects from Linear workspace"""
    try:
        result = await linear_client.get_projects(
            limit=min(limit, 250),
            filter_query=search,
            include_archived=include_archived,
            team_id=team_id,
            initiative_id=initiative_id,
            after=cursor_after,
            before=cursor_before
        )

        projects = result.get("projects", {})
        nodes = projects.get("nodes", [])
        page_info = projects.get("pageInfo", {})

        # Format the response
        formatted_projects = []
        for project in nodes:
            formatted_projects.append({
                "id": project["id"],
                "name": project["name"],
                "description": project.get("description"),
                "state": project.get("state"),
                "progress": project.get("progress"),
                "lead": project.get("lead", {}).get("name") if project.get("lead") else None,
                "teams": [team["name"] for team in project.get("teams", {}).get("nodes", [])],
                "initiatives": [init["name"] for init in project.get("initiatives", {}).get("nodes", [])],
                "target_date": project.get("targetDate"),
                "completed_at": project.get("completedAt"),
                "archived_at": project.get("archivedAt"),
                "color": project.get("color"),
                "icon": project.get("icon")
            })

        return {
            "projects": formatted_projects,
            "total_count": len(formatted_projects),
            "pagination": {
                "has_next_page": page_info.get("hasNextPage", False),
                "has_previous_page": page_info.get("hasPreviousPage", False),
                "end_cursor": page_info.get("endCursor"),
                "start_cursor": page_info.get("startCursor")
            }
        }
    except Exception as e:
        return {"error": str(e)}


async def _get_project(id: str) -> Dict[str, Any]:
    """Internal function to get detailed information about a specific project"""
    try:
        result = await linear_client.get_project(id)
        project = result.get("project")

        if not project:
            return {"error": f"Project with ID '{id}' not found"}

        # Format issues
        issues = []
        for issue in project.get("issues", {}).get("nodes", []):
            issues.append({
                "id": issue["id"],
                "identifier": issue["identifier"],
                "title": issue["title"],
                "state": issue.get("state", {}).get("name") if issue.get("state") else None,
                "state_type": issue.get("state", {}).get("type") if issue.get("state") else None,
                "priority": issue.get("priority")
            })

        # Format documents
        documents = []
        for doc in project.get("documents", {}).get("nodes", []):
            documents.append({
                "id": doc["id"],
                "title": doc["title"],
                "created_at": doc.get("createdAt"),
                "updated_at": doc.get("updatedAt")
            })

        # Format teams
        teams = []
        for team in project.get("teams", {}).get("nodes", []):
            teams.append({
                "id": team["id"],
                "name": team["name"],
                "key": team["key"]
            })

        # Format initiatives
        initiatives = []
        for init in project.get("initiatives", {}).get("nodes", []):
            initiatives.append({
                "id": init["id"],
                "name": init["name"]
            })

        return {
            "id": project["id"],
            "name": project["name"],
            "description": project.get("description"),
            "content": project.get("content"),
            "state": project.get("state"),
            "progress": project.get("progress"),
            "lead": {
                "name": project.get("lead", {}).get("name"),
                "email": project.get("lead", {}).get("email")
            } if project.get("lead") else None,
            "teams": teams,
            "initiatives": initiatives,
            "issues": issues,
            "documents": documents,
            "target_date": project.get("targetDate"),
            "completed_at": project.get("completedAt"),
            "archived_at": project.get("archivedAt"),
            "created_at": project.get("createdAt"),
            "updated_at": project.get("updatedAt"),
            "color": project.get("color"),
            "icon": project.get("icon")
        }
    except Exception as e:
        return {"error": str(e)}


async def _list_documents(
    limit: int = 50,
    search: Optional[str] = None,
    include_archived: bool = False,
    project_id: Optional[str] = None,
    initiative_id: Optional[str] = None,
    cursor_after: Optional[str] = None,
    cursor_before: Optional[str] = None
) -> Dict[str, Any]:
    """Internal function to list documents from Linear workspace"""
    try:
        result = await linear_client.get_documents(
            limit=min(limit, 250),
            filter_query=search,
            include_archived=include_archived,
            project_id=project_id,
            initiative_id=initiative_id,
            after=cursor_after,
            before=cursor_before
        )

        documents = result.get("documents", {})
        nodes = documents.get("nodes", [])
        page_info = documents.get("pageInfo", {})

        # Format the response
        formatted_documents = []
        for doc in nodes:
            formatted_documents.append({
                "id": doc["id"],
                "title": doc["title"],
                "creator": doc.get("creator", {}).get("name") if doc.get("creator") else None,
                "project": doc.get("project", {}).get("name") if doc.get("project") else None,
                "initiative": doc.get("initiative", {}).get("name") if doc.get("initiative") else None,
                "archived_at": doc.get("archivedAt"),
                "created_at": doc.get("createdAt"),
                "updated_at": doc.get("updatedAt"),
                "color": doc.get("color"),
                "icon": doc.get("icon")
            })

        return {
            "documents": formatted_documents,
            "total_count": len(formatted_documents),
            "pagination": {
                "has_next_page": page_info.get("hasNextPage", False),
                "has_previous_page": page_info.get("hasPreviousPage", False),
                "end_cursor": page_info.get("endCursor"),
                "start_cursor": page_info.get("startCursor")
            }
        }
    except Exception as e:
        return {"error": str(e)}


async def _get_document(id: str) -> Dict[str, Any]:
    """Internal function to get detailed information about a specific document"""
    try:
        result = await linear_client.get_document(id)
        doc = result.get("document")

        if not doc:
            return {"error": f"Document with ID '{id}' not found"}

        return {
            "id": doc["id"],
            "title": doc["title"],
            "content": doc.get("content"),
            "creator": {
                "name": doc.get("creator", {}).get("name"),
                "email": doc.get("creator", {}).get("email")
            } if doc.get("creator") else None,
            "project": {
                "id": doc.get("project", {}).get("id"),
                "name": doc.get("project", {}).get("name")
            } if doc.get("project") else None,
            "initiative": {
                "id": doc.get("initiative", {}).get("id"),
                "name": doc.get("initiative", {}).get("name")
            } if doc.get("initiative") else None,
            "archived_at": doc.get("archivedAt"),
            "created_at": doc.get("createdAt"),
            "updated_at": doc.get("updatedAt"),
            "color": doc.get("color"),
            "icon": doc.get("icon")
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# MCP Tool Wrappers
# ============================================================================

# Initiative Tools
@mcp.tool
async def list_initiatives(
    limit: int = Field(default=50, description="Number of initiatives to return (max 250)"),
    search: Optional[str] = Field(default=None, description="Search term to filter initiatives by name"),
    include_archived: bool = Field(default=False, description="Whether to include archived initiatives"),
    cursor_after: Optional[str] = Field(default=None, description="Cursor for pagination (from previous results)"),
    cursor_before: Optional[str] = Field(default=None, description="Cursor for backward pagination")
) -> Dict[str, Any]:
    """List initiatives from Linear workspace"""
    return await _list_initiatives(
        limit=limit,
        search=search,
        include_archived=include_archived,
        cursor_after=cursor_after,
        cursor_before=cursor_before
    )


@mcp.tool
async def get_initiative(
    id: str = Field(description="The ID of the initiative to retrieve")
) -> Dict[str, Any]:
    """Get detailed information about a specific initiative, including its projects and documents"""
    return await _get_initiative(id)


# Project Tools
@mcp.tool
async def list_projects(
    limit: int = Field(default=50, description="Number of projects to return (max 250)"),
    search: Optional[str] = Field(default=None, description="Search term to filter projects by name"),
    include_archived: bool = Field(default=False, description="Whether to include archived projects"),
    team_id: Optional[str] = Field(default=None, description="Filter by team ID"),
    initiative_id: Optional[str] = Field(default=None, description="Filter by initiative ID"),
    cursor_after: Optional[str] = Field(default=None, description="Cursor for pagination (from previous results)"),
    cursor_before: Optional[str] = Field(default=None, description="Cursor for backward pagination")
) -> Dict[str, Any]:
    """List projects from Linear workspace"""
    return await _list_projects(
        limit=limit,
        search=search,
        include_archived=include_archived,
        team_id=team_id,
        initiative_id=initiative_id,
        cursor_after=cursor_after,
        cursor_before=cursor_before
    )


@mcp.tool
async def get_project(
    id: str = Field(description="The ID of the project to retrieve")
) -> Dict[str, Any]:
    """Get detailed information about a specific project, including its issues and documents"""
    return await _get_project(id)


# Document Tools
@mcp.tool
async def list_documents(
    limit: int = Field(default=50, description="Number of documents to return (max 250)"),
    search: Optional[str] = Field(default=None, description="Search term to filter documents by title"),
    include_archived: bool = Field(default=False, description="Whether to include archived documents"),
    project_id: Optional[str] = Field(default=None, description="Filter by project ID"),
    initiative_id: Optional[str] = Field(default=None, description="Filter by initiative ID"),
    cursor_after: Optional[str] = Field(default=None, description="Cursor for pagination (from previous results)"),
    cursor_before: Optional[str] = Field(default=None, description="Cursor for backward pagination")
) -> Dict[str, Any]:
    """List documents from Linear workspace"""
    return await _list_documents(
        limit=limit,
        search=search,
        include_archived=include_archived,
        project_id=project_id,
        initiative_id=initiative_id,
        cursor_after=cursor_after,
        cursor_before=cursor_before
    )


@mcp.tool
async def get_document(
    id: str = Field(description="The ID of the document to retrieve")
) -> Dict[str, Any]:
    """Get detailed information about a specific document, including its full content"""
    return await _get_document(id)


# Run the server
if __name__ == "__main__":
    # Run with stdio transport (default)
    mcp.run()
