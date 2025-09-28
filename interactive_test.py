#!/usr/bin/env python3
"""Interactive testing for Linear API - call specific functions with custom parameters"""

import asyncio
import json
from typing import Optional
from linear_client import LinearClient
from dotenv import load_dotenv

load_dotenv()

# Import the internal functions directly (no MCP decorators)
from server import (
    _list_initiatives as list_initiatives,
    _get_initiative as get_initiative,
    _list_projects as list_projects,
    _get_project as get_project,
    _list_documents as list_documents,
    _get_document as get_document
)


async def pretty_print(data, indent=2):
    """Pretty print JSON data"""
    if isinstance(data, dict) or isinstance(data, list):
        print(json.dumps(data, indent=indent, default=str))
    else:
        print(data)


async def interactive_menu():
    """Interactive menu for testing functions"""

    while True:
        print("\n" + "=" * 60)
        print("LINEAR API INTERACTIVE TESTER")
        print("=" * 60)
        print("\n1. List Initiatives")
        print("2. Get Initiative by ID")
        print("3. List Projects")
        print("4. Get Project by ID (with Milestones and Issues)")
        print("5. List Documents")
        print("6. Get Document by ID")
        print("7. Raw GraphQL Query (advanced)")
        print("8. Exit")

        choice = input("\nSelect an option (1-8): ").strip()

        if choice == "1":
            # List Initiatives
            limit = input("Enter limit (default 50): ").strip() or "50"
            search = input("Search term (optional): ").strip() or None
            include_archived = input("Include archived? (y/N): ").lower() == "y"

            print("\nFetching initiatives...")
            result = await list_initiatives(
                limit=int(limit),
                search=search,
                include_archived=include_archived
            )
            await pretty_print(result)

        elif choice == "2":
            # Get Initiative
            init_id = input("Enter Initiative ID: ").strip()
            if init_id:
                print("\nFetching initiative...")
                result = await get_initiative(id=init_id)
                await pretty_print(result)
            else:
                print("ID is required!")

        elif choice == "3":
            # List Projects
            limit = input("Enter limit (default 50): ").strip() or "50"
            search = input("Search term (optional): ").strip() or None
            team_id = input("Filter by Team ID (optional): ").strip() or None
            initiative_id = input("Filter by Initiative ID (optional): ").strip() or None
            include_archived = input("Include archived? (y/N): ").lower() == "y"

            print("\nFetching projects...")
            result = await list_projects(
                limit=int(limit),
                search=search,
                team_id=team_id,
                initiative_id=initiative_id,
                include_archived=include_archived
            )
            await pretty_print(result)

        elif choice == "4":
            # Get Project with Milestones and Issues
            proj_id = input("Enter Project ID: ").strip()
            if proj_id:
                print("\nFetching project with milestones and associated issues...")
                result = await get_project(id=proj_id)
                await pretty_print(result)
            else:
                print("ID is required!")

        elif choice == "5":
            # List Documents
            limit = input("Enter limit (default 50): ").strip() or "50"
            search = input("Search term (optional): ").strip() or None
            project_id = input("Filter by Project ID (optional): ").strip() or None
            initiative_id = input("Filter by Initiative ID (optional): ").strip() or None
            include_archived = input("Include archived? (y/N): ").lower() == "y"

            print("\nFetching documents...")
            result = await list_documents(
                limit=int(limit),
                search=search,
                project_id=project_id,
                initiative_id=initiative_id,
                include_archived=include_archived
            )
            await pretty_print(result)

        elif choice == "6":
            # Get Document
            doc_id = input("Enter Document ID: ").strip()
            if doc_id:
                print("\nFetching document...")
                result = await get_document(id=doc_id)
                await pretty_print(result)
            else:
                print("ID is required!")

        elif choice == "7":
            # Raw GraphQL Query
            print("\nEnter your GraphQL query (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)

            query = "\n".join(lines[:-1])  # Remove last empty line

            variables_str = input("\nEnter variables as JSON (optional, press Enter to skip): ").strip()
            variables = {}
            if variables_str:
                try:
                    variables = json.loads(variables_str)
                except json.JSONDecodeError:
                    print("Invalid JSON for variables!")
                    continue

            try:
                client = LinearClient()
                print("\nExecuting query...")
                result = await client.query(query, variables)
                await pretty_print(result)
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "8":
            print("\nExiting...")
            break

        else:
            print("\nInvalid choice! Please select 1-8.")

        if choice != "8":
            input("\nPress Enter to continue...")


async def quick_test():
    """Quick test mode - run a specific function directly"""
    import sys

    if len(sys.argv) < 2:
        print("Quick test mode usage:")
        print("  python interactive_test.py list_initiatives [limit]")
        print("  python interactive_test.py get_initiative <id>")
        print("  python interactive_test.py list_projects [limit]")
        print("  python interactive_test.py get_project <id>")
        print("  python interactive_test.py list_documents [limit]")
        print("  python interactive_test.py get_document <id>")
        return

    command = sys.argv[1]

    if command == "list_initiatives":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        result = await list_initiatives(limit=limit)
        await pretty_print(result)

    elif command == "get_initiative" and len(sys.argv) > 2:
        result = await get_initiative(id=sys.argv[2])
        await pretty_print(result)

    elif command == "list_projects":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        result = await list_projects(limit=limit)
        await pretty_print(result)

    elif command == "get_project" and len(sys.argv) > 2:
        result = await get_project(id=sys.argv[2])
        await pretty_print(result)

    elif command == "list_documents":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        result = await list_documents(limit=limit)
        await pretty_print(result)

    elif command == "get_document" and len(sys.argv) > 2:
        result = await get_document(id=sys.argv[2])
        await pretty_print(result)

    else:
        print(f"Unknown command or missing arguments: {command}")
        await quick_test()  # Show usage


async def main():
    """Main entry point"""
    import sys

    if len(sys.argv) > 1:
        # Quick test mode
        await quick_test()
    else:
        # Interactive mode
        print("\nStarting Interactive Linear API Tester...")
        print("Make sure you have set LINEAR_API_KEY in your .env file\n")
        await interactive_menu()


if __name__ == "__main__":
    asyncio.run(main())