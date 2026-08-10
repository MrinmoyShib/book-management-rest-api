from datetime import date

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Book

User = get_user_model()


class BookAPITestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='tester', password='testpass123')
        self.book = Book.objects.create(
            title='Python Crash Course',
            author='Eric Matthes',
            category='Programming',
            price='34.99',
            published_date=date(2019, 5, 3),
        )

    def authenticate(self):
        """Obtain a JWT pair and attach the access token to self.client."""
        response = self.client.post('/api/token/', {'username': 'tester', 'password': 'testpass123'})
        access = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        return response.data

    # --- Read access is open to everyone --------------------------------

    def test_anyone_can_list_books(self):
        response = self.client.get('/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anyone_can_retrieve_a_book(self):
        response = self.client.get(f'/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Crash Course')

    # --- Writes require a valid JWT --------------------------------------

    def test_create_book_requires_authentication(self):
        response = self.client.post('/books/', {
            'title': 'New Book', 'author': 'Someone', 'category': 'Fiction',
            'price': '10.00', 'published_date': '2020-01-01',
        })
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_create_book_with_valid_token(self):
        self.authenticate()
        response = self.client.post('/books/', {
            'title': 'New Book', 'author': 'Someone', 'category': 'Fiction',
            'price': '10.00', 'published_date': '2020-01-01',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_update_book_with_valid_token(self):
        self.authenticate()
        response = self.client.patch(f'/books/{self.book.id}/', {'price': '19.99'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(str(self.book.price), '19.99')

    def test_delete_book_with_valid_token(self):
        self.authenticate()
        response = self.client.delete(f'/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)

    # --- JWT obtain / refresh flow ----------------------------------------

    def test_obtain_and_refresh_token(self):
        data = self.authenticate()
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        refresh_response = self.client.post('/api/token/refresh/', {'refresh': data['refresh']})
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_obtain_token_fails_with_bad_credentials(self):
        response = self.client.post('/api/token/', {'username': 'tester', 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Filtering / searching / ordering -----------------------------------

    def test_filter_by_category(self):
        Book.objects.create(title='Clean Code', author='Robert Martin', category='Engineering',
                             price='30', published_date='2008-01-01')
        response = self.client.get('/books/', {'category': 'Programming'})
        titles = [b['title'] for b in response.data['results']]
        self.assertIn('Python Crash Course', titles)
        self.assertNotIn('Clean Code', titles)

    def test_search_by_title(self):
        Book.objects.create(title='Clean Code', author='Robert Martin', category='Engineering',
                             price='30', published_date='2008-01-01')
        response = self.client.get('/books/', {'search': 'Python'})
        titles = [b['title'] for b in response.data['results']]
        self.assertIn('Python Crash Course', titles)
        self.assertNotIn('Clean Code', titles)

    def test_ordering_by_price_descending(self):
        Book.objects.create(title='Expensive Book', author='X', category='Programming',
                             price='999.99', published_date='2020-01-01')
        response = self.client.get('/books/', {'ordering': '-price'})
        prices = [float(b['price']) for b in response.data['results']]
        self.assertEqual(prices, sorted(prices, reverse=True))

    # --- Pagination -----------------------------------------------------------

    def test_pagination_returns_5_per_page_with_next_link(self):
        for i in range(9):
            Book.objects.create(title=f'Book {i}', author='Author', category='Programming',
                                 price='10', published_date='2020-01-01')
        response = self.client.get('/books/')
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    # --- Throttling ---------------------------------------------------------

    def test_throttling_blocks_after_limit(self):
        from rest_framework.throttling import AnonRateThrottle

        original_rates = AnonRateThrottle.THROTTLE_RATES
        AnonRateThrottle.THROTTLE_RATES = {'anon': '2/min', 'user': '2/min'}
        self.addCleanup(setattr, AnonRateThrottle, 'THROTTLE_RATES', original_rates)

        cache.clear()
        self.client.credentials()  # ensure anonymous (no auth header)
        for _ in range(2):
            response = self.client.get('/books/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/books/')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
