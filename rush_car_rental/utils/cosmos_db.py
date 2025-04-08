from django.db import connection
import logging

logger = logging.getLogger(__name__)

class CosmosDBManager:
    """
    Azure Cosmos DB (PostgreSQL接口) 管理器
    
    提供连接测试和信息获取功能
    """
    
    @staticmethod
    def test_connection():
        """
        测试与Azure Cosmos DB的连接
        
        返回:
            bool: 连接是否成功
        """
        try:
            # 简单的连接测试，执行查询
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"Cosmos DB连接测试失败: {str(e)}")
            return False
    
    @staticmethod
    def get_database_info():
        """
        获取当前数据库信息
        
        返回:
            dict: 数据库信息
        """
        try:
            info = {}
            
            # 获取PostgreSQL版本
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                info['version'] = version
            
            # 获取表数量
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT count(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
                table_count = cursor.fetchone()[0]
                info['table_count'] = table_count
            
            # 获取数据库大小信息 (如果是支持的版本)
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT pg_database_size(current_database())
                    """)
                    size_bytes = cursor.fetchone()[0]
                    info['size_bytes'] = size_bytes
                    info['size_mb'] = round(size_bytes / (1024 * 1024), 2)
            except Exception:
                # 某些托管版本可能不支持pg_database_size函数
                pass
                
            return info
        except Exception as e:
            logger.error(f"获取数据库信息失败: {str(e)}")
            return {"error": str(e)}