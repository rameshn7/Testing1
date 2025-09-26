import os
import json
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import secrets

class TelegramSessionToTData:
    def __init__(self, string_session, api_id, api_hash):
        self.string_session = string_session
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = None
        self.tdata_path = "tdata_output"
        
    async def initialize_client(self):
        """Initialize Telegram client with string session"""
        self.client = TelegramClient(
            StringSession(self.string_session),
            self.api_id,
            self.api_hash
        )
        await self.client.connect()
        
    async def validate_session(self):
        """Validate if the session is active"""
        if not await self.client.is_user_authorized():
            raise Exception("Invalid session string or session expired")
        
        me = await self.client.get_me()
        print(f"✓ Session validated for: {me.first_name} (ID: {me.id})")
        return me

    def extract_session_components(self):
        """Extract raw session components"""
        session = self.client.session
        
        auth_key = session.auth_key
        if not auth_key:
            raise Exception("No auth key found in session")
            
        return {
            'auth_key': auth_key.hex(),
            'dc_id': session.dc_id,
            'server_address': session.server_address,
            'port': session.port,
            'api_id': self.api_id,
            'api_hash': self.api_hash
        }

    def create_tdata_structure(self, user_data):
        """Create the complete tdata folder structure"""
        
        # Create main directory
        if os.path.exists(self.tdata_path):
            # Remove existing directory
            import shutil
            shutil.rmtree(self.tdata_path)
        
        os.makedirs(self.tdata_path)
        
        # Create key file
        key_data = {
            'auth_key': user_data['auth_key'],
            'user_id': user_data.get('user_id', 0),
            'dc_id': user_data['dc_id'],
            'main_dc_id': user_data['dc_id']
        }
        
        with open(os.path.join(self.tdata_path, 'key_data'), 'w') as f:
            json.dump(key_data, f, indent=2)
        
        # Create config file
        config = {
            'api_id': user_data['api_id'],
            'api_hash': user_data['api_hash'],
            'test_mode': False,
            'base_dc_id': user_data['dc_id']
        }
        
        with open(os.path.join(self.tdata_path, 'config'), 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create DCs file
        dcs_content = f"{user_data['dc_id']}\n{user_data['server_address']}\n{user_data['port']}"
        with open(os.path.join(self.tdata_path, 'dcs'), 'w') as f:
            f.write(dcs_content)
            
        print(f"✓ TData structure created in: {self.tdata_path}")

    async def convert(self):
        """Main conversion function"""
        try:
            print("Initializing Telegram client...")
            await self.initialize_client()
            
            print("Validating session...")
            user = await self.validate_session()
            
            print("Extracting session data...")
            session_data = self.extract_session_components()
            session_data['user_id'] = user.id
            session_data['phone'] = user.phone
            session_data['username'] = user.username
            
            print("Creating TData structure...")
            self.create_tdata_structure(session_data)
            
            print("\n" + "="*50)
            print("✅ CONVERSION SUCCESSFUL!")
            print("="*50)
            print(f"Account: {user.first_name} {user.last_name or ''}")
            print(f"User ID: {user.id}")
            print(f"Username: @{user.username}" if user.username else "No username")
            print(f"Phone: {user.phone}")
            print(f"DC ID: {session_data['dc_id']}")
            print(f"Output folder: {self.tdata_path}")
            print("\nFiles created:")
            for file in os.listdir(self.tdata_path):
                print(f"  - {file}")
                
            return True
            
        except Exception as e:
            print(f"❌ Conversion failed: {str(e)}")
            return False
        finally:
            if self.client:
                await self.client.disconnect()

async def main():
    # ⚠️ REPLACE THESE WITH YOUR ACTUAL DATA ⚠️
    STRING_SESSION = "YOUR_STRING_SESSION_HERE"
    API_ID = 1234567  # YOUR_API_ID_HERE
    API_HASH = "YOUR_API_HASH_HERE"
    
    if STRING_SESSION == "YOUR_STRING_SESSION_HERE":
        print("❌ Please replace the placeholder values with your actual data!")
        return
    
    converter = TelegramSessionToTData(STRING_SESSION, API_ID, API_HASH)
    await converter.convert()

if __name__ == "__main__":
    asyncio.run(main())
