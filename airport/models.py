from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Countries"

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities"
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Cities"

    def __str__(self) -> str:
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255)
    iata_code = models.CharField(max_length=3, unique=True)
    closest_big_city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="airports"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.iata_code}) - {self.closest_big_city.name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )
    image = models.ImageField(upload_to="airplanes", null=True, blank=True)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} {self.airplane_type}"


class Route(models.Model):
    distance = models.IntegerField()
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_to"
    )

    def __str__(self) -> str:
        return f"From {self.source} to {self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.position})"


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    crew = models.ManyToManyField(
        Crew,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["departure_time"]

    def __str__(self) -> str:
        return f"Flight {self.route} on the {self.airplane} at {self.departure_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.created_at)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name:f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError
        )

    def save(
        self,
        *args,
        force_insert = False,
        force_update= False,
        using= None,
        update_fields = None
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    class Meta:
        unique_together = ["flight", "row", "seat"]
        ordering = ["flight"]

    def __str__(self) -> str:
        return f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"
