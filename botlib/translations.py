TRANSLATIONS = {
    'welcome': {
        'en': 'Welcome! Use /products to list products.',
        'fa': 'به بات خوش آمدید! برای مشاهده محصولات از /products استفاده کنید.'
    },
    'admin_phone': {
        'en': 'Admin phone: {phone}',
        'fa': 'شماره مدیر: {phone}'
    },
    'buy_button': {
        'en': 'Buy',
        'fa': 'خرید'
    },
    'no_products': {
        'en': 'No products available',
        'fa': 'محصولی موجود نیست'
    },
    'send_proof': {
        'en': 'Send payment proof as a photo to proceed.',
        'fa': 'برای ادامه، رسید پرداخت را به صورت عکس ارسال کنید.'
    },
    'payment_submitted': {
        'en': 'Payment submitted. Wait for admin approval.',
        'fa': 'پرداخت ثبت شد. منتظر تایید مدیر باشید.'
    },
    'approve_usage': {
        'en': 'Usage: /approve <user_id> <product_id>',
        'fa': 'استفاده: /approve <user_id> <product_id>'
    },
    'approved': {
        'en': 'Approved.',
        'fa': 'تایید شد.'
    },
    'pending_not_found': {
        'en': 'Pending purchase not found.',
        'fa': 'خرید در انتظار یافت نشد.'
    },
    'code_usage': {
        'en': 'Usage: /code <product_id>',
        'fa': 'استفاده: /code <product_id>'
    },
    'product_not_found': {
        'en': 'Product not found',
        'fa': 'محصول یافت نشد'
    },
    'not_purchased': {
        'en': 'You have not purchased this product.',
        'fa': 'شما این محصول را خریداری نکرده اید.'
    },
    'no_secret': {
        'en': 'No TOTP secret set for this product.',
        'fa': 'رمز TOTP برای این محصول تنظیم نشده است.'
    },
    'code_msg': {
        'en': 'Code: {code}',
        'fa': 'کد: {code}'
    },
    'setlang_usage': {
        'en': 'Usage: /setlang <code>',
        'fa': 'استفاده: /setlang <code>'
    },
    'language_set': {
        'en': 'Language updated.',
        'fa': 'زبان به روز شد.'
    },
    'addproduct_usage': {
        'en': 'Usage: /addproduct <id> <price> <username> <password> <secret> [name]',
        'fa': 'استفاده: /addproduct <id> <price> <username> <password> <secret> [name]'
    },
    'product_added': {
        'en': 'Product added',
        'fa': 'محصول اضافه شد'
    },
    'editproduct_usage': {
        'en': 'Usage: /editproduct <id> <field> <value>',
        'fa': 'استفاده: /editproduct <id> <field> <value>'
    },
    'invalid_field': {
        'en': 'Invalid field',
        'fa': 'فیلد نامعتبر'
    },
    'product_updated': {
        'en': 'Product updated',
        'fa': 'محصول به روز شد'
    },
    'deleteproduct_usage': {
        'en': 'Usage: /deleteproduct <id>',
        'fa': 'استفاده: /deleteproduct <id>'
    },
    'product_deleted': {
        'en': 'Product deleted',
        'fa': 'محصول حذف شد'
    },
    'resend_usage': {
        'en': 'Usage: /resend <product_id> [user_id]',
        'fa': 'استفاده: /resend <product_id> [user_id]'
    },
    'invalid_user_id': {
        'en': 'Invalid user id',
        'fa': 'آی‌دی کاربر نامعتبر'
    },
    'no_buyers_send': {
        'en': 'No buyers to send to',
        'fa': 'خریداری برای ارسال وجود ندارد'
    },
    'credentials_resent': {
        'en': 'Credentials resent',
        'fa': 'اطلاعات ورود دوباره ارسال شد'
    },
    'credentials_msg': {
        'en': 'Username: {username}\nPassword: {password}',
        'fa': 'نام کاربری: {username}\nرمز عبور: {password}'
    },
    'use_code_hint': {
        'en': 'Use /code {pid} to get your current authenticator code.',
        'fa': 'برای دریافت کد احراز هویت، از /code {pid} استفاده کنید.'
    },
    'stats_usage': {
        'en': 'Usage: /stats <product_id>',
        'fa': 'استفاده: /stats <product_id>'
    },
    'price_line': {
        'en': 'Price: {price}',
        'fa': 'قیمت: {price}'
    },
    'total_buyers_line': {
        'en': 'Total buyers: {count}',
        'fa': 'تعداد خریداران: {count}'
    },
    'buyers_usage': {
        'en': 'Usage: /buyers <product_id>',
        'fa': 'استفاده: /buyers <product_id>'
    },
    'buyers_list': {
        'en': 'Buyers: {list}',
        'fa': 'خریداران: {list}'
    },
    'no_buyers': {
        'en': 'No buyers',
        'fa': 'خریداری وجود ندارد'
    },
    'deletebuyer_usage': {
        'en': 'Usage: /deletebuyer <product_id> <user_id>',
        'fa': 'استفاده: /deletebuyer <product_id> <user_id>'
    },
    'buyer_removed': {
        'en': 'Buyer removed',
        'fa': 'خریدار حذف شد'
    },
    'buyer_not_found': {
        'en': 'Buyer not found',
        'fa': 'خریدار یافت نشد'
    },
    'clearbuyers_usage': {
        'en': 'Usage: /clearbuyers <product_id>',
        'fa': 'استفاده: /clearbuyers <product_id>'
    },
    'all_buyers_removed': {
        'en': 'All buyers removed',
        'fa': 'همه خریداران حذف شدند'
    },
    'help_user_header': {
        'en': '*User commands*',
        'fa': '*دستورات کاربر*'
    },
    'help_admin_header': {
        'en': '*Admin commands*',
        'fa': '*دستورات مدیر*'
    },
    'help_user_start': {
        'en': '/start - start the bot',
        'fa': '/start - شروع ربات'
    },
    'help_user_products': {
        'en': '/products - list available products',
        'fa': '/products - لیست محصولات موجود'
    },
    'help_user_code': {
        'en': '/code <product_id> - get authenticator code',
        'fa': '/code <product_id> - دریافت کد احراز هویت'
    },
    'help_user_contact': {
        'en': '/contact - view admin phone number',
        'fa': '/contact - مشاهده شماره مدیر'
    },
    'help_user_setlang': {
        'en': '/setlang <code> - change your language',
        'fa': '/setlang <code> - تغییر زبان'
    },
    'help_user_help': {
        'en': '/help - show this message',
        'fa': '/help - نمایش این پیام'
    },
    'help_admin_approve': {
        'en': '/approve <user_id> <product_id> - approve a pending purchase',
        'fa': '/approve <user_id> <product_id> - تایید خرید در انتظار'
    },
    'help_admin_addproduct': {
        'en': '/addproduct <id> <price> <username> <password> <secret> [name] - add a product',
        'fa': '/addproduct <id> <price> <username> <password> <secret> [name] - افزودن محصول'
    },
    'help_admin_editproduct': {
        'en': '/editproduct <id> <field> <value> - edit product information',
        'fa': '/editproduct <id> <field> <value> - ویرایش اطلاعات محصول'
    },
    'help_admin_buyers': {
        'en': '/buyers <product_id> - list buyers of a product',
        'fa': '/buyers <product_id> - لیست خریداران محصول'
    },
    'help_admin_deletebuyer': {
        'en': '/deletebuyer <product_id> <user_id> - remove a buyer',
        'fa': '/deletebuyer <product_id> <user_id> - حذف یک خریدار'
    },
    'help_admin_clearbuyers': {
        'en': '/clearbuyers <product_id> - remove all buyers',
        'fa': '/clearbuyers <product_id> - حذف همه خریداران'
    },
    'help_admin_resend': {
        'en': '/resend <product_id> [user_id] - resend credentials',
        'fa': '/resend <product_id> [user_id] - ارسال دوباره اطلاعات'
    },
    'help_admin_stats': {
        'en': '/stats <product_id> - show product statistics',
        'fa': '/stats <product_id> - نمایش آمار محصول'
    },
}


def tr(key: str, lang: str = 'en') -> str:
    """Return the translation for *key* in the given language."""
    return TRANSLATIONS.get(key, {}).get(lang, key)
