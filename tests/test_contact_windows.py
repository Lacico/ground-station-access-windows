from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from numpy.testing import assert_almost_equal

from gsaw_analyser import (
    CommLink,
    GroundStation,
    GsawDataModel,
    LinkBudgetAnalysis,
    MissionContactWindows,
    SpacecraftModel,
    SpacecraftState,
)


@pytest.fixture
def groundstation_models() -> list[GroundStation]:
    return [
        GroundStation(id="North", lat=60.0, lon=0.0, alt=100.0),
        GroundStation(id="South", lat=-80.0, lon=0.0, alt=100.0),
    ]


@pytest.fixture
def spacecraft_models() -> list[SpacecraftModel]:
    return [
        SpacecraftModel(
            id="LEMUR-1",
            tle=[
                "1 40044U 14033AL  24216.88520316  .00005471  00000+0  72454-3 0  9992",
                "2 40044  97.7034  16.9847 0054844 150.4922 209.9405 14.79230479544353",
            ],
            comm_links=[CommLink(id="1")],
            link_budget_analyses={
                "A": LinkBudgetAnalysis(comm_link_id="1", ground_station_id="North", min_elevation_angle=15.0),
                "B": LinkBudgetAnalysis(comm_link_id="1", ground_station_id="South", min_elevation_angle=25.0),
            },
        ),
        SpacecraftModel(
            id="LEMUR-2-GREENBERG",
            tle=[
                "1 42837U 17042N   24216.98410763  .00016825  00000+0  11687-2 0  9997",
                "2 42837  97.3640  43.4679 0013992 224.3117 135.6991 15.05527928384836",
            ],
            comm_links=[CommLink(id="1")],
            link_budget_analyses={
                "A": LinkBudgetAnalysis(comm_link_id="1", ground_station_id="North", min_elevation_angle=15.0),
                "B": LinkBudgetAnalysis(comm_link_id="1", ground_station_id="South", min_elevation_angle=20.0),
            },
        ),
        SpacecraftModel(
            id="LEMUR-2-ANDIS",
            tle=[
                "1 42838U 17042P   24216.49462025  .00011388  00000+0  80201-3 0  9990",
                "2 42838  97.3621  42.7207 0015586 233.7631 126.2156 15.05085487384750",
            ],
            comm_links=[CommLink(id="1")],
            link_budget_analyses={
                "A": LinkBudgetAnalysis(comm_link_id="1", ground_station_id="North", min_elevation_angle=20.0),
                "B": LinkBudgetAnalysis(comm_link_id="1", ground_station_id="South", min_elevation_angle=25.0),
            },
        ),
    ]


@pytest.fixture
def gsaw_model(groundstation_models, spacecraft_models) -> GsawDataModel:
    start_time = datetime(2024, 8, 4, 11, 26, 0, 0, UTC)
    end_time = start_time + timedelta(minutes=2)

    return GsawDataModel(
        analysis_start_time=start_time,
        analysis_end_time=end_time,
        ground_stations=groundstation_models,
        spacecraft=spacecraft_models,
    )


@pytest.fixture
def mcw(gsaw_model) -> MissionContactWindows:
    return MissionContactWindows(gsaw_model)


@pytest.fixture
def spacecraft_state(mcw) -> SpacecraftState:
    return mcw.spacecraft[0]


@patch(
    "gsaw_analyser.SpacecraftState.contact_windows",
    lambda a, b: [(datetime(2024, 8, 4, 11, 26, 0, 0, UTC), datetime(2024, 8, 4, 11, 26, 0, 0, UTC))],
)
def test_get_contact_windows(mcw, spacecraft_models):
    cw = mcw.get_contact_windows()
    print(cw)
    assert list(cw.keys()) == [scm.id for scm in spacecraft_models]


def test_eci_positions(spacecraft_state):
    positions = spacecraft_state.eci_positions
    assert_almost_equal(
        positions,
        [
            [-615687.41138241, -186132.40592336],
            [800843.69587572, 935404.51505035],
            [-6962636.79989206, -6972747.00790911],
        ],
    )


def test_contact_windows(spacecraft_state, groundstation_models):
    v = spacecraft_state.contact_windows(groundstation_models)
    assert v == {"A": [], "B": [(datetime(2024, 8, 4, 11, 26, tzinfo=UTC), datetime(2024, 8, 4, 11, 27, tzinfo=UTC))]}

    # Second pass to hit the branch that skips recalculating the contact windows if they've been calculated before.
    v = spacecraft_state.contact_windows(groundstation_models)
    assert v == {"A": [], "B": [(datetime(2024, 8, 4, 11, 26, tzinfo=UTC), datetime(2024, 8, 4, 11, 27, tzinfo=UTC))]}
