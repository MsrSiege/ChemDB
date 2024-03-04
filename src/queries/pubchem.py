# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
from collections import namedtuple
from datetime import datetime
from typing import Any

from pubchempy import Compound, PubChemPyError, get_compounds

from src.fctlib.converter import TryConvert
from src.fctlib.decorators import Retry, RetryException, RetryFailedException
from src.fctlib.logging import LogLOGGER
from src.fctlib.regex import CheckCasNo
from src.settings import NOT_LISTED


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.1     Extracted from QueryPubChem() to use retry decorator
# ++---------------------------------------------------------------------------------------------------------------------++#
@Retry(RetryException)
def GetCompoundsList(query_term: str) -> list[Compound]:
    """Gets PubChem compound list for query term.\n
    - -> | <query_term> Query term to get PubChem compound(s)\n
    - <- | <return> List of PubChem compound(s)\n
    This requires a PubChem request which can fail server-sided, so it is wrapped in a retry decorator."""

    try:
        return get_compounds(identifier=query_term, namespace="name")
    except PubChemPyError as Error:
        raise RetryException(Error)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      0.1     Extracted from GetCompoundData() to use retry decorator
# ++---------------------------------------------------------------------------------------------------------------------++#
@Retry(RetryException)
def GetCasNumbersFromSynonyms(PcpCpd: Compound) -> str:
    """Get all CAS numbers from synonyms of PubChem compound.\n
    - -> | <PcpCpd> PubChem compound to get synonyms for\n
    - <- | <return> Concatenated CAS numbers\n
    This requires a PubChem request which can fail server-sided, so it is wrapped in a retry decorator."""

    try:
        return (
            ", ".join([synonym for synonym in PcpCpd.synonyms if CheckCasNo(synonym)])
            if hasattr(PcpCpd, "synonyms")
            else NOT_LISTED
        )
    except PubChemPyError as Error:
        raise RetryException(Error)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      1.1     Extracted GetCasNumbersFromSynonyms() to use retry decorator
# ++ 24-02-16    fJ      1.0     Unit test: passed
# ++ 24-02-16    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def GetCompoundData(query_term: str, query_status: str, PcpCpd: Compound | None, nt_init: bool = False) -> dict[str, Any]:
    """Returns a dictionary of selected compound data from an PubChem compound object.\n
    - -> | <query_status> Status of PubChem compound query\n
    - -> | <query_term> Term of the PubChem query\n
    - -> | <cpd> PubChem compound object\n
    - -> | <nt_init> Switch for initialisation of the named tuple\n
    - <- | <return> Compound data dictionary"""
    cpd_data: dict[str, Any] = {}

    # Get basic compound data that allways should be returned
    cpd_data["query_status_pc"] = query_status
    cpd_data["query_term_pc"] = query_term
    cpd_data["query_database_pc"] = "PubChem"
    cpd_data["query_time_pc"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Skip compound data collection if no compound was passed
    if PcpCpd is not None or nt_init:
        # Get remaining compound data
        cpd_data["query_finding_pc"] = getattr(PcpCpd, "iupac_name", NOT_LISTED)
        cpd_data["query_link_pc"] = (
            f"https://pubchem.ncbi.nlm.nih.gov/compound/{PcpCpd.cid}" if hasattr(PcpCpd, "cid") else NOT_LISTED
        )
        cpd_data["id_cid"] = getattr(PcpCpd, "cid", NOT_LISTED)

        # We'll get CAS numbers from synonyms in an Retry-decorated function because of the extra PubChem request
        try:
            cpd_data["cas_numbers"] = GetCasNumbersFromSynonyms(PcpCpd)
        except RetryFailedException as Error:
            LogLOGGER.error(f"Failed to get CAS numbers from synonyms for <{query_term}>: {Error}")
            cpd_data["cas_numbers"] = "Error while getting synonyms!"

        cpd_data["mass_exact"] = TryConvert(value=getattr(PcpCpd, "exact_mass", NOT_LISTED), datatype=float)
        cpd_data["mass_molecular"] = TryConvert(value=getattr(PcpCpd, "molecular_weight", NOT_LISTED), datatype=float)
        cpd_data["mass_monoisotopic"] = TryConvert(value=getattr(PcpCpd, "monoisotopic_mass", NOT_LISTED), datatype=float)
        cpd_data["mol_formula"] = getattr(PcpCpd, "molecular_formula", NOT_LISTED)
        cpd_data["mol_image_2d"] = (
            f"https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?t=l&cid={PcpCpd.cid}"
            if hasattr(PcpCpd, "cid")
            else NOT_LISTED
        )
        cpd_data["mol_inchi"] = getattr(PcpCpd, "inchi", NOT_LISTED)
        cpd_data["mol_inchikey"] = getattr(PcpCpd, "inchikey", NOT_LISTED)
        cpd_data["mol_smiles_canonical"] = getattr(PcpCpd, "canonical_smiles", NOT_LISTED)
        cpd_data["mol_smiles_isomeric"] = getattr(PcpCpd, "isomeric_smiles", NOT_LISTED)
        cpd_data["name_iupac_eng"] = getattr(PcpCpd, "iupac_name", NOT_LISTED)
        cpd_data["pc_complexity"] = getattr(PcpCpd, "complexity", NOT_LISTED)
        cpd_data["pc_count_hydrogen_bond_acceptors"] = getattr(PcpCpd, "h_bond_acceptor_count", NOT_LISTED)
        cpd_data["pc_count_hydrogen_bond_donors"] = getattr(PcpCpd, "h_bond_donor_count", NOT_LISTED)
        cpd_data["pc_count_heavy_atoms"] = getattr(PcpCpd, "heavy_atom_count", NOT_LISTED)
        cpd_data["pc_count_stereocenters"] = getattr(PcpCpd, "atom_stereo_count", NOT_LISTED)
        cpd_data["pc_formal_charge"] = getattr(PcpCpd, "charge", NOT_LISTED)
        cpd_data["pc_xlogp"] = getattr(PcpCpd, "xlogp", NOT_LISTED)

    return cpd_data


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      2.0     Dev tests: passed ... works as intended
# ++ 24-02-28    fJ      1.1     Extracted GetCompounds() to use retry decorator
# ++ 24-02-16    fJ      1.0     Unit test: passed
# ++ 24-02-15    fJ      0.3     Reworked and pythonised
# ++ 24-02-06    fJ      0.2     Added docstring
# ++ 24-02-04    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
def QueryPubChem(query_term: str) -> dict[str, Any]:
    """Queries PubChem for a query term and returns compound data.\n
    - -> | <query_term> Term to query the database\n
    - <- | <return> Compound data"""

    try:
        compounds: list[Compound] = GetCompoundsList(query_term=query_term)
    except RetryFailedException as Error:
        LogLOGGER.error(f"An PubChem error occurred while querying compound <{query_term}>: <{Error}>.")
        status = f"PubChem | Skipped <{query_term}>: Error! This is not your fault. Retrying later may help ..."
        compounds = None
        compound = None

    if compounds is not None:
        if len(compounds) == 0:
            status = f"PubChem | Skipped <{query_term}>: No query hit found!"
        elif len(compounds) > 1:
            status = f"PubChem | Skipped <{query_term}>: More than one query hit found!"
        else:
            status = "PubChem | Success!"

        compound = compounds[0] if len(compounds) == 1 else None

    return GetCompoundData(query_term=query_term, query_status=status, PcpCpd=compound)


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ DATE        DEV     VER     ACTIONS
# ++ 24-03-04    fJ      1.0     Dev tests: passed ... works as intended
# ++ 24-02-16    fJ      0.1     Created
# ++---------------------------------------------------------------------------------------------------------------------++#
DATASET = GetCompoundData(query_status="", query_term="", PcpCpd=None, nt_init=True).keys()
NtpPC_CONSTRUCTOR = namedtuple(typename="compound_data", field_names=DATASET, defaults=(None,) * len(DATASET))
"""Named tuple constructor for compound data. Gets initialized by GetCompoundData()."""
