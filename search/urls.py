from django.urls import path
from .views import AdvancedPropertySearchView

urlpatterns = [
    path("advanced/", AdvancedPropertySearchView.as_view(), name="advanced-property-search",),
]
