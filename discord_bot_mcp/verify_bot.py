import os
import discord
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # The critical one for your project

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as: {client.user.name}')
    print(f'🆔 Bot ID: {client.user.id}')
    
    # Check if intents are actually enabled
    if client.intents.message_content:
        print("🟢 Message Content Intent: ENABLED")
    else:
        print("🔴 Message Content Intent: DISABLED (LLM won't be able to read DMs!)")
    
    print("\nVerification complete. Press Ctrl+C to stop.")

if __name__ == "__main__":
    if not token:
        print("❌ Error: No token found in .env file.")
    else:
        client.run(token)
