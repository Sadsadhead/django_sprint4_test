from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    ),
    path(
        'posts/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostsView.as_view(),
        name='category_posts'
    ),
    path(
        'profile/<str:username>/',
        views.UserProfileView.as_view(),
        name='profile'
    ),
    path(
        'posts/create/',
        views.CreatePostView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:pk>/edit/',
        views.EditPostView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:pk>/comment/',
        views.PostDetailView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:pk>/',
        views.EditCommentView.as_view(),
        name='edit_comment'
    ),
    path(
        'user/edit/',
        views.EditProfileView.as_view(),
        name='edit_profile'
    ),
    path(
        'posts/<int:pk>/delete/',
        views.DeletePostView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:pk>/',
        views.DeleteCommentView.as_view(),
        name='delete_comment'
    ),
]
