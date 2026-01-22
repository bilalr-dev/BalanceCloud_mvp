"""
Database Query Optimization Utilities

Provides utilities for optimizing PostgreSQL queries:
- Index creation
- Query analysis
- Performance monitoring
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseOptimizer:
    """Utilities for database query optimization"""

    @staticmethod
    async def create_indexes(db: AsyncSession) -> dict:
        """
        Create recommended indexes for optimal query performance
        
        Returns:
            dict with index creation results
        """
        indexes = {
            "users_email_idx": """
                CREATE INDEX IF NOT EXISTS users_email_idx 
                ON users(email);
            """,
            "files_user_id_idx": """
                CREATE INDEX IF NOT EXISTS files_user_id_idx 
                ON files(user_id);
            """,
            "files_user_id_parent_id_idx": """
                CREATE INDEX IF NOT EXISTS files_user_id_parent_id_idx 
                ON files(user_id, parent_id) 
                WHERE parent_id IS NOT NULL;
            """,
            "files_user_id_path_idx": """
                CREATE INDEX IF NOT EXISTS files_user_id_path_idx 
                ON files(user_id, path);
            """,
            "storage_chunks_file_id_idx": """
                CREATE INDEX IF NOT EXISTS storage_chunks_file_id_idx 
                ON storage_chunks(file_id);
            """,
            "storage_chunks_file_id_chunk_index_idx": """
                CREATE INDEX IF NOT EXISTS storage_chunks_file_id_chunk_index_idx 
                ON storage_chunks(file_id, chunk_index);
            """,
            "cloud_accounts_user_id_provider_idx": """
                CREATE INDEX IF NOT EXISTS cloud_accounts_user_id_provider_idx 
                ON cloud_accounts(user_id, provider);
            """,
        }

        results = {}
        for index_name, index_sql in indexes.items():
            try:
                await db.execute(text(index_sql))
                await db.commit()
                results[index_name] = "created"
            except Exception as e:
                results[index_name] = f"error: {str(e)}"

        return results

    @staticmethod
    async def analyze_query(db: AsyncSession, query: str) -> dict:
        """
        Analyze a query using EXPLAIN ANALYZE
        
        Args:
            db: Database session
            query: SQL query to analyze
            
        Returns:
            dict with analysis results
        """
        try:
            result = await db.execute(text(f"EXPLAIN ANALYZE {query}"))
            plan = "\n".join([row[0] for row in result.fetchall()])
            return {"plan": plan, "status": "success"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @staticmethod
    async def get_table_stats(db: AsyncSession, table_name: str) -> dict:
        """
        Get statistics for a table
        
        Args:
            db: Database session
            table_name: Name of the table
            
        Returns:
            dict with table statistics
        """
        try:
            query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation,
                    most_common_vals,
                    most_common_freqs
                FROM pg_stats
                WHERE tablename = :table_name
                ORDER BY attname;
            """)
            result = await db.execute(query, {"table_name": table_name})
            stats = [dict(row._mapping) for row in result.fetchall()]
            return {"status": "success", "stats": stats}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @staticmethod
    async def vacuum_analyze(db: AsyncSession, table_name: str = None) -> dict:
        """
        Run VACUUM ANALYZE on a table or all tables
        
        Args:
            db: Database session
            table_name: Optional table name, if None analyzes all tables
            
        Returns:
            dict with results
        """
        try:
            if table_name:
                query = text(f"VACUUM ANALYZE {table_name};")
            else:
                query = text("VACUUM ANALYZE;")
            
            await db.execute(query)
            await db.commit()
            return {"status": "success", "table": table_name or "all"}
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Create singleton instance
db_optimizer = DatabaseOptimizer()
