"""
Custom tools for the time-series forecasting agent.

Tool pipeline:
  1. check_data                   ->  check if the cluster catalogs are present and download the eRASS1 if needed
  2. preprocess_time_series_data  ->  clean outliers, engineer features, scale, save
  3. train_xgboost_forecaster     ->  train XGBoost with cross-validation, save model
  4. forecast_next_7_days         ->  load model, predict next week, save forecast
  5. create_forecast_plot         ->  plot historical + forecast data
  6. generate_final_report        ->  collect all artifacts into a dated report folder
"""

import os

from smolagents import tool


@tool
def check_data() -> tuple[str, str] | None:
    """
    Checks whether the data exists and downloads the eROSITA eRASS1 catalog if not. Catalogs are expected to be in the
    ./data folder. The expected full paths are
    - ./data/erass1cl_primary_v3.2.fits.tgz
    - ./data/HFI_PCCS_SZ-union_R2.08.fits
    for the eRASS1 data and the Planck data (PR3) respectively.

    Returns:
        The eRASS1 gc catalog path and the PR4 gc catalog path as a tuple if the files exist, else None.
    """
    import os
    import tarfile

    import requests

    eRASS1_url = (
        "https://erosita.mpe.mpg.de/dr1/AllSkySurveyData_dr1/Catalogues_dr1/BulbulE_DR1/erass1cl_primary_v3.2.fits.tgz"
    )
    eRASS1_out_path = "./data/erass1cl_primary_v3.2.fits"
    PR4_out_path = "./data/HFI_PCCS_SZ-union_R2.08.fits"

    if not os.path.exists(f"{eRASS1_out_path}.tgz"):
        with requests.get(eRASS1_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(f"{eRASS1_out_path}.tgz", "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)

    with tarfile.open(f"{eRASS1_out_path}.tgz", mode="r:gz") as tf:
        tf.extractall(path=os.path.dirname(eRASS1_out_path))

    if os.path.exists(eRASS1_out_path) and os.path.exists(PR4_out_path):
        return eRASS1_out_path, PR4_out_path
    else:
        return None


@tool
def get_catalog_column_names(catalog_path: str) -> list[str]:
    """
    Returns a list of column names from the catalog. This can be used to identify useful columns such as coordinates,
    redshift or mass to extract values from the catalog or infer units.

    Args:
        catalog_path:   Path to the catalog file.

    Returns:
        List of column names from the catalog file.
    """

    from astropy.io import fits

    with fits.open(catalog_path) as hdul:
        return hdul[1].columns.names


@tool
def get_mass_unit(catalog_path: str, column_name: str) -> str:
    """
    Extracts the unit of mass from the catalog.

    Args:
        catalog_path: Path to the catalog file.
        column_name: Name of the mass column, e.g. M500.

    Returns:
        The unit of mass as written to the fits file as an interpretable string, e.g. '10^10 M_sun'.
    """
    from astropy.io import fits

    with fits.open(catalog_path) as hdul:
        return hdul[1].columns[column_name].unit


@tool
def get_cluster_coordinates(catalog_path: str, cluster_name: str) -> tuple[float, float] | None:
    """
    Extracts the cluster coordinates from the catalog. Returns None if the cluster name is not in the catalog.
    Coordinates are returned as a tuple of RA and DEC.

    Args:
        catalog_path: Path to the catalog file.
        cluster_name: Cluster name according to the respective column of the catalog.

    Returns:
        A tuple of RA and DEC if the cluster name is in the catalog, else None.
    """
    from astropy.table import Table

    table = Table.read(catalog_path)
    if cluster_name in table["NAME"]:
        return table[table["NAME"] == cluster_name]["RA"].value[0], table[table["NAME"] == cluster_name]["DEC"].value[0]
    else:
        return None


@tool
def get_cluster_in_range(
    catalog_path: str, ra: float, dec: float, tolerance: float | int = 2, frame: str = "icrs"
) -> tuple[float, float] | None:
    """
    For a given set of coordinates, returns a cluster name from the catalog for which the path is given. If multiple
    clusters are within the angular tolerance, the closest one is returned. If no cluster is within the angular
    tolerance, the function returns None.

    Args:
        catalog_path: Path to the catalog file.
        ra: Right ascension of the cluster in degrees.
        dec: Declination of the cluster in degrees.
        tolerance: Maximal deviation of the given coordinates from the found cluster coordinates in arcsec.
        frame: Coordinate frame for the astropy SkyCoord objects, defaults to 'icrs'.

    Returns:
        The name of the cluster if a cluster is within the tolerance boundary, else None.
    """
    import astropy.units as u
    from astropy.coordinates import SkyCoord
    from astropy.table import Table
    from tqdm import tqdm

    reference_cluster_center = SkyCoord(ra, dec, unit="deg", frame=frame)
    table = Table.read(catalog_path)
    closest_cluster_name = None
    closest_separation = 2 * tolerance
    for _name, _ra, _dec in tqdm(
        zip(table["NAME"], table["RA"], table["DEC"]),
        desc="Matching clusters...",
        total=len(table),
    ):
        currenct_cluster_center = SkyCoord(_ra, _dec, unit="deg", frame=frame)
        separation = reference_cluster_center.separation(currenct_cluster_center).to(u.arcsec)
        if separation < tolerance * u.arcsec and separation < closest_separation * u.arcsec:
            closest_cluster_name = _name
            closest_separation = separation

    return closest_cluster_name
