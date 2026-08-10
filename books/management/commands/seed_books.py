from datetime import date

from django.core.management.base import BaseCommand

from books.models import Book

# 7 "Python"-titled books (to demo ?search=Python across 2 pages) + 5 others.
SAMPLE_BOOKS = [
    ("Python Crash Course", "Eric Matthes", "Programming", "34.99", date(2019, 5, 3)),
    ("Fluent Python", "Luciano Ramalho", "Programming", "49.99", date(2022, 4, 30)),
    ("Automate the Boring Stuff with Python", "Al Sweigart", "Programming", "29.99", date(2019, 11, 12)),
    ("Python for Data Analysis", "Wes McKinney", "Data Science", "54.99", date(2022, 8, 9)),
    ("Learning Python", "Mark Lutz", "Programming", "59.99", date(2013, 7, 4)),
    ("Python Tricks", "Dan Bader", "Programming", "24.99", date(2017, 10, 25)),
    ("Head First Python", "Paul Barry", "Programming", "32.99", date(2016, 11, 21)),
    ("Clean Code", "Robert C. Martin", "Software Engineering", "44.99", date(2008, 8, 1)),
    ("The Pragmatic Programmer", "Andrew Hunt", "Software Engineering", "42.50", date(2019, 9, 13)),
    ("Introduction to Algorithms", "Thomas H. Cormen", "Computer Science", "89.99", date(2009, 7, 31)),
    ("Deep Learning", "Ian Goodfellow", "Artificial Intelligence", "72.00", date(2016, 11, 18)),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "Software Engineering", "54.99", date(2017, 3, 16)),
]


class Command(BaseCommand):
    help = "Seed the database with sample books (for testing filters, search, ordering, pagination)."

    def handle(self, *args, **options):
        created = 0
        for title, author, category, price, published_date in SAMPLE_BOOKS:
            _, was_created = Book.objects.get_or_create(
                title=title,
                author=author,
                defaults={
                    "category": category,
                    "price": price,
                    "published_date": published_date,
                },
            )
            created += int(was_created)
        self.stdout.write(
            self.style.SUCCESS(f"Seeded {created} new book(s). Total books in DB: {Book.objects.count()}")
        )
