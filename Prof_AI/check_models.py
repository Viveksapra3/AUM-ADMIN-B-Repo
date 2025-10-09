#!/usr/bin/env python3
"""
Script to check available OpenAI models and test the fine-tuned model
"""

import asyncio
import sys
import os
from openai import AsyncOpenAI

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config

async def list_available_models():
    """List all available OpenAI models."""
    print("🔍 Checking available OpenAI models...")
    
    try:
        client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        
        # List all models
        models = await client.models.list()
        
        print(f"\n📋 Found {len(models.data)} total models")
        
        # Filter for fine-tuned models
        fine_tuned_models = [model for model in models.data if model.id.startswith('ft:')]
        
        print(f"\n🎯 Fine-tuned models ({len(fine_tuned_models)}):")
        for model in fine_tuned_models:
            print(f"   - {model.id}")
            if 'aum' in model.id.lower() or 'professor' in model.id.lower():
                print(f"     ⭐ This looks like your AUM model!")
        
        if not fine_tuned_models:
            print("   ❌ No fine-tuned models found")
            print("   💡 Make sure your fine-tuned model is deployed and accessible")
        
        return fine_tuned_models
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []

async def test_specific_model(model_id: str):
    """Test a specific model with a sample query."""
    print(f"\n🧪 Testing model: {model_id}")
    
    try:
        client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        
        messages = [
            {
                "role": "system",
                "content": """
                You are Alex, an experienced international admission counselor at
                Auburn University at Montgomery (AUM). You help prospective students
                from around the world understand AUM programs, admission process,
                visa support, scholarships, housing, and campus life.
                Always be polite, encouraging, and factual — respond as an official
                AUM representative.
                """
            },
            {
                "role": "user",
                "content": "What programs does Auburn University Montgomery offer for international students?"
            }
        ]
        
        response = await client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        
        answer = response.choices[0].message.content
        print(f"✅ Model response successful!")
        print(f"📝 Response preview: {answer[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

async def main():
    """Main function to check models and test."""
    print("=" * 60)
    print("🎓 OpenAI Model Checker for AUM Integration")
    print("=" * 60)
    
    # List available models
    fine_tuned_models = await list_available_models()
    
    # Test the current model in config
    current_model = "ft:gpt-4.1-mini-2025-04-14:professor-ai:aum:COPCJu5T"
    print(f"\n🎯 Testing current configured model: {current_model}")
    success = await test_specific_model(current_model)
    
    if not success and fine_tuned_models:
        print(f"\n💡 Current model failed. Let's test available fine-tuned models:")
        for model in fine_tuned_models:
            if 'aum' in model.id.lower() or 'professor' in model.id.lower():
                print(f"\n🧪 Testing potential AUM model: {model.id}")
                if await test_specific_model(model.id):
                    print(f"✅ This model works! Update your config to use: {model.id}")
                    break
    
    print("\n" + "=" * 60)
    print("🏁 Model check complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
