# Ground Station Access Windows (Contact Windows)

Analyses potential access windows where an Earth Satellite is in the radio field of view of a ground station. The code will perform analysis for collections of ground stations and spacecraft. Each spacecraft can have multiple comm links.

In order to perform the analysis we need to propagate the spacecraft from an initial starting location at a known starting time to an end time. This implementation is using SGP4 for the spacecraft propagation and requires that the spacecraft location is defined by a TLE to run the SGP4 analysis.

The SGP4 implementation being used is that which is included in the [skyfield](https://github.com/skyfielders/python-skyfield) library. WGS84 spheroid will be used throughout and [pymap3d](https://pypi.org/project/pymap3d/) will be used for coordinate transformations.

## How It Works

* Propagate each spacecraft between the analysis start and end times, recording the ECI coordinates at one minute resolution.
* Calculate AER coordinates for each ground station to target the spacecraft ECI coordinates.
* If elevation is larger than the minimum elevation from the link budget analysis, a contact can be made.

## Development

The project uses [poetry](https://github.com/python-poetry/poetry) for it's python environment and [poe the poet](https://github.com/nat-n/poethepoet) for a task runner. [Pre-commit](https://github.com/pre-commit/pre-commit) should be installed prior to commiting changes. [ruff](https://github.com/astral-sh/ruff) is used for linting and formatting, [pytest](https://github.com/pytest-dev/pytest) along with [pytest-benchmark](https://github.com/ionelmc/pytest-benchmark) and [pytest-mock](https://github.com/pytest-dev/pytest-mock/) are used for testing, reports are generated using coverage. [mypy](https://github.com/python/mypy) is used for static typing. A number of poe tasks have been configured to simplify running these commands, `poe all` will run all commands required to pass prior to merge.

The pre-commit hooks will run the ruff linting, formatting and mypy typing checks prior to commiting. Tests must be passing and test coverage must be 100% before code is merged to main.

To make changes a branch should be opened off of main and a pull-request opened back to main once complete.

## Data Model

This tool is designed as a module for the spacecraft analysis software suite. It is decoupled through use of the mission data model that is passed between, and popultated by, different modules. The parameters in the following snippet needs to be populated for this module to function.

```json
{
    analysis_start_time: String
    analysis_end_time: String
    spacecraft: [
        {
            id: string,
            comm_links: [
                {
                    id: String,
                    ...
                }
            ]
            link_budget_analyses: [
                {
                    id: String,
                    link_budget_analysis: {
                        comm_link_id: String,
                        ground_station_id: String,
                        min_elevation_angle: Number,
                    }
                }
            ],
            tle: String[],
            ...
        }
    ],
    ground_stations: [
        {
            id: String,
            lat: Number,
            lon: Number,
            alt: Number,
            ...
        }
    ],
    ...
}
```

Link budget analysis needs to be performed before this module can be used.
