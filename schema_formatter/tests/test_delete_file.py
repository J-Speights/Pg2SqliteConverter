import os
from pytest_mock import MockFixture
from schema_formatter.worker_functions import delete_file


def test_delete_existing_file():
    temp_file = "test_file.txt"
    with open(temp_file, "w") as file:
        file.write("Test File")

    result = delete_file(temp_file)

    assert not os.path.exists(temp_file)
    assert result == 0


def test_delete_fake_file():
    fake_file = "fake_file.txt"
    result = delete_file(fake_file)

    assert result == 0


def test_delete_file_permission_error(mocker: MockFixture):
    mocker.patch("os.path.exists", return_value=True)  # Fake the path existing
    mocker.patch(
        "os.remove", side_effect=PermissionError
    )  # Fake that we didn't have permission

    result = delete_file("anyfile.txt")
    assert result == 1
