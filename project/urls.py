from django.urls import path, include

from .views import (
    FileUpload, RegisterView, ProjectDetailView
)

urlpatterns = [
    path('/register', RegisterView.as_view()),
    path('/file', FileUpload.as_view()),
    path('/<project_uri>', ProjectDetailView.as_view())
]
