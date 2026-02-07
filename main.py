import os
import asyncio
import discord
from fastmcp import FastMCP

# 1. Initialize MCP
mcp = FastMCP("Roulo-Matchmaker")

# 2. Setup Discord 
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

message_queue = []

@client.event
async def on_ready():
    print(f"✅ Roulo is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        message_queue.append({
            "sender": str(message.author),
            "sender_id": str(message.author.id),
            "text": message.content
        })

@mcp.tool()
def get_new_messages() -> str:
    """Retrieves and clears the latest Discord DMs."""
    if not message_queue:
        return "No new messages."
    snapshot = list(message_queue)
    message_queue.clear()
    return str(snapshot)

@mcp.tool()
async def send_discord_dm(user_id: str, content: str) -> str:
    """Sends a Discord DM by user ID."""
    try:
        user = await client.fetch_user(int(user_id))
        await user.send(content)
        return f"Successfully sent to {user.name}"
    except Exception as e:
        return f"Failed: {e}"

# 3. Use the MCP lifecycle to start the bot
@mcp.on_startup()
async def start_bot():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if token:
        # We use .start() instead of .run() to keep the loop shared
        asyncio.create_task(client.start(token))
    else:
        print("❌ DISCORD_BOT_TOKEN missing in Credentials tab")

if __name__ == "__main__":
    # Host must be 0.0.0.0 and transport must be SSE for Dedalus
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
