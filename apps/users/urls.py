from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView,
    UserProfileView,
    StoreViewSet,
    UserListView,
    UserApprovalView,
    current_user
)

router = DefaultRouter()
router.register(r'stores', StoreViewSet, basename='store')

urlpatterns = [
    # User management
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('current/', current_user, name='current-user'),
    path('list/', UserListView.as_view(), name='user-list'),
    path('<int:pk>/approve/', UserApprovalView.as_view(), name='user-approve'),
    
    # Router URLs
    path('', include(router.urls)),
]
