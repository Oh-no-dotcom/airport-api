from django.db.models import F, Count
from django.db.models.query import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from airport.models import (
    Country,
    City,
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Crew,
    Flight,
    Order,
    Ticket,
)
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    AirportSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    RouteSerializer,
    CrewSerializer,
    FlightSerializer,
    OrderSerializer,
    AirportListSerializer,
    AirportDetailSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
    OrderListSerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.select_related("country")
    serializer_class = CitySerializer
    filterset_fields = ["country"]


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    filterset_fields = [
        "name",
        "iata_code",
        "closest_big_city__name"
    ]

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportDetailSerializer
        return AirportSerializer

    def get_queryset(self):
        return Airport.objects.select_related(
            "closest_big_city",
            "closest_big_city__country"
        )


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        parser_classes=[MultiPartParser]
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related(
        "source__closest_big_city__country",
        "destination__closest_big_city__country"
    )
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    filterset_fields = [
        "route",
        "airplane",
        "departure_time",
        "arrival_time"
    ]

    def get_queryset(self):
        queryset = Flight.objects.select_related(
        "route__source__closest_big_city__country",
        "route__destination__closest_big_city__country",
        "airplane__airplane_type",
        ).prefetch_related("crew")

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("tickets")

        if self.action == "list":
            queryset = queryset.annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        )
        return queryset


    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        Prefetch(
            "tickets",
            queryset=Ticket.objects.select_related(
                "flight__route__source__closest_big_city",
                "flight__route__destination__closest_big_city",
                "flight__airplane__airplane_type"
            ).prefetch_related(
                "flight__crew"
            )
        )
    )
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
