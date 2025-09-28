#!/usr/bin/env python3
"""Test script to demonstrate milestone issues functionality"""

import asyncio
import json
from server import _get_project, _list_projects
from dotenv import load_dotenv

load_dotenv()


async def test_milestone_issues():
    """Test the milestone issues feature"""

    print("=" * 70)
    print("TESTING MILESTONE ISSUES FEATURE")
    print("=" * 70)

    # First, list projects to find ones with milestones
    print("\n1. Finding projects...")
    projects_result = await _list_projects(limit=10)

    if "error" in projects_result:
        print(f"Error listing projects: {projects_result['error']}")
        return

    # Test with multiple projects
    for project in projects_result.get("projects", [])[:3]:
        print(f"\n{'=' * 70}")
        print(f"PROJECT: {project['name']}")
        print(f"ID: {project['id']}")
        print("=" * 70)

        # Get detailed project info with milestones
        result = await _get_project(project['id'])

        if "error" in result:
            print(f"Error: {result['error']}")
            continue

        milestones = result.get("milestones", [])
        issues_without_milestone = result.get("issues_without_milestone", [])
        total_issues = len(result.get("issues", []))

        print(f"\nProject Statistics:")
        print(f"  - Total issues: {total_issues}")
        print(f"  - Total milestones: {len(milestones)}")
        print(f"  - Issues without milestone: {len(issues_without_milestone)}")

        if milestones:
            print(f"\nMilestones with Issues:")
            for milestone in milestones:
                print(f"\n  📍 {milestone['name']}")
                print(f"     Status: {milestone.get('status', 'N/A')}")
                print(f"     Progress: {milestone['progress']:.1%}")
                print(f"     Target Date: {milestone.get('target_date', 'Not set')}")
                print(f"     Issues ({milestone['issue_count']}):")

                if milestone['issues']:
                    for issue in milestone['issues'][:3]:  # Show first 3 issues
                        identifier = issue.get('identifier', 'N/A')
                        title = issue['title'][:50] + ('...' if len(issue['title']) > 50 else '')
                        print(f"       - [{identifier}] {title}")
                    if milestone['issue_count'] > 3:
                        print(f"       ... and {milestone['issue_count'] - 3} more issues")
                else:
                    print("       (No issues assigned)")
        else:
            print("\n  No milestones in this project")

        if issues_without_milestone:
            print(f"\n  📋 Issues NOT in any milestone ({len(issues_without_milestone)}):")
            for issue in issues_without_milestone[:5]:
                identifier = issue.get('identifier', 'N/A')
                title = issue['title'][:50] + ('...' if len(issue['title']) > 50 else '')
                print(f"     - [{identifier}] {title}")
            if len(issues_without_milestone) > 5:
                print(f"     ... and {len(issues_without_milestone) - 5} more issues")
        else:
            print("\n  ✅ All issues are assigned to milestones")

        print()


async def test_specific_project():
    """Test with a specific project ID"""
    project_id = "8c9001da-246e-46c8-b081-852b9da27e63"

    print("\n" + "=" * 70)
    print("TESTING SPECIFIC PROJECT")
    print("=" * 70)

    result = await _get_project(project_id)

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    # Create summary
    milestones = result.get("milestones", [])
    total_milestone_issues = sum(m['issue_count'] for m in milestones)
    issues_without_milestone = result.get("issues_without_milestone", [])

    print(f"\nProject: {result['name']}")
    print(f"\nIssue Distribution:")
    print(f"  - Issues in milestones: {total_milestone_issues}")
    print(f"  - Issues without milestone: {len(issues_without_milestone)}")
    print(f"  - Total issues: {len(result.get('issues', []))}")

    # Show milestone breakdown
    if milestones:
        print(f"\nMilestone Breakdown:")
        for milestone in milestones:
            percentage = (milestone['issue_count'] / len(result.get('issues', [])) * 100) if result.get('issues') else 0
            print(f"  - {milestone['name']}: {milestone['issue_count']} issues ({percentage:.1f}% of total)")


async def main():
    """Main test function"""
    print("Testing Linear API Milestone Issues Feature\n")

    # Test with multiple projects
    await test_milestone_issues()

    # Test with specific project
    await test_specific_project()


if __name__ == "__main__":
    asyncio.run(main())