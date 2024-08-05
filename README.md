# Ground Station Access Windows

Analyses potential access windows where an Earth Satellite is in the radio field of view of a ground station. The code will perform analysis for collections of ground stations and spacecraft. Each spacecraft can have multiple comm links.

In order to perform the analysis we need to propagate the spacecraft from an initial starting location at a known starting time to an end time. This implementation is using SGP4 for the spacecraft propagation and requires that the spacecraft location is defined by a TLE to run the SGP4 analysis.

The SGP4 implementation being used is that which is included in the [skyfield](https://github.com/skyfielders/python-skyfield) library. WGS84 spheroid will be used throughout and [pymap3d](https://pypi.org/project/pymap3d/) will be used for coordinate transformations.

## How It Works

* Propagate each spacecraft between the analysis start and end times, recording the ECI coordinates at one minute resolution.
* Calculate AER coordinates for each ground station to target the spacecraft ECI coordinates.
* If elevation is larger than the minimum elevation from the link budget analysis, a contact can be made.

## Development

Formatting and linting are performed using [ruff]

## Data Model

This tool is designed as a module for the spacecraft analysis software suite. It is decoupled through use of the mission data model that is passed between, and popultated by, different modules. The parameters in the following snippet needs to be populated for this module to function.

```json
{
    analysis-start-time: String
    analysis-end-time: String
    spacecraft: [
        {
            id: string,
            comm-links: [
                {
                    id: String,
                    ...
                }
            ]
            link-budget-analysis: [
                {
                    comm-link-id: String,
                    ground-station-id: String,
                    min-elevation-angle: Number,
                }
            ],
            tle: String[],
            ...
        }
    ],
    ground-stations: [
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