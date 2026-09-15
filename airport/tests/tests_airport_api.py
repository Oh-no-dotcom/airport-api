import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from airport.models import (
    Flight,
    Country,
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane
)
from airport.serializers import AirportDetailSerializer, FlightListSerializer

AIRPORT_URL = reverse("airport:airport-list")
AIRPLANE_URL = reverse("airport:airplane-list")
FLIGHT_URL = reverse("airport:flight-list")
ORDER_URL = reverse("airport:order-list")


def sample_country(**params):
    defaults = {
        "name": "Ukraine",
    }
    defaults.update(**params)

    return Country.objects.create(**defaults)


def sample_city(**params):
    country = params.pop("country", None)

    if country is None:
        country = sample_country()

    defaults = {
        "name": "Kyiv",
        "country": country
    }
    defaults.update(**params)

    return City.objects.create(**defaults)


def sample_airport(**params):
    city = params.pop("closest_big_city", None)

    if city is None:
        city = sample_city()

    defaults = {
        "name": "Boryspil International Airport",
        "iata_code": "KBP",
        "closest_big_city": city,
    }
    defaults.update(**params)

    return Airport.objects.create(**defaults)


def sample_route(**params):
    source = params.pop("source", None)

    if source is None:
        country = sample_country()
        source = sample_airport(
            closest_big_city=sample_city(
                country=country
            )
        )

    destination = params.pop("destination", None)

    if destination is None:
        destination = sample_airport(
            name="Frankfurt Airport",
            iata_code="FRA",
            closest_big_city=sample_city(
                name="Frankfurt",
                country=country
            ),
        )

    defaults = {
        "source": source,
        "destination": destination,
        "distance": 1200,
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
    airplane_type = params.pop("airplane_type", None)

    if airplane_type is None:
        airplane_type = sample_airplane_type()

    defaults = {
        "name": "Boing 747",
        "rows": 20,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(**params)

    return Airplane.objects.create(**defaults)

def sample_flight(**params):
    route = params.pop("route", None)
    if route is None:
        route = sample_route()

    airplane = params.pop("airplane", None)
    if airplane is None:
        airplane = sample_airplane()

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


def airport_detail_url(airport_id):
    return reverse("airport:airport-detail", args=[airport_id])


def flight_detail_url(flight_id):
    return reverse(
        "airport:flight-detail",
        args=[flight_id]
    )


class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@admid.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.airplane_type = sample_airplane_type()
        self.airplane = sample_airplane(
            airplane_type=self.airplane_type
        )
        self.flight = sample_flight(
            airplane=self.airplane
        )

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        url = image_upload_url(self.airplane.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 19))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            res = self.client.post(
                url,
                {"image": ntf},
                format="multipart"
            )

        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.airplane.id)
        res = self.client.post(
            url,
            {"image": "not image"},
            format="multipart",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list(self):
        url = AIRPLANE_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "Airbus A320",
                    "rows": 30,
                    "seats_in_row": 6,
                    "airplane_type_id": self.airplane_type.id,
                    "image": ntf
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(name="Airbus A320")
        self.assertTrue(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.airplane.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airplane_list(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPLANE_URL)
        print(res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"][0]["id"], self.airplane.id)
        self.assertTrue(res.data["results"][0]["image"])

    def test_image_url_is_shown_on_flight_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(
                url,
                {"image": ntf},
                format="multipart"
            )
        res = self.client.get(flight_detail_url(self.flight.id))

        self.assertIn("image", res.data["airplane"])


class AirportApiRetrieveTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassoword123"
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_airport(self):
        airport = sample_airport()

        url = airport_detail_url(airport.id)

        res = self.client.get(url)

        serializer = AirportDetailSerializer(airport)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AuthenticateFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)

    def test_flight_list(self):
        sample_flight()

        res = self.client.get(FLIGHT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

        flight = res.data["results"][0]
        self.assertIn("tickets_available", flight)
        self.assertEqual(flight["tickets_available"], 120)
        self.assertEqual(flight["airplane_capacity"], 120)

