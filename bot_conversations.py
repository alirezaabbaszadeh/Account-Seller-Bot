from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from bot import ADMIN_ID, data, storage, ensure_lang

ASK_ID, ASK_PRICE, ASK_USERNAME, ASK_PASSWORD, ASK_SECRET, ASK_NAME = range(6)
CANCEL_TEXT = "Cancel"

async def addproduct_menu(update, context):
    ensure_lang(context, update.effective_user.id)
    lang = context.user_data["lang"]
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Unauthorized")
        return ConversationHandler.END
    await update.message.reply_text(
        "Send product id",
        reply_markup=ReplyKeyboardMarkup([[CANCEL_TEXT]], one_time_keyboard=True),
    )
    return ASK_ID

async def addproduct_id(update, context):
    if update.message.text == CANCEL_TEXT:
        return await addproduct_cancel(update, context)
    context.user_data["pid"] = update.message.text
    await update.message.reply_text(
        "Send price", reply_markup=ReplyKeyboardMarkup([[CANCEL_TEXT]], one_time_keyboard=True)
    )
    return ASK_PRICE

async def addproduct_price(update, context):
    if update.message.text == CANCEL_TEXT:
        return await addproduct_cancel(update, context)
    context.user_data["price"] = update.message.text
    await update.message.reply_text(
        "Send username", reply_markup=ReplyKeyboardMarkup([[CANCEL_TEXT]], one_time_keyboard=True)
    )
    return ASK_USERNAME

async def addproduct_username(update, context):
    if update.message.text == CANCEL_TEXT:
        return await addproduct_cancel(update, context)
    context.user_data["username"] = update.message.text
    await update.message.reply_text(
        "Send password", reply_markup=ReplyKeyboardMarkup([[CANCEL_TEXT]], one_time_keyboard=True)
    )
    return ASK_PASSWORD

async def addproduct_password(update, context):
    if update.message.text == CANCEL_TEXT:
        return await addproduct_cancel(update, context)
    context.user_data["password"] = update.message.text
    await update.message.reply_text(
        "Send secret", reply_markup=ReplyKeyboardMarkup([[CANCEL_TEXT]], one_time_keyboard=True)
    )
    return ASK_SECRET

async def addproduct_secret(update, context):
    if update.message.text == CANCEL_TEXT:
        return await addproduct_cancel(update, context)
    context.user_data["secret"] = update.message.text
    await update.message.reply_text(
        "Send name or - to skip", reply_markup=ReplyKeyboardMarkup([[CANCEL_TEXT]], one_time_keyboard=True)
    )
    return ASK_NAME

async def addproduct_name(update, context):
    if update.message.text == CANCEL_TEXT:
        return await addproduct_cancel(update, context)
    name = update.message.text
    pid = context.user_data["pid"]
    data["products"][pid] = {
        "price": context.user_data["price"],
        "username": context.user_data["username"],
        "password": context.user_data["password"],
        "secret": context.user_data["secret"],
        "buyers": [],
    }
    if name and name != "-":
        data["products"][pid]["name"] = name
    await storage.save(data)
    await update.message.reply_text("Product added", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def addproduct_cancel(update, context):
    await update.message.reply_text("Cancelled", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
