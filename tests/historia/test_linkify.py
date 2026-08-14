import pytest

from pipelines.historia.analizer import _curly_quotes, _linkify


def test_bare_url_is_wrapped():
    texto = _linkify("consultada en junio de 2026, https://www.jalisco.gob.mx/a")

    assert texto.endswith(r"\url{https://www.jalisco.gob.mx/a}")


@pytest.mark.parametrize("punct", [".", ",", ";", ":", ")"])
def test_trailing_punctuation_stays_outside_the_command(punct):
    texto = _linkify(f"ver https://x.mx/a{punct}")

    assert texto == rf"ver \url{{https://x.mx/a}}{punct}"


def test_already_wrapped_url_is_not_double_wrapped():
    original = r"ver \url{https://x.mx/a}"

    assert _linkify(original) == original


def test_multiple_urls_are_each_wrapped():
    texto = _linkify("https://a.mx/1 y https://b.mx/2")

    assert texto == r"\url{https://a.mx/1} y \url{https://b.mx/2}"


def test_http_and_https_are_both_detected():
    texto = _linkify("http://a.mx y https://b.mx")

    assert texto.count(r"\url{") == 2


def test_text_without_urls_is_unchanged():
    original = "El municipio fue fundado en 1821."

    assert _linkify(original) == original


def test_underscores_in_url_are_preserved():
    texto = _linkify("ver https://x.mx/a_b_c")

    assert texto == r"ver \url{https://x.mx/a_b_c}"


def test_straight_quotes_become_curly():
    texto = _curly_quotes('Jalisco, "Atenguillo”, información')

    assert texto == "Jalisco, “Atenguillo”, información"
    assert '"' not in texto


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ('El "Río" pasa.', "El “Río” pasa."),
        ('"Inicio" del texto', "“Inicio” del texto"),
        ('("entre paréntesis")', "(“entre paréntesis”)"),
        ('mide 5" de largo', "mide 5” de largo"),
    ],
)
def test_quote_direction_depends_on_previous_character(entrada, esperado):
    assert _curly_quotes(entrada) == esperado


def test_existing_curly_quotes_are_untouched():
    original = "ya tiene “comillas” correctas"

    assert _curly_quotes(original) == original
