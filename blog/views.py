from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from .models import BlogPost, BlogCategory, BlogTag, BlogComment

def blog_home(request):
    """Blog homepage with all posts"""
    posts = BlogPost.objects.filter(status='published').select_related('category')
    
    # Filter by post type
    post_type = request.GET.get('type')
    if post_type:
        posts = posts.filter(post_type=post_type)
    
    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get featured posts
    featured_posts = BlogPost.objects.filter(status='published', is_featured=True)[:3]
    
    # Get categories with post count
    categories = BlogCategory.objects.filter(is_active=True)
    for category in categories:
        category.post_count = BlogPost.objects.filter(category=category, status='published').count()
    
    # Get recent posts
    recent_posts = BlogPost.objects.filter(status='published')[:5]
    
    context = {
        'page_obj': page_obj,
        'featured_posts': featured_posts,
        'categories': categories,
        'recent_posts': recent_posts,
        'current_type': post_type,
    }
    return render(request, 'blog/blog_home.html', context)

def category_posts(request, slug):
    """Display posts by category"""
    category = get_object_or_404(BlogCategory, slug=slug, is_active=True)
    posts = BlogPost.objects.filter(category=category, status='published')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category': category,
        'title': f'Posts in {category.name}',
    }
    return render(request, 'blog/blog_list.html', context)

def tag_posts(request, slug):
    """Display posts by tag"""
    tag = get_object_or_404(BlogTag, slug=slug)
    posts = BlogPost.objects.filter(tags=tag, status='published')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tag': tag,
        'title': f'Posts tagged with {tag.name}',
    }
    return render(request, 'blog/blog_list.html', context)

def post_detail(request, slug):
    """Display single blog post"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count
    post.views += 1
    post.save()
    
    # Get related posts (same category)
    related_posts = BlogPost.objects.filter(
        category=post.category, 
        status='published'
    ).exclude(id=post.id)[:3]
    
    # Get approved comments
    comments = post.comments.filter(is_approved=True)
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'comments': comments,
    }
    return render(request, 'blog/post_detail.html', context)

def like_post(request, post_id):
    """Handle post likes via AJAX"""
    post = get_object_or_404(BlogPost, id=post_id)
    post.likes += 1
    post.save()
    return JsonResponse({'likes': post.likes})

def add_comment(request, post_id):
    """Handle comment submission"""
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, id=post_id)
        name = request.POST.get('name')
        email = request.POST.get('email')
        comment = request.POST.get('comment')
        
        BlogComment.objects.create(
            post=post,
            name=name,
            email=email,
            comment=comment
        )
        
        messages.success(request, 'Your comment has been submitted and will appear after approval.')
    
    return redirect('blog:post_detail', slug=post.slug)