import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import json

class TelegramMessageReader:
    def __init__(self, session_string=None, api_id=None, api_hash=None):
        self.session_string = session_string or os.getenv('TELEGRAM_SESSION_STRING')
        self.api_id = api_id or int(os.getenv('TELEGRAM_API_ID', 0))
        self.api_hash = api_hash or os.getenv('TELEGRAM_API_HASH')
        self.client = None
        
        if not all([self.session_string, self.api_id, self.api_hash]):
            raise ValueError("Missing required credentials")
    
    async def initialize_client(self):
        """Initialize the Telegram client"""
        self.client = TelegramClient(
            StringSession(self.session_string),
            self.api_id,
            self.api_hash
        )
        
        await self.client.start()
        print("✅ Client initialized successfully!")
        print(f"🤖 Logged in as: {await self.client.get_me()}")
    
    async def get_recent_dialogs(self, limit=10):
        """Get recent conversations"""
        print(f"\n📋 Recent Dialogs (Last {limit}):")
        print("-" * 50)
        
        dialogs = await self.client.get_dialogs(limit=limit)
        
        for i, dialog in enumerate(dialogs):
            entity = dialog.entity
            if entity:
                print(f"{i+1}. {entity.title if hasattr(entity, 'title') else entity.first_name}")
                print(f"   💬 Last message: {dialog.message.text[:50]}..." if dialog.message and dialog.message.text else "   💬 No text message")
                print(f"   📞 Unread: {dialog.unread_count} | ID: {dialog.id}")
                print()
    
    async def get_messages_from_chat(self, chat_id, limit=20):
        """Get messages from a specific chat"""
        print(f"\n💬 Messages from {chat_id}:")
        print("-" * 50)
        
        try:
            messages = await self.client.get_messages(chat_id, limit=limit)
            
            for i, message in enumerate(messages):
                sender = await message.get_sender()
                sender_name = ""
                if sender:
                    sender_name = sender.first_name or sender.title or sender.username or "Unknown"
                
                print(f"{i+1}. {sender_name}:")
                print(f"   📅 {message.date}")
                if message.text:
                    print(f"   💭 {message.text[:100]}{'...' if len(message.text) > 100 else ''}")
                if message.media:
                    print(f"   📎 Media attached")
                print()
                
        except Exception as e:
            print(f"❌ Error reading messages from {chat_id}: {e}")
    
    async def listen_realtime(self, chat_id=None):
        """Listen for new messages in real-time"""
        print(f"\n🎧 Listening for new messages... (Press Ctrl+C to stop)")
        print("-" * 50)
        
        @self.client.on(events.NewMessage(chats=chat_id))
        async def handler(event):
            sender = await event.get_sender()
            sender_name = sender.first_name if sender else "Unknown"
            chat_title = event.chat.title if hasattr(event.chat, 'title') else sender_name
            
            print(f"🆕 NEW MESSAGE in {chat_title}:")
            print(f"   👤 From: {sender_name}")
            print(f"   💭 {event.message.text}")
            print(f"   📅 {event.message.date}")
            print()
        
        await self.client.run_until_disconnected()
    
    async def search_chats(self, search_term):
        """Search for chats by name"""
        print(f"\n🔍 Searching for chats: '{search_term}'")
        print("-" * 50)
        
        dialogs = await self.client.get_dialogs()
        found_chats = []
        
        for dialog in dialogs:
            if dialog.name and search_term.lower() in dialog.name.lower():
                found_chats.append(dialog)
                print(f"✅ Found: {dialog.name} (ID: {dialog.id})")
        
        return found_chats

async def main():
    # Configuration - FILL THESE WITH YOUR CREDENTIALS
    SESSION_STRING = "YOUR_SESSION_STRING_HERE"  # Get this from session_generator.py
    API_ID = 123456  # Your API ID from https://my.telegram.org
    API_HASH = "your_api_hash_here"  # Your API Hash
    
    # Initialize reader
    reader = TelegramMessageReader(SESSION_STRING, API_ID, API_HASH)
    
    try:
        await reader.initialize_client()
        
        while True:
            print("\n" + "="*60)
            print("📱 TELEGRAM MESSAGE READER")
            print("="*60)
            print("1. Show recent dialogs")
            print("2. Read messages from specific chat")
            print("3. Search chats")
            print("4. Listen for new messages (real-time)")
            print("5. Exit")
            
            choice = input("\nChoose an option (1-5): ").strip()
            
            if choice == '1':
                limit = input("How many dialogs to show? (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                await reader.get_recent_dialogs(limit)
                
            elif choice == '2':
                chat_input = input("Enter chat username/ID/phone: ").strip()
                limit = input("How many messages? (default 20): ").strip()
                limit = int(limit) if limit.isdigit() else 20
                await reader.get_messages_from_chat(chat_input, limit)
                
            elif choice == '3':
                search_term = input("Enter search term: ").strip()
                await reader.search_chats(search_term)
                
            elif choice == '4':
                chat_input = input("Enter chat to monitor (leave empty for all): ").strip()
                chat_id = None if not chat_input else chat_input
                await reader.listen_realtime(chat_id)
                
            elif choice == '5':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice!")
                
            input("\nPress Enter to continue...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if reader.client:
            await reader.client.disconnect()

# Helper script to generate session string
async def generate_session():
    """Run this first to generate a session string"""
    API_ID = input("Enter your API ID: ")
    API_HASH = input("Enter your API Hash: ")
    
    client = TelegramClient(StringSession(), int(API_ID), API_HASH)
    await client.start()
    
    session_string = client.session.save()
    print(f"\n✅ Session generated successfully!")
    print(f"🔐 Your session string: {session_string}")
    print("\n💡 Save this string for future use!")
    
    await client.disconnect()

if __name__ == "__main__":
    # Uncomment the next line if you need to generate a session first
    # asyncio.run(generate_session())
    
    asyncio.run(main())
