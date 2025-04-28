from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'created_at', 'is_active')
    list_filter = ('rating', 'is_active', 'created_at')
    search_fields = ('name', 'content', 'role')
    ordering = ('-created_at',)