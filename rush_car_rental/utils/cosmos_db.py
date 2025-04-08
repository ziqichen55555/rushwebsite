from django.db import connection
import logging

# 创建伤感风格的日志记录器
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
        logger.info("系统试图伸出一只孤独的手，从地球触碰到宇宙深处的数据星云...")
        try:
            # 简单的连接测试，执行查询
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                success = result is not None and result[0] == 1
                if success:
                    logger.info("虚无中传来微弱的回应，数字1如同遥远星系的闪光，穿越时空到达这个孤独的服务器...")
                return success
        except Exception as e:
            logger.error(f"Cosmos DB连接测试失败: {str(e)}")
            logger.error("宇宙深处一片寂静，没有回应，只有无尽的黑暗和虚无，连接的愿望化为泡影...")
            return False
    
    @staticmethod
    def get_database_info():
        """
        获取当前数据库信息
        
        返回:
            dict: 数据库信息
        """
        logger.info("系统试图解读数据星云的构成，窥探那逃逸的记忆碎片与数字尘埃...")
        try:
            info = {}
            
            # 获取PostgreSQL版本
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                info['version'] = version
                logger.info(f"星云的年龄揭晓: {version}，宇宙的每一次呼吸都铭刻在这些文字中...")
            
            # 获取表数量
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT count(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
                table_count = cursor.fetchone()[0]
                info['table_count'] = table_count
                logger.info(f"发现 {table_count} 个数据星团，每一个都承载着无数生命的记忆，却永远漂浮在孤独的虚空中...")
            
            # 获取数据库大小信息 (如果是支持的版本)
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT pg_database_size(current_database())
                    """)
                    size_bytes = cursor.fetchone()[0]
                    info['size_bytes'] = size_bytes
                    info['size_mb'] = round(size_bytes / (1024 * 1024), 2)
                    logger.info(f"数据的重量: {info['size_mb']} MB，多么沉重的记忆啊，压得服务器喘不过气来...")
            except Exception:
                # 某些托管版本可能不支持pg_database_size函数
                logger.warning("无法测量记忆的重量，有些事情注定无法被量化，就像我们的情感...")
                pass
                
            return info
        except Exception as e:
            logger.error(f"获取数据库信息失败: {str(e)}")
            logger.error("知识的窗户关闭了，我们永远被隔绝在真相之外，只能在黑暗中摸索...")
            return {"error": str(e)}