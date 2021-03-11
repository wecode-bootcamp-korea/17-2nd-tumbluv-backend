from django.urls import path, include

urlpatterns = [
    path('user', include('user.urls')),
    path('project', include('project.urls')),
]