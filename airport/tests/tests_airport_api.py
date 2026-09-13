from django.test import TestCase
from django.urls import reverse

from airport.models import (
    Flight,
    Country,
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane
)


AIRPORT_URL = reverse("airport:airport-list")
AIRPLANE_URL = reverse("airplane:airplane-list")
FLIGHT_URL = reverse("flight:flight-list")
ORDER_URL = reverse("airport:order-list")


def sample_country(**params):
    defaults = {
        "name": "Ukraine",
    }
    defaults.update(**params)

    return Country.objects.create(**defaults)


def sample_city(**params):
    country = params.pop("country", sample_country())

    defaults = {
        "name": "Kyiv",
        "country": country
    }
    defaults.update(**params)

    return City.objects.create(**defaults)


def sample_airport(**params):
    city = params.pop("closest_big_city", sample_city())

    defaults = {
        "name": "Boryspil International Airport",
        "iata_code": "KBP",
        "closest_big_city": city,
    }
    defaults.update(**params)

    return Airport.objects.create(**defaults)


def sample_route(**params):
    source = params.pop("source", sample_airport())

    destination = params.pop(
        "destination",
        sample_airport(
            name="Frankfurt Airport",
            iata_code="FRA",
            closest_big_city=sample_city(name="Frankfurt"),
        )
    )

    defaults = {
        "source": source,
        "destination": destination,
    }
    defaults.update(**params)

    return Route.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {
        "name": "Airliner",
    }
    defaults.update(**params)

    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    airplane_type = params.pop(
        "airplane_type",
        sample_airplane_type(),
    )
    defaults = {
        "name": "Boing 747",
        "rows": 20,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(**params)

    return Airplane.objects.create(**defaults)

def sample_flight(**params):
    route = params.pop("route", sample_route())
    airplane = params.pop("airplane", sample_airplane())

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2026-09-20 14:00:00",
        "arrival_time": "2026-09-20 17:00:00"
    }
    defaults.update(**params)

    return Flight.objects.create(**defaults)


def image_upload_url(airplane_id):
    return reverse("airport:airplane-upload-image", args=[airplane_id])


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])



