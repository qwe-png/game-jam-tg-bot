import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import datetime as dt
import sqlite3
import random


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

con.close()

for item in result:
    print(item[0])


names = []
dates = []
links = []
htm = ''
images = []
cou = 0
phs = []
idsph = []
flood = []
id_otvet = 0
id_pay = 0


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
    global phs, cou, id_otvet, idsph, id_pay
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
        daten = dt.datetime.now()
        daten = str(daten)
        code = random.randint(10000, 99999)
        bot.send_message(message.from_user.id, "отправьте фото с платежом {}".format(code))


        @bot.message_handler(content_types=["photo"])
        def photo(message):
            idphoto = message.photo[0].file_id
            bot.send_message(704213045, "кто-то произвел оплату, всего непрочитанных: {}".format(cou))
            bot.send_message(message.from_user.id, "фото отправленно")
            idsph.append("{}, {}, {}".format(code, daten, message.from_user.id))
            phs.append(idphoto)
            print(idphoto)
            sqlite_connection = sqlite3.connect('tg_bot')
            cursor = sqlite_connection.cursor()
            sqlite_insert_with_param = """INSERT INTO dateofpays
                                  (tg_id, date, code, photo_id)
                                  VALUES (?, ?, ?, ?);"""
            data_tuple = (message.from_user.id, str(daten), code, idphoto)
            cursor.execute(sqlite_insert_with_param, data_tuple)
            sqlite_connection.commit()
            cursor.close()
        cou += 1

    elif message.text == "/check":
        if message.from_user.id == 704213045:
            if phs:
                for i in range(len(phs)):
                    bot.send_photo(704213045, phs[i], idsph[i], reply_markup=markup_c)
            else:
                bot.send_message(704213045, "новых фотографий не было")
        else:
            bot.send_message(message.from_user.id, "отказано в доступе")



    elif message.text == "/clear":
        if message.from_user.id == 704213045:
            phs = []
            bot.send_message(704213045, "готово")
        else:
            bot.send_message(message.from_user.id, "отказано в доступе")



    elif message.text.split()[0] == "/answer":
        try:
            m = message.text.split()
            id_otvet = m[1]
            bot.send_message(message.from_user.id, "введите сообщение")
            bot.register_next_step_handler(message, otvet)
        except IndexError:
            bot.send_message(message.from_user.id, "неверный айди")

    elif message.text == "/test":
        pass

    elif message.text.split()[0] == "/confirm":
        try:
            m = message.text.split()
            id_pay = m[1]
            if message.from_user.id == 704213045:
                sqlite_connection = sqlite3.connect('tg_bot')
                cursor = sqlite_connection.cursor()
                cursor.execute("""INSERT INTO data_telega (id_vip_1) VALUES ({})""".format(id_pay))
                sqlite_connection.commit()
                cursor.close()
                bot.send_message(704213045, "confd {}".format(id_pay))
                bot.send_message(id_pay, "ваша оплата подтверждена")
            else:
                bot.send_message(message.from_user.id, "отказано в доступе")
        except IndexError:
            bot.send_message(message.from_user.id, "неверный айди")


    elif message.text.split()[0] == "/confirm":
        try:
            m = message.text.split()
            id_pay = m[1]
            if message.from_user.id == 704213045:
                sqlite_connection = sqlite3.connect('tg_bot')
                cursor = sqlite_connection.cursor()
                cursor.execute("""INSERT INTO data_telega (id_vip_1) VALUES ({})""".format(id_pay))
                sqlite_connection.commit()
                cursor.close()
                bot.send_message(704213045, "confd {}".format(id_pay))
                bot.send_message(id_pay, "ваша оплата подтверждена")
            else:
                bot.send_message(message.from_user.id, "отказано в доступе")
        except IndexError:
            bot.send_message(message.from_user.id, "неверный айди")


    elif message.text.split()[0] == "/reject":
        try:
            m = message.text.split()
            id_pay = m[1]
            if message.from_user.id == 704213045:
                bot.send_message(704213045, "not confd {}".format(id_pay))
                bot.send_message(id_pay, "платеж не подтвержден, отправьте сообщение на 704213045"
                                         " с кодом указанном при оплате (/answer 704213045 [сообщение])")
                bot.register_next_step_handler(message, confirm)
            else:
                bot.send_message(message.from_user.id, "отказано в доступе")
        except IndexError:
            bot.send_message(message.from_user.id, "неверный айди")


    elif message.text == "/bd":
        if message.from_user.id == 704213045:
            sqlite_connection = sqlite3.connect('tg_bot')
            cursor = sqlite_connection.cursor()
            result = cursor.execute("""
            SELECT * FROM dateofpays
            """).fetchall()
            cursor.close()
            for item in result:
                stroka = str(str(item[1]) + " " + str(item[2]) + " " + str(item[3]))
                bot.send_photo(704213045, item[4], stroka)
        else:
            bot.send_message(message.from_user.id, "отказано в доступе")


    elif message.text.split()[0] == "/cl_bd":
        try:
            if message.from_user.id == 704213045:
                sqlite_connection = sqlite3.connect('tg_bot')
                cursor = sqlite_connection.cursor()
                result = cursor.execute(f"""
                            DELETE FROM dateofpays WHERE id = {message.text.split()[1]}
                            """).fetchall()
                sqlite_connection.commit()
                cursor.close()
            else:
                bot.send_message(message.from_user.id, "отказано в доступе")
        except IndexError:
            bot.send_message(message.from_user.id, "неверный айди")
            
            
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
        flood.append(id_pay)
        bot.send_message(id_pay, "вы были отправлены в список нарушителей за неверное фото,"
                                 "если это было сделано по ошибке напишите на айди 704213045 "
                                 "(/answer 704213045 [сообщение])")
    elif message.text == "no":
        pass


bot.polling(none_stop=True, interval=0)


# sqlite_connection = sqlite3.connect('tg_bot')
# cursor = sqlite_connection.cursor()
# result = cursor.execute("""
#             SELECT * FROM dateofpays
#             """).fetchall()
# sqlite_connection.commit()
# cursor.close()


# if message.from_user.id == 704213045:
#
# else:
#     bot.send_message(message.from_user.id, "отказано в доступе")

# try:
#
# except IndexError:
#     bot.send_message(message.from_user.id, "неверный айди")
