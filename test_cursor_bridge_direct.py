#!/usr/bin/env python3
"""
Direct test of Cursor LLM Bridge without importing enhanced_autogen
"""

import sys
import asyncio
sys.path.append('/media/hannesn/storage/Code/cursor/src')

async def test_cursor_bridge():
    """Test the Cursor LLM Bridge directly"""
    try:
        # Import just the bridge components
        from llm.cursor_llm_bridge import CursorLLMBridge
        from llm.autogen_cursor_client import AutoGenCursorClient
        from llm.message_processing_bridge import MessageProcessingBridge
        
        print('🔄 Testing Cursor LLM Bridge components...')
        
        # Test 1: CursorLLMBridge
        print('\n1. Testing CursorLLMBridge...')
        bridge = CursorLLMBridge()
        
        # Discover models
        models = await bridge.discover_models()
        print(f'✅ Discovered {len(models)} models:')
        for model in models[:5]:  # Show first 5
            status = '✅' if model.is_available else '❌'
            print(f'  {status} {model.name} ({model.provider}, {model.model_type.value})')
        
        # Test generation if models available
        available_models = [m for m in models if m.is_available]
        if available_models:
            test_model = available_models[0]
            print(f'\n🧪 Testing generation with {test_model.name}...')
            
            test_messages = [
                {'role': 'system', 'content': 'You are a helpful coding assistant.'},
                {'role': 'user', 'content': 'Write a simple Python function to calculate the square of a number.'}
            ]
            
            response = await bridge.generate_response(
                model_name=test_model.name,
                messages=test_messages,
                temperature=0.7,
                max_tokens=200
            )
            
            print(f'✅ Generation successful!')
            print(f'Model: {response["model"]}')
            print(f'Content preview: {response["choices"][0]["message"]["content"][:150]}...')
            print(f'Tokens: {response["usage"]["total_tokens"]}')
        
        # Test 2: AutoGenCursorClient
        print('\n2. Testing AutoGenCursorClient...')
        client = AutoGenCursorClient(bridge)
        await client.initialize()
        
        available_models = client.cursor_bridge.get_available_model_names()
        print(f'✅ Client initialized with {len(available_models)} models')
        
        # Test completion
        if available_models:
            completion_response = await client.chat.create(
                model=available_models[0],
                messages=[
                    {"role": "user", "content": "What is the capital of France?"}
                ]
            )
            
            print(f'✅ Completion successful!')
            print(f'Response: {completion_response.choices[0].message.content[:100]}...')
        
        # Test 3: MessageProcessingBridge
        print('\n3. Testing MessageProcessingBridge...')
        msg_bridge = MessageProcessingBridge()
        
        test_messages = [
            {"role": "system", "content": "You are a developer agent."},
            {"role": "user", "content": "Help me debug this Python code."}
        ]
        
        prompt, context = await msg_bridge.process_autogen_messages(
            messages=test_messages,
            agent_role="developer",
            task_type="coding"
        )
        
        print(f'✅ Message processing successful!')
        print(f'Context: {context.agent_role.value}, Task: {context.task_type}')
        print(f'Prompt preview: {prompt[:100]}...')
        
        # Integration test
        print('\n4. Testing integration...')
        if available_models:
            llm_response = await bridge.generate_response(
                model_name=available_models[0],
                messages=test_messages,
                temperature=0.7
            )
            
            processed_response = await msg_bridge.process_cursor_response(
                llm_response["choices"][0]["message"]["content"],
                context
            )
            
            print(f'✅ Integration test successful!')
            print(f'Final response: {processed_response["content"][:100]}...')
        
        print('\n🎉 All Cursor LLM Bridge tests passed!')
        
        return {
            "success": True,
            "models_discovered": len(models),
            "available_models": len(available_models),
            "bridge_working": True,
            "client_working": True,
            "message_bridge_working": True
        }
        
    except Exception as e:
        print(f'❌ Error testing Cursor LLM Bridge: {e}')
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(test_cursor_bridge())
    print(f'\n📊 Test Results: {result}')
