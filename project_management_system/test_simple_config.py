#!/usr/bin/env python3
"""
Simple test script for the simplified configuration system.

This script tests that the configuration system works even without
a configuration file, using the fallback mechanisms.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_config():
    """Test the simplified configuration system"""
    print("🔧 Testing Simplified Configuration System")
    print("=" * 50)
    
    try:
        # Test that we can get a config manager without a config file
        from config.settings import get_config_manager
        
        print("📋 Testing configuration manager creation...")
        config_manager = get_config_manager()
        
        print("✅ Configuration manager created successfully")
        print(f"  • LLM Provider: {config_manager.llm_provider.value}")
        print(f"  • LLM Model: {config_manager.llm_config.model}")
        print(f"  • Log Level: {config_manager.logging.log_level}")
        print(f"  • Console Logging: {config_manager.logging.console_logging}")
        print(f"  • Max Concurrent Agents: {config_manager.runtime.max_concurrent_agents}")
        print(f"  • Session Timeout: {config_manager.runtime.session_timeout}s")
        print(f"  • Tracing Enabled: {config_manager.runtime.enable_tracing}")
        print(f"  • Knowledge Base Path: {config_manager.system.knowledge_base_path}")
        
        print("\n🎉 Configuration system test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Simplified Configuration System Test\n")
    
    success = test_simple_config()
    
    if success:
        print("\n✅ All tests passed! Configuration system is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed. Please check the configuration system.")
        sys.exit(1)
