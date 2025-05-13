from django.contrib.auth import views as auth_views
from django.urls import path, include
from .views import BlogListView, BlogDetailView, ReviewCreateView, CommentCreateView, BlogCreateView, BlogUpdateView, BlogDeleteView, LoginView, LogoutView, SignUpView, ProfileView, ProfileUpdateView, ProfileDeleteView
from .views import LoginView
from .views import RegisterView

app_name = 'blogapp'


urlpatterns = [
    path('', BlogListView.as_view(), name='blog_list'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', SignUpView.as_view(), name='sign_up'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/<str:username>/', ProfileView.as_view(), name='profile'),
    path('user/<str:username>/edit/', ProfileUpdateView.as_view(), name='edit_profile'),
    path('user/<str:username>/delete/', ProfileDeleteView.as_view(), name='delete_profile'),
    path('blog/add/', BlogCreateView.as_view(), name='add_blog'),
    path('blog/<int:pk>/edit/', BlogUpdateView.as_view(), name='edit_blog'),
    path('blog/<int:pk>/delete/', BlogDeleteView.as_view(), name='delete_blog'),
    path('blog/<int:pk>/', BlogDetailView.as_view(), name='blog_detail'),
    path('blog/<int:pk>/review/', ReviewCreateView.as_view(), name='add_review'),
    path('blog/<int:blog_pk>/review/<int:review_pk>/comment/', CommentCreateView.as_view(), name='add_comment'),
    path('login_modal', LoginView.as_view(), name='login_modal'),
    path('register_modal', RegisterView.as_view(), name='register_modal'),
]