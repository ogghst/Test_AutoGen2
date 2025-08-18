#!/usr/bin/env python3
"""
Test script for the Handoffs Multi-Agent Pattern

This script demonstrates how the handoffs pattern works with sample conversations.
Run this to see the agents in action without manual input.
"""

import asyncio
from handoffs_pattern import main


async def test_handoffs():
    """
    Test the handoffs pattern with automated input
    """
    print("=" * 80)
    print("HANDOFFS MULTI-AGENT PATTERN TEST")
    print("=" * 80)
    print()
    print("This test will demonstrate:")
    print("1. Triage Agent routing to Planning Agent")
    print("2. Planning Agent creating a project plan")
    print("3. Transfer back to Triage Agent")
    print("4. Triage Agent routing to Execution Agent")
    print("5. Execution Agent executing tasks")
    print("6. Escalation to Human Agent for complex issues")
    print()
    
    try:
        await main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        raise


if __name__ == "__main__":
    print("Starting Handoffs Pattern Test...")
    print("Note: This will require manual input during the conversation.")
    print("You can test different scenarios:")
    print("- Project planning requests")
    print("- Task execution requests") 
    print("- Quality review requests")
    print("- Complex issues for human escalation")
    print()
    
    # Run the test
    asyncio.run(test_handoffs())
