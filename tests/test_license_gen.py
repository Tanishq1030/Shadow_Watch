import sys
from pathlib import Path
# Add parent directory to path so we can import license_server
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from license_server.admin_client import AdminClient

async def main():
    admin = AdminClient(
        api_url="https://shadow-watch-ten.vercel.app",
        admin_secret="ff790df853cc45fc83eb94f4c15086c9c21f91c1d632886703ec9ac9bf869259"
    )
    
    print("🔑 Generating Invariant license...")
    license = await admin.create_invariant_license(user_id="test_user")
    
    print(f"\n✅ License Generated!")
    print(f"License Key: {license['license_key']}")
    print(f"Type: {license['license_type']}")
    print(f"Expires: {license['expires_at']}")
    print(f"Metadata: {license.get('metadata', {})}")

if __name__ == "__main__":
    asyncio.run(main())