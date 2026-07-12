# Secret-file contract

Create real secret files only after explicit owner approval, outside this repository at `JARVIS_SECRETS_DIR`. The initial required file is `postgres_password`; it contains one random password and is mounted read-only by Compose. Never commit, log, or copy secret values into `.env`.

MQTT credentials and ACL files are deferred until the device/MQTT authorization design is approved.
