# Book-Keeper

A personal media tracker for books, manga, and comics with a content-based
recommendation engine. Log what you've read with a rating and note, and the
app suggests what to read next based on your taste.

**Stack:** FastAPI · PostgreSQL · SQLAlchemy · Alembic · Pydantic · JWT

---

## What it does
- **Track your library** - log books, manga, and comics with a 1–5 rating,
  notes, and reading status
- **Personalized recommendations** - the recommender builds a weighted
  taste vector from your ratings and scores every unread item by tag overlap
- **Explainable picks** — every recommendation comes with a reason
  ("matches tags: cyberpunk, sci-fi")
- **Feedback logging** — clicks and ratings on recommendations are stored
  so the system can learn from what you actually engage with

---

## How the recommender works

For each user:

1. **Build a taste vector** from rated items
   - Items rated 4–5 add their tags with weight proportional to rating
     (5★ → +2, 4★ → +1)
   - Items rated 1–2 subtract from their tags (penalty scaled by how low)
   - Items rated 3 or unrated are ignored

2. **Score each unread item**
