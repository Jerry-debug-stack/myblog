from django.db import models
from django.utils import timezone
from slugify import slugify

class Category(models.Model):
    """分类模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name='URL标识')
    description = models.TextField(blank=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':  # 如果没有slug，自动生成
            print("fault")
            self.slug = slugify(self.name)
        print(self.slug)
        
        # 确保slug唯一（处理重名情况）
        original_slug = self.slug
        counter = 1
        while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        super().save(*args, **kwargs)

class Article(models.Model):
    """文章模型"""
    title = models.CharField(max_length=200, verbose_name='标题')
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name='URL标识')
    content = models.TextField(verbose_name='内容')
    excerpt = models.TextField(blank=True, max_length=500, verbose_name='摘要')
    
    # 分类关系（多对多）
    categories = models.ManyToManyField(
        Category, 
        related_name='articles',
        verbose_name='分类'
    )
    
    # 文章元数据
    is_published = models.BooleanField(default=True, verbose_name='是否发布')
    is_markdown = models.BooleanField(default=True, verbose_name='Markdown格式')
    pub_date = models.DateTimeField(default=timezone.now, verbose_name='发布日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-pub_date']
        indexes = [
            models.Index(fields=['-pub_date']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        # 可以在urls.py中定义
        from django.urls import reverse
        return reverse('article_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':  # 如果没有slug，自动生成
            self.slug = slugify(self.title)
        
        # 确保slug唯一（处理重名情况）
        original_slug = self.slug
        counter = 1
        while Article.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        super().save(*args, **kwargs)

class Comment(models.Model):
    """评论模型"""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='文章'
    )
    content = models.TextField(verbose_name='评论内容')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    
    # 可选：如果需要简单审核功能
    is_approved = models.BooleanField(default=True, verbose_name='是否审核通过')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-pub_date']
    
    def __str__(self):
        return f'评论于 {self.pub_date.strftime("%Y-%m-%d %H:%M")}'