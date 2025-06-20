from django.urls import path
from .views import (
    PropertyListCreateView,
    PropertyRetrieveUpdateView,
    PropertyDeleteView,
    AddRemoveFavoriteView,
    UserFavoritesListView,
    PropertyCompareView,
    PropertyReviewCreateView,
    PropertyReviewListView,
    PropertyTypeListView,
)

urlpatterns = [
    path("properties/", PropertyListCreateView.as_view(), name="property-list"),
    path("properties/create/", PropertyListCreateView.as_view(), name="property-create"),
    path("properties/<int:id>/", PropertyRetrieveUpdateView.as_view(), name="property-detail"),
    path("properties/<int:id>/delete/", PropertyDeleteView.as_view(), name="property-delete"),
    path("properties/<int:id>/favorite/", AddRemoveFavoriteView.as_view(), name="add-remove-favorite"),
    path("users/favorites/", UserFavoritesListView.as_view(), name="user-favorites"),
    path("properties/compare/", PropertyCompareView.as_view(), name="property-compare"),
    path("properties/<int:property_id>/reviews/", PropertyReviewListView.as_view(), name="property-review-list"),
    path("properties/<int:property_id>/reviews/add/", PropertyReviewCreateView.as_view(), name="property-review-create"),
    path("properties/types/", PropertyTypeListView.as_view(), name="property-types"),
]
