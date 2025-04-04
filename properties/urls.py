from django.urls import path
from .views import (
    PropertyListCreateView,
    PropertyRetrieveUpdateView,
    PropertyDeleteView,
)

urlpatterns = [
    path("properties/", PropertyListCreateView.as_view(), name="property-list"),
    path(
        "properties/create/", PropertyListCreateView.as_view(), name="property-create"
    ),
    path(
        "properties/<int:id>/",
        PropertyRetrieveUpdateView.as_view(),
        name="property-detail",
    ),
    path(
        "properties/<int:id>/delete/",
        PropertyDeleteView.as_view(),
        name="property-delete",
    ),
]
