from schema_formatter.schema_management import fix_primary_key


def test_old_and_busted():
    test_string = "     id text NOT NULL"
    result = fix_primary_key(test_string)

    assert result.strip() == "id text PRIMARY KEY"


def test_old_and_really_busted():
    test_string = "id text  NOT NULL"
    result = fix_primary_key(test_string)

    assert result == "id text PRIMARY KEY"


def test_invalid_replacement():
    test_string = "text does not match"
    result = fix_primary_key(test_string)

    assert result == test_string
