#!/usr/bin/env python3
"""Debug script to test milestone queries directly"""

import asyncio
import json
from linear_client import LinearClient
from dotenv import load_dotenv

load_dotenv()


async def test_milestone_query():
    """Test milestone queries with different approaches"""

    client = LinearClient()
    project_id = "8c9001da-246e-46c8-b081-852b9da27e63"  # Data indexing project

    print("=" * 60)
    print("MILESTONE DEBUGGING")
    print("=" * 60)
    print(f"Testing project: {project_id}")
    print()

    # Test 1: Simple milestone query
    print("Test 1: Basic projectMilestones query")
    print("-" * 40)
    query1 = """
    query GetProjectMilestones($id: String!) {
        project(id: $id) {
            id
            name
            projectMilestones {
                nodes {
                    id
                    name
                }
            }
        }
    }
    """

    try:
        result = await client.query(query1, {"id": project_id})
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n")

    # Test 2: Try with pagination parameters
    print("Test 2: With pagination parameters")
    print("-" * 40)
    query2 = """
    query GetProjectMilestones($id: String!) {
        project(id: $id) {
            id
            name
            projectMilestones(first: 10) {
                nodes {
                    id
                    name
                    targetDate
                    status
                    progress
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
    }
    """

    try:
        result = await client.query(query2, {"id": project_id})
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n")

    # Test 3: Try includeArchived
    print("Test 3: With includeArchived parameter")
    print("-" * 40)
    query3 = """
    query GetProjectMilestones($id: String!) {
        project(id: $id) {
            id
            name
            projectMilestones(first: 10, includeArchived: true) {
                nodes {
                    id
                    name
                    targetDate
                    status
                    progress
                    archivedAt
                }
            }
        }
    }
    """

    try:
        result = await client.query(query3, {"id": project_id})
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n")

    # Test 4: Check if milestones exist via global query
    print("Test 4: Query all project milestones globally")
    print("-" * 40)
    query4 = """
    query GetAllMilestones {
        projectMilestones(first: 10) {
            nodes {
                id
                name
                project {
                    id
                    name
                }
            }
        }
    }
    """

    try:
        result = await client.query(query4, {})
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n")

    # Test 5: Check if project has different milestone field
    print("Test 5: Check all project fields")
    print("-" * 40)
    query5 = """
    query GetProject($id: String!) {
        project(id: $id) {
            id
            name
            state
            progress
        }
    }
    """

    try:
        result = await client.query(query5, {"id": project_id})
        print(f"Basic project info: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_milestone_query())