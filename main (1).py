from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from datetime import datetime
import re

# Константы
TOKEN = "TOKEN"
MASTER_CHAT_ID = None  # Сначала chat_id мастера не задан

# Функция для определения приветствия в зависимости от времени суток
def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Доброе утро☀️!"
    elif 12 <= hour < 16:
        return "Добрый день🕛!"
    else:
        return "Добрый вечер🌙!"

# Проверка валидности текста (имя, описание проблемы) без английских символов
def is_valid_text(text):
    return bool(re.match(r"^(?![ .])[А-Яа-я0-9 ,.!?]{2,}$", text.strip()))

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    greeting = get_greeting()
    message = (
        f"""{greeting} Я — Алексей, частный мастер с 14-летним опытом работы. Моя специализация — ремонт холодильников и морозильных камер, и я работаю напрямую с клиентами, поэтому мои цены гораздо ниже, чем у крупных компаний.

<b>Почему стоит выбрать именно меня?</b>
  🕒 Быстрый выезд в течение 30-60 минут.  
  🛠 Диагностика бесплатно при заказе ремонта.  
  🔧 Использую только оригинальные запчасти.  
  🏆 Гарантия на все виды работ — до 12 месяцев.  
  📅 Работаю 24/7, без выходных и праздников.

<b>Для оформления заявки, выберите ваш город, нажав на одну из кнопок ниже.</b>
"""
    )

    # Клавиатура для выбора города
    keyboard = ReplyKeyboardMarkup(
        [["Чебоксары", "Новочебоксарск"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(
        message,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )

    # Сохраняем chat_id мастера, если его ещё нет
    global MASTER_CHAT_ID
    if MASTER_CHAT_ID is None:
        MASTER_CHAT_ID = update.message.chat_id

# Команда /getid для получения chat_id мастера
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if MASTER_CHAT_ID is None:
        await update.message.reply_text("Ваш chat_id ещё не сохранён.")
    else:
        await update.message.reply_text(f"Ваш chat_id: {MASTER_CHAT_ID}")

# Сохранение chat_id мастера
async def save_master_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MASTER_CHAT_ID
    if MASTER_CHAT_ID is None:  # Сохраняем chat_id только один раз
        MASTER_CHAT_ID = update.message.chat_id
        await update.message.reply_text(f"Спасибо! Ваш chat_id сохранён: {MASTER_CHAT_ID}")
    else:
        await update.message.reply_text(f"Ваш chat_id уже сохранён: {MASTER_CHAT_ID}")

# Обработка выбора города
async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    if city in ["Чебоксары", "Новочебоксарск"]:
        context.user_data['city'] = city

        # Убираем клавиатуру после выбора города
        await update.message.reply_text(
            f"📌Вы выбрали город: {city}. Теперь напишите, пожалуйста, ваше имя.",
            reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True),  # Убираем кнопки
        )
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите город, нажав на одну из кнопок: Чебоксары или Новочебоксарск."
        )

# Обработка имени
async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if is_valid_text(name):
        context.user_data['name'] = name
        await update.message.reply_text(
            f"Спасибо, {name}! Теперь напишите, пожалуйста, в чём заключается проблема с вашим холодильником или морозильной камерой.⚙️"
        )
    else:
        await update.message.reply_text(
            "Имя должно содержать минимум 2 символа, состоять только из русских букв, цифр или допустимых знаков. Попробуйте ещё раз."
        )

# Обработка описания проблемы
async def handle_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    problem = update.message.text.strip()
    if is_valid_text(problem):
        context.user_data['problem'] = problem
        await update.message.reply_text("Спасибо! Теперь отправьте, пожалуйста, ваш номер телефона📞.")
    else:
        await update.message.reply_text(
            "Описание проблемы должно содержать минимум 2 символа и быть составлено на русском языке. Попробуйте ещё раз."
        )

# Проверка и обработка номера телефона
async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if re.match(r'^\+?\d{10,15}$', phone):
        context.user_data['phone'] = phone
        await update.message.reply_text("Спасибо! Мы свяжемся с вами в течение часа.")

        # Отправка заявки мастеру
        name = context.user_data.get('name', 'Не указано')
        city = context.user_data.get('city', 'Не указан')
        problem = context.user_data.get('problem', 'Не указана')
        phone_number = context.user_data.get('phone', 'Не указан')
        username = update.message.from_user.username or 'Не указан'

        summary = (
            f"🔔 <b>Новая заявка от клиента:</b>\n\n"
            f"📍 <b>Город:</b> {city}\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"🛠 <b>Проблема:</b> {problem}\n"
            f"📞 <b>Телефон:</b> {phone_number}\n"
            f"📝 <b>Юзернейм:</b> @{username}"
        )

        if MASTER_CHAT_ID:
            try:
                await context.bot.send_message(
                    chat_id=MASTER_CHAT_ID, text=summary, parse_mode=ParseMode.HTML
                )
            except Exception as e:
                await update.message.reply_text(f"Ошибка при отправке заявки мастеру: {e}")
    else:
        await update.message.reply_text(
            "Указан некорректный номер телефона. Номер должен содержать только цифры и может начинаться с '+'. Попробуйте ещё раз."
        )

# Обработка текстовых сообщений
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'city' not in context.user_data:
        await handle_city(update, context)
    elif 'name' not in context.user_data:
        await handle_name(update, context)
    elif 'problem' not in context.user_data:
        await handle_problem(update, context)
    elif 'phone' not in context.user_data:
        await handle_phone(update, context)

# Основная функция запуска бота
def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getid", get_id))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(MessageHandler(filters.TEXT, save_master_id))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()




