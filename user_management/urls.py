
from django.urls import path
from .views import login, refresh, logout, UserView, UserDetailView

urlpatterns = [
    path('login/', login, name='login'),
    path('refresh/', refresh, name='refresh'),
    path('logout/', logout, name='logout'),
    path('users/', UserView.as_view(), name='users'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user-details'),
];