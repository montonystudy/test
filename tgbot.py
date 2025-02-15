import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Токен бота не найден.")

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Отправьте ссылку на видео youtube, чтобы скачать аудио.")

async def download_and_send(update: Update, context: CallbackContext):
    url = update.message.text
    status_message = await update.message.reply_text("Загружаю...")

    try:
        # Настройки для скачивания
        ydl_opts = {
            'format': 'bestaudio/best',
            'nocheckcertificate': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'no_warnings': True,
            'noplaylist': True,
        }

        # Скачиваем и конвертируем
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            mp3_file = filename.rsplit(".", 1)[0] + ".mp3"

        # Отправляем файл
        await status_message.edit_text("Отправляю файл...")
        with open(mp3_file, 'rb') as audio:
            await update.message.reply_audio(audio)

        # Удаляем файл и обновляем статус
        os.remove(mp3_file)
        await status_message.edit_text("работаем 🔥🔥🔥")

    except Exception as e:
        await status_message.edit_text(f"Ошибка: {str(e)}")
        if 'mp3_file' in locals():
            try:
                os.remove(mp3_file)
            except:
                pass

def main():
    # Создаём папку для загрузок
    os.makedirs("downloads", exist_ok=True)

    # Запускаем бота
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send))

    print("✅ Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
    