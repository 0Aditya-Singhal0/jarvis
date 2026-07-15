# Migrations

Add reviewed Alembic revision files in `versions/`. The application deliberately reports unavailable health until exactly one migration head exists and the database is at that head.

Do not create, apply, or autogenerate a migration without a separate owner-approved database action.
