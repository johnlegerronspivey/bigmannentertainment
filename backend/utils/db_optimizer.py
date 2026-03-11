"""
Database optimization utilities
Includes connection pooling configuration and query optimization helpers
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Helper class for database optimizations"""
    
    @staticmethod
    async def ensure_indexes(db):
        """Ensure all necessary indexes are created for optimal query performance"""
        try:
            # Users collection indexes
            await db.users.create_index("email", unique=True)
            await db.users.create_index("created_at")
            await db.users.create_index([("email", 1), ("is_active", 1)])
            
            # Media content indexes
            await db.media_content.create_index("owner_id")
            await db.media_content.create_index("category")
            await db.media_content.create_index("is_published")
            await db.media_content.create_index([("owner_id", 1), ("is_published", 1)])
            await db.media_content.create_index([("category", 1), ("is_published", 1)])
            await db.media_content.create_index("created_at")
            
            # Labels collection indexes (ULN)
            await db.labels.create_index("global_id", unique=True)
            await db.labels.create_index("label_name")
            await db.labels.create_index("label_type")
            await db.labels.create_index([("label_type", 1), ("status", 1)])
            
            # Distribution collections
            await db.content_distribution.create_index("media_id")
            await db.content_distribution.create_index("status")
            await db.content_distribution.create_index([("media_id", 1), ("status", 1)])
            
            # Activity logs
            await db.activity_logs.create_index("user_id")
            await db.activity_logs.create_index("created_at")
            await db.activity_logs.create_index([("user_id", 1), ("created_at", -1)])
            
            # Purchases
            await db.purchases.create_index("user_id")
            await db.purchases.create_index("media_id")
            await db.purchases.create_index("payment_status")
            await db.purchases.create_index([("user_id", 1), ("created_at", -1)])
            
            logger.info("✅ Database indexes created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {str(e)}")
            return False
    
    @staticmethod
    async def get_collection_stats(db) -> Dict[str, Any]:
        """Get statistics about database collections"""
        stats = {}
        collections = await db.list_collection_names()
        
        for collection_name in collections:
            try:
                count = await db[collection_name].count_documents({})
                indexes = await db[collection_name].index_information()
                stats[collection_name] = {
                    'document_count': count,
                    'index_count': len(indexes),
                    'indexes': list(indexes.keys())
                }
            except Exception as e:
                stats[collection_name] = {'error': str(e)}
        
        return stats
    
    @staticmethod
    def get_optimized_query_options(limit: int = 100, skip: int = 0) -> Dict:
        """Get optimized query options with pagination"""
        return {
            'limit': min(limit, 1000),  # Max 1000 docs per query
            'skip': skip,
            'batch_size': 100  # Process in batches
        }
    
    @staticmethod
    async def optimize_connection_pool(mongo_url: str, max_pool_size: int = 50) -> AsyncIOMotorClient:
        """Create MongoDB client with optimized connection pool settings"""
        client = AsyncIOMotorClient(
            mongo_url,
            maxPoolSize=max_pool_size,
            minPoolSize=10,
            maxIdleTimeMS=45000,  # Close idle connections after 45 seconds
            waitQueueTimeoutMS=10000,  # Wait max 10 seconds for connection
            serverSelectionTimeoutMS=5000,  # Server selection timeout
            connectTimeoutMS=10000,  # Connection timeout
            socketTimeoutMS=30000,  # Socket timeout
        )
        return client
    
    @staticmethod
    async def cleanup_old_data(db, days: int = 90):
        """Clean up old temporary data (activity logs, sessions, etc.)"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        cleanup_results = {}
        
        try:
            # Clean old activity logs
            result = await db.activity_logs.delete_many({
                'created_at': {'$lt': cutoff_date}
            })
            cleanup_results['activity_logs'] = result.deleted_count
            
            # Clean expired sessions
            result = await db.user_sessions.delete_many({
                'expires_at': {'$lt': datetime.utcnow()}
            })
            cleanup_results['expired_sessions'] = result.deleted_count
            
            # Clean failed distributions older than 30 days
            old_cutoff = datetime.utcnow() - timedelta(days=30)
            result = await db.content_distribution.delete_many({
                'status': 'failed',
                'created_at': {'$lt': old_cutoff}
            })
            cleanup_results['failed_distributions'] = result.deleted_count
            
            logger.info(f"✅ Cleanup completed: {cleanup_results}")
            return cleanup_results
        except Exception as e:
            logger.error(f"❌ Cleanup error: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def build_paginated_query(
        filter_dict: Dict[str, Any],
        page: int = 1,
        page_size: int = 20,
        sort_by: str = 'created_at',
        sort_order: int = -1
    ) -> tuple:
        """Build optimized paginated query with sorting"""
        skip = (page - 1) * page_size
        limit = min(page_size, 100)  # Max 100 per page
        
        sort = [(sort_by, sort_order)]
        
        return filter_dict, skip, limit, sort


# Helper functions for query optimization
def optimize_projection(fields: Optional[List[str]] = None) -> Optional[Dict]:
    """Create projection dict to fetch only needed fields"""
    if not fields:
        return None
    return {field: 1 for field in fields}


def optimize_aggregation_pipeline(
    match_stage: Dict,
    group_stage: Optional[Dict] = None,
    sort_stage: Optional[Dict] = None,
    limit: int = 100
) -> List[Dict]:
    """Build optimized aggregation pipeline"""
    pipeline = [{'$match': match_stage}]
    
    if group_stage:
        pipeline.append({'$group': group_stage})
    
    if sort_stage:
        pipeline.append({'$sort': sort_stage})
    
    pipeline.append({'$limit': limit})
    
    return pipeline
