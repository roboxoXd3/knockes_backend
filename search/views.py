from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from properties.models import Property
from properties.serializers import PropertySerializer


class AdvancedPropertySearchView(APIView):
    def get_permissions(self):
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Property.objects.all()

    def get(self, request):
        qs = self.apply_filters(self.get_queryset(), request.GET)
        serializer = PropertySerializer(qs.distinct(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        search = request.data.get("search", "").strip().lower()
        if not search:
            return Response(
                {"detail": "Empty search string"}, status=status.HTTP_400_BAD_REQUEST
            )

        tokens = search.split()
        query = Q()

        for token in tokens:
            if token in {"1bhk", "2bhk", "3bhk", "4bhk", "5bhk"}:
                bhk = int(token[0])
                query |= Q(bedrooms=bhk)
            elif token.isdigit():
                num = int(token)
                # Smart handling: assume it's a price or room count
                if num <= 10:
                    query |= Q(bedrooms=num)
                else:
                    query |= Q(mini_price__lte=num) | Q(max_price__gte=num)
            elif token in ["flat", "apartment"]:
                query |= Q(type__icontains="flat_apartment")
            elif token in ["house", "villa", "detached"]:
                query |= Q(type__icontains="detached_house")
            elif token in ["office", "workspace"]:
                query |= Q(type__icontains="office_space")
            elif token in ["shop", "store"]:
                query |= Q(type__icontains="shop")
            elif token in ["furnished"]:
                query |= Q(furnished=True)
            elif token in ["unfurnished"]:
                query |= Q(furnished=False)
            elif token in ["serviced"]:
                query |= Q(serviced=True)
            elif token in ["nonserviced", "unserviced"]:
                query |= Q(serviced=False)
            elif token in ["rent", "sale", "shortlet", "jv"]:
                query |= Q(category__icontains=token)
            else:
                query |= (
                    Q(title__icontains=token)
                    | Q(description__icontains=token)
                    | Q(location__icontains=token)
                    | Q(city__icontains=token)
                    | Q(state__icontains=token)
                    | Q(keyword_tags__icontains=token)
                )

        qs = self.get_queryset().filter(query).distinct()
        serializer = PropertySerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def apply_filters(self, qs, params):
        location = params.get("location")
        category = params.get("category")
        type_ = params.get("type")
        bedrooms = params.get("bedrooms")
        mini_price = params.get("mini_price")
        max_price = params.get("max_price")
        furnished = params.get("furnished")
        serviced = params.get("serviced")
        keyword = params.get("keyword")

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
        return qs
