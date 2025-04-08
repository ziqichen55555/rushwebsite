from django.db import connection
import logging

# 创建日志记录器
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
        logger.info("[DB_CONNECT] 开始数据库连接测试")
        try:
            # 简单的连接测试，执行查询
            with connection.cursor() as cursor:
                logger.debug("[DB_CONNECT] 执行测试查询 'SELECT 1'")
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                success = result is not None and result[0] == 1
                if success:
                    logger.info("[DB_CONNECT] 数据库连接测试成功 - 返回值: 1")
                else:
                    logger.warning("[DB_CONNECT] 数据库连接测试成功但返回异常值: %s", result)
                return success
        except Exception as e:
            logger.error("[DB_CONNECT] 数据库连接测试失败: %s", str(e), exc_info=True)
            return False
    
    @staticmethod
    def get_database_info():
        """
        获取当前数据库信息
        
        返回:
            dict: 数据库信息
        """
        logger.info("[DB_INFO] 开始获取数据库信息")
        try:
            info = {}
            
            # 获取PostgreSQL版本
            with connection.cursor() as cursor:
                logger.debug("[DB_INFO] 执行查询: SELECT version()")
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                info['version'] = version
                logger.info("[DB_INFO] 数据库版本: %s", version)
            
            # 获取表数量
            with connection.cursor() as cursor:
                logger.debug("[DB_INFO] 执行查询: 获取表数量")
                cursor.execute("""
                    SELECT count(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
                table_count = cursor.fetchone()[0]
                info['table_count'] = table_count
                logger.info("[DB_INFO] 数据库包含 %d 个表", table_count)
            
            # 获取数据库大小信息 (如果是支持的版本)
            try:
                with connection.cursor() as cursor:
                    logger.debug("[DB_INFO] 执行查询: 获取数据库大小")
                    cursor.execute("""
                        SELECT pg_database_size(current_database())
                    """)
                    size_bytes = cursor.fetchone()[0]
                    info['size_bytes'] = size_bytes
                    info['size_mb'] = round(size_bytes / (1024 * 1024), 2)
                    logger.info("[DB_INFO] 数据库大小: %s MB (%s bytes)", 
                                info['size_mb'], size_bytes)
            except Exception as e:
                # 某些托管版本可能不支持pg_database_size函数
                logger.warning("[DB_INFO] 无法获取数据库大小信息: %s", str(e))
                pass
                
            logger.info("[DB_INFO] 数据库信息获取完成")
            return info
        except Exception as e:
            logger.error("[DB_INFO] 获取数据库信息失败: %s", str(e), exc_info=True)
            return {"error": str(e)}