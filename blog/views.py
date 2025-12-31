from django.shortcuts import render,get_object_or_404
from django.http import HttpRequest
from .models import Article,Category
from django.db.models import Count,Q
from django.utils import timezone
from collections import defaultdict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import markdown
from django.utils.safestring import mark_safe

# tags recent_article archives
def get_normal():
    recent_articles = Article.objects.filter(is_published=True).order_by('-pub_date')[:5]
    tags = Category.objects.all()[:5]
    return tags,recent_articles

def fault_view(request:HttpRequest,exception=None):
    tags,recent_articles = get_normal()
    return render(request,"404.html",{"tags":tags,"recent_articles":recent_articles})

# article_title article_created_at article_updated_at article_tags
# article_content_html article_content
# previous_article next_article
def article_detail(request, slug):
    # 获取当前文章
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    # 如果是Markdown内容，转换为HTML
    if article.is_markdown:
        article_content_html = markdown.markdown(
            article.content,
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'pymdownx.tasklist',
                'pymdownx.tilde',
            ]
        )
        article_content = ""
    else:
        article_content_html = ""
        article_content = article.content
    
    # 获取上一篇文章和下一篇文章
    previous_article = Article.objects.filter(
        is_published=True,
        created_at__lt=article.created_at
    ).order_by('-created_at').first()
    
    next_article = Article.objects.filter(
        is_published=True,
        created_at__gt=article.created_at
    ).order_by('created_at').first()

    tags,recent_articles = get_normal()
    
    context = {
        'tags': tags,"recent_articles":recent_articles,
        'previous_article': previous_article,'next_article': next_article,
        'article_title':article.title,"article_created_at":article.created_at,
        "article_updated_at":article.updated_at,"article_content_html":mark_safe(article_content_html),
        "article_content":article_content,"article_tags":article.categories.all()
    }
    
    return render(request, 'article_detail.html', context)

def index_view(request:HttpRequest):
    tags,recent_articles = get_normal()
    return render(request,"index.html",{"tags":tags,"recent_articles":recent_articles})

def about_view(request:HttpRequest):
    tags,recent_articles = get_normal()
    return render(request,"about.html",{"tags":tags,"recent_articles":recent_articles})

def archive_view(request):
    # 获取所有已发布的文章，按时间倒序排列
    articles = Article.objects.filter(is_published=True).order_by('-pub_date')
    
    # 组织归档数据：按年份和月份分组
    archive_data = defaultdict(lambda: defaultdict(list))
    for article in articles:
        year = article.pub_date.year
        month = article.pub_date.month
        archive_data[year][month].append(article)
    
    # 计算每年的文章总数
    year_total_counts = {}
    for year, months in archive_data.items():
        total = 0
        for month_articles in months.values():
            total += len(month_articles)
        year_total_counts[year] = total
    
    # 统计信息
    total_articles = articles.count()
    total_tags = Category.objects.filter(articles__is_published=True).distinct().count()
    
    # 获取最早的文章日期
    oldest_article = articles.last()
    oldest_article_date = oldest_article.pub_date if oldest_article else timezone.now()
    
    # 计算每年文章数量（用于年份导航）
    year_counts = {}
    for year in archive_data.keys():
        year_counts[year] = year_total_counts[year]
    
    tags,recent_articles = get_normal()
    archive_data_opt = {}
    for i in archive_data.keys():
        temp = {}
        temptar = archive_data[i]
        for j in temptar.keys():
            temp[j] = temptar[j]
        archive_data_opt[i] = temp

    context = {
        'archive_data': archive_data_opt,
        'year_total_counts': year_total_counts,
        'total_articles': total_articles,
        'total_tags': total_tags,
        'oldest_article_date': oldest_article_date,
        'year_counts': year_counts,
        
        # 侧边栏数据
        'tags': tags,
        'recent_articles': recent_articles,
    }
    
    return render(request, 'archive.html', context)

def tags_view(request):
    # 获取所有标签，并动态计算每个标签下的文章数量
    # 使用 annotate 动态添加 article_count 字段
    tags = Category.objects.annotate(
        article_count=Count('articles',filter=Q(articles__is_published=True))  # 这会动态计算每个标签关联的文章数量
    ).order_by('-article_count', 'name')
    
    # 计算总文章数
    total_articles = Article.objects.filter(is_published=True).count()
    
    # 为标签云计算字体大小和颜色
    if tags.exists():
        # 获取有文章的标签的文章数量列表
        tag_article_counts = [tag.article_count for tag in tags if tag.article_count > 0] # type: ignore
        
        if tag_article_counts:  # 确保有标签有文章
            max_count = max(tag_article_counts)
            min_count = min(tag_article_counts) if len(tag_article_counts) > 1 else 0
            
            for tag in tags:
                article_count = tag.article_count # type: ignore
                
                # 计算标签云的字体大小（根据文章数量动态调整）
                if max_count != min_count and article_count > 0:
                    # 字体大小范围：14px 到 36px
                    font_size = 14 + (article_count - min_count) * 22 / (max_count - min_count)
                elif article_count > 0:
                    font_size = 28  # 所有有文章的标签文章数量相同时的默认值
                else:
                    font_size = 14  # 没有文章的标签
                
                tag.font_size = round(font_size) # type: ignore
                
                # 根据文章数量分配不同的颜色主题
                if article_count > 10:
                    tag.color = '#ffffff' # type: ignore
                    tag.bg_color = '#007bff'  # type: ignore # 蓝色 - 热门
                elif article_count > 5:
                    tag.color = '#ffffff' # type: ignore
                    tag.bg_color = '#28a745'  # type: ignore # 绿色 - 较热门
                elif article_count > 2:
                    tag.color = '#212529' # type: ignore
                    tag.bg_color = '#ffc107'  # type: ignore # 黄色 - 一般
                elif article_count > 0:
                    tag.color = '#212529' # type: ignore
                    tag.bg_color = '#e9ecef'  # type: ignore # 灰色 - 较少
                else:
                    tag.color = '#6c757d' # type: ignore
                    tag.bg_color = '#f8f9fa'  # type: ignore # 更浅的灰色 - 无文章
                
                # 获取该标签下的最新文章发布时间
                latest_article = tag.articles.filter(is_published=True).order_by('-created_at').first() # type: ignore
                
                if latest_article:
                    tag.latest_update = latest_article.created_at # type: ignore
                else:
                    tag.latest_update = None # type: ignore
                    
                # 为模板添加简化的文章数量显示
                if article_count == 0:
                    tag.article_count_display = "暂无文章" # type: ignore
                elif article_count == 1:
                    tag.article_count_display = "1 篇文章" # type: ignore
                else:
                    tag.article_count_display = f"{article_count} 篇文章" # type: ignore
        else:
            # 没有标签有文章的情况
            for tag in tags:
                tag.font_size = 14 # type: ignore
                tag.color = '#6c757d' # type: ignore
                tag.bg_color = '#f8f9fa' # type: ignore
                tag.latest_update = None # type: ignore
                tag.article_count_display = "暂无文章" # type: ignore
    else:
        # 没有标签的情况
        tags = []
    recent_articles = Article.objects.filter(is_published=True).order_by('-pub_date')[:5]
    # 准备上下文数据
    context = {
        'tags': tags,
        'total_articles': total_articles,
        'recent_articles':recent_articles
    }
    
    return render(request, 'tags.html', context)

def tag_detail_view(request, slug):
    # 获取标签对象
    tag = get_object_or_404(Category, slug=slug)
    # 获取该标签下的所有文章
    articles_list = tag.articles.filter(is_published=True).order_by('-pub_date') # type: ignore
    # 分页
    paginator = Paginator(articles_list, 10)  # 每页10篇文章
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)
    
    tags,recent_articles = get_normal()

    context = {
        'tag': tag,
        'articles': articles,
        'articles_count': articles_list.count(),
        'recent_articles': recent_articles,
        'tags': tags,
    }
    
    return render(request, 'tag.html', context)
