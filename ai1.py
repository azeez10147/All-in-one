from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
import yt_dlp
import asyncio
import os
import tempfile

# التوكن الخاص بك
TOKEN = '7202973235:AAGXdGkbWx3cayRvh8Www0Rfqq5rJZ7uo78'

# ID الخاص بالمطور
DEVELOPER = 7100583957

# الحالات المطلوبة للمحادثة
WAITING_FOR_POINTS, WAITING_FOR_IMAGE, SONGS_MENU, SONGS_CHOOSE, SONG_NAME = range(5)


# أمر البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first = update.effective_user.first_name
    keyboard = [
        [KeyboardButton("🎼 خدمات الأغاني 🎶")],
        [KeyboardButton("⛩️ شراء رصيد ⛩️")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if update.message:
        await update.message.reply_photo(
            photo='https://files.catbox.moe/uk7r4l.jpg',
            caption=(
                f"مرحبا بك {user_first} 😄\n\n"
                "☄بوت كلشيء بالواحد لجميع الخدمات🪐\n\n"
                "⛩ استمتع بالتجربة وابدأ الآن!\n\n"
                "اختر احد الأزرار أدناه لاختيار القسم المطلوب 👇"
            ),
            reply_markup=reply_markup
        )


# عند اختيار "⛩️ شراء رصيد ⛩️"
async def buy_points_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text != "⛩️ شراء رصيد ⛩️":
        return ConversationHandler.END

    keyboard = [[KeyboardButton("❌ إلغاء")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("⛩️ ارسل كمية النقاط المراد الحصول عليها ⛩️", reply_markup=reply_markup)
    return WAITING_FOR_POINTS


# استلام كمية النقاط
async def receive_points_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = update.message.text
    if not amount.isdigit():
        await update.message.reply_text("الرجاء إدخال عدد صحيح من النقاط.")
        return WAITING_FOR_POINTS

    context.user_data['points_amount'] = amount

    keyboard = [
        [KeyboardButton("SYRIATEL CASH")],
        [KeyboardButton("❌ إلغاء")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"✅ تم تسجيل طلبك للحصول على {amount} نقطة.\n\n"
        "يرجى تحويل الرصيد عبر سيرياتيل كاش من الزر أدناه للمتابعة.",
        reply_markup=reply_markup
    )

    return WAITING_FOR_IMAGE


# عند اختيار زر SYRIATEL CASH
async def syriatel_cash_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text != "SYRIATEL CASH":
        return ConversationHandler.END

    keyboard = [[KeyboardButton("❌ إلغاء")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🔻 حول المبلغ إلى الرقم التالي:\n"
        "`0938408859`\n\n"
        "عن طريق تطبيق أقرب إليك (خدمة تحويل يدوي) أو عبر الرمز:\n"
        "`*3040*`\n\n"
        "⚠️ ملاحظة: لسنا مسؤولين إن قمت بتحويل رصيد أو شيء آخر غير سيرياتيل كاش.\n\n"
        "الآن، أرسل صورة التحويل للتحقق.",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return WAITING_FOR_IMAGE


# استلام صورة التحويل
async def receive_transfer_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("الرجاء إرسال صورة التحويل.")
        return WAITING_FOR_IMAGE

    user = update.effective_user
    amount = context.user_data.get('points_amount', 'غير محدد')
    photo = update.message.photo[-1].file_id

    caption = (
        f"طلب شراء نقاط:\n\n"
        f"الاسم: {user.first_name}\n"
        f"الآيدي: {user.id}\n"
        f"الكمية المطلوبة: {amount}\n"
        f"اسم المستخدم: @{user.username if user.username else 'لا يوجد'}"
    )

    try:
        await context.bot.send_photo(chat_id=DEVELOPER, photo=photo, caption=caption)
    except Exception as e:
        await update.message.reply_text("حدث خطأ أثناء إرسال الطلب للمطور، الرجاء المحاولة لاحقًا.")
        print(f"Error sending photo to developer: {e}")
        return WAITING_FOR_IMAGE

    keyboard = [[KeyboardButton("🔝 القائمة الرئيسية")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "✅ تم إرسال طلب شراء النقاط للمطور، سيتم التواصل معك قريباً!\n\n"
        "اضغط الزر أدناه للعودة إلى القائمة الرئيسية.",
        reply_markup=reply_markup
    )

    return ConversationHandler.END

# إلغاء المحادثة
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        text = update.message.text
        if text == "❌ إلغاء":
            context.user_data.clear()
            await start(update, context)
            return ConversationHandler.END
    return ConversationHandler.END


# زر خدمات الأغاني - إرسال القائمة
async def songs_services_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text != "🎼 خدمات الأغاني 🎶":
        return ConversationHandler.END

    menu_text = (
        "إلك قائمة خدمات الأغاني اختر المطلوب:\n\n"
        "1. تحميل أغنية من اسم\n"
        "2. خدمة ٢\n"
        "3. خدمة ٣\n"
        "4. خدمة ٤\n"
        "5. خدمة ٥\n"
        "6. خدمة ٦\n\n"
        "اختر رقم الخدمة بكتابة الرقم أو بالضغط على الزر أدناه:"
    )
    keyboard = [
        [KeyboardButton("1"), KeyboardButton("2")],
        [KeyboardButton("3"), KeyboardButton("4")],
        [KeyboardButton("5"), KeyboardButton("6")],
        [KeyboardButton("❌ إلغاء")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(menu_text, reply_markup=reply_markup)
    return SONGS_CHOOSE


# عند اختيار رقم الخدمة
async def song_choice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "1":
        keyboard = [[KeyboardButton("❌ إلغاء")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "لقد اخترت الخدمة الأولى والتي هي:\n"
            "🎵 تحميل أغنية من اسم\n\n"
            "الرجاء إدخال اسم الأغنية بدقة للبحث عنها وجلبها.",
            reply_markup=reply_markup
        )
        return SONG_NAME
    elif text in ["2", "3", "4", "5", "6"]:
        await update.message.reply_text("هذه الخدمة قيد التطوير حالياً.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("الرجاء اختيار رقم صحيح من القائمة.")
        return SONGS_CHOOSE


# البحث عن الأغنية وتنزيلها بصيغة mp3
async def search_and_send_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    song_name = update.message.text.strip()

    if song_name == "❌ إلغاء":
        context.user_data.clear()
        await start(update, context)
        return ConversationHandler.END

    await update.message.reply_text(f"جاري البحث عن الأغنية: {song_name} ... الرجاء الانتظار قليلاً")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': os.path.join(tempfile.gettempdir(), '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    loop = asyncio.get_event_loop()

    def run_yt_dlp():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{song_name}", download=True)
            video = info['entries'][0]
            file_path = ydl.prepare_filename(video)
            # yt_dlp يقوم بالتنزيل بامتداد الفيديو الأصلي، نحتاج لتغييره إلى mp3 بعد المعالجة
            mp3_path = os.path.splitext(file_path)[0] + '.mp3'
            return mp3_path

    try:
        file_path = await loop.run_in_executor(None, run_yt_dlp)
        # التأكد أن الملف موجود قبل الإرسال
        if not os.path.isfile(file_path):
            await update.message.reply_text("عذراً، لم أتمكن من تنزيل الأغنية.")
            return ConversationHandler.END
    except Exception as e:
        print(f"Error downloading song: {e}")
        await update.message.reply_text("عذراً، لم أتمكن من العثور على الأغنية أو حدث خطأ في التنزيل.")
        return ConversationHandler.END

    try:
        with open(file_path, 'rb') as audio_file:
            await update.message.reply_audio(audio=audio_file, title=song_name)
    except Exception as e:
        print(f"Error sending audio: {e}")
        await update.message.reply_text("حدث خطأ أثناء إرسال الأغنية.")
        return ConversationHandler.END
    finally:
        # حذف الملف بعد الإرسال للحفاظ على مساحة التخزين
        if os.path.isfile(file_path):
            os.remove(file_path)

    context.user_data.clear()
    return ConversationHandler.END


# تشغيل البوت
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^⛩️ شراء رصيد ⛩️$'), buy_points_callback)],
        states={
            WAITING_FOR_POINTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_points_amount)],
            WAITING_FOR_IMAGE: [
                MessageHandler(filters.Regex('^SYRIATEL CASH$'), syriatel_cash_callback),
                MessageHandler(filters.PHOTO, receive_transfer_image)
            ],
        },
        fallbacks=[MessageHandler(filters.Regex('^❌ إلغاء$'), cancel), CommandHandler('cancel', cancel)],
    )

    songs_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🎼 خدمات الأغاني 🎶$'), songs_services_callback)],
        states={
            SONGS_CHOOSE: [MessageHandler(filters.Regex('^[1-6]$'), song_choice_callback)],
            SONG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_and_send_song)],
        },
        fallbacks=[MessageHandler(filters.Regex('^❌ إلغاء$'), cancel), CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(conv_handler)
    app.add_handler(songs_conv)
    app.add_handler(MessageHandler(filters.Regex('^🔝 القائمة الرئيسية$'), start))
    print("البوت شغال...")
    app.run_polling()
