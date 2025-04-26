from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from properties.models import Property
from properties.serializers import PropertySerializer


class AdvancedPropertySearchView(APIView):
    def get(self, request):
        qs = Property.objects.all()

        location = request.GET.get("location")
        category = request.GET.get("category")
        type_ = request.GET.get("type")
        bedrooms = request.GET.get("bedrooms")
        mini_price = request.GET.get("mini_price")
        max_price = request.GET.get("max_price")
        furnished = request.GET.get("furnished")
        serviced = request.GET.get("serviced")
        keyword = request.GET.get("keyword")

        if location:
            qs = qs.filter(location__icontains=location)

        if category:
            qs = qs.filter(category=category)

        if type_:
            qs = qs.filter(type=type_)

        if bedrooms:
            qs = qs.filter(bedrooms__gte=int(bedrooms))

        if mini_price:
            qs = qs.filter(mini_price__gte=float(mini_price))

        if max_price:
            qs = qs.filter(max_price__lte=float(max_price))

        if furnished is not None:
            if furnished.lower() == "true":
                qs = qs.filter(furnished=True)
            elif furnished.lower() == "false":
                qs = qs.filter(furnished=False)

        if serviced is not None:
            if serviced.lower() == "true":
                qs = qs.filter(serviced=True)
            elif serviced.lower() == "false":
                qs = qs.filter(serviced=False)

        if keyword:
            qs = qs.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(keyword_tags__icontains=keyword)
            )

        # ✅ FIX HERE:
        serializer = PropertySerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
