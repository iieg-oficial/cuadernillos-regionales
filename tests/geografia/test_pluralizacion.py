import pytest

from pipelines.geografia.helpers.formatting import pluralize_comparatives


@pytest.mark.parametrize(
    "value,expected",
    [
        ("mayor a 0 y menor a 5", "mayores a 0 y menores a 5"),
        ("mayor a 30%", "mayores a 30%"),
        ("mayor a 2% y hasta 5%", "mayores a 2% y hasta 5%"),
        ("menor a 5", "menores a 5"),
    ],
)
def test_pluralizes_comparatives_for_plural_subjects(value, expected):
    assert pluralize_comparatives(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "0 a 2%",
        "más de 200",
        "50 a 100",
        "0",
    ],
)
def test_leaves_ranges_without_comparatives_untouched(value):
    assert pluralize_comparatives(value) == value


@pytest.mark.parametrize("value", [None, "", "ND"])
def test_passes_through_missing_values(value):
    assert pluralize_comparatives(value) == value
