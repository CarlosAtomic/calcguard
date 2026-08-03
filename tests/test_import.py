def test_package_imports_and_exposes_its_version():
    import calcguard
    assert isinstance(calcguard.__version__, str)


def test_calcguard_error_is_an_assertion_error():
    """Assertions must fail tests, not crash them, so the base class matters."""
    from calcguard.errors import CalcGuardError
    assert issubclass(CalcGuardError, AssertionError)
