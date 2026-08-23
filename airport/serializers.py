from rest_framework import serializers

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


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        source="country",
        queryset=Country.objects.all(),
        write_only=True,
    )

    class Meta:
        model = City
        fields = ("id", "name", "country", "country_id")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "iata_code", "closest_big_city")


class AirportListSerializer(serializers.ModelSerializer):
    closest_big_city = serializers.StringRelatedField()

    class Meta:
        model = Airport
        fields = ("id", "name", "iata_code", "closest_big_city")


class AirportDetailSerializer(serializers.ModelSerializer):
    closest_big_city = CitySerializer(many=False, read_only=True)

    class Meta:
        model = Airport
        fields = ("id", "name", "iata_code", "closest_big_city")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.StringRelatedField()
    airplane_type_id = serializers.PrimaryKeyRelatedField(
        source="airplane_type",
        queryset=AirplaneType.objects.all(),
        write_only=True
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "airplane_type_id"
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "distance", "source", "destination")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()

    class Meta:
        model = Route
        fields = ("id", "distance", "source", "destination")


class RouteAirportSerializer(serializers.ModelSerializer):
    closest_big_city = CitySerializer(read_only=True)

    class Meta:
        model = Airport
        fields = ("id", "name", "iata_code", "closest_big_city")


class RouteRetrieveSerializer(serializers.ModelSerializer):
    source = RouteAirportSerializer(many=False, read_only=True)
    destination = RouteAirportSerializer(many=False, read_only=True)

    class Meta:
        model = Route
        fields = ("id", "distance", "source", "destination")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "position")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time"
        )


class FlightListSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField()
    airplane = serializers.StringRelatedField()
    crew = serializers.StringRelatedField(many=True)


    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time"
        )



class FlightRetrieveSerializer(serializers.ModelSerializer):
    route = RouteRetrieveSerializer(many=False, read_only=True)
    airplane = AirplaneSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time"
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")
