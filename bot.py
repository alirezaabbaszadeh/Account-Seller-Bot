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

DATA_FILE = Path('data.json')
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))
except ValueError as e:
    logging.error("ADMIN_ID must be an integer")
    raise SystemExit("ADMIN_ID must be an integer") from e
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "+989152062041")  # manager contact number

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

# Supported translations for messages
MESSAGES = {
    'en': {
        'start': 'Welcome! Use /products to list products.',
        'contact': 'Admin phone: {phone}',
        'no_products': 'No products available',
        'buy': 'Buy',
        'send_payment_proof': 'Send payment proof as a photo to proceed.',
        'payment_submitted': 'Payment submitted. Wait for admin approval.',
        'approve_usage': 'Usage: /approve <user_id> <product_id>',
        'approved': 'Approved.',
        'pending_not_found': 'Pending purchase not found.',
        'code_usage': 'Usage: /code <product_id>',
        'product_not_found': 'Product not found',
        'not_purchased': 'You have not purchased this product.',
        'no_totp': 'No TOTP secret set for this product.',
        'code': 'Code: {code}',
        'addproduct_usage': 'Usage: /addproduct <id> <price> <username> <password> <secret>',
        'product_added': 'Product added',
        'editproduct_usage': 'Usage: /editproduct <id> <field> <value>',
        'invalid_field': 'Invalid field',
        'product_updated': 'Product updated',
        'resend_usage': 'Usage: /resend <product_id> [user_id]',
        'invalid_user_id': 'Invalid user id',
        'no_buyers': 'No buyers to send to',
        'credentials_resent': 'Credentials resent',
        'stats_usage': 'Usage: /stats <product_id>',
        'price_total_buyers': 'Price: {price}\nTotal buyers: {total}',
        'buyers_usage': 'Usage: /buyers <product_id>',
        'buyers_list': 'Buyers: {list}',
        'no_buyers_list': 'No buyers',
        'deletebuyer_usage': 'Usage: /deletebuyer <product_id> <user_id>',
        'buyer_removed': 'Buyer removed',
        'buyer_not_found': 'Buyer not found',
        'clearbuyers_usage': 'Usage: /clearbuyers <product_id>',
        'all_buyers_removed': 'All buyers removed',
        'use_code': 'Use /code {pid} to get your current authenticator code.',
        'language_usage': 'Usage: /setlanguage <en|fa>',
        'language_set': 'Language set to {lang}.',
        'languages_supported': 'Supported languages: en, fa',
    },
    'fa': {
        'start': 'خوش آمدید! از دستور /products برای مشاهده محصولات استفاده کنید.',
        'contact': 'شماره مدیر: {phone}',
        'no_products': 'محصولی موجود نیست',
        'buy': 'خرید',
        'send_payment_proof': 'برای ادامه، رسید پرداخت را به صورت عکس ارسال کنید.',
        'payment_submitted': 'پرداخت ارسال شد. منتظر تأیید مدیر بمانید.',
        'approve_usage': 'استفاده: /approve <user_id> <product_id>',
        'approved': 'تأیید شد.',
        'pending_not_found': 'پرداخت در انتظار یافت نشد.',
        'code_usage': 'استفاده: /code <product_id>',
        'product_not_found': 'محصول پیدا نشد',
        'not_purchased': 'شما این محصول را نخریده‌اید.',
        'no_totp': 'رمز TOTP برای این محصول تنظیم نشده است.',
        'code': 'کد: {code}',
        'addproduct_usage': 'استفاده: /addproduct <id> <price> <username> <password> <secret>',
        'product_added': 'محصول اضافه شد',
        'editproduct_usage': 'استفاده: /editproduct <id> <field> <value>',
        'invalid_field': 'فیلد نامعتبر است',
        'product_updated': 'محصول به‌روزرسانی شد',
        'resend_usage': 'استفاده: /resend <product_id> [user_id]',
        'invalid_user_id': 'آی‌دی کاربر نامعتبر است',
        'no_buyers': 'خریداری برای ارسال وجود ندارد',
        'credentials_resent': 'اطلاعات دوباره ارسال شد',
        'stats_usage': 'استفاده: /stats <product_id>',
        'price_total_buyers': 'قیمت: {price}\nتعداد خریداران: {total}',
        'buyers_usage': 'استفاده: /buyers <product_id>',
        'buyers_list': 'خریداران: {list}',
        'no_buyers_list': 'خریداری وجود ندارد',
        'deletebuyer_usage': 'استفاده: /deletebuyer <product_id> <user_id>',
        'buyer_removed': 'خریدار حذف شد',
        'buyer_not_found': 'خریدار پیدا نشد',
        'clearbuyers_usage': 'استفاده: /clearbuyers <product_id>',
        'all_buyers_removed': 'تمام خریداران حذف شدند',
        'use_code': 'برای دریافت کد احراز هویت از دستور /code {pid} استفاده کنید.',
        'language_usage': 'استفاده: /setlanguage <en|fa>',
        'language_set': 'زبان به {lang} تغییر یافت.',
        'languages_supported': 'زبان‌های پشتیبانی‌شده: en, fa',
    },
}


def tr(context: ContextTypes.DEFAULT_TYPE, key: str, **kwargs) -> str:
    """Return a translated message for the user's language."""
    lang = context.user_data.get('lang', 'en')
    msgs = MESSAGES.get(lang, MESSAGES['en'])
    template = msgs.get(key, MESSAGES['en'].get(key, key))
    return template.format(**kwargs)


def user_lang(user_id: int) -> str:
    """Return stored language for given user id."""
    return data.get('languages', {}).get(str(user_id), 'en')


async def send_tr(bot, user_id: int, key: str, **kwargs):
    """Send a translated message to a user based on saved language."""
    lang = user_lang(user_id)
    msgs = MESSAGES.get(lang, MESSAGES['en'])
    text = msgs.get(key, MESSAGES['en'].get(key, key)).format(**kwargs)
    await bot.send_message(user_id, text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(tr(context, 'start'))


async def setlanguage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        lang = context.args[0].lower()
    except IndexError:
        await update.message.reply_text(tr(context, 'language_usage'))
        return
    if lang not in MESSAGES:
        await update.message.reply_text(tr(context, 'languages_supported'))
        return
    context.user_data['lang'] = lang
    data['languages'][str(update.message.from_user.id)] = lang
    save_data(data)
    name = 'English' if lang == 'en' else 'Persian'
    await update.message.reply_text(tr(context, 'language_set', lang=name))


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send admin phone number."""
    await update.message.reply_text(tr(context, 'contact', phone=ADMIN_PHONE))


def product_keyboard(context: ContextTypes.DEFAULT_TYPE, product_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(tr(context, 'buy'), callback_data=f'buy:{product_id}')]])


async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data['products']:
        await update.message.reply_text(tr(context, 'no_products'))
        return
    for pid, info in data['products'].items():
        text = f"{pid}: {info['price']}\n{info.get('name', '')}"
        await update.message.reply_text(text, reply_markup=product_keyboard(context, pid))


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pid = query.data.split(':')[1]
    context.user_data['buy_pid'] = pid
    await query.message.reply_text(tr(context, 'send_payment_proof'))


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pid = context.user_data.get('buy_pid')
    if not pid:
        return
    photo = update.message.photo[-1]
    file_id = photo.file_id
    data['pending'].append({'user_id': update.message.from_user.id, 'product_id': pid, 'file_id': file_id})
    save_data(data)
    await update.message.reply_text(tr(context, 'payment_submitted'))
    await context.bot.send_photo(ADMIN_ID, file_id, caption=f"/approve {update.message.from_user.id} {pid}")


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(context.args[0])
        pid = context.args[1]
    except (IndexError, ValueError):
        await update.message.reply_text(tr(context, 'approve_usage'))
        return
    for p in data['pending']:
        if p['user_id'] == user_id and p['product_id'] == pid:
            data['pending'].remove(p)
            buyers = data['products'].setdefault(pid, {}).setdefault('buyers', [])
            if user_id not in buyers:
                buyers.append(user_id)
            save_data(data)
            creds = data['products'][pid]
            msg = f"Username: {creds.get('username')}\nPassword: {creds.get('password')}"
            await context.bot.send_message(user_id, msg)
            await send_tr(context.bot, user_id, 'use_code', pid=pid)
            await update.message.reply_text(tr(context, 'approved'))
            return
    await update.message.reply_text(tr(context, 'pending_not_found'))


async def code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        pid = context.args[0]
    except IndexError:
        await update.message.reply_text(tr(context, 'code_usage'))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr(context, 'product_not_found'))
        return
    if update.message.from_user.id not in product.get('buyers', []):
        await update.message.reply_text(tr(context, 'not_purchased'))
        return
    secret = product.get('secret')
    if not secret:
        await update.message.reply_text(tr(context, 'no_totp'))
        return
    totp = pyotp.TOTP(secret)
    await update.message.reply_text(tr(context, 'code', code=totp.now()))


async def addproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
        price = context.args[1]
        username = context.args[2]
        password = context.args[3]
        secret = context.args[4]
    except IndexError:
        await update.message.reply_text(tr(context, 'addproduct_usage'))
        return
    data['products'][pid] = {
        'price': price,
        'username': username,
        'password': password,
        'secret': secret,
        'buyers': []
    }
    save_data(data)
    await update.message.reply_text(tr(context, 'product_added'))


async def editproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
        field = context.args[1]
        value = context.args[2]
    except IndexError:
        await update.message.reply_text(tr(context, 'editproduct_usage'))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr(context, 'product_not_found'))
        return
    if field not in {'price', 'username', 'password', 'secret'}:
        await update.message.reply_text(tr(context, 'invalid_field'))
        return
    product[field] = value
    save_data(data)
    await update.message.reply_text(tr(context, 'product_updated'))


async def resend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
    except IndexError:
        await update.message.reply_text(tr(context, 'resend_usage'))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr(context, 'product_not_found'))
        return
    buyers = product.get('buyers', [])
    if len(context.args) > 1:
        try:
            uid = int(context.args[1])
        except ValueError:
            await update.message.reply_text(tr(context, 'invalid_user_id'))
            return
        buyers = [uid] if uid in buyers else []
    if not buyers:
        await update.message.reply_text(tr(context, 'no_buyers'))
        return
    msg = f"Username: {product.get('username')}\nPassword: {product.get('password')}"
    for uid in buyers:
        await context.bot.send_message(uid, msg)
        await send_tr(context.bot, uid, 'use_code', pid=pid)
    await update.message.reply_text(tr(context, 'credentials_resent'))


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
    except IndexError:
        await update.message.reply_text(tr(context, 'stats_usage'))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr(context, 'product_not_found'))
        return
    buyers = product.get('buyers', [])
    text = tr(
        context,
        'price_total_buyers',
        price=product.get('price'),
        total=len(buyers),
    )
    await update.message.reply_text(text)


async def buyers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
    except IndexError:
        await update.message.reply_text(tr(context, 'buyers_usage'))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr(context, 'product_not_found'))
        return
    buyers_list = product.get('buyers', [])
    if buyers_list:
        await update.message.reply_text(tr(context, 'buyers_list', list=', '.join(map(str, buyers_list))))
    else:
        await update.message.reply_text(tr(context, 'no_buyers_list'))


async def deletebuyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
        uid = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text(tr(context, 'deletebuyer_usage'))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr(context, 'product_not_found'))
        return
    if uid in product.get('buyers', []):
        product['buyers'].remove(uid)
        save_data(data)
        await update.message.reply_text(tr(context, 'buyer_removed'))
    else:
        await update.message.reply_text(tr(context, 'buyer_not_found'))


async def clearbuyers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    try:
        pid = context.args[0]
    except IndexError:
        await update.message.reply_text(tr(context, 'clearbuyers_usage'))
        return
    product = data['products'].get(pid)
    if not product:
        await update.message.reply_text(tr(context, 'product_not_found'))
        return
    product['buyers'] = []
    save_data(data)
    await update.message.reply_text(tr(context, 'all_buyers_removed'))


def main(token: str):
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('contact', contact))
    app.add_handler(CommandHandler('setlanguage', setlanguage))
    app.add_handler(CommandHandler('products', products))
    app.add_handler(CallbackQueryHandler(buy_callback, pattern=r'^buy:'))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CommandHandler('approve', approve))
    app.add_handler(CommandHandler('code', code))
    app.add_handler(CommandHandler('addproduct', addproduct))
    app.add_handler(CommandHandler('editproduct', editproduct))
    app.add_handler(CommandHandler('buyers', buyers))
    app.add_handler(CommandHandler('deletebuyer', deletebuyer))
    app.add_handler(CommandHandler('clearbuyers', clearbuyers))
    app.add_handler(CommandHandler('resend', resend))
    app.add_handler(CommandHandler('stats', stats))

    app.run_polling()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python bot.py <TOKEN>')
    else:
        main(sys.argv[1])
