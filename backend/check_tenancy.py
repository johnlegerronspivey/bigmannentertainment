import os, asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client[os.environ.get('DB_NAME')]
    
    cols = await db.list_collection_names()
    print('Collections:', sorted(cols))
    
    cve_cols = [c for c in cols if c.startswith('cve_')]
    print('\nCVE-related collections:')
    for col_name in sorted(cve_cols):
        col = db[col_name]
        total = await col.count_documents({})
        no_tenant = await col.count_documents({"tenant_id": {"$exists": False}})
        empty_tenant = await col.count_documents({"tenant_id": ""})
        has_tenant = await col.count_documents({"tenant_id": {"$nin": [None, ""]}})
        print(f'  {col_name}: total={total}, no_tenant_id={no_tenant}, empty_tenant_id={empty_tenant}, has_tenant_id={has_tenant}')
    
    users_col = db['users']
    total_users = await users_col.count_documents({})
    users_no_tenant = await users_col.count_documents({"tenant_id": {"$exists": False}})
    users_empty_tenant = await users_col.count_documents({"tenant_id": ""})
    users_has_tenant = await users_col.count_documents({"tenant_id": {"$nin": [None, ""]}})
    print(f'\n  users: total={total_users}, no_tenant_id={users_no_tenant}, empty_tenant_id={users_empty_tenant}, has_tenant_id={users_has_tenant}')
    
    admin = await users_col.find_one({"email": "cveadmin@test.com"}, {"_id": 0, "tenant_id": 1, "tenant_name": 1, "email": 1})
    print(f'\nAdmin user: {admin}')
    
    ent = await users_col.find_one({"email": "enterprise@test.com"}, {"_id": 0, "tenant_id": 1, "tenant_name": 1, "email": 1})
    print(f'Enterprise user: {ent}')
    
    # Sample a document from each collection to see structure
    for col_name in sorted(cve_cols)[:3]:
        col = db[col_name]
        doc = await col.find_one({}, {"_id": 0})
        if doc:
            keys = list(doc.keys())
            print(f'\n  {col_name} sample keys: {keys}')
            print(f'    tenant_id value: {doc.get("tenant_id", "FIELD_MISSING")}')

asyncio.run(check())
