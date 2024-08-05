from datetime import datetime

from numpy.typing import NDArray

from .data_model import GroundStation, GsawDataModel, SpacecraftModel
from .utils import (
    calculate_elevation_angles,
    get_eci_positions,
    get_time_range,
    group_boolean_list,
    values_from_grouped_indices,
)


class MissionContactWindows:
    def __init__(self, model: GsawDataModel):
        self.ground_stations = model.ground_stations
        datetimes = get_time_range(model.analysis_start_time, model.analysis_end_time)
        self.spacecraft = [SpacecraftState(sc, datetimes) for sc in model.spacecraft]

    def get_contact_windows(self):
        """
        Returns all possible contact windows for all spacecraft comm link and ground station combinations.
        """
        contact_windows: dict[str, dict] = {}
        for sc in self.spacecraft:
            contact_windows[sc.model.id] = sc.contact_windows(self.ground_stations)
        return contact_windows


class SpacecraftState:
    def __init__(self, model: SpacecraftModel, datetimes: list[datetime]):
        self.model = model
        self.lba = model.link_budget_analysis
        self.datetimes = datetimes
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
            self._eci_positions = get_eci_positions(self.model.tle, self.datetimes)
        return self._eci_positions

    def contact_windows(self, ground_stations: list[GroundStation]) -> dict[list[dict[str, datetime]]]:
        """
        Returns the contact windows available for the spacecraft during the simulation for all valid
        combinations of ground station and comm link defined in the link budget analyses.
        """
        if not self._contact_windows:
            self._gs_elevations = self._gs_elevation_angles(ground_stations)
            self._get_all_contact_windows()
        return self._contact_windows

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

    def _get_all_contact_windows(self):
        """
        Iterate through all link budget analyses and find the times when the specified ground station
        has field of view on the spacecraft for all positions simulated.
        """
        for lba_id in self.lba.keys():
            lba = self.lba[lba_id]
            self._contact_windows[lba_id] = self._get_contact_time_windows(
                lba.ground_station_id, lba.min_elevation_angle
            )

    def _gs_elevation_angles(self, ground_stations: list[GroundStation]):
        """
        Iterate over supplied ground_stations and calculate the elevation angle the ground station requires
        to target the spacecraft at each of it's simulated positions.
        """
        return {gs.id: calculate_elevation_angles(gs, self.eci_positions, self.datetimes) for gs in ground_stations}
