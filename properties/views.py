# views.py

from rest_framework import generics, filters
from properties.permissions import ReadOnlyOrAuthenticated
from .models import Property
from .serializers import PropertySerializer

class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = Property.objects.all().prefetch_related("images", "amenities")
    serializer_class = PropertySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "city", "state"]
    ordering_fields = ["price", "created_at"]


class PropertyRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [ReadOnlyOrAuthenticated]  # 👈 Here!
    lookup_field = "id"


class PropertyDeleteView(generics.DestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_field = "id"
