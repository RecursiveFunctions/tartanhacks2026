import asyncio
from dedalus_labs import AsyncDedalus, DedalusRunner

async def main():
    # 1. Initialize Dedalus (Uses your API Key from env)
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    # 2. Point directly to your tunnel URL
    result = await runner.run(
        input="Check my Discord DMs and summarize them.",
        model="anthropic/claude-3-5-sonnet",
        mcp_servers=["https://friend-roulette.cm-unity.org/sse"] # 🚀 Bridge to your PC
    )
    print(f"Roulo's Response: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
