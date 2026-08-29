from datetime import UTC, datetime

from fpl_bot.evaluation import (
    performance_summary,
    record_forecast,
    settle_finished_forecasts,
)
from fpl_bot.models import Event, PlayerProjection, Recommendation


class FakeLiveClient:
    def event_live(self, event_id):
        assert event_id == 2
        return {
            "elements": [
                {"id": 1, "stats": {"total_points": 8, "minutes": 90}},
                {"id": 2, "stats": {"total_points": 2, "minutes": 30}},
            ]
        }


def test_recorded_forecast_is_settled_and_summarized():
    history = {}
    recommendation = Recommendation(
        event=Event(2, "Gameweek 2", datetime(2026, 8, 28, tzinfo=UTC)),
        transfers=[],
        points_hit=0,
        captain="Captain",
        vice_captain="Vice",
        starting_xi=["Captain", "Vice"],
        bench=[],
        reserve_goalkeeper="Keeper",
        chip="None — save the chip",
        confidence="Medium",
        explanation="Test",
        player_projections=(
            PlayerProjection(1, "Captain", 6.0, 85.0, "captain"),
            PlayerProjection(2, "Vice", 4.0, 70.0, "vice-captain"),
        ),
    )

    record_forecast(history, recommendation, datetime(2026, 8, 28, tzinfo=UTC))
    settled = settle_finished_forecasts(
        history,
        {"events": [{"id": 2, "finished": True}]},
        FakeLiveClient(),
    )
    summary = performance_summary(history)

    assert settled == [2]
    assert history["settled"]["2"]["expected_team_points"] == 16.0
    assert history["settled"]["2"]["actual_team_points"] == 18.0
    assert history["settled"]["2"]["expected_starter_hit_rate"] == 0.5
    assert summary == {"gameweeks": 1, "points_mae": 2.0, "minutes_mae": 22.5}
