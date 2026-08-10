from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    """
    CRUD API for books.

    - list / retrieve (GET) -> open to everyone
    - create / update / partial_update / destroy -> authenticated users only

    Query params:
      ?category=Programming&author=...   filter (exact match)
      ?search=Python                     search in title or author
      ?ordering=price / -price           order by title, price, or published_date
      ?page=2                            pagination (5 per page, set in settings.py)
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['category', 'author']
    search_fields = ['title', 'author']
    ordering_fields = ['title', 'price', 'published_date']
    ordering = ['id']
