from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView
from django.views.generic.edit import UpdateView

from blog.forms import CommentForm, EditProfileForm, PostForm
from blog.mixins import CommentAuthorCheckMixin, CommonMixin
from blog.models import Category, Comment, Post

User = get_user_model()


class IndexView(CommonMixin, ListView):
    pass


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.all().order_by('created_date')
        context['form'] = CommentForm()
        context['comment_count'] = post.comments.count()
        return context

    def get_object(self, queryset=None):
        post = super().get_object(queryset=queryset)
        if not post.is_published and (
            not self.request.user.is_authenticated or
            (self.request.user != post.author and not
             self.request.user.is_staff)
        ):
            raise Http404('Такого поста не существует!')
        return post


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[str(self.kwargs['pk'])])


class CategoryPostsView(CommonMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs['category_slug']
        self.category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        queryset = queryset.filter(category=self.category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class UserProfileView(CommonMixin, ListView):
    template_name = 'blog/profile.html'

    def get_queryset(self):
        current_user = self.request.user
        username = self.kwargs['username']
        self.user = get_object_or_404(User, username=username)
        queryset = Post.objects.select_related(
            'location',
            'author',
            'category'
        ).filter(
            author=self.user
        ).order_by(
            '-pub_date'
        ).annotate(
            comment_count=Count('comments')
        )
        if current_user == self.user:
            return queryset
        return super().get_queryset().filter(
            author=self.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
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
    CommentAuthorCheckMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.id}
        )


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class DeletePostView(
    CommentAuthorCheckMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView
):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(instance=self.get_object())
        return context


class DeleteCommentView(
    CommentAuthorCheckMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView
):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.id}
        )
