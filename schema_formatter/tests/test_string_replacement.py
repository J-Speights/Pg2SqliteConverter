from schema_formatter.schema_management import string_replacement


def test_public():
    test_line = "fancy public.test NOT NULL"
    result = string_replacement(test_line)

    assert result == "fancy test NOT NULL"


def test_multi_replace():
    test_line = "id uuid DEFAULT public.uuid_generate_v4()"
    result = string_replacement(test_line)

    assert result.strip() == "id text"


def test_no_replace():
    test_line = "this is a test line"
    result = string_replacement(test_line)

    assert result == test_line
