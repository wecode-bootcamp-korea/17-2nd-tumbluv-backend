from django.urls import path

from user.views import ValidateCodeView, KakaoSignInView

urlpatterns = [
    path('/signup/email-validation', ValidateCodeView.as_view()),
    path('/signin/kakao', KakaoSignInView.as_view()),
]
