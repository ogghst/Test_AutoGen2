import asyncio
from autogen_core import SingleThreadedAgentRuntime, AgentId
from ctx_agent import PromptToGraphRoutedAgent, PromptToGraphRequest, PromptToGraphResponse

async def run_test():
    """
    Sandboxed test for the PromptToGraphRoutedAgent.
    """
    # 1. Create a runtime
    runtime = SingleThreadedAgentRuntime()

    # 2. Register the agent
    await PromptToGraphRoutedAgent.register(
        runtime,
        "prompt_to_graph_agent",
        lambda: PromptToGraphRoutedAgent()
    )
    agent_id = AgentId("prompt_to_graph_agent", "default")

    # 3. Start the runtime
    runtime.start()

    # 4. Create a request
    request = PromptToGraphRequest(
        prompt="""
        The machine learning is a branch of artificial intelligence that uses algorithms
        to learn from data. The neural networks are a type of machine learning algorithm
        that imitates the human brain.
        """,
        graph_type="knowledge_graph",
        max_nodes=20,
        max_depth=3,
        include_relationships=True
    )

    # 5. Send the message and get the response
    response = await runtime.send_message(request, agent_id)

    if response:
        if isinstance(response, PromptToGraphResponse):
            if response.success:
                print("✅ Graph generated successfully!")
                print(f"Nodes: {len(response.graph.nodes)}")
                print(f"Edges: {len(response.graph.edges)}")

                # Export to JSON
                json_output = response.graph.to_json()
                print("📄 Export JSON:", json_output[:300] + "...")

                # Export to Cypher for Neo4j
                cypher_output = response.graph.export_to_cypher()
                print("🌲 Export Cypher:", cypher_output[:300] + "...")
            else:
                print(f"❌ Error: {response.error_message}")
    else:
        print("❌ No response received from the agent.")


    # 6. Stop the runtime
    await runtime.stop()

if __name__ == "__main__":
    asyncio.run(run_test())
