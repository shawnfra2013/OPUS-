#!/usr/bin/env python3
"""
Quick test of native macOS approval system
No token cost - runs entirely on your Mac
"""

import sys
sys.path.insert(0, '/Users/shawnfrahm/hungry')

from macos_approver import process_approval_request, macOSApprover
import json

def test_approval_dialog():
    """Test the native approval dialog"""
    print("🧪 Testing native macOS approval dialog...")
    print("   (A dialog should appear on your screen)\n")
    
    test_approval = {
        "id": "test-scraper-001",
        "title": "Production Web Scraper",
        "description": "This would create a web scraper with:\n- Logging system\n- Retry logic\n- Error handling\n- BeautifulSoup parsing",
        "risk_level": "LOW",
        "files": {
            "/tmp/web_scraper.py": "#!/usr/bin/env python3\nimport requests\nfrom bs4 import BeautifulSoup\n..."
        },
        "commands": [
            "python3 -m py_compile /tmp/web_scraper.py",
            "python3 /tmp/web_scraper.py --url https://example.com"
        ]
    }
    
    # Process the approval (will show native dialog)
    result = process_approval_request(test_approval)
    
    print("\n✅ Dialog closed. Result:")
    print(json.dumps(result, indent=2))
    
    if result['approved']:
        print("\n✓ APPROVED - Code would be created and tests would run")
    else:
        print("\n✗ DENIED - Code not created, request archived")
    
    return result['approved']

def test_notification():
    """Test native notification"""
    print("\n🧪 Testing native notification...")
    macOSApprover.show_notification(
        "Test Notification",
        "This is a lightweight notification (no cost)"
    )
    print("✓ Notification sent (should appear in corner)")

def test_input_dialog():
    """Test input dialog"""
    print("\n🧪 Testing input dialog...")
    result = macOSApprover.ask_for_input("Enter a test value:")
    print(f"You entered: {result}")

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════╗")
    print("║  Native macOS Approval System - Cost: ZERO             ║")
    print("║  Running entirely on your Mac - no API calls          ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    try:
        # Test approval dialog
        approved = test_approval_dialog()
        
        # Test notification
        test_notification()
        
        # Optionally test input
        # test_input_dialog()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        print("\nIntegration Status:")
        print("  ✅ Native dialogs working")
        print("  ✅ Zero token cost (all local)")
        print("  ✅ Lightweight (no background processes)")
        print("  ✅ Ready for agent integration")
        print("\nNext step: Start agent with 'python3 run_agent.py'")
        print("Dialogs will appear automatically when code is generated.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you're on macOS with osascript available")
        sys.exit(1)
