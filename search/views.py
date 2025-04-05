from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from properties.models import Property
from properties.serializers import PropertySerializer


class AdvancedPropertySearchView(APIView):
    def get(self, request):
        query = Property.objects.prefetch_related("amenities").all()
        params = request.query_params

        # filters same as discussed
        title = params.get("title")
        city = params.get("city")
        state = params.get("state")
        country = params.get("country")
        price_min = params.get("price_min")
        price_max = params.get("price_max")
        area_min = params.get("area_min")
        area_max = params.get("area_max")
        bedrooms = params.get("bedrooms")
        bathrooms = params.get("bathrooms")
        amenities = params.getlist("amenities")

        if title:
            query = query.filter(Q(title__icontains=title) | Q(description__icontains=title))
        if city:
            query = query.filter(city__iexact=city)
        if state:
            query = query.filter(state__iexact=state)
        if country:
            query = query.filter(country__iexact=country)
        if price_min:
            query = query.filter(price__gte=price_min)
        if price_max:
            query = query.filter(price__lte=price_max)
        if area_min:
            query = query.filter(area_sqft__gte=area_min)
        if area_max:
            query = query.filter(area_sqft__lte=area_max)
        if bedrooms:
            query = query.filter(bedrooms=bedrooms)
        if bathrooms:
            query = query.filter(bathrooms=bathrooms)
        if amenities:
            for amenity in amenities:
                query = query.filter(amenities__name__iexact=amenity)

        serializer = PropertySerializer(query.distinct(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
