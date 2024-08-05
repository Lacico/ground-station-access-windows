from datetime import UTC, datetime, timedelta
from unittest import TestCase

import numpy as np

from gsaw_analyser import (
    GroundStation,
    calculate_elevation_angles,
    get_time_range,
    group_boolean_list,
    values_from_grouped_indices,
)


class TestUtils(TestCase):
    def test_get_time_range(self):
        start_time = datetime(2024, 8, 4, 11, 26, 0, 0, UTC)
        end_time = start_time + timedelta(minutes=5)
        times, datetimes = get_time_range(start_time, end_time)
        print(datetimes)
        self.assertEqual(len(times), 5)
        self.assertEqual(len(datetimes), 5)

    def test_calculate_elevation_angles(self):
        times = [
            datetime(2024, 8, 4, 11, 26, tzinfo=UTC),
            datetime(2024, 8, 4, 11, 27, tzinfo=UTC),
            datetime(2024, 8, 4, 11, 28, tzinfo=UTC),
        ]
        elevations = calculate_elevation_angles(
            GroundStation(id="test", lat=90.0, lon=0.0, alt=0.0), np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]), times
        )
        self.assertEqual(len(elevations), len(times))

    def test_group_boolean_list(self):
        bool_list = [True, True, False, False, True, True]
        groups = group_boolean_list(bool_list)
        self.assertEqual(groups, [(0, 1), (4, 5)])
        bool_list = [False, False, True, True, True, True, False]
        groups = group_boolean_list(bool_list)
        self.assertEqual(groups, [(2, 5)])

    def test_values_from_grouped_indices(self):
        grouped_indices = [(0, 1), (4, 5)]
        vals = values_from_grouped_indices(grouped_indices, ["a", "b", "c", "d", "e", "f"])
        self.assertEqual(vals, [("a", "b"), ("e", "f")])
