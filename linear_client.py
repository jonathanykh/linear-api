"""Linear API Client for GraphQL queries"""

import os
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class LinearClient:
    """Client for interacting with Linear GraphQL API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("LINEAR_API_KEY")
        if not self.api_key:
            raise ValueError("LINEAR_API_KEY is required. Set it as environment variable or pass it to the constructor.")

        self.base_url = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

    async def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query against Linear API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    json={"query": query, "variables": variables or {}},
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # Try to get more details from the response
                try:
                    error_detail = e.response.json()
                    error_msg = f"Linear API error {e.response.status_code}: {error_detail}"
                except:
                    error_msg = f"Linear API error {e.response.status_code}: {e.response.text}"

                if e.response.status_code == 400:
                    error_msg += "\n\nCommon causes:\n"
                    error_msg += "1. Invalid API key - Check that LINEAR_API_KEY is set correctly\n"
                    error_msg += "2. API key should start with 'lin_api_'\n"
                    error_msg += "3. Get your API key from: https://linear.app/settings/api"
                elif e.response.status_code == 401:
                    error_msg = "Authentication failed. Your Linear API key is invalid or expired.\n"
                    error_msg += "Get a new key from: https://linear.app/settings/api"

                raise Exception(error_msg) from e
            except httpx.RequestError as e:
                raise Exception(f"Network error connecting to Linear API: {str(e)}") from e

            data = response.json()
            if "errors" in data:
                error_details = "\n".join([f"- {err.get('message', str(err))}" for err in data['errors']])
                raise Exception(f"GraphQL errors:\n{error_details}")
            return data.get("data", {})

    async def get_initiatives(
        self,
        limit: int = 50,
        filter_query: Optional[str] = None,
        include_archived: bool = False,
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get initiatives from Linear"""
        query = """
        query GetInitiatives($first: Int, $after: String, $before: String) {
            initiatives(first: $first, after: $after, before: $before) {
                nodes {
                    id
                    name
                    description
                    status
                    owner {
                        id
                        name
                        email
                    }
                    targetDate
                    startedAt
                    completedAt
                    archivedAt
                    createdAt
                    updatedAt
                    icon
                    color
                }
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                    endCursor
                    startCursor
                }
            }
        }
        """

        variables = {
            "first": limit,
            "after": after,
            "before": before
        }

        # Note: Linear API doesn't support filtering archived initiatives in the query
        # The include_archived parameter is kept for compatibility but doesn't affect the query

        return await self.query(query, variables)

    async def get_initiative(self, id: str) -> Dict[str, Any]:
        """Get a single initiative by ID"""
        query = """
        query GetInitiative($id: String!) {
            initiative(id: $id) {
                id
                name
                description
                content
                status
                owner {
                    id
                    name
                    email
                }
                targetDate
                startedAt
                completedAt
                archivedAt
                createdAt
                updatedAt
                icon
                color
                projects(first: 50) {
                    nodes {
                        id
                        name
                        description
                        state
                        progress
                        startedAt
                        targetDate
                    }
                }
                documents(first: 50) {
                    nodes {
                        id
                        title
                        content
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """
        return await self.query(query, {"id": id})

    async def get_projects(
        self,
        limit: int = 50,
        filter_query: Optional[str] = None,
        include_archived: bool = False,
        team_id: Optional[str] = None,
        initiative_id: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get projects from Linear"""
        query = """
        query GetProjects($first: Int, $after: String, $before: String, $filter: ProjectFilter) {
            projects(first: $first, after: $after, before: $before, filter: $filter) {
                nodes {
                    id
                    name
                    description
                    state
                    progress
                    startedAt
                    startDate
                    targetDate
                    completedAt
                    canceledAt
                    archivedAt
                    createdAt
                    updatedAt
                    icon
                    color
                    slugId
                    lead {
                        id
                        name
                        email
                    }
                    teams(first: 10) {
                        nodes {
                            id
                            name
                            key
                        }
                    }
                    initiatives(first: 10) {
                        nodes {
                            id
                            name
                        }
                    }
                }
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                    endCursor
                    startCursor
                }
            }
        }
        """

        variables = {
            "first": limit,
            "after": after,
            "before": before
        }

        # Build filter if needed
        filter_obj = {}
        if filter_query:
            filter_obj["name"] = {"contains": filter_query}

        if team_id:
            filter_obj["teams"] = {"some": {"id": {"eq": team_id}}}

        if initiative_id:
            filter_obj["initiatives"] = {"some": {"id": {"eq": initiative_id}}}

        if filter_obj:
            variables["filter"] = filter_obj

        return await self.query(query, variables)

    async def get_project(self, id: str) -> Dict[str, Any]:
        """Get a single project by ID"""
        query = """
        query GetProject($id: String!) {
            project(id: $id) {
                id
                name
                description
                content
                state
                progress
                startedAt
                startDate
                targetDate
                completedAt
                canceledAt
                archivedAt
                createdAt
                updatedAt
                icon
                color
                slugId
                lead {
                    id
                    name
                    email
                }
                teams(first: 50) {
                    nodes {
                        id
                        name
                        key
                    }
                }
                issues(first: 50) {
                    nodes {
                        id
                        title
                        identifier
                        state {
                            name
                            type
                        }
                        priority
                    }
                }
                documents(first: 50) {
                    nodes {
                        id
                        title
                        content
                        createdAt
                        updatedAt
                    }
                }
                initiatives(first: 50) {
                    nodes {
                        id
                        name
                    }
                }
            }
        }
        """
        return await self.query(query, {"id": id})

    async def get_documents(
        self,
        limit: int = 50,
        filter_query: Optional[str] = None,
        include_archived: bool = False,
        project_id: Optional[str] = None,
        initiative_id: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get documents from Linear"""
        query = """
        query GetDocuments($first: Int, $after: String, $before: String, $filter: DocumentFilter) {
            documents(first: $first, after: $after, before: $before, filter: $filter) {
                nodes {
                    id
                    title
                    content
                    icon
                    color
                    archivedAt
                    createdAt
                    updatedAt
                    creator {
                        id
                        name
                        email
                    }
                    project {
                        id
                        name
                    }
                    initiative {
                        id
                        name
                    }
                }
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                    endCursor
                    startCursor
                }
            }
        }
        """

        variables = {
            "first": limit,
            "after": after,
            "before": before
        }

        # Build filter if needed
        filter_obj = {}
        if filter_query:
            filter_obj["title"] = {"contains": filter_query}

        if project_id:
            filter_obj["project"] = {"id": {"eq": project_id}}

        if initiative_id:
            filter_obj["initiative"] = {"id": {"eq": initiative_id}}

        if filter_obj:
            variables["filter"] = filter_obj

        return await self.query(query, variables)

    async def get_document(self, id: str) -> Dict[str, Any]:
        """Get a single document by ID"""
        query = """
        query GetDocument($id: String!) {
            document(id: $id) {
                id
                title
                content
                icon
                color
                archivedAt
                createdAt
                updatedAt
                creator {
                    id
                    name
                    email
                }
                project {
                    id
                    name
                }
                initiative {
                    id
                    name
                }
            }
        }
        """
        return await self.query(query, {"id": id})