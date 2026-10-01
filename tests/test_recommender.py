from types import SimpleNamespace

from app.services.recommender import _score_item, _taste_weights


def make_item(item_id: int, title: str, tags: list[str]):
    return SimpleNamespace(
        id=item_id,
        title=title,
        tags=[SimpleNamespace(name=t) for t in tags],
    )


def make_entry(item, rating):
    return SimpleNamespace(item=item, rating=rating, item_id=item.id)


# ---------- _taste_weights ----------

def test_taste_weights_empty_library():
    assert _taste_weights([]) == {}


def test_taste_weights_high_rating_adds():
    item = make_item(1, "Neuromancer", ["cyberpunk", "sci-fi"])
    weights = _taste_weights([make_entry(item, 5)])
    assert weights["cyberpunk"] == 2
    assert weights["sci-fi"] == 2


def test_taste_weights_four_star_adds_half():
    item = make_item(1, "Something", ["fantasy"])
    weights = _taste_weights([make_entry(item, 4)])
    assert weights["fantasy"] == 1


def test_taste_weights_low_rating_penalizes():
    item = make_item(1, "Berserk", ["dark", "epic"])
    weights = _taste_weights([make_entry(item, 2)])
    assert weights["dark"] < 0
    assert weights["epic"] < 0


def test_taste_weights_mixed_signals():
    liked = make_item(1, "Hobbit", ["fantasy", "adventure"])
    disliked = make_item(2, "Berserk", ["fantasy", "dark"])

    weights = _taste_weights([make_entry(liked, 5), make_entry(disliked, 2)])

    assert weights["fantasy"] == 1.5
    assert weights["adventure"] == 2
    assert weights["dark"] == -0.5


def test_taste_weights_ignores_null_rating():
    item = make_item(1, "Unrated", ["whatever"])
    weights = _taste_weights([make_entry(item, None)])
    assert weights == {}


# ---------- _score_item ----------

def test_score_item_no_tags_returns_zero():
    item = make_item(1, "Unknown", [])
    score, reason = _score_item(item, {"sci-fi": 2})
    assert score == 0.0
    assert reason == "no tags"


def test_score_item_no_overlap_returns_zero():
    item = make_item(1, "Unrelated", ["romance"])
    score, _ = _score_item(item, {"sci-fi": 2})
    assert score == 0.0


def test_score_item_positive_overlap():
    item = make_item(1, "Snow Crash", ["cyberpunk", "sci-fi", "fast-paced"])
    taste = {"cyberpunk": 2, "sci-fi": 2}

    score, reason = _score_item(item, taste)
    expected = 4 / (3 ** 0.5)
    assert abs(score - expected) < 1e-9
    assert "cyberpunk" in reason
    assert "sci-fi" in reason


def test_score_item_negative_overlap_filtered():
    item = make_item(1, "Watchmen", ["dark", "superhero"])
    taste = {"dark": -1.0}

    score, _ = _score_item(item, taste)
    assert score == 0.0


def test_score_item_normalizes_by_tag_count():
    small = make_item(1, "Small", ["sci-fi"])
    big = make_item(2, "Big", ["sci-fi", "cyberpunk", "space", "future"])

    taste = {"sci-fi": 2, "cyberpunk": 2}
    small_score, _ = _score_item(small, taste)
    big_score, _ = _score_item(big, taste)

    assert big_score > small_score
    assert big_score < 3


def test_score_item_reason_lists_top_tags():
    item = make_item(1, "Test", ["a", "b", "c", "d"])
    taste = {"a": 3, "b": 2, "c": 1}
    _, reason = _score_item(item, taste)
    assert "a" in reason
    assert "b" in reason