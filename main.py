import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import datetime as dt


bot = telebot.TeleBot('5163172103:AAHmUeEMMw_NrG8TiY-ZZbasxjs806DAVRc')
markup = types.ReplyKeyboardMarkup()
itembtngst = types.KeyboardButton('/gst')
itembtnhelp = types.KeyboardButton('/help')
itembtna = types.KeyboardButton('/id')
itembtny = types.KeyboardButton('/file')
markup.row(itembtngst, itembtnhelp, itembtny, itembtna)
bot.send_message(704213045, "Выберете действие:", reply_markup=markup)
names = []
dates = []
links = []
htm = ''
images = []
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
    if message.text == "/gst":
        for i in range(len(names)):
            bot.send_message(message.from_user.id, f'{names[i]}\n{dates[i]}\nhttps://itch.io{links[i]}')
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "/gst - выводит даты начала ближайших game jams")
        bot.send_message(message.from_user.id, "/id - выводит id пользователя")
        bot.send_message(message.from_user.id, "/file - отправляет фото с моим именем")
    elif message.text == "/id":
        bot.send_message(message.from_user.id, message.chat.id)
    elif message.text == "/file":
        photo = open('res.jpg', 'rb')
        bot.send_photo(message.from_user.id, photo)
        photo.close()
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")



bot.polling(none_stop=True, interval=0)
