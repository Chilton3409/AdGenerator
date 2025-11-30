from django.urls import path
from . import views
from two_factor.views import ProfileView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Core application views
    path('', views.home, name='home'),
    path('generate_advertisement/', views.generate_advertisement, name='generate_advertisement'),
    path('register/', views.register_and_setup_2fa, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
    path('api/post-data/', views.generate_advertisement, name='api_generate_ad'),

    # Ad management views
    path('ads/', views.AdListView.as_view(), name='ad_list'),
    path('ads/<int:pk>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('ad/<pk>/update/', views.AdUpdateView.as_view(), name='ad_update'),
    path('ad/<pk>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),

    # Subscription views
    path('subscribe/', views.create_checkout_session, name='subscribe'),
    path('success/', views.success_view, name='success'),
    path('cancel/', views.cancel_view, name='cancel'),
    path('cancel_subscription/', views.cancel_subscription, name='cancel_subscription'),
    # path('stripe/webhook/', webhooks.Webhook.as_view(), name='stripe-webhook'), # Still commented out

    # Password Reset functionality (using custom views where specified, default Auth views otherwise)
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    # The 'done' view below was a duplicate and is covered by the 'auth_views' version if you use Django defaults
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # The 'complete' view below was a duplicate and is covered by the 'auth_views' version if you use Django defaults
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='your_app_name/password_reset_complete.html'), name='password_reset_complete'),
]