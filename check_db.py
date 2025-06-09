import os
import django
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rush_car_rental.settings')
django.setup()

from django.db import connection
from cars.models import VehicleCategory, VehicleType, VehicleCategoryType, Car, CarCategory
from locations.models import Location

def check_table_structure():
    """检查数据库表结构"""
    print("\n=== 检查数据库表结构 ===")
    with connection.cursor() as cursor:
        # 获取所有表名
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\n检查表: {table_name}")
            
            # 获取表结构
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
            """)
            columns = cursor.fetchall()
            
            for column in columns:
                print(f"  - {column[0]}: {column[1]}")

def check_model_data():
    """检查模型数据"""
    print("\n=== 检查模型数据 ===")
    
    # 检查 VehicleType
    print("\nVehicleType 数据:")
    vehicle_types = VehicleType.objects.all()
    print(f"总数: {vehicle_types.count()}")
    for vt in vehicle_types:
        print(f"  - ID: {vt.id}, Name: {vt.name}")
    
    # 检查 VehicleCategoryType
    print("\nVehicleCategoryType 数据:")
    category_types = VehicleCategoryType.objects.all()
    print(f"总数: {category_types.count()}")
    for ct in category_types:
        print(f"  - ID: {ct.id}, Type: {ct.category_type}, Web Available: {ct.web_available}")
    
    # 检查 VehicleCategory
    print("\nVehicleCategory 数据:")
    categories = VehicleCategory.objects.all()
    print(f"总数: {categories.count()}")
    for cat in categories:
        print(f"  - ID: {cat.id}")
        print(f"    Name: {cat.name}")
        print(f"    Category Type: {cat.category_type}")
        print(f"    Vehicle Type: {cat.vehicle_type}")
        print(f"    Daily Rate: {cat.daily_rate}")
        print(f"    Is Available: {cat.is_available}")
        print(f"    Renting Category: {cat.renting_category}")
    
    # 检查 Location
    print("\nLocation 数据:")
    locations = Location.objects.all()
    print(f"总数: {locations.count()}")
    for loc in locations:
        print(f"  - ID: {loc.id}, Name: {loc.name}, Is Airport: {loc.is_airport}")

def check_relationships():
    """检查模型关系"""
    print("\n=== 检查模型关系 ===")
    
    # 检查 VehicleCategory 和 VehicleType 的关系
    print("\nVehicleCategory 和 VehicleType 的关系:")
    categories = VehicleCategory.objects.select_related('vehicle_type').all()
    for cat in categories:
        print(f"  - Category: {cat.name}")
        print(f"    Vehicle Type: {cat.vehicle_type.name if cat.vehicle_type else 'None'}")
    
    # 检查 VehicleCategory 和 Location 的关系
    print("\nVehicleCategory 和 Location 的关系:")
    categories = VehicleCategory.objects.prefetch_related('locations').all()
    for cat in categories:
        print(f"  - Category: {cat.name}")
        print(f"    Locations: {', '.join(loc.name for loc in cat.locations.all())}")

if __name__ == '__main__':
    try:
        check_table_structure()
        check_model_data()
        check_relationships()
        print("\n检查完成！")
    except Exception as e:
        print(f"\n检查过程中出现错误: {str(e)}")
        sys.exit(1) 