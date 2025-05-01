from django.contrib.auth import views as auth_views
from django.urls import path, include
<<<<<<< HEAD
from .views import BlogListView, BlogDetailView, ReviewCreateView, CommentCreateView, BlogCreateView, login_view, logout_view, sign_up, social_auth_error
=======
from .views import BlogListView, BlogDetailView, ReviewCreateView, CommentCreateView, BlogCreateView, BlogUpdateView, BlogDeleteView, login_view, logout_view, sign_up
>>>>>>> b61a8fc60e9d38d950e69fb10e0f3390a729539a

app_name = 'blogapp'


urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', sign_up, name = 'sign_up'),
    path('', BlogListView.as_view(), name='blog_list'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('blog/add/', BlogCreateView.as_view(), name='add_blog'),
    path('blog/<int:pk>/edit/', BlogUpdateView.as_view(), name='edit_blog'),
    path('blog/<int:pk>/delete/', BlogDeleteView.as_view(), name='delete_blog'),
    path('blog/<int:pk>/', BlogDetailView.as_view(), name='blog_detail'),
    path('blog/<int:pk>/review/', ReviewCreateView.as_view(), name='add_review'),
    path('blog/<int:blog_pk>/review/<int:review_pk>/comment/', CommentCreateView.as_view(), name='add_comment'),
]