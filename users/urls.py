from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/toggle-block/', views.toggle_user_block, name='toggle_user_block'),
    path('users/<int:user_id>/change-role/', views.change_user_role, name='change_user_role'),
]