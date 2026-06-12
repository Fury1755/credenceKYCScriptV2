"""
This module tests functions related to individuals.
For now, only sort_individuals exists.
"""

from typing import List

import pytest

from core.individual import Individual, sort_individuals


@pytest.mark.parametrize(
    "roles, test_ok",
    [
        (
            [
                "SHAREHOLDER",
                "SHAREHOLDER/DIRECTOR",
                "SHAREHOLDER",
                "DIRECTOR",
                "SHAREHOLDER",
            ],
            True,
        ),
        (["nonsensical gibberish role", "totally invalid role"], False),
    ],
)
def test_sort_individuals(roles: List[str], test_ok: bool):
    """
    Validates that:
    - the pure function sort_individuals returns individuals sorted by role
    """

    def create_dummy_individuals(roles: List[str]):
        output = []
        for role in roles:
            new_ind = Individual(
                "dont matter",
                "-",
                "id_value",
                "no idea",
                "-",
                False,
                False,
                False,
                role,
            )
            output.append(new_ind)
        return output

    role_order = {"SHAREHOLDER/DIRECTOR": 1, "SHAREHOLDER": 2, "DIRECTOR": 3}

    dummies = create_dummy_individuals(roles)
    if not test_ok:
        with pytest.raises(ValueError):
            sorted_dummies = sort_individuals(dummies)
        return

    sorted_dummies = sort_individuals(dummies)

    for i, dummy in enumerate(sorted_dummies):
        if i < len(sorted_dummies) - 1:
            next_dummy = sorted_dummies[i + 1]
            assert next_dummy.role and dummy.role is not None
            assert role_order[next_dummy.role] >= role_order[dummy.role]
