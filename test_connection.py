#!/usr/bin/env python3
"""Test Linear API connection and authentication"""

import asyncio
import os
from linear_client import LinearClient
from dotenv import load_dotenv

load_dotenv()


async def test_connection():
    """Test the Linear API connection with a simple query"""

    api_key = os.getenv("LINEAR_API_KEY")

    print("=" * 60)
    print("LINEAR API CONNECTION TEST")
    print("=" * 60)
    print()

    # Check if API key exists
    if not api_key:
        print("❌ ERROR: LINEAR_API_KEY not found in environment variables!")
        print("\nTo fix this:")
        print("1. Copy .env.example to .env:")
        print("   cp .env.example .env")
        print("2. Edit .env and add your Linear API key")
        print("3. Get your API key from: https://linear.app/settings/api")
        return

    # Check API key format
    if not api_key.startswith("lin_api_"):
        print(f"⚠️  WARNING: API key doesn't start with 'lin_api_'")
        print(f"   Current prefix: {api_key[:8]}...")
        print("   Linear API keys should start with 'lin_api_'")
    else:
        print(f"✅ API key format looks correct (starts with 'lin_api_')")

    # Mask the API key for display
    masked_key = f"{api_key[:12]}...{api_key[-4:]}" if len(api_key) > 16 else "***"
    print(f"📝 Using API key: {masked_key}")
    print()

    # Test the connection with a simple query
    client = LinearClient(api_key)

    print("Testing connection with a simple query...")
    print("-" * 40)

    try:
        # Try to fetch the viewer (current user) - simplest query
        test_query = """
        query TestConnection {
            viewer {
                id
                name
                email
            }
        }
        """

        result = await client.query(test_query)

        if result and result.get("viewer"):
            viewer = result["viewer"]
            print("✅ SUCCESS! Connected to Linear API")
            print()
            print("Authenticated as:")
            print(f"  Name: {viewer.get('name', 'N/A')}")
            print(f"  Email: {viewer.get('email', 'N/A')}")
            print(f"  ID: {viewer.get('id', 'N/A')}")
            print()
            print("Your Linear API key is working correctly!")

            # Try a simple initiatives query
            print("\n" + "-" * 40)
            print("Testing initiatives query...")
            try:
                initiatives_result = await client.get_initiatives(limit=1)
                count = len(initiatives_result.get("initiatives", {}).get("nodes", []))
                print(f"✅ Can query initiatives (found {count} initiative(s))")
            except Exception as e:
                print(f"❌ Failed to query initiatives: {str(e)}")

        else:
            print("❌ Connected but couldn't fetch user information")
            print("Response:", result)

    except Exception as e:
        print(f"❌ FAILED to connect to Linear API")
        print()
        print("Error details:")
        print(str(e))

        if "400" in str(e) or "401" in str(e):
            print("\n" + "=" * 60)
            print("TROUBLESHOOTING STEPS:")
            print("=" * 60)
            print("1. Verify your API key is correct:")
            print("   - Go to: https://linear.app/settings/api")
            print("   - Create a new Personal API key if needed")
            print("   - Copy the full key (starts with 'lin_api_')")
            print()
            print("2. Update your .env file:")
            print("   - Open .env in your editor")
            print("   - Set: LINEAR_API_KEY=lin_api_YOUR_KEY_HERE")
            print("   - Save the file")
            print()
            print("3. Make sure you're logged into Linear")
            print("   - The API key is tied to your Linear account")
            print("   - Ensure your account has access to the workspace")


if __name__ == "__main__":
    asyncio.run(test_connection())