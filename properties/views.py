from django.db.models import Avg
from rest_framework import generics, filters, status, permissions
from properties.permissions import ReadOnlyOrAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Property, Favorite, PropertyReview
from .serializers import FavoriteSerializer, PropertySerializer, PropertyReviewSerializer
from rest_framework.exceptions import PermissionDenied


class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = Property.objects.all().prefetch_related("images", "amenities")
    serializer_class = PropertySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "city", "state"]
    ordering_fields = ["price", "created_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        user = self.request.user

        if user.user_type != "owner":
            raise PermissionDenied(
                "Only users with 'owner' user_type can create properties."
            )

        serializer.save(owner=user)


class PropertyRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Property.objects.all().prefetch_related("images", "amenities")
    serializer_class = PropertySerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    lookup_field = "id"


class PropertyDeleteView(generics.DestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_field = "id"


class AddRemoveFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        user = request.user
        property = Property.objects.filter(id=id).first()

        if not property:
            return Response(
                {"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND
            )

        favorite, created = Favorite.objects.get_or_create(user=user, property=property)
        if created:
            return Response(
                {"message": "Property added to favorites."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"message": "Property already in favorites."}, status=status.HTTP_200_OK
        )

    def delete(self, request, id):
        user = request.user
        Favorite.objects.filter(user=user, property_id=id).delete()
        return Response(
            {"message": "Property removed from favorites."},
            status=status.HTTP_204_NO_CONTENT,
        )


class UserFavoritesListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related(
            "property"
        )


class PropertyCompareView(APIView):
    def post(self, request):
        ids = request.data.get("property_ids", [])
        if not ids or not isinstance(ids, list):
            return Response(
                {"error": "A list of property IDs is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        properties = Property.objects.filter(id__in=ids)
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)


class PropertyReviewCreateView(generics.CreateAPIView):
    queryset = PropertyReview.objects.all()
    serializer_class = PropertyReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class PropertyReviewListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, property_id):
        reviews = PropertyReview.objects.filter(property_id=property_id).order_by(
            "-created_at"
        )
        total_reviews = reviews.count()
        avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"] or 0.0

        serializer = PropertyReviewSerializer(reviews, many=True)

        formatted_reviews = [
            {
                "id": index + 1,  # serial number
                "user": {
                    "name": item["user"]["name"],
                    "avatar": item["user"]["avatar"],
                },
                "rating": item["rating"],
                "comment": item["comment"],
                "date": item["created_at"],
            }
            for index, item in enumerate(serializer.data)
        ]

        return Response(
            {
                "reviews": {
                    "total_reviews": total_reviews,
                    "average_rating": round(avg_rating, 1),
                    "reviews_list": formatted_reviews,
                }
            }
        )
