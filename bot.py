# Telegram bot for managing product sales with TOTP support
import json
import logging
import os
import sys
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
import pyotp
from botlib.translations import tr

# Store data.json in the same directory as this script
DATA_FILE = Path(__file__).resolve().parent / 'data.json'
try:
    ADMIN_ID = int(os.environ["ADMIN_ID"])
except KeyError:
    logging.error("ADMIN_ID environment variable not set")
    raise SystemExit("ADMIN_ID environment variable not set")
except ValueError as e:
    logging.error("ADMIN_ID must be an integer")
    raise SystemExit("ADMIN_ID must be an integer") from e

ADMIN_PHONE = os.environ.get("ADMIN_PHONE")  # manager contact number
if not ADMIN_PHONE:
    logging.error("ADMIN_PHONE environment variable not set")
    raise SystemExit("ADMIN_PHONE environment variable not set")

logging.basicConfig(level=logging.INFO)


def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'products': {}, 'pending': [], 'languages': {}}


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


data = load_data()
data.setdefault('languages', {})


def user_lang(user_id: int) -> str:
    """Return stored language for a user, defaulting to 'en'."""
    return data.get('languages', {}).get(str(user_id), 'en')


def ensure_lang(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Ensure ``context.user_data['lang']`` is set for the user."""
    context.user_data.setdefault('lang', user_lang(user_id))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    await update.message.reply_text(tr('welcome', lang))


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send admin phone number."""
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    await update.message.reply_text(tr('admin_phone', lang).format(phone=ADMIN_PHONE))


async def setlang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change the user's language preference."""
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    try:
        lang_code = context.args[0].lower()
    except IndexError:
        await update.message.reply_text(tr('setlang_usage', lang))
        return
    data.setdefault('languages', {})[str(update.effective_user.id)] = lang_code
    save_data(data)
    context.user_data['lang'] = lang_code
    await update.message.reply_text(tr('language_set', lang_code))


def product_keyboard(product_id: str, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(tr('buy_button', lang), callback_data=f'buy:{product_id}')]])


async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if not data['products']:
        await update.message.reply_text(tr('no_products', lang))
        return
    for pid, info in data['products'].items():
        text = f"{pid}: {info['price']}"
        name = info.get('name')
        if name:
            text += f"\n{name}"
        await update.message.reply_text(text, reply_markup=product_keyboard(pid, lang))


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    query = update.callback_query
    await query.answer()
    pid = query.data.split(':')[1]
    context.user_data['buy_pid'] = pid
    await query.message.reply_text(tr('send_proof', lang))


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    pid = context.user_data.get('buy_pid')
    if not pid:
        return
    photo = update.message.photo[-1]
    file_id = photo.file_id
    data['pending'].append({'user_id': update.message.from_user.id, 'product_id': pid, 'file_id': file_id})
    # Remove the pid after recording the pending payment so later photos aren't
    # mistakenly associated with this purchase.
    context.user_data.pop('buy_pid', None)
    save_data(data)
    await update.message.reply_text(tr('payment_submitted', lang))
    await context.bot.send_photo(ADMIN_ID, file_id, caption=f"/approve {update.message.from_user.id} {pid}")


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(context.args[0])
        pid = context.args[1]
    except (IndexError, ValueError):
        await update.message.reply_text(tr('approve_usage', lang))
        return
    for p in data['pending']:
        if p['user_id'] == user_id and p['product_id'] == pid:
            data['pending'].remove(p)
            buyers = data['products'].setdefault(pid, {}).setdefault('buyers', [])
            if user_id not in buyers:
                buyers.append(user_id)
            save_data(data)
            creds = data['products'][pid]
            msg = tr('credentials_msg', lang).format(
                username=creds.get('username'),
                password=creds.get('password'),
            )
            await context.bot.send_message(user_id, msg)
            await context.bot.send_message(user_id, tr('use_code_hint', lang).format(pid=pid))
            await update.message.reply_text(tr('approved', lang))
            return
    await update.message.reply_text(tr('pending_not_found', lang))


async def code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    try:
        pid = context.args[0]
    except IndexError:
        await update.message.reply_text(tr('code_usage', lang))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr('product_not_found', lang))
        return
    if update.message.from_user.id not in product.get('buyers', []):
        await update.message.reply_text(tr('not_purchased', lang))
        return
    secret = product.get('secret')
    if not secret:
        await update.message.reply_text(tr('no_secret', lang))
        return
    totp = pyotp.TOTP(secret)
    await update.message.reply_text(tr('code_msg', lang).format(code=totp.now()))


async def addproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
        price = context.args[1]
        username = context.args[2]
        password = context.args[3]
        secret = context.args[4]
    except IndexError:
        await update.message.reply_text(tr('addproduct_usage', lang))
        return
    name = " ".join(context.args[5:]) if len(context.args) > 5 else None
    data['products'][pid] = {
        'price': price,
        'username': username,
        'password': password,
        'secret': secret,
        'buyers': []
    }
    if name:
        data['products'][pid]['name'] = name
    save_data(data)
    await update.message.reply_text(tr('product_added', lang))


async def editproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
        field = context.args[1]
        value = " ".join(context.args[2:])
    except IndexError:
        await update.message.reply_text(tr('editproduct_usage', lang))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr('product_not_found', lang))
        return
    if field not in {'price', 'username', 'password', 'secret', 'name'}:
        await update.message.reply_text(tr('invalid_field', lang))
        return
    product[field] = value
    save_data(data)
    await update.message.reply_text(tr('product_updated', lang))


async def deleteproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
    except IndexError:
        await update.message.reply_text(tr('deleteproduct_usage', lang))
        return
    if pid in data["products"]:
        del data["products"][pid]
        save_data(data)
        await update.message.reply_text(tr('product_deleted', lang))
    else:
        await update.message.reply_text(tr('product_not_found', lang))


async def resend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
    except IndexError:
        await update.message.reply_text(tr('resend_usage', lang))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr('product_not_found', lang))
        return
    buyers = product.get('buyers', [])
    if len(context.args) > 1:
        try:
            uid = int(context.args[1])
        except ValueError:
            await update.message.reply_text(tr('invalid_user_id', lang))
            return
        buyers = [uid] if uid in buyers else []
    if not buyers:
        await update.message.reply_text(tr('no_buyers_send', lang))
        return
    msg = tr('credentials_msg', lang).format(
        username=product.get('username'),
        password=product.get('password'),
    )
    for uid in buyers:
        await context.bot.send_message(uid, msg)
        await context.bot.send_message(uid, tr('use_code_hint', lang).format(pid=pid))
    await update.message.reply_text(tr('credentials_resent', lang))


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
    except IndexError:
        await update.message.reply_text(tr('stats_usage', lang))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr('product_not_found', lang))
        return
    buyers = product.get('buyers', [])
    text = "\n".join(
        [
            tr('price_line', lang).format(price=product.get('price')),
            tr('total_buyers_line', lang).format(count=len(buyers)),
        ]
    )
    await update.message.reply_text(text)


async def pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all pending purchases for the admin."""
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if update.message.from_user.id != ADMIN_ID:
        return
    if not data['pending']:
        await update.message.reply_text(tr('no_pending', lang))
        return
    lines = [
        tr('pending_entry', lang).format(
            user_id=p['user_id'],
            product_id=p['product_id'],
        )
        for p in data['pending']
    ]
    await update.message.reply_text('\n'.join(lines))


async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject a pending purchase without approving it."""
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(context.args[0])
        pid = context.args[1]
    except (IndexError, ValueError):
        await update.message.reply_text(tr('reject_usage', lang))
        return
    for p in data['pending']:
        if p['user_id'] == user_id and p['product_id'] == pid:
            data['pending'].remove(p)
            save_data(data)
            await update.message.reply_text(tr('rejected', lang))
            return
    await update.message.reply_text(tr('pending_not_found', lang))


async def buyers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
    except IndexError:
        await update.message.reply_text(tr('buyers_usage', lang))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr('product_not_found', lang))
        return
    buyers_list = product.get('buyers', [])
    if buyers_list:
        await update.message.reply_text(tr('buyers_list', lang).format(list=', '.join(map(str, buyers_list))))
    else:
        await update.message.reply_text(tr('no_buyers', lang))


async def deletebuyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
        uid = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text(tr('deletebuyer_usage', lang))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr('product_not_found', lang))
        return
    if uid in product.get('buyers', []):
        product['buyers'].remove(uid)
        save_data(data)
        await update.message.reply_text(tr('buyer_removed', lang))
    else:
        await update.message.reply_text(tr('buyer_not_found', lang))


async def clearbuyers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
    except IndexError:
        await update.message.reply_text(tr('clearbuyers_usage', lang))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr('product_not_found', lang))
        return
    product['buyers'] = []
    save_data(data)
    await update.message.reply_text(tr('all_buyers_removed', lang))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display available commands for users and admins."""
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data['lang']
    user_cmds = [
        tr('help_user_start', lang),
        tr('help_user_products', lang),
        tr('help_user_code', lang),
        tr('help_user_contact', lang),
        tr('help_user_setlang', lang),
        tr('help_user_help', lang),
    ]
    admin_cmds = [
        tr('help_admin_approve', lang),
        tr('help_admin_reject', lang),
        tr('help_admin_pending', lang),
        tr('help_admin_addproduct', lang),
        tr('help_admin_editproduct', lang),
        tr('help_admin_buyers', lang),
        tr('help_admin_deletebuyer', lang),
        tr('help_admin_clearbuyers', lang),
        tr('help_admin_resend', lang),
        tr('help_admin_stats', lang),
    ]
    text = tr('help_user_header', lang) + '\n' + '\n'.join(user_cmds)
    text += '\n\n' + tr('help_admin_header', lang) + '\n' + '\n'.join(admin_cmds)
    await update.message.reply_text(text)


def main(token: str):
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('contact', contact))
    app.add_handler(CommandHandler('products', products))
    app.add_handler(CommandHandler('setlang', setlang))
    app.add_handler(CallbackQueryHandler(buy_callback, pattern=r'^buy:'))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CommandHandler('approve', approve))
    app.add_handler(CommandHandler('reject', reject))
    app.add_handler(CommandHandler('pending', pending))
    app.add_handler(CommandHandler('code', code))
    app.add_handler(CommandHandler('addproduct', addproduct))
    app.add_handler(CommandHandler('editproduct', editproduct))
    app.add_handler(CommandHandler('deleteproduct', deleteproduct))
    app.add_handler(CommandHandler('buyers', buyers))
    app.add_handler(CommandHandler('deletebuyer', deletebuyer))
    app.add_handler(CommandHandler('clearbuyers', clearbuyers))
    app.add_handler(CommandHandler('resend', resend))
    app.add_handler(CommandHandler('stats', stats))
    app.add_handler(CommandHandler('help', help_command))

    app.run_polling()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python bot.py <TOKEN>')
    else:
        main(sys.argv[1])
