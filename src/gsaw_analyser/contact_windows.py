from datetime import datetime

from numpy.typing import NDArray
from skyfield.api import EarthSatellite, Time

from .data_model import GroundStation, GsawDataModel, SpacecraftModel
from .utils import calculate_elevation_angles, get_time_range, group_boolean_list, values_from_grouped_indices


class MissionContactWindows:
    def __init__(self, model: GsawDataModel):
        self.ground_stations = model.ground_stations
        times, datetimes = get_time_range(model.analysis_start_time, model.analysis_end_time)
        self.spacecraft = [SpacecraftState(sc, times, datetimes) for sc in model.spacecraft]

    def get_contact_windows(self):
        contact_windows: dict[str, dict] = {}
        for sc in self.spacecraft:
            contact_windows[sc.model.id] = sc.contact_windows(self.ground_stations)
        return contact_windows


class SpacecraftState:
    def __init__(self, model: SpacecraftModel, times: Time, datetimes: list[datetime]):
        self.model = model
        self.times = times
        self.datetimes = datetimes
        self.skyfield_earth_satellite = EarthSatellite(model.tle[0], model.tle[1])
        self._eci_positions: NDArray | None = None
        self._gs_elevations: dict[str, NDArray] = {}
        self._in_fov: dict[str, list[bool]] = {}
        self._contact_windows: dict[str, list[tuple[datetime, datetime]]] = {}

    @property
    def eci_positions(self) -> NDArray:
        """
        Returns the positions of the spacecraft for each interval of the simulation in Earth
        Centred Inertial coordinates with units of metres (m).
        """
        if self._eci_positions is None:
            self._eci_positions: NDArray = self.skyfield_earth_satellite.at(self.times).position.m
        return self._eci_positions

    def contact_windows(self, ground_stations: list[GroundStation]) -> dict[list[dict[str, datetime]]]:
        """
        Returns the contact windows available for the spacecraft during the simulation for all valid
        combinations of ground station and comm link defined in the link budget analyses.
        """
        if not self._contact_windows:
            self._populate_elevation_angles(ground_stations)
            self._determine_when_in_view()
        return self._contact_windows

    def _populate_elevation_angles(self, ground_stations: list[GroundStation]):
        """
        Iterate over supplied ground_stations and calculate the elevation angle the ground station requires
        to target the spacecraft at each of it's simulated positions.
        """
        for gs in ground_stations:
            elevation_angles = calculate_elevation_angles(gs, self.eci_positions, self.datetimes)
            self._gs_elevations[gs.id] = elevation_angles

    def _get_contact_time_windows(
        self, ground_station_id: str, min_elevation_angle: float
    ) -> list[tuple[datetime, datetime]]:
        """
        For the given ground_station_id and min_elevation_angle retrieve the list of start and end datetimes
        of contact windows for the spacecraft during the simulation.
        """
        in_fov = self._gs_elevations[ground_station_id] > min_elevation_angle
        contact_windows = group_boolean_list(in_fov)
        return values_from_grouped_indices(contact_windows, self.datetimes)

    def _determine_when_in_view(self):
        """
        Iterate through all link budget analyses and determine if the specified ground station
        has field of view on the spacecraft for all positions simulated.
        """
        for lba_id in self.model.link_budget_analysis.keys():
            lba = self.model.link_budget_analysis[lba_id]
            self._contact_windows[lba_id] = self._get_contact_time_windows(
                lba.ground_station_id, lba.min_elevation_angle
            )
