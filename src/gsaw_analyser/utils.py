from datetime import datetime, timedelta
from itertools import groupby
from typing import TypeVar

import numpy as np
from numpy.typing import NDArray
from pymap3d import eci2aer
from skyfield.api import EarthSatellite, load

from .data_model import GroundStation


T = TypeVar("T")


def calculate_elevation_angles(gs: GroundStation, eci_positions: NDArray, times: list[datetime]):
    return eci2aer(
        eci_positions[0, :],
        eci_positions[1, :],
        eci_positions[2, :],
        gs.lat,
        gs.lon,
        gs.alt,
        times,
    )[1]


def get_time_range(start_time: datetime, end_time: datetime) -> list[datetime]:
    """
    Returns python datetimes for each interval between the start and end times supplied.
    """
    num_minutes = int((end_time - start_time).total_seconds() // 60)
    dt_range = [start_time + timedelta(minutes=i) for i in range(0, num_minutes)]
    return dt_range


def get_eci_positions(tle: list[str], datetimes: list[datetime]) -> NDArray:
    """
    For a given two line element and list of python datetimes, compute the spacecraft
    ECI position in metres. Propagation is perfomed using the Skyfield libraries implementation
    of SGP4.
    """
    ts = load.timescale()
    times = ts.from_datetimes(datetimes)
    return EarthSatellite(tle[0], tle[1]).at(times).position.m


def group_boolean_list(bools: list[bool]) -> list[tuple[int, int]]:
    """
    Converts the list of boolean values with into a list of tuples of integer values
    indicating the start and end indices of sequences of True values.
    """
    groups = []
    for mask, grp in groupby(zip(np.arange(len(bools)), bools), key=lambda x: x[1]):
        if mask:
            idx = [idx for idx, _ in grp]
            groups.append((idx[0], idx[-1]))
    return groups


def values_from_grouped_indices(grouped_indices: list[tuple[int, int]], values: list[T]) -> list[tuple[T, T]]:
    """
    Returns the values from the values list that are indexed by the values in the grouped_indices list.

    Example
    -------

    grouped_indices = [(0,0),(2,4)] \n
    values = ['foo', 'bar', 'baz', 'qux', 'quux', 'quuz'] \n
    result = [('foo','foo'), ('baz','quux')]
    """
    return [(values[i], values[j]) for i, j in grouped_indices]
