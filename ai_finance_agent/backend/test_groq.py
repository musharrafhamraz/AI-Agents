#!/usr/bin/env python3
"""
Simple test script to verify GROQ integration works
"""
import os
import sys

def load_env_file():
    """Load environment variables from .env file"""
    try:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print("✓ Loaded environment variables from .env file")
            return True
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")
    return False

def test_imports():
    """Test if all required packages can be imported"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import fastapi
        print("✓ FastAPI imported successfully")
        
        import uvicorn
        print("✓ Uvicorn imported successfully")
        
        # Test GROQ import
        try:
            import groq
            print("✓ GROQ package imported successfully")
        except ImportError:
            print("✗ GROQ package not found. Install with: pip install groq")
            return False
        
        # Test agno imports
        try:
            from agno.agent import Agent
            from agno.team import Team
            from agno.models.groq import Groq
            from agno.db.sqlite import SqliteDb
            from agno.tools.duckduckgo import DuckDuckGoTools
            from agno.tools.yfinance import YFinanceTools
            from agno.os import AgentOS
            print("✓ All agno components imported successfully")
        except ImportError as e:
            print(f"✗ Agno import error: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_groq_key():
    """Test if GROQ API key is set"""
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print(f"✓ GROQ_API_KEY environment variable is set (key starts with: {groq_key[:10]}...)")
        return True
    else:
        print("✗ GROQ_API_KEY environment variable not set")
        print("  Please set it with: set GROQ_API_KEY=your-key-here")
        print("  Or add it to the .env file in the backend folder")
        return False

def main():
    print("=== AI Finance Agent - GROQ Integration Test ===\n")
    
    # Load .env file first
    load_env_file()
    print()
    
    # Test imports
    imports_ok = test_imports()
    print()
    
    # Test API key
    key_ok = test_groq_key()
    print()
    
    if imports_ok and key_ok:
        print("✅ All tests passed! You can now run the backend with: python simple_main.py")
    else:
        print("❌ Some tests failed. Please fix the issues above before running the backend.")
        
    return imports_ok and key_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)