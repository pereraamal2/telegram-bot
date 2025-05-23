import os
import re
from telethon import TelegramClient, events

# Fetch credentials from environment variables
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_name = 'autobot'

SOURCE_CHAT_ID = int(os.environ.get("SOURCE_CHAT_ID"))
DESTINATION_CHAT_ID = int(os.environ.get("DESTINATION_CHAT_ID"))

client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(chats=SOURCE_CHAT_ID))
async def handler(event):
    original_message = event.message.message
    modified_message = original_message

    # Define a regex pattern to match each Entry block (LONG or SHORT)
    pattern = r"(LONG|SHORT).*?Entry:\s*([\d.]+)(.*?Target 1:\s*)([\d.%+-]+)(.*?Stop Loss:\s*)([\d.%+-]+)"
    
    def repl(match):
        position = match.group(1).upper()
        entry_price = float(match.group(2))
        target1_prefix = match.group(3)
        stoploss_prefix = match.group(5)

        if position == "LONG":
            target1 = round(entry_price * 1.01, 6)
            stoploss = round(entry_price * 0.985, 6)
        else:  # SHORT
            target1 = round(entry_price * 0.99, 6)
            stoploss = round(entry_price * 1.015, 6)

        return f"{position} SCALP\nEntry: {entry_price}{target1_prefix}{target1}{match.group(4)[-1] if match.group(4)[-1] in ' ' else ''}{stoploss_prefix}{stoploss}"

    modified_message = re.sub(pattern, repl, modified_message, flags=re.DOTALL | re.IGNORECASE)

    # Send to destination
    await client.send_message(DESTINATION_CHAT_ID, modified_message)
    print("[✅ MODIFIED & FORWARDED]")
    print(modified_message)

print("🤖 Bot is running...")
client.start()
client.run_until_disconnected()
