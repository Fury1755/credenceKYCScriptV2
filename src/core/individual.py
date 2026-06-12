"""This module holds the class 'Individual' and its attributes."""

import logging
from typing import List, Optional


class Individual:
    """The 'Individual' class"""

    def __init__(
        self,
        name: str,
        chinese_name: str,
        id_value: str,
        id_type: str,
        id_status: str,
        kyc_status: bool,
        google: bool,
        baidu: bool,
        role: Optional[str],
    ):
        self.name = name
        self.chinese_name = chinese_name
        self.id_value = id_value
        self.id_type = id_type
        self.id_status = id_status
        self.kyc_status = kyc_status
        self.google = google
        self.baidu = baidu
        self.role = role


def sort_individuals(kah_list: List[Individual]):
    """
    This function sorts individuals based on their
    role.

    Args:
        kah_list(List[Individual]): The list of individuals pdf_processing returns.

    Returns:
        A List of individuals sorted according to their role in the respective order:
        1. SHAREHOLDER/DIRECTOR
        2. SHAREHOLDER
        3. DIRECTOR
        4. RELATED
    """

    # precondition: Every individual has a proper role
    role_list = ["SHAREHOLDER/DIRECTOR", "SHAREHOLDER", "DIRECTOR", "RELATED"]
    for individual in kah_list:
        if individual.role not in role_list:
            logging.error(
                "Individual '%s' has invalid role '%s'",
                individual.name,
                individual.role,
            )
            raise ValueError(
                "Invalid/non-existing role for individual passed into sort_individuals"
            )

    shareholder_director = [
        ind for ind in kah_list if ind.role == "SHAREHOLDER/DIRECTOR"
    ]
    shareholder = [ind for ind in kah_list if ind.role == "SHAREHOLDER"]
    director = [ind for ind in kah_list if ind.role == "DIRECTOR"]
    related = [ind for ind in kah_list if ind.role == "RELATED"]

    return shareholder_director + shareholder + director + related
