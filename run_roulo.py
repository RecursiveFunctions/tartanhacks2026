import asyncio
from dedalus_labs import AsyncDedalus, DedalusRunner

async def main():
    # 1. Connect to the Dedalus Cloud
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    # 2. Tell the agent to use your self-hosted tunnel
    result = await runner.run(
        input="Check my Discord DMs. Summarize any new students who want a match.",
        model="anthropic/claude-3-5-sonnet",
        mcp_servers=["https://friend-roulette.cm-unity.org/sse"] # 🚀 Your Tunnel
    )
    
    print(f"Roulo says: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
