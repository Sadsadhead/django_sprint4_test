from blog.forms import CommentForm, EditProfileForm, PostForm
from blog.models import Category, Comment, Post
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView
from django.views.generic.edit import UpdateView

from blogicum.settings import POSTS_PER_PAGE

User = get_user_model()


class CommonMixin:
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE
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
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for post in context['page_obj']:
            post.comment_count = Comment.objects.filter(post=post).count()
        return context


class IndexView(CommonMixin, ListView):
    ...


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        post = get_object_or_404(Post, pk=pk)
        context['post'] = post
        context['comments'] = Comment.objects.filter(post=post).order_by(
            'created_date'
        )
        context['form'] = CommentForm()
        context['comment_count'] = Comment.objects.filter(post=post).count()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(comment_count=Count('comments'))
        return queryset

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid() and request.user.is_authenticated:
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
            comment_form = CommentForm()
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        if not post.is_published and (
            not request.user.is_authenticated or request.user != post.author
        ):
            raise Http404('Такого поста не существует!')
        return super().get(request, *args, **kwargs)


class CategoryPostsView(CommonMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        queryset = Post.objects.filter(
            category=category,
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
        return queryset

    def get_context_data(self, **kwargs):
        category_slug = self.kwargs['category_slug']
        category = Category.objects.get(slug=category_slug)
        context = super().get_context_data(**kwargs)
        context['category'] = category
        return context


class UserProfileView(CommonMixin, ListView):
    template_name = 'blog/profile.html'

    def get_queryset(self):
        current_user = self.request.user
        username = self.kwargs['username']
        try:
            profile_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404('Пользователь не найден')
        queryset = Post.objects.select_related(
            'location',
            'author',
            'category'
        ).filter(
            author=profile_user
        ).order_by('-pub_date')
        if current_user.is_authenticated and current_user.username == username:
            return queryset
        else:
            return queryset.filter(
                pub_date__lte=timezone.now()
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = User.objects.get(
                username=self.kwargs['username']
            )
        except User.DoesNotExist:
            raise Http404('Пользователь не найден')
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class EditPostView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        post = self.get_object()
        if not request.user == post.author:
            return redirect(reverse(
                'blog:post_detail', kwargs={'pk': post.pk}
            ))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class EditCommentView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.id}
        )


class EditProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'blog/user.html'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class DeletePostView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView
):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.id}
        )
