from django.urls import path, include

from .views import KakaoSignInView

urlpatterns = [
    path('/signin/kakao', KakaoSignInView.as_view())
]