# BookKeeper — Working Notes

## To resume
1. cd C:\Users\Surface\OneDrive\Documents\PersonalProjects\BookKeeper\Book-Keeper-
2. .\venv\Scripts\Activate.ps1
3. uvicorn app.main:app --reload
4. Open http://127.0.0.1:8000/docs

## Done
- FastAPI + Postgres + Alembic
- Auth (register, login, JWT)
- Items + tags
- User library (user_items)
- Content-based recommender with caching + feedback fields
- tests/test_recommender.py (12 pure-logic tests)

## In progress
- Fix test_score_item_normalizes_by_tag_count (assertion was wrong, not the code)
- Add tests/test_auth.py and tests/test_library.py (integration tests, see NOTES for content)

## Next
- Run full pytest suite
- Deploy to Render or Railway
- (Optional) React frontend
- (Optional) Fix Pydantic class Config deprecation warnings in schemas

## Key files
- app/services/recommender.py — the scoring logic
- app/core/deps.py — get_current_user dependency
- app/models/ — User, Item, Tag, UserItem, Recommendation
- alembic/versions/ — migrations
