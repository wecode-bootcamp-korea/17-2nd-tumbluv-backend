from django.urls    import path
from .views  import ProjectDetailView

urlpatterns = [
        path('/<project_uri>', ProjectDetailView.as_view())
        ]
