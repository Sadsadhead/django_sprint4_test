from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import redirect

from blog.models import Post

User = get_user_model()


class CommonMixin:
    model = Post
    template_name = 'blog/index.html'
    paginate_by = settings.POSTS_PER_PAGE
    ordering = '-pub_date'

    def get_queryset(self):
        return Post.objects.select_related(
            'location',
            'author',
            'category'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')


class CommentAuthorCheckMixin:

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author


class EditPostDispatchMixin:

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if not request.user == post.author:
            return redirect(reverse(
                'blog:post_detail', kwargs={'pk': post.pk}
            ))
        return super().dispatch(request, *args, **kwargs)
