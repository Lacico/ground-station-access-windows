from datetime import UTC, datetime, timedelta

import numpy as np
import pytest
from numpy.testing import assert_almost_equal

from gsaw_analyser import (
    GroundStation,
    calculate_elevation_angles,
    get_eci_positions,
    get_time_range,
    group_boolean_list,
    values_from_grouped_indices,
)


@pytest.fixture
def tle():
    return [
        "1 40044U 14033AL  24216.88520316  .00005471  00000+0  72454-3 0  9992",
        "2 40044  97.7034  16.9847 0054844 150.4922 209.9405 14.79230479544353",
    ]


@pytest.fixture
def datetimes():
    return [
        datetime(2024, 8, 4, 11, 26, tzinfo=UTC),
        datetime(2024, 8, 4, 11, 27, tzinfo=UTC),
        datetime(2024, 8, 4, 11, 28, tzinfo=UTC),
    ]


@pytest.fixture
def ground_station():
    return GroundStation(id="test", lat=90.0, lon=0.0, alt=0.0)


def test_calculate_elevation_angles(ground_station, datetimes):
    elevations = calculate_elevation_angles(
        ground_station, np.array([[0, 1e7, 0], [0, 0, 1e7], [1e7, 1e7, 1e7]]), datetimes
    )
    print(elevations)
    assert len(elevations) == len(datetimes)
    assert_almost_equal(elevations, np.array([90.0, 20.01793507, 20.01793507]))


def test_get_time_range(datetimes):
    start_time = datetime(2024, 8, 4, 11, 26, 0, 0, UTC)
    end_time = start_time + timedelta(minutes=3)
    times = get_time_range(start_time, end_time)
    assert len(times) == 3
    assert times == datetimes


def test_get_eci_positions(tle, datetimes):
    positions = get_eci_positions(tle, datetimes)
    assert_almost_equal(
        positions,
        np.array(
            [
                [-615687.41138241, -186132.40592336, 244184.90890844],
                [800843.69587572, 935404.51505035, 1066136.03886217],
                [-6962636.79989206, -6972747.00790911, -6954235.1281239],
            ]
        ),
    )


def test_group_boolean_list():
    bool_list = [True, True, False, False, True, True]
    groups = group_boolean_list(bool_list)
    assert groups == [(0, 1), (4, 5)]
    bool_list = [False, False, True, True, True, True, False]
    groups = group_boolean_list(bool_list)
    assert groups == [(2, 5)]


def test_values_from_grouped_indices():
    grouped_indices = [(0, 1), (4, 5)]
    vals = values_from_grouped_indices(grouped_indices, ["a", "b", "c", "d", "e", "f"])
    assert vals == [("a", "b"), ("e", "f")]
