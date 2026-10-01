# BookKeeper — Working Notes

## To resume
1. cd C:\Users\Surface\OneDrive\Documents\PersonalProjects\BookKeeper\Book-Keeper-
2. .\venv\Scripts\Activate.ps1
3. uvicorn app.main:app --reload
4. Open http://127.0.0.1:8000/docs

## Done
- Auth (register, login, JWT)
- Items + tags
- User library (user_items)

## Next
- Recommender (app/services/recommender.py)
  - Content-based: score items by tag overlap with user's 4+ rated items
  - Endpoint: GET /me/recommendations
  - Cache table: recommendations
- React frontend (optional)
- Deploy

## Key files
- app/core/deps.py — get_current_user dependency
- app/models/ — User, Item, Tag, UserItem
- app/routers/ — auth, items, library
- alembic/versions/ — migrations
