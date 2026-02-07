import os
import asyncio
import threading
import discord
from fastmcp import FastMCP
from dotenv import load_dotenv

# 1. Load your secrets from the .env file
load_dotenv()

# 2. Initialize the MCP Server (This is what Dedalus connects to)
mcp = FastMCP("Roulo-Matchmaker")

# 3. Setup Discord with the correct "Hearing" permissions
intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

# 4. Storage for the latest DMs
message_queue = []

@client.event
async def on_ready():
    print(f"✅ Roulo is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if isinstance(message.channel, discord.DMChannel):
        print(f"📩 New DM from {message.author}: {message.content}")
        message_queue.append({
            "sender": str(message.author),
            "sender_id": str(message.author.id),
            "text": message.content
        })

# 5. The tool Dedalus will use to read DMs
@mcp.tool()
def get_new_messages() -> str:
    """Retrieves and clears the latest Discord DMs received by Roulo."""
    if not message_queue:
        return "No new messages."
    
    snapshot = list(message_queue)
    message_queue.clear()
    return str(snapshot)

# 6. The tool Dedalus will use to send DMs
@mcp.tool()
async def send_discord_dm(user_id: str, content: str) -> str:
    """Sends a Discord DM to a specific user by their ID."""
    try:
        user = await client.fetch_user(int(user_id))
        await user.send(content)
        return f"Successfully sent to {user.name}"
    except Exception as e:
        return f"Failed to send DM: {e}"

# 7. Run Discord in the background so it doesn't block the web server
def start_discord():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if token:
        client.run(token)
    else:
        print("❌ Error: DISCORD_BOT_TOKEN not found in .env")

threading.Thread(target=start_discord, daemon=True).start()

# 8. Start the MCP Server
if __name__ == "__main__":
    # This matches the port for your Cloudflare tunnel
  mcp.run(transport="sse", host="0.0.0.0", port=8000)
