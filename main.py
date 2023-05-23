import telebot
import config
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
from time import sleep
import threading

bot = telebot.TeleBot(config.Token)
m = []
date = ""
time = ""
notif = ""
mes = ""
hour = 12
minute = 30


@bot.message_handler(commands=['start'])
def start(message):
    global mes
    mes = message
    buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("✏Задать Напоминание✏")
    btn2 = KeyboardButton("📒Список Напоминаний📒")
    buttons.add(btn1, btn2)
    bot.send_sticker(message.chat.id, open("stickers/Welcome.webp", 'rb'))
    bot.send_message(message.chat.id, "Привет! Меня зовут Wit\nМой создатель: [Rushan Shafeev](https://shafeev.site)\nЯ буду помогать тебе не забывать о важных вещах.\nЗадай своё первое напоминание!", parse_mode='Markdown', reply_markup=buttons)


@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == "✏Задать Напоминание✏":
        # bot.send_message(message.chat.id, "Введите дату в которое должно прийти уведомление в формате DD.MM.YY")
        # bot.register_next_step_handler(message, get_date)
        bot.send_message(message.chat.id, 'Введи Название Напоминания')
        bot.register_next_step_handler(message, get_notif)
    elif message.text == "📒Список Напоминаний📒":
        bot.send_sticker(message.chat.id, open("stickers/tasks.webp", 'rb'))
        bot.send_message(message.chat.id,f"📚Все Напоминания📚")
        if not len(m):
            bot.send_message(message.chat.id, f"💭Пока тут пусто!💭")
        else:
            for i in m:
                bot.send_message(message.chat.id, f"{i[0]} - {i[1]}")
    else:
        bot.send_sticker(message.chat.id, open("stickers/error.webp", 'rb'))
        bot.send_message(message.chat.id,
                         f"🚫Я не знаю, что ответить на это!🚫\n🔍Введи команду /help для просмотра моих команд🔍")


def get_notif(message):
    global notif
    notif = message.text
    # date = message.text.split('.')
    # bot.send_message(message.chat.id, 'Введите время в которое должно прийти уведомление', reply_markup=create_clock())
    bot.send_message(message.chat.id, "🗓 Введи дату в формате DD.MM.YYYY 🗓")
    bot.register_next_step_handler(message, get_date)


def get_date(message):
    global date
    # proverka date
    date = message.text.split('.')
    try:
        if (datetime(int(date[-1]), int(date[-2]), int(date[-3])) - datetime.now()).days < -1:
            bot.send_sticker(message.chat.id, open("stickers/incorrect.webp", 'rb'))
            bot.send_message(message.chat.id, "⚠Неверно Введена дата⚠\n❗Дата напоминания не может быть прошедшей❗")
            return
    except:
        bot.send_sticker(message.chat.id, open("stickers/incorrect.webp", 'rb'))
        bot.send_message(message.chat.id, "⚠Неверно Введена дата⚠\n❗Введи дату в формате DD.MM.YYYY❗")
        return
    # bot.send_message(message.chat.id, 'Введите Название Уведомления')
    # bot.register_next_step_handler(message, get_notif)
    bot.send_message(message.chat.id, '⏰Введи время в ввиде HH:MM⏰')
    bot.register_next_step_handler(message, get_time)


def get_time(message):
    global hour, minute
    hour, minute = map(str, message.text.split(':'))
    try:
        if (timedelta(hours=int(hour), minutes=int(minute)) - timedelta(hours=datetime.now().hour, minutes=datetime.now().minute)).days < 0:
            bot.send_sticker(message.chat.id, open("stickers/incorrect.webp", 'rb'))
            bot.send_message(message.chat.id, "⚠Неверно Введено время⚠\n❗Время напоминания не может быть прошедшим❗")
            return
    except:
        bot.send_sticker(message.chat.id, open("stickers/incorrect.webp", 'rb'))
        bot.send_message(message.chat.id, "⚠Неверно Введено время⚠\n❗Введи время в формате HH:MM❗")
        return
    # notif = message.text
    if len(str(hour)) == 1:
        hour = f"0{hour}"
    if len(str(minute)) == 1:
        minute = f"0{minute}"
    m.append([f"{hour}:{minute} - {date[-3]}.{date[-2]}.{date[-1]}", notif])
    bot.send_message(message.chat.id, f'✉Напоминание на {date[-3]}.{date[-2]}.{date[-1]} {hour}:{minute}, с названием {notif}✉\n✅Добавлено✅')


def send_notif(text):
    bot.send_sticker(mes.chat.id, open("stickers/notif.webp", 'rb'))
    bot.send_message(mes.chat.id, f"🔔 Тебе Пришло Напоминание! 🔔\n📍 {text} 📍")


def reminder():
    global m
    ar = m.copy()
    for i in range(len(ar)):
        print(datetime.now().strftime('%H:%M - %d.%m.%Y'), m[i][0])
        print(datetime.now().strftime('%H:%M - %d.%m.%Y') == m[i][0])
        if datetime.now().strftime('%H:%M - %d.%m.%Y') == m[i][0]:
            print("message sended")
            send_notif(m[i][1])
            del ar[i]
    m = ar.copy()


def checker():
    while True:
        reminder()
        sleep(31)


# def create_clock(m=None, user=None):
#     global hour, minute
#     keyboard = []
#     now = datetime.now()
#     utc = 0
#     if not hour:
#         hour = now.hour
#         if hour > 12:
#             m = "pm"
#         else:
#             m = "am"
#         if hour > 12:
#             hour -= 12
#         if hour + utc > 12:
#             hour += utc - 12
#         elif hour + utc < 0:
#             hour += utc + 12
#         else:
#             hour += utc
#
#     row = []
#     row.append(InlineKeyboardButton("↑", callback_data="PLUS-HOUR"))
#     row.append(InlineKeyboardButton("↑", callback_data="PLUS-MINUTE"))
#     keyboard.append(row)
#
#     row = []
#     row.append(InlineKeyboardButton(str(hour), callback_data="data_ignore"))
#     row.append(InlineKeyboardButton(str(minute), callback_data="data_ignore"))
#     keyboard.append(row)
#
#     row = []
#     row.append(InlineKeyboardButton("↓", callback_data="MINUS-HOUR"))
#     row.append(InlineKeyboardButton("↓", callback_data="MINUS-MINUTE"))
#     keyboard.append(row)
#
#     row = []
#     row.append(InlineKeyboardButton("OK", callback_data="OK"))
#     keyboard.append(row)
#     return InlineKeyboardMarkup(keyboard)

#
# @bot.callback_query_handler(func=lambda call: True)
# def handle(call):
#     global hour, minute
#     if call.data == "PLUS-HOUR":
#         if hour + 1 > 24:
#             hour = 0
#         else:
#             hour += 1
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=create_clock(),
#                               text=f'Введите время в которое должно прийти уведомление {hour}:{minute}')
#     elif call.data == "MINUS-HOUR":
#         if hour - 1 < 0:
#             hour = 24
#         else:
#             hour -= 1
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=create_clock(),
#                               text=f'Введите время в которое должно прийти уведомление {hour}:{minute}')
#     elif call.data == "PLUS-MINUTE":
#         if minute + 5 > 55:
#             minute = 0
#         else:
#             minute += 5
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=create_clock(),
#                               text=f'Введите время в которое должно прийти уведомление {hour}:{minute}')
#     elif call.data == "MINUS-MINUTE":
#         if minute - 5 < 0:
#             minute = 55
#         else:
#             minute -= 5
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=create_clock(),
#                               text=f'Введите время в которое должно прийти уведомление {hour}:{minute}')
#     elif call.data == "OK":
#         bot.register_next_step_handler(mes, get_time(mes))
#
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=None,
#                               text=f'Введите время в которое должно прийти уведомление {hour}:{minute}')


x = threading.Thread(target=checker)
x.start()

print("Бот Запущен!...")
bot.polling(none_stop=True)
print("Бот Отключен!...")

