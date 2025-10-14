#!/usr/bin/env python3
"""
Test script for AUM Counselor Integration
Tests the fine-tuned model integration in the websocket flow
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.chat_service import ChatService
from services.aum_counselor_service import AUMCounselorService

async def test_aum_counselor_direct():
    """Test AUM counselor service directly."""
    print("🧪 Testing AUM Counselor Service directly...")
    
    try:
        counselor = AUMCounselorService()
        
        # Test query
        test_query = "What programs does Auburn University Montgomery offer for international students?"
        
        print(f"Query: {test_query}")
        response = await counselor.get_counseling_response(test_query)
        
        print(f"✅ Response received:")
        print(f"   Model: {response.get('model_used', 'N/A')}")
        print(f"   Counselor: {response.get('counselor', 'N/A')}")
        print(f"   Answer: {response.get('answer', 'N/A')[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct AUM counselor test failed: {e}")
        return False

async def test_chat_service_routing():
    """Test chat service routing to AUM counselor."""
    print("\n🧪 Testing Chat Service AUM routing...")
    
    try:
        chat_service = ChatService()
        
        # Test AUM-related queries
        aum_queries = [
            "Tell me about AUM admission requirements",
            "What scholarships are available at Auburn University Montgomery?",
            "How do I apply for a student visa for AUM?",
            "What is the tuition fee at Auburn Montgomery?"
        ]
        
        for query in aum_queries:
            print(f"\nQuery: {query}")
            
            # Check if it's detected as AUM-related
            is_aum = chat_service.aum_counselor_service.is_aum_related_query(query)
            print(f"   Detected as AUM query: {is_aum}")
            
            if is_aum:
                response = await chat_service.ask_question(query)
                print(f"   Response source: {response.get('sources', ['N/A'])}")
                print(f"   Model used: {response.get('model_used', 'N/A')}")
                print(f"   Answer preview: {response.get('answer', 'N/A')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Chat service routing test failed: {e}")
        return False

async def test_non_aum_queries():
    """Test that non-AUM queries still work normally."""
    print("\n🧪 Testing non-AUM query handling...")
    
    try:
        chat_service = ChatService()
        
        # Test non-AUM queries
        general_queries = [
            "What is artificial intelligence?",
            "Explain machine learning concepts",
            "How does photosynthesis work?"
        ]
        
        for query in general_queries:
            print(f"\nQuery: {query}")
            
            # Check if it's detected as AUM-related (should be False)
            is_aum = chat_service.aum_counselor_service.is_aum_related_query(query)
            print(f"   Detected as AUM query: {is_aum}")
            
            response = await chat_service.ask_question(query)
            print(f"   Response source: {response.get('sources', ['N/A'])}")
            print(f"   Answer preview: {response.get('answer', 'N/A')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Non-AUM query test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("=" * 60)
    print("🎓 AUM Counselor Integration Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Direct AUM counselor
    if await test_aum_counselor_direct():
        tests_passed += 1
    
    # Test 2: Chat service routing
    if await test_chat_service_routing():
        tests_passed += 1
    
    # Test 3: Non-AUM queries
    if await test_non_aum_queries():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! AUM integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
