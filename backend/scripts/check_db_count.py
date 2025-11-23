#!/usr/bin/env python3
"""Script to check total legislations in database"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.persistence.postgres.database import AsyncSessionLocal
from src.infrastructure.persistence.postgres.legislation_repository_impl import PostgresLegislationRepository


async def main():
    async with AsyncSessionLocal() as session:
        repo = PostgresLegislationRepository(session)
        all_items = await repo.find_all(limit=1000, offset=0)
        print(f"📊 Total de legislações no banco: {len(all_items)}")
        
        if len(all_items) > 0:
            print(f"\n📋 Primeiras 5 legislações:")
            for i, item in enumerate(all_items[:5], 1):
                print(f"  {i}. {item.title[:60]}...")
                print(f"     Autor: {item.author} | Status: {item.status}")
        
        # Check by status
        status_count = {}
        for item in all_items:
            status = item.status or "SEM_STATUS"
            status_count[status] = status_count.get(status, 0) + 1
        
        if status_count:
            print(f"\n📊 Por status:")
            for status, count in status_count.items():
                print(f"  - {status}: {count}")


if __name__ == "__main__":
    asyncio.run(main())

