import telebot
from telebot import types
from telebot.types import Message
from geopy.distance import vincenty

DACHA ={
    'title': 'ДАЧА У ОЛЕГА',
    'lonm': 104.244784,
    'latm': 52.399846,
    'address': 'г. Иркутск, СНТ "Веселое", ул. Земляничная, д.228'
        }

USERS={1: 1}
poset=[]
bot=telebot.TeleBot('969319994:AAETSx5cNFDCwJy7Rz7ef4R5Ip137da2zTk')

markup_menu=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1,one_time_keyboard=True )
btn_address=types.KeyboardButton('Узнать адрес дачи',request_location=True)
btn_payment=types.KeyboardButton('Способы оплаты и цена')
btn_see_pay=types.KeyboardButton('Посмотреть, кто уже тут')
markup_menu.add(btn_address,btn_payment,btn_see_pay)

markup_menu_back=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1,one_time_keyboard=True )
btn_menu_back=types.KeyboardButton('<- Назад')
markup_menu_back.add(btn_menu_back)

markup_inline_payment=types.InlineKeyboardMarkup(row_width=1)
btn_in_cash=types.InlineKeyboardButton('Наличные при встрече', callback_data='cash')
btn_in_card=types.InlineKeyboardButton('Перевод на карту Сбербанка', callback_data='card')
markup_inline_payment.add(btn_in_cash,btn_in_card)

markup_inline_back=types.InlineKeyboardMarkup(row_width=1)
btn_back=types.InlineKeyboardButton('<- Назад', callback_data='back')
markup_inline_back.add(btn_back)

markup_inline_payment_true=types.InlineKeyboardMarkup(row_width=1)
btn_true=types.InlineKeyboardButton('Я Оплатил', callback_data='true')
markup_inline_payment_true.add(btn_true,btn_back)

@bot.message_handler(commands=['start','help'])
def command_handler(message: Message):
    if message.text=='/start':
        if message.from_user.id in USERS:
            bot.send_message(message.chat.id,'И снова привет, ' + message.from_user.first_name + '!' + "\nЖми /help")
        else:
            poset.append(message.from_user.first_name)
            USERS[message.from_user.id]="+-"
            bot.send_message(message.chat.id,'Привет, '+ message.from_user.first_name + '!' + "\nЧтобы узнать поподробнее нажми\n /help")
            print(USERS)
    elif message.text=='/help':
        bot.send_message(message.chat.id, 'Этот бот для тех, кто едет тусить по полной!\nТут ты можешь понажимать на кнопки и узнать подробнее обо всем!\nА так же сразу оплатить пропитание!', reply_markup=markup_menu)
    else:
        bot.send_message(message.chat.id, 'Я еще не знаю такой команды(', reply_markup=markup_menu)

@bot.message_handler(func=lambda message: True)
def handler(message: Message):
    if message.text=='Способы оплаты и цена':
        bot.send_message(message.chat.id, 'Для вас доступны следующие способы оплаты', reply_markup=markup_inline_payment)
        bot.send_message(message.chat.id, 'Чтобы вернуться в главное меню нажмите "<- Назад"',
                         reply_markup=markup_menu_back)
    elif message.text=='Посмотреть, кто уже тут':
        if not poset:
            bot.send_message(message.chat.id, "Пока никого нет!", reply_markup=markup_menu_back)
        else:
            str=""
            for i in range(len(poset)):
                str+=poset[i]+"\n"
            bot.send_message(message.chat.id, str, reply_markup=markup_menu_back)
    elif message.text=='<- Назад':
        bot.send_message(message.chat.id, 'Нажми другую кнопку!', reply_markup=markup_menu)
    else:
        bot.send_message(message.chat.id, message.text, reply_markup=markup_menu)

@bot.message_handler(content_types=['location'])
def magazin_location(message):
    lon=message.location.longitude
    lat=message.location.latitude

    result = vincenty((DACHA['latm'],DACHA['lonm']),(lat,lon))

    bot.send_message(message.chat.id,'Место отдыха ', reply_markup=markup_menu_back)
    bot.send_venue(message.chat.id, DACHA['latm'],DACHA['lonm'],DACHA['title'],DACHA['address'])

@bot.callback_query_handler(func=lambda call:True)
def call_back_payment(call):
    if call.data == 'cash':
        bot.send_message(call.message.chat.id, text= """
        Наличная оплата производится в рублях, непосредственно на даче
        """, reply_markup=markup_inline_back)
    if call.data == 'card':
        bot.send_message(call.message.chat.id, text="""
Номер карты: 4276 3100 2188 9763
Владелец: Олег Дмитриевич С.
        """, reply_markup=markup_inline_payment_true)
    if call.data == 'true':
        print(call)
        print(call.from_user.id)
        if USERS[call.from_user.id][1]=='-':
            USERS[call.from_user.id]="++"
            for i in range(len(poset)):
                if poset[i]==call.from_user.first_name:
                    poset[i]+=' +'
            bot.send_message(call.message.chat.id, text="""
                Мои поздравления, вы в списке!
                        """, reply_markup=markup_menu)
        else:
            bot.send_message(call.message.chat.id, text="""
                Вы уже оплатили!
                        """, reply_markup=markup_menu)
    if call.data == 'back':
        bot.send_message(call.message.chat.id, text='Попробуй другое!',reply_markup=markup_inline_payment)
bot.polling()