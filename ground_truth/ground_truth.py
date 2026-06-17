from astropy.table import Table
from tqdm import tqdm

from tools import check_data, get_cluster_coordinates, get_cluster_in_range


def find_all_matching_clusters(tolerance: int | float):
    """
    tolerance in arcsec
    """
    eRASS1_catalog_path, PR4_catalog_path = check_data()

    eRASS1_table = Table.read(eRASS1_catalog_path)

    matches = []

    # TODO: needs a separate tool for that, way to slown
    for cluster_name in tqdm(eRASS1_table["NAME"], desc="Iterating eRASS1 clusters...", total=len(eRASS1_table)):
        ra, dec = get_cluster_coordinates(catalog_path=eRASS1_catalog_path, cluster_name=cluster_name)
        matched_name = get_cluster_in_range(catalog_path=PR4_catalog_path, ra=ra, dec=dec, tolerance=tolerance)
        if matched_name is not None:
            matches.append((cluster_name, matched_name))

    print(len(matches))

    return matches


if __name__ == "__main__":
    matches = find_all_matching_clusters(tolerance=2)
