from django.db import models


class Book(models.Model):
    """A single book available in the catalog."""

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    published_date = models.DateField()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.title} by {self.author}"
