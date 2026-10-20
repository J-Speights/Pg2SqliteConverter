from schema_formatter.schema_management import (
    remove_alter_table_statements,
    convert_schema_from_pg_to_sqlite,
)


def test_no_valid_backup_file():
    pass


def test_no_create_statements():
    pass


def test_remove_comments():
    pass


def test_remove_alters():
    lines = [
        "CREATE TABLE public.helpdesk_tickets (ticket_number text);\n",
        "ALTER TABLE public.helpdesk_tickets OWNER TO nimbleadmin;\n",
        "ALTER TABLE public.helpdesk_tickets ALTER COLUMN ticket_number "
        "ADD GENERATED ALWAYS AS IDENTITY (\n",
        "    SEQUENCE NAME public.helpdesk_tickets_ticket_number_seq\n",
        "    START WITH 1\n",
        "    INCREMENT BY 1\n",
        "    NO MINVALUE\n",
        "    NO MAXVALUE\n",
        "    CACHE 1\n",
        ");\n",
        "CREATE TABLE public.next_table (id text);\n",
    ]

    assert remove_alter_table_statements(lines) == [
        "CREATE TABLE public.helpdesk_tickets (ticket_number text);\n",
        "CREATE TABLE public.next_table (id text);\n",
    ]
