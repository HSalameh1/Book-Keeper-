from collections import Counter

from sqlalchemy.orm import Session, joinedload

from app.models.item import Item
from app.models.user_item import UserItem

# Items rated at or above this get counted as "liked"
LIKE_THRESHOLD = 4
# Items rated at or below this get counted as "disliked"
DISLIKE_THRESHOLD = 2
# How much a dislike subtracts from the score
DISLIKE_PENALTY = 0.5
# How many recommendations to keep
TOP_N = 10


def _taste_weights(entries: list[UserItem]) -> Counter:
    """
    Build a Counter of tag -> weight from the user's rated items.

    Liked items (rating >= LIKE_THRESHOLD) add their tags with weight
    proportional to how much they were liked. Disliked items subtract.
    """
    weights: Counter = Counter()

    for entry in entries:
        if entry.rating is None or entry.item is None:
            continue

        tag_names = [t.name for t in entry.item.tags]

        if entry.rating >= LIKE_THRESHOLD:
            # 5 -> +2, 4 -> +1
            weight = entry.rating - 3
            for tag in tag_names:
                weights[tag] += weight
        elif entry.rating <= DISLIKE_THRESHOLD:
            # 2 -> -1, 1 -> -2
            penalty = (DISLIKE_THRESHOLD + 1) - entry.rating
            for tag in tag_names:
                weights[tag] -= penalty * DISLIKE_PENALTY

    return weights


def _score_item(item: Item, taste: Counter) -> tuple[float, str]:
    """
    Score a single item against the taste vector.

    Score = sum(taste[tag] for tag in item.tags) / sqrt(len(item.tags))

    The sqrt denominator prevents items with lots of tags from
    automatically winning just because they have more tags.
    """
    if not item.tags:
        return 0.0, "no tags"

    tag_names = [t.name for t in item.tags]
    raw = sum(taste.get(name, 0.0) for name in tag_names)

    if raw <= 0:
        return 0.0, "no overlap with your taste"

    divisor = len(tag_names) ** 0.5
    score = raw / divisor

    # Build a human-readable reason from the top contributing tags
    contributions = sorted(
        ((name, taste.get(name, 0.0)) for name in tag_names),
        key=lambda kv: kv[1],
        reverse=True,
    )
    top = [name for name, w in contributions if w > 0][:3]
    reason = "matches tags: " + ", ".join(top) if top else "small match"

    return score, reason


def generate_recommendations(
    db: Session, user_id: int, top_n: int = TOP_N
) -> list[tuple[Item, float, str]]:
    """
    Return a list of (item, score, reason) tuples for items the user
    hasn't logged yet, sorted by score descending.
    """
    # 1. Pull the user's library with items + tags eagerly loaded
    entries = (
        db.query(UserItem)
        .options(joinedload(UserItem.item).joinedload(Item.tags))
        .filter(UserItem.user_id == user_id)
        .all()
    )

    taste = _taste_weights(entries)

    # 2. Get IDs the user already has
    logged_item_ids = {e.item_id for e in entries}

    # 3. Score every other item in the catalog
    candidates = (
        db.query(Item)
        .options(joinedload(Item.tags))
        .filter(~Item.id.in_(logged_item_ids) if logged_item_ids else True)
        .all()
    )

    scored = []
    for item in candidates:
        score, reason = _score_item(item, taste)
        if score > 0:
            scored.append((item, score, reason))

    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:top_n]