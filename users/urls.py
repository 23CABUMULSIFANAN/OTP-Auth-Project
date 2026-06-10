from django.urls import path
from .views import (
    RegisterView,
    VerifyOTPView,
    LoginView,
    DashboardView,
    UserDashboardView,
    PropertyView,
    AllUsersView,
    SavePropertyView,
    GetSavedPropertiesView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('user-dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
    path('properties/', PropertyView.as_view(), name='properties'),
    path('all-users/', AllUsersView.as_view(), name='all-users'),
    path('save-property/', SavePropertyView.as_view(), name='save-property'),
    path('saved-properties/', GetSavedPropertiesView.as_view(), name='saved-properties'),
]