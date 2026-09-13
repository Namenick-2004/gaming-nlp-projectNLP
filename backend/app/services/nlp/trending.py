"""
Rule-based trending analysis (deliberately NOT an LLM, per spec).
Compares a "current window" of mentions/comments/views against a
"previous window" of the same length to compute growth rate.
"""
from datetime import datetime, timedelta


def compute_growth(current: float, previous: float) -> float:
    if previous <= 0:
        return 100.0 if current > 0 else 0.0
    return round((current - previous) / previous * 100, 1)


def trending_topics_from_keyword_history(
    current_counts: dict[str, int],
    previous_counts: dict[str, int],
    top_n: int = 10,
) -> list[dict]:
    """current_counts / previous_counts: {keyword: mention_count} for
    two comparable time windows (e.g. last 7 days vs the 7 days before
    that). Ranked by absolute mentions, annotated with growth %."""
    rows = []
    for kw, mentions in current_counts.items():
        rows.append({
            "topic": kw,
            "mentions": mentions,
            "growth_percent": compute_growth(mentions, previous_counts.get(kw, 0)),
        })
    return sorted(rows, key=lambda r: r["mentions"], reverse=True)[:top_n]


def trending_games_from_video_stats(game_stats_current: dict[str, dict],
                                     game_stats_previous: dict[str, dict]) -> list[dict]:
    """game_stats_*: {game_name: {"mentions": int, "views": int, ...}}"""
    rows = []
    for game, stats in game_stats_current.items():
        prev = game_stats_previous.get(game, {"mentions": 0})
        rows.append({
            "name": game,
            "growth_percent": compute_growth(stats.get("mentions", 0), prev.get("mentions", 0)),
        })
    return sorted(rows, key=lambda r: r["growth_percent"], reverse=True)


def time_window_bounds(days: int = 7) -> tuple[datetime, datetime, datetime]:
    now = datetime.utcnow()
    current_start = now - timedelta(days=days)
    previous_start = now - timedelta(days=days * 2)
    return previous_start, current_start, now
