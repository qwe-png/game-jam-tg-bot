import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import datetime as dt
import sqlite3


bot = telebot.TeleBot('5163172103:AAHmUeEMMw_NrG8TiY-ZZbasxjs806DAVRc')
# 704213045

markup = types.ReplyKeyboardMarkup()
itembtngst = types.KeyboardButton('/gst')
itembtnhelp = types.KeyboardButton('/help')
itembtna = types.KeyboardButton('/id')
itembtny = types.KeyboardButton('/file')
itembtno = types.KeyboardButton('/about us')

markup_c = types.ReplyKeyboardMarkup()
itembtnyes = types.KeyboardButton('yes')
itembtnno = types.KeyboardButton('no')
markup_c.add(itembtnyes, itembtnno)

markup.add(itembtngst, itembtnhelp, itembtny, itembtna, itembtno)
con = sqlite3.connect("tg_bot", check_same_thread=False)
cur = con.cursor()

result = cur.execute("""
SELECT t.id_vip_1 FROM data_telega AS t
""").fetchall()

for item in result:
    print(item[0])


names = []
dates = []
links = []
htm = ''
images = []
cou = 1
phs = []
id_otvet = 0


url = 'https://itch.io/jams'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
quotes = soup.find_all('div', class_="conversion_link_widget")
dat = soup.find_all('span', class_="date_countdown")
imag = soup.find_all('div', class_='jam_cover')
lin = soup.find_all(['div'], class_="conversion_link_widget")
for i in imag:
    images.append(str(i).split('data-background_image="')[1].split('"')[0])
for i in quotes:
    if i.text != '':
        names.append(i.text)
for i in dat:
    if 'title' in str(i):
        ong = ''
    else:
        ong = 'Ongoing, ends: '
    time = i.text[:-1].split('T')
    datet = list(map(int, time[0].split('-')))
    my_date = dt.date(datet[0], datet[1], datet[-1])
    datet = list(map(int, time[1].split(':')))
    my_time = dt.time(datet[0], datet[1], datet[-1])
    my_datetime = dt.datetime.combine(my_date, my_time)
    delta_time1 = dt.timedelta(hours=3)
    dates.append(ong + str(my_datetime + delta_time1))
for i in lin:
    links.append(str(i).split('a href="')[1].split('"')[0])
links = links[::2]


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global phs, cou, id_otvet
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Вас приветствует телеграм бот Game Jams Bot."
                                               " Напишите /help для продолжения", reply_markup=markup)


    elif message.text == "/gst":
        for i in range(len(names)):
            bot.send_message(message.from_user.id, f'{names[i]}\n{dates[i]}\nhttps://itch.io{links[i]}')


    elif message.text == "/help":
        bot.send_message(message.from_user.id, "/gst - выводит даты начала ближайших game jams \n"
                                               "/id - выводит id пользователя \n"
                                               "/file - отправляет фото \n"
                                               "/about us - информация о разработчиках\n"
                                               "/support - отправить сообщение разработичку\n")


    elif message.text == "/id":
        bot.send_message(message.from_user.id, "/check {}", format(message.chat.id))


    elif message.text == "/file":
        photo = open('res.jpg', 'rb')
        bot.send_photo(message.from_user.id, photo)
        photo.close()


    elif message.text == "/about us":
        photo = open('res.jpg', 'rb')
        bot.send_photo(message.from_user.id, photo, "Мы команда учеников яндекс лицея и это телеграм бот нашего"
                                                    " проекта. Здесь вы можете узнать его возможности и ими "
                                                    "воспользоваться.")
        photo.close()


    elif message.text == "/support":
        bot.send_message(message.from_user.id, "Напишите ваше сообщение для разработчика")
        bot.register_next_step_handler(message, ans)


    elif message.text == "/payment":
        bot.send_message(message.from_user.id, "отправьте фото с платежом")

        @bot.message_handler(content_types=["photo"])
        def photo(message):
            idphoto = message.photo[0].file_id
            bot.send_message(704213045, "кто-то произвел оплату, всего непрочитанных: {}".format(cou))
            bot.send_message(message.from_user.id, "фото отправленно")
            phs.append(idphoto)

        cou += 1

    elif message.text == "/check 704213045":
        if phs:
            for i in range(len(phs)):
                bot.send_photo(704213045, phs[i], reply_markup=markup_c)
                bot.register_next_step_handler(message, confirm)
        else:
            bot.send_message(704213045, "новых фотографий не было")


    elif message.text == "/clear 704213045":
        phs = []
        bot.send_message(704213045, "готово")


    elif message.text.split()[0] == "/answer":
        try:
            m = message.text.split()
            id_otvet = m[1]
            bot.send_message(message.from_user.id, "введите сообщение")
            bot.register_next_step_handler(message, otvet)
        except IndexError:
            bot.send_message(message.from_user.id, "неверный айди")

    elif message.text == "/test":
        bot.register_next_step_handler(message, confirm)


    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


def ans(message):
    bot.send_message(704213045, "сообщение от пользователя: \"{}\". Его айди - {}".format(message.text,
                                                                                          message.from_user.id))
    bot.send_message(message.from_user.id, "сообщение отправлено")

    # добавить функцию получении новых фоторафий и отправление уведолмения при получении


def otvet(message):
    global id_otvet
    bot.send_message(int(id_otvet), "вам пришло сообщение от {}".format(message.from_user.id))
    bot.send_message(message.from_user.id, "сообщение отправлено {}".format(id_otvet))
    bot.send_message(int(id_otvet), message.text)


def confirm(message):
    if message.text == "yes":
        iiddd = message.from_user.id
        cur.execute("""INSERT INTO data_telega (id_vip_1) VALUES ({})""".format(iiddd))
        con.commit()

        bot.send_message(704213045, "confd")
    elif message.text == "no":
        bot.send_message(704213045, "not confd")


bot.polling(none_stop=True, interval=0)

