import telebot
import config
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
from time import sleep
import threading
import calendar

bot = telebot.TeleBot(config.Token)
m = []
time = ""
notif = ""
mes = ""
hour = 12
minute = 30
year = None
month = None
day = None


@bot.message_handler(commands=['start'])
def start(message):
    global mes
    mes = message
    buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("✏Задать Напоминание✏")
    btn2 = KeyboardButton("📒Список Напоминаний📒")
    buttons.add(btn1, btn2)
    bot.send_sticker(message.chat.id, open("stickers/Welcome.webp", 'rb'))
    bot.send_message(message.chat.id,
                     "Привет! Меня зовут Wit\nМой создатель: [Rushan Shafeev](https://shafeev.site)\nЯ буду помогать тебе не забывать о важных вещах.\nЗадай своё первое напоминание!",
                     parse_mode='Markdown', reply_markup=buttons)


@bot.message_handler(content_types=['text'])
def text(message):
    global year, month, mes
    mes = message
    if message.text == "✏Задать Напоминание✏":
        bot.send_message(message.chat.id, 'Введи Название Напоминания')
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
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
    bot.send_message(message.chat.id, "🗓 Ввыбери дату в календаре 🗓", reply_markup=create_calendar())


def get_time(message):
    global hour, minute, day, month
    hour, minute = map(str, message.text.split(':'))
    try:
        if month - datetime.now().month == 0:
            if int(day) - datetime.now().day == 0:
                if (timedelta(hours=int(hour), minutes=int(minute)) - timedelta(hours=datetime.now().hour, minutes=datetime.now().minute)).days < 0:
                    bot.send_sticker(message.chat.id, open("stickers/incorrect.webp", 'rb'))
                    bot.send_message(message.chat.id, "⚠Неверно Введено время⚠\n❗Время напоминания не может быть прошедшим❗")
                    return
    except ValueError:
        bot.send_sticker(message.chat.id, open("stickers/incorrect.webp", 'rb'))
        bot.send_message(message.chat.id, "⚠Неверно Введено время⚠\n❗Введи время в формате HH:MM❗")
        return

    if len(str(hour)) == 1:
        hour = f"0{hour}"
    if len(str(minute)) == 1:
        minute = f"0{minute}"
    if len(str(day)) == 1:
        day = f"0{day}"
    if len(str(month)) == 1:
        month = f"0{month}"
    m.append([f"{hour}:{minute} - {day}.{month}.{year}", notif])
    bot.send_message(message.chat.id, f'✉Напоминание на {day}.{month}.{year} {hour}:{minute}✉\n✉C Именем {notif}✉\n✅Добавлено✅')
    month = int(month[1:])


def send_notif(note):
    bot.send_sticker(mes.chat.id, open("stickers/notif.webp", 'rb'))
    bot.send_message(mes.chat.id, f"🔔 Тебе Пришло Напоминание! 🔔\n📍 {note} 📍")


def create_calendar():
    keyboard = list()
    keyboard.append([InlineKeyboardButton(f"{calendar.month_name[month]} {str(year)}",callback_data="IGNORE")])
    keyboard.append([InlineKeyboardButton(i, callback_data="IGNORE") for i in ["ПН","ВТ","СР","ЧТ","ПТ","СБ","ВС"]])
    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        keyboard.append([InlineKeyboardButton(" ", callback_data="IGNORE") if i == 0 else InlineKeyboardButton(str(i), callback_data=f"DAY{i}") for i in week])
    keyboard.append([InlineKeyboardButton(i[0], callback_data=i[1]) for i in [("<", "PREV-MONTH"), (" ", "IGNORE"), (">", "NEXT-MONTH")]])
    return InlineKeyboardMarkup(keyboard)


@bot.callback_query_handler(func=lambda call: True)
def process_calendar_selection(call):
    global year, month, day
    if call.data == "PREV-MONTH":
        if month - 1 < 1:
            month = 12
        else:
            month -= 1
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="🗓 Ввыбери дату в календаре 🗓", reply_markup=create_calendar())
    elif call.data == "NEXT-MONTH":
        if month + 1 > 12:
            month = 1
        else:
            month += 1
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="🗓 Ввыбери дату в календаре 🗓", reply_markup=create_calendar())
    elif call.data[:3] == "DAY":
        day = call.data[3:]
        if (datetime(int(year), int(month), int(day)) - datetime.now()).days < -1:
            bot.send_sticker(mes.chat.id, open("stickers/incorrect.webp", 'rb'))
            bot.send_message(mes.chat.id, "⚠Неверно Ввыбрана дата⚠\n❗Дата напоминания не может быть прошедшей❗")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="🗓 Ввыбери дату в календаре 🗓", reply_markup=None)
            bot.send_message(mes.chat.id, "🗓 Ввыбери дату в календаре 🗓", reply_markup=create_calendar())

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="🗓 Ввыбери дату в календаре 🗓", reply_markup=None)
        bot.send_message(mes.chat.id, '⏰Введи время в ввиде HH:MM⏰')
        bot.register_next_step_handler(mes, get_time)


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


x = threading.Thread(target=checker)
x.start()

print("Бот Запущен!...")
bot.polling(none_stop=True)
print("Бот Отключен!...")

