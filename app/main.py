from fastapi import FastAPI

from app.routers import auth, items, library, recommendations

app = FastAPI(title="Media Recommender", version="0.1.0")

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(library.router)
app.include_router(recommendations.router)


@app.get("/health")
def health():
    return {"status": "ok"}