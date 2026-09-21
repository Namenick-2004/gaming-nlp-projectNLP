from unittest.mock import MagicMock, patch

import pytest

from app.services.youtube_service import YouTubeService


@pytest.mark.parametrize("chart_count, extra_count, expected_count", [(3, 13, 10), (0, 10, 10), (3, 4, 4), (10, 0, 10)])
def test_trending_fills_short_chart_without_duplicates(chart_count, extra_count, expected_count):
    service = YouTubeService.__new__(YouTubeService)
    service.client = MagicMock()
    chart = [{"video_id": str(i), "snippet": {"categoryId": "17"}} for i in range(chart_count)]
    service.client.videos.return_value.list.return_value.execute.return_value = {"items": chart}
    service.search_sports = MagicMock(return_value=[{"video_id": str(i)} for i in range(extra_count)])

    with patch("app.services.youtube_service.cache_get", return_value=None), patch(
        "app.services.youtube_service.cache_set", side_effect=lambda key, value: value
    ), patch("app.services.youtube_service._map_video", side_effect=lambda item: {"video_id": item["video_id"]}):
        result = service.trending(10)

    assert [video["video_id"] for video in result] == [str(i) for i in range(expected_count)]
    if chart_count == 10:
        service.search_sports.assert_not_called()
    else:
        service.search_sports.assert_called_once()
