# Account-Seller-Bot

This project contains a simple Telegram bot for selling products with manual payment approval and two-factor authentication codes.

## Features
- Admin can add products with price, credentials, TOTP secret, and an optional name.
- Users can browse products and submit payment proof.
- Admin approves purchases and credentials are sent to the buyer.
- Buyers can obtain a current authenticator code with `/code <product_id>`.
- Admin can list and manage buyers.
- Admin can edit product fields (including the name) with `/editproduct` and resend credentials with `/resend`.
- Admin can remove a product with `/deleteproduct <id>`.
- Admin can list pending purchases with `/pending` and reject them with `/reject`.
- Stats for each product available via `/stats`.
- Users can view the admin phone number with `/contact`.
- Users can get a list of all commands with `/help`.
- Bot messages support both English and Farsi.

### Changing language
Users can switch their preferred language with:

```bash
/setlang <code>
```

Replace `<code>` with a language code such as `en` or `fa`.

The `/addproduct` command accepts an optional `[name]` argument to label the product:

```bash
/addproduct <id> <price> <username> <password> <secret> [name]
```

Example adding a product with a name:

```bash
/addproduct 1001 9.99 someuser somepass JBSWY3DPEHPK3PXP "My Product"
```

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. The bot stores its state in a `data.json` file located next to `bot.py`.
   **Do not commit this file.** It is excluded via `.gitignore` and will be
   created automatically on first run if it doesn't exist.
   If you prefer to create it manually, start with the following content:

   ```json
   {"products": {}, "pending": [], "languages": {}}
   ```

   Set the following environment variables **before running the bot**. The
   application will exit if any is missing or invalid:
   - `ADMIN_ID` – Telegram user ID of the admin (integer)
   - `ADMIN_PHONE` – phone number shown when users run `/contact`
   - `FERNET_KEY` – encryption key for credentials (generate with
     `python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'`)
   Keep this key secret and consistent. Changing it will make existing
   `data.json` contents unreadable.
   - `DATA_FILE` – optional path to the JSON storage file. Defaults to
     `data.json` next to `bot.py`.
3. Run the bot with your bot token. Pass it as an argument or via the
   `BOT_TOKEN` environment variable:
   ```bash
   python bot.py <TOKEN>
   # or
   BOT_TOKEN=<TOKEN> python bot.py
   ```

This is a minimal implementation and does not include persistent database storage or full error handling.

## Docker

A `Dockerfile` is provided to run the bot in a container.

Build the image:

```bash
docker build -t accounts-bot .
```

Run the container with your bot token and required admin environment variables
using `-e` flags:

```bash
docker run --rm -e ADMIN_ID=<YOUR_ID> -e ADMIN_PHONE=<YOUR_PHONE> \
    -e BOT_TOKEN=<TOKEN> accounts-bot
```

### Managing pending purchases

List pending purchases:

```bash
/pending
```

Reject a pending purchase:

```bash
/reject <user_id> <product_id>
```

## Development
Run code style checks and tests with the following commands:

```bash
flake8
pytest
```
The unit tests require `python-telegram-bot`. Tests depending on it are skipped
automatically when the package is missing so the suite can run without the
dependency.
