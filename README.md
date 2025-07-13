# Account-Seller-Bot

This project contains a simple Telegram bot for selling products with manual payment approval and two-factor authentication codes.

## Features
- Admin can add products with price, credentials, TOTP secret, and an optional name.
- Products may also be added interactively from the admin menu or by running `/addproduct` with no arguments.
- Users can browse products and submit payment proof.
- Admin approves purchases and credentials are sent to the buyer.
- Buyers can obtain a current authenticator code with `/code <product_id>`.
- Admin can list and manage buyers.
- Admin can edit product fields (including the name) via inline buttons in the admin menu or the `/editproduct` command. Credentials can also be resent using the "Resend" button or `/resend`.
- Admin can remove a product with `/deleteproduct <id>` or by pressing the inline "Delete" button and confirming.
- Admin can list pending purchases with `/pending` and reject them with `/reject`.
- Stats for each product available via `/stats`.
- Users can view the admin phone number with `/contact`.
- Users can get a list of all commands with `/help`.
- Users may switch language from the main menu through the "Language" button or via `/setlang`. Bot messages support both English and Farsi.
- پشتیبانی از منوهای سلسله‌مراتبی با دکمه‌های تلگرامی.
- دکمه «بازگشت» و دکمه‌های جدید مدیریتی به منو افزوده شده‌اند.

### Changing language
Users can switch their preferred language with:

```bash
/setlang <code>
```

Replace `<code>` with a language code such as `en` or `fa`.

You can also change the language from the main menu by pressing the
"Language" button and selecting your preferred option.

The `/addproduct` command accepts an optional `[name]` argument to label the product:

```bash
/addproduct <id> <price> <username> <password> <secret> [name]
```

Example adding a product with a name:

```bash
/addproduct 1001 9.99 someuser somepass JBSWY3DPEHPK3PXP "My Product"
```

Alternatively, run `/addproduct` with no arguments or choose "Add product" from
the admin menu to add items interactively.

## Setup
1. Install the project in editable mode:
   ```bash
   pip install -e .
   ```
   For development, include optional dependencies with:
   ```bash
   pip install -e .[dev]
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

   # using the installed script
   account-seller-bot <TOKEN>
   # or
   BOT_TOKEN=<TOKEN> account-seller-bot
   ```

### ناوبری منوها
پس از اجرای ربات با دستور `/start`، منوی اصلی نمایش داده می‌شود که شامل دکمه‌های «محصولات»، «تماس»، «راهنما» و «زبان» است. اگر کاربر مدیر باشد، گزینه «مدیریت» نیز دیده می‌شود. برای ورود به هر بخش روی دکمه مربوطه بزنید و در هر مرحله با دکمه «بازگشت» می‌توانید به مرحله قبل بروید.

**مثال کاربر**
1. ارسال `/start`
2. انتخاب «محصولات» برای مشاهده لیست حساب‌ها
3. انتخاب «زبان» و تعیین زبان دلخواه
4. فشردن «بازگشت» جهت بازگشت به منوی اصلی
**مثال مدیر**
1. ارسال `/start`
2. انتخاب «مدیریت»
3. انتخاب «مدیریت محصولات»
4. انتخاب محصول و استفاده از دکمه‌های «حذف» یا «ارسال دوباره»
5. انتخاب «در انتظار» برای مشاهده خریدهای معلق
6. فشردن «بازگشت» جهت بازگشت به منوی قبل

**مثال ویرایش محصول**
1. ورود به بخش «مدیریت»
2. انتخاب «ویرایش محصول»
3. انتخاب شناسهٔ محصول
4. انتخاب فیلد موردنظر (مثلاً «قیمت») و ارسال مقدار جدید

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
