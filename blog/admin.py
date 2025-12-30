from django.contrib import admin
from .models import Category, Article, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'pub_date', 'is_published', 'is_markdown']
    list_filter = ['is_published', 'is_markdown', 'categories', 'pub_date']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'content']
    filter_horizontal = ['categories']  # 方便选择分类
    date_hierarchy = 'pub_date'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('分类设置', {
            'fields': ('categories',)
        }),
        ('发布设置', {
            'fields': ('is_published', 'is_markdown', 'pub_date')
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['content_preview', 'article', 'pub_date', 'is_approved']
    list_filter = ['is_approved', 'pub_date']
    search_fields = ['content', 'article__title']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
