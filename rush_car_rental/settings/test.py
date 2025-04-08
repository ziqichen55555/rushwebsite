import os

# 数据库设置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('TEST_DB_NAME', 'rush_car_rental_test'),
        'USER': os.environ.get('TEST_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('TEST_DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('TEST_DB_HOST', 'localhost'),
        'PORT': os.environ.get('TEST_DB_PORT', '5432'),
    }
}

# 测试环境特定设置
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 缓存设置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 测试环境Stripe设置
STRIPE_PUBLISHABLE_KEY = os.environ.get('VITE_STRIPE_PUBLIC_KEY', 'pk_test_sample')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_sample')