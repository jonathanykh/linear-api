#!/usr/bin/env python3
"""Direct testing script for Linear API functions"""

import asyncio
import json
from linear_client import LinearClient
from dotenv import load_dotenv

load_dotenv()


async def test_linear_api():
    """Test all Linear API functions directly"""

    # Initialize the client
    client = LinearClient()

    print("=" * 60)
    print("TESTING LINEAR API FUNCTIONS")
    print("=" * 60)

    # Test 1: List Initiatives
    print("\n1. Testing list_initiatives (first 5)...")
    print("-" * 40)
    try:
        result = await client.get_initiatives(limit=5)
        initiatives = result.get("initiatives", {}).get("nodes", [])
        print(f"Found {len(initiatives)} initiatives:")
        for init in initiatives:
            print(f"  - {init.get('name')} (ID: {init.get('id')})")
            if init.get('description'):
                print(f"    Description: {init.get('description')[:50]}...")
            print(f"    Status: {init.get('status', {}).get('name') if init.get('status') else 'No status'}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Get a specific initiative (if any exist)
    if initiatives:
        print(f"\n2. Testing get_initiative for '{initiatives[0].get('name')}'...")
        print("-" * 40)
        try:
            result = await client.get_initiative(initiatives[0]['id'])
            init = result.get("initiative")
            if init:
                print(f"Name: {init.get('name')}")
                print(f"Progress: {init.get('progress')}")
                print(f"Project Count: {init.get('projectCount')}")
                projects = init.get('projects', {}).get('nodes', [])
                print(f"Associated Projects: {len(projects)}")
                for proj in projects[:3]:  # Show first 3
                    print(f"  - {proj.get('name')}")
        except Exception as e:
            print(f"Error: {e}")

    # Test 3: List Projects
    print("\n3. Testing list_projects (first 5)...")
    print("-" * 40)
    try:
        result = await client.get_projects(limit=5)
        projects = result.get("projects", {}).get("nodes", [])
        print(f"Found {len(projects)} projects:")
        for proj in projects:
            print(f"  - {proj.get('name')} (ID: {proj.get('id')})")
            print(f"    State: {proj.get('state')}")
            print(f"    Progress: {proj.get('progress')}")
            teams = proj.get('teams', {}).get('nodes', [])
            if teams:
                print(f"    Teams: {', '.join([t.get('name') for t in teams])}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 4: Get a specific project (if any exist)
    if projects:
        print(f"\n4. Testing get_project for '{projects[0].get('name')}'...")
        print("-" * 40)
        try:
            result = await client.get_project(projects[0]['id'])
            proj = result.get("project")
            if proj:
                print(f"Name: {proj.get('name')}")
                print(f"State: {proj.get('state')}")
                print(f"Progress: {proj.get('progress')}")
                issues = proj.get('issues', {}).get('nodes', [])
                print(f"Associated Issues: {len(issues)}")
                for issue in issues[:3]:  # Show first 3
                    print(f"  - [{issue.get('identifier')}] {issue.get('title')}")
        except Exception as e:
            print(f"Error: {e}")

    # Test 5: List Documents
    print("\n5. Testing list_documents (first 5)...")
    print("-" * 40)
    try:
        result = await client.get_documents(limit=5)
        documents = result.get("documents", {}).get("nodes", [])
        print(f"Found {len(documents)} documents:")
        for doc in documents:
            print(f"  - {doc.get('title')} (ID: {doc.get('id')})")
            if doc.get('project'):
                print(f"    Project: {doc.get('project', {}).get('name')}")
            if doc.get('initiative'):
                print(f"    Initiative: {doc.get('initiative', {}).get('name')}")
            print(f"    Created: {doc.get('createdAt')[:10] if doc.get('createdAt') else 'Unknown'}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 6: Get a specific document (if any exist)
    if documents:
        print(f"\n6. Testing get_document for '{documents[0].get('title')}'...")
        print("-" * 40)
        try:
            result = await client.get_document(documents[0]['id'])
            doc = result.get("document")
            if doc:
                print(f"Title: {doc.get('title')}")
                print(f"Creator: {doc.get('creator', {}).get('name') if doc.get('creator') else 'Unknown'}")
                if doc.get('content'):
                    print(f"Content preview: {doc.get('content')[:100]}...")
                print(f"Created: {doc.get('createdAt')}")
                print(f"Updated: {doc.get('updatedAt')}")
        except Exception as e:
            print(f"Error: {e}")

    # Test 7: Search with filters
    print("\n7. Testing search and filter capabilities...")
    print("-" * 40)
    try:
        # Search projects by name
        result = await client.get_projects(limit=5, filter_query="API")
        projects = result.get("projects", {}).get("nodes", [])
        print(f"Projects with 'API' in name: {len(projects)}")
        for proj in projects:
            print(f"  - {proj.get('name')}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 8: Pagination test
    print("\n8. Testing pagination...")
    print("-" * 40)
    try:
        # Get first page
        result = await client.get_projects(limit=2)
        projects = result.get("projects", {})
        page_info = projects.get("pageInfo", {})
        nodes = projects.get("nodes", [])

        print(f"First page (2 items):")
        for proj in nodes:
            print(f"  - {proj.get('name')}")

        if page_info.get("hasNextPage"):
            print(f"Has next page: Yes (cursor: {page_info.get('endCursor')[:20]}...)")

            # Get next page
            result = await client.get_projects(limit=2, after=page_info.get("endCursor"))
            projects = result.get("projects", {})
            nodes = projects.get("nodes", [])

            print(f"Second page (2 items):")
            for proj in nodes:
                print(f"  - {proj.get('name')}")
        else:
            print("Has next page: No")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)


async def test_mcp_tools():
    """Test the MCP tool functions directly"""
    from server import (
        _list_initiatives as list_initiatives,
        _get_initiative as get_initiative,
        _list_projects as list_projects,
        _get_project as get_project,
        _list_documents as list_documents,
        _get_document as get_document
    )

    print("\n" + "=" * 60)
    print("TESTING MCP TOOL FUNCTIONS")
    print("=" * 60)

    # Test MCP tool: list_initiatives
    print("\n1. Testing MCP tool: list_initiatives...")
    print("-" * 40)
    try:
        result = await list_initiatives(limit=3, include_archived=False)
        if "error" not in result:
            print(f"Found {result['total_count']} initiatives")
            for init in result['initiatives'][:3]:
                print(f"  - {init['name']} (Status: {init.get('status', 'No status')})")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Error: {e}")

    # Test MCP tool: list_projects
    print("\n2. Testing MCP tool: list_projects...")
    print("-" * 40)
    try:
        result = await list_projects(limit=3, include_archived=False)
        if "error" not in result:
            print(f"Found {result['total_count']} projects")
            for proj in result['projects'][:3]:
                print(f"  - {proj['name']} (State: {proj.get('state', 'No state')})")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Error: {e}")

    # Test MCP tool: list_documents
    print("\n3. Testing MCP tool: list_documents...")
    print("-" * 40)
    try:
        result = await list_documents(limit=3, include_archived=False)
        if "error" not in result:
            print(f"Found {result['total_count']} documents")
            for doc in result['documents'][:3]:
                print(f"  - {doc['title']}")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("MCP TOOLS TESTING COMPLETE")
    print("=" * 60)


async def main():
    """Main test function"""
    print("\nStarting Linear API Tests...")
    print("Make sure you have set LINEAR_API_KEY in your .env file\n")

    # Test the raw API functions
    await test_linear_api()

    # Test the MCP tool wrappers
    await test_mcp_tools()

    print("\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(main())