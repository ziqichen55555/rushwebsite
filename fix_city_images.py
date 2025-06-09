#!/usr/bin/env python3

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rush_car_rental.settings.development')
django.setup()

from locations.models import CityHighlight

def fix_city_images():
    """修复墨尔本和布里斯班的城市图片"""
    
    highlights = CityHighlight.objects.all()

    # 墨尔本 - 使用真正的墨尔本城市CBD和雅拉河景观
    melbourne = highlights.filter(city='Melbourne').first()
    if melbourne:
        # 使用墨尔本CBD天际线和雅拉河的专业照片
        melbourne.image_url = 'https://images.unsplash.com/photo-1545044846-351ba102b6d5?w=500&h=300&fit=crop&auto=format'
        melbourne.save()
        print(f'✅ 修复墨尔本图片: 墨尔本CBD天际线')
        print(f'   URL: {melbourne.image_url}')

    # 布里斯班 - 使用一个可靠的布里斯班城市图片
    brisbane = highlights.filter(city='Brisbane').first()  
    if brisbane:
        # 使用一个更可靠的布里斯班图片URL
        brisbane.image_url = 'https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?w=500&h=300&fit=crop&auto=format'
        brisbane.save()
        print(f'✅ 更新布里斯班图片: 使用可靠的城市景观')
        print(f'   URL: {brisbane.image_url}')

    print('\n🎉 墨尔本和布里斯班的图片已修复！')

if __name__ == '__main__':
    fix_city_images() 