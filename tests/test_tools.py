from tools import (
    check_data,
    get_catalog_column_names,
    get_cluster_coordinates,
    get_cluster_in_range,
    get_mass_unit,
)


def test_check_data() -> None:
    eRASS1_out_path = "./data/erass1cl_primary_v3.2.fits"
    PR4_out_path = "./data/HFI_PCCS_SZ-union_R2.08.fits"

    assert (eRASS1_out_path, PR4_out_path) == check_data()


def test_get_catalog_column_names() -> None:
    eRASS1_out_path, PR4_out_path = check_data()

    eRASS1_column_names = [
        "DETUID",
        "NAME",
        "RA",
        "DEC",
        "RA_XFIT",
        "DEC_XFIT",
        "EXT_LIKE",
        "DET_LIKE_0",
        "EXP",
        "BEST_Z",
        "BEST_ZERR",
        "BEST_Z_TYPE",
        "PCONT",
        "CR300kpc",
        "CR300kpc_L",
        "CR300kpc_H",
        "CR500",
        "CR500_L",
        "CR500_H",
        "CTS300kpc",
        "CTS300kpc_L",
        "CTS300kpc_H",
        "CTS500",
        "CTS500_L",
        "CTS500_H",
        "F300kpc",
        "F300kpc_L",
        "F300kpc_H",
        "F500",
        "F500_L",
        "F500_H",
        "L300kpc",
        "L300kpc_L",
        "L300kpc_H",
        "L500",
        "L500_L",
        "L500_H",
        "CR300kpc0520",
        "CR300kpc_L0520",
        "CR300kpc_H0520",
        "CR500_0520",
        "CR500_L_0520",
        "CR500_H_0520",
        "CTS300kpc0520",
        "CTS300kpc_L0520",
        "CTS300kpc_H0520",
        "CTS500_0520",
        "CTS500_L_0520",
        "CTS500_H_0520",
        "F300kpc0520",
        "F300kpc_L0520",
        "F300kpc_H0520",
        "F500_0520",
        "F500_L_0520",
        "F500_H_0520",
        "L300kpc0520",
        "L300kpc_L0520",
        "L300kpc_H0520",
        "L500_0520",
        "L500_L_0520",
        "L500_H_0520",
        "Lbol500",
        "Lbol500_L",
        "Lbol500_H",
        "KT",
        "KT_L",
        "KT_H",
        "MGAS500",
        "MGAS500_L",
        "MGAS500_H",
        "YX500",
        "YX500_L",
        "YX500_H",
        "M500",
        "M500_L",
        "M500_H",
        "FGAS500",
        "FGAS500_L",
        "FGAS500_H",
        "R500",
        "R500_L",
        "R500_H",
        "MATCH_NAME",
        "M500_PDF",
        "M500_PDF_array",
    ]

    PR4_column_names = [
        "INDEX",
        "NAME",
        "GLON",
        "GLAT",
        "RA",
        "DEC",
        "POS_ERR",
        "SNR",
        "PIPELINE",
        "PIPE_DET",
        "PCCS2",
        "PSZ",
        "IR_FLAG",
        "Q_NEURAL",
        "Y5R500",
        "Y5R500_ERR",
        "VALIDATION",
        "REDSHIFT_ID",
        "REDSHIFT",
        "MSZ",
        "MSZ_ERR_UP",
        "MSZ_ERR_LOW",
        "MCXC",
        "REDMAPPER",
        "ACT",
        "SPT",
        "WISE_FLAG",
        "AMI_EVIDENCE",
        "COSMO",
        "COMMENT",
    ]

    assert eRASS1_column_names == get_catalog_column_names(eRASS1_out_path)
    assert PR4_column_names == get_catalog_column_names(PR4_out_path)


def test_get_mass_unit() -> None:
    eRASS1_mass_unit = "10**13 solMass"
    PR4_mass_unit = "10^14 Msol"
    eRASS1_out_path, PR4_out_path = check_data()

    assert get_mass_unit(catalog_path=eRASS1_out_path, column_name="M500") == eRASS1_mass_unit
    assert get_mass_unit(catalog_path=PR4_out_path, column_name="MSZ") == PR4_mass_unit


def test_get_cluster_coordinates() -> None:
    eRASS1_out_path, PR4_out_path = check_data()

    assert get_cluster_coordinates(catalog_path=eRASS1_out_path, cluster_name="1eRASS J000005.2-383729") == (
        0.021729666982255817,
        -38.6249030550687,
    )
    assert get_cluster_coordinates(catalog_path=PR4_out_path, cluster_name="PSZ2 G000.04+45.13") == (
        229.19051197148607,
        -1.0172220494487687,
    )


def test_get_cluster_in_range() -> None:
    eRASS1_out_path, PR4_out_path = check_data()
    ra = 0.021729666982255817
    dec = -38.6249030550687
    print(get_cluster_in_range(catalog_path=eRASS1_out_path, ra=ra, dec=dec))
