# test_ollama_autogen.py
import json
import requests
from openai import OpenAI
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ChatCompletionClient

async def main():


    # Test 1: Connessione diretta
    print("=== Test 1: Connessione diretta ===")
    try:
        response = requests.get("http://172.28.224.1:11434/api/tags")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"Modelli disponibili: {[m['name'] for m in models]}")
        else:
            print(f"Errore: {response.text}")
    except Exception as e:
        print(f"Errore connessione: {e}")

    # Test 2: OpenAI client con Ollama
    print("\n=== Test 2: OpenAI client ===")
    try:
        client = OpenAI(
            base_url="http://172.28.224.1:11434/v1",
            api_key="ollama"
        )
        
        models = client.models.list()
        print(f"Modelli via OpenAI API: {[m.id for m in models.data]}")
        
        # Test chat
        response = client.chat.completions.create(
            model="gpt-oss:20b",
            messages=[{"role": "user", "content": "Hello, test message"}],
            max_tokens=10
        )
        print(f"Risposta chat: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"Errore OpenAI client: {e}")

    # Test 3: AutoGen config
    print("\n=== Test 3: AutoGen config ===")
    try:

        
        llm_config = OpenAIChatCompletionClient(
            model="gpt-oss:20b",
            api_key="NotRequiredSinceWeAreLocal",
            base_url="http://172.28.224.1:11434/v1",
            model_capabilities={
                "json_output": True,
                "vision": False,
                "function_calling": True,
                "structured_output": True,
            },
        )
        
        async def get_weather(city: str) -> str:
            """Get the weather for a given city."""
            return f"The weather in {city} is 73 degrees and Sunny."


        agent = AssistantAgent(
            name="weather_agent",
            model_client=llm_config,
            tools=[get_weather],
            system_message="You are a helpful assistant.",
            reflect_on_tool_use=True,
            model_client_stream=True,  # Enable streaming tokens from the model client.
        )
        
        result = await agent.run(task="What is the weather in New York?")
        print(result)
        
        print("Agente AutoGen creato con successo")
        
    except Exception as e:
        print(f"Errore AutoGen: {e}")
        
# Run main if this file is executed directly
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
