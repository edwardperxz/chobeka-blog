from django.contrib.auth import views as auth_views
from django.urls import path, include
from .views import RegisterView, BlogListView, BlogDetailView, ReviewCreateView, CommentCreateView, BlogCreateView, BlogUpdateView, BlogDeleteView, LoginView, LogoutView, SignUpView, ProfileView, ProfileUpdateView, ProfileSettingsView, PasswordUpdateView, EmailUpdateView, ProfileDeleteView, add_comment


app_name = 'blogapp'


urlpatterns = [
    path('', BlogListView.as_view(), name='blog_list'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', SignUpView.as_view(), name='sign_up'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/<str:username>/', ProfileView.as_view(), name='profile'),
    path('user/<str:username>/settings/', ProfileSettingsView.as_view(), name='profile_settings'),
    path('user/<str:username>/email-change/', EmailUpdateView.as_view(), name='email_change'),
    path('user/<str:username>/password-change/', PasswordUpdateView.as_view(), name='password_change'),
    path('user/<str:username>/edit-profile/', ProfileUpdateView.as_view(), name='edit_profile'),
    path('user/<str:username>/delete-profile/', ProfileDeleteView.as_view(), name='delete_profile'),
    path('blog/add/', BlogCreateView.as_view(), name='add_blog'),
    path('blog/<int:pk>/edit/', BlogUpdateView.as_view(), name='edit_blog'),
    path('blog/<int:pk>/delete/', BlogDeleteView.as_view(), name='delete_blog'),
    path('blog/<int:pk>/', BlogDetailView.as_view(), name='blog_detail'),
    path('blog/<int:pk>/review/', ReviewCreateView.as_view(), name='add_review'),
    path('blog/<int:blog_pk>/review/<int:review_pk>/comment/', add_comment, name='add_comment'),
    path('login_modal', LoginView.as_view(), name='login_modal'),
    path('register_modal', RegisterView.as_view(), name='register_modal'),
]