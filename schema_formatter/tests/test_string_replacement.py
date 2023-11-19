import os
from schema_formatter.worker_functions import string_replacement


def test_underscore_id():
    test_line = "customer_id text NOT NULL"
