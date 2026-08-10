# Book Management REST API

A Django REST Framework API for managing a book catalog, with JWT authentication,
filtering, searching, ordering, pagination, and throttling.

Built for the "Book Management REST API with JWT Authentication" assignment.

## Tech stack

- Django 6.1
- Django REST Framework 3.18
- djangorestframework-simplejwt 5.5 (JWT auth)
- django-filter 26.1 (filtering)
- SQLite (default dev database)

## Features

- **Book model** — `id`, `title`, `author`, `category`, `price`, `published_date`
- **JWT authentication** — obtain/refresh tokens at `/api/token/` and `/api/token/refresh/`
- **Permissions** — anyone can read (`GET`); only authenticated users can create, update, or delete
- **Filtering** — `?category=` and `?author=`
- **Searching** — `?search=` across `title` and `author`
- **Ordering** — `?ordering=title` / `price` / `published_date` (prefix with `-` for descending)
- **Pagination** — 5 books per page, with `count` / `next` / `previous`
- **Throttling** — 20 requests/minute for anonymous users, 60/minute for authenticated users

## Project structure

```
book_api/
├── book_api/            # project settings, root URLs
│   ├── settings.py
│   └── urls.py
├── books/                # the app
│   ├── models.py         # Book model
│   ├── serializers.py    # BookSerializer
│   ├── views.py           # BookViewSet (permissions, filter/search/order)
│   ├── urls.py            # DRF router -> /books/
│   ├── admin.py
│   ├── tests.py           # automated test suite
│   └── management/commands/seed_books.py   # sample data loader
├── manage.py
├── requirements.txt
└── .gitignore
```

## Setup

```bash
# 1. Clone your repo and enter it
git clone <your-repo-url>
cd book_api

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. (Optional) load sample books — 12 books, 7 with "Python" in the title,
#    so you have enough data to see pagination/search/ordering in action
python manage.py seed_books

# 6. Create a user to authenticate with
python manage.py createsuperuser

# 7. Run the server
python manage.py runserver
```

The API is now at `http://127.0.0.1:8000/`.

## Authentication

Only `GET` requests are open to everyone. `POST` / `PUT` / `PATCH` / `DELETE`
require a JWT access token in the `Authorization` header.

**Obtain a token:**
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"<your-username>","password":"<your-password>"}'
```
Returns:
```json
{"refresh": "<refresh-token>", "access": "<access-token>"}
```

**Refresh an expired access token:**
```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh-token>"}'
```

**Use the access token on write requests:**
```bash
curl -X POST http://127.0.0.1:8000/books/ \
  -H "Authorization: Bearer <access-token>" \
  -d "title=Test Driven Development&author=Kent Beck&category=Programming&price=39.99&published_date=2002-11-18"
```
Access tokens expire after 30 minutes; refresh tokens after 1 day (see `SIMPLE_JWT` in `settings.py`).

## Endpoints

| Method        | Endpoint          | Auth required | Purpose          |
|---------------|-------------------|:-------------:|------------------|
| GET           | `/books/`         | No            | List all books   |
| GET           | `/books/<id>/`    | No            | View one book    |
| POST          | `/books/`         | Yes           | Create a book    |
| PUT / PATCH   | `/books/<id>/`    | Yes           | Update a book    |
| DELETE        | `/books/<id>/`    | Yes           | Delete a book    |
| POST          | `/api/token/`     | No            | Obtain JWT pair  |
| POST          | `/api/token/refresh/` | No        | Refresh access token |

## Filtering, searching, ordering, pagination

```
GET /books/?category=Programming        # filter by category
GET /books/?author=Eric Matthes         # filter by author
GET /books/?search=Python               # search title/author
GET /books/?ordering=price              # ascending
GET /books/?ordering=-price             # descending
GET /books/?page=2                      # page 2 (5 per page)
```

All of these combine, exactly as required by the assignment:

```
GET /books/?search=Python&ordering=-price&page=2
```
This searches for "Python", orders results by price highest → lowest, and returns
page 2. Verified response (with the seeded sample data, 7 books match "Python"):
```json
{
  "count": 7,
  "next": null,
  "previous": "http://127.0.0.1:8000/books/?ordering=-price&search=Python",
  "results": [
    {"id": 3, "title": "Automate the Boring Stuff with Python", "author": "Al Sweigart", "category": "Programming", "price": "29.99", "published_date": "2019-11-12"},
    {"id": 6, "title": "Python Tricks", "author": "Dan Bader", "category": "Programming", "price": "24.99", "published_date": "2017-10-25"}
  ]
}
```

## Throttling

Configured globally in `settings.py`:
- Anonymous users: **20 requests/minute**
- Authenticated users: **60 requests/minute**

Once exceeded, the API returns `HTTP 429 Too Many Requests`:
```json
{"detail": "Request was throttled. Expected available in 34 seconds."}
```
Adjust these in `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]` in `book_api/settings.py`.

## Running the tests

```bash
python manage.py test books -v 2
```
13 tests cover: read access for everyone, write access blocked without a token,
write access allowed with a valid token, the token obtain/refresh flow, filtering,
searching, ordering, pagination, and throttling. All pass.

## Pushing to GitHub

```bash
git init
git add .
git commit -m "Book Management REST API with JWT auth, filtering, search, ordering, pagination, throttling"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

`db.sqlite3` is intentionally excluded via `.gitignore` — anyone cloning the repo
builds their own local database with `migrate` (+ optionally `seed_books`).
