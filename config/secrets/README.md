# Secret-file contract

Create real secret files only after explicit owner approval, outside this repository at `JARVIS_SECRETS_DIR`. The initial required file is `postgres_password`; it contains one random password and is mounted read-only by Compose. Never commit, log, or copy secret values into `.env`.

EMQX credentials and MQTT authorization rules are deferred until the device/EMQX authorization design is approved.
