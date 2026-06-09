"""This module holds the class 'Individual' and its attributes."""

from typing import Optional

months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
"""This is the array of months"""


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
