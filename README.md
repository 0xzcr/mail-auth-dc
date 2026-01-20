### mail-auth-dc

Discord bot (discord.py) that verifies a user’s email for a specific domain and assigns a role.

### Setup (no run commands here—just what must be true)

- **Install deps**: see `requirements.txt`
- **Env vars needed** (set these in your shell or a dotenv file):
  - `DISCORD_TOKEN`
  - `ALLOWED_DOMAIN` (e.g. `example.edu`)
  - `GUILD_ID` (numeric server id)
  - `ROLE_NAME` (role must already exist)
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL`

### Code

Main bot is in `xaegis.py`.