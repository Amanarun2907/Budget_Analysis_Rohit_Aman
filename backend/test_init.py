import asyncio
import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import init_db, engine

async def main():
    print("Initializing database...")
    await init_db()
    print("Database tables created!")
    await engine.dispose()
    print("Engine disposed.")

if __name__ == "__main__":
    asyncio.run(main())

