from django.urls import path

from .views import (
    FileUpload, RegisterView, ProjectDetailView, ProjectView
)

urlpatterns = [
    path('/register', RegisterView.as_view()),
    path('/file', FileUpload.as_view()),
    path('/<project_uri>', ProjectDetailView.as_view()),
    path('', ProjectView.as_view())
]
