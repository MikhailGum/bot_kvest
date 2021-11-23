import telebot
from telebot import types
import sqlite3
import config_bot #Импорт файла конфигурации
import requests, re
import pandas as pd
from bs4 import BeautifulSoup
import time
import functions_bot

# Бот предлагает проити тестирование или квест
voprosi = pd.read_excel('test_voprosi.xlsx', sheet_name='Tests')
results = pd.read_excel('test_voprosi.xlsx', sheet_name='Results')
nomer_otveta = []
var_otveta = ['Var_1','Var_2','Var_3','Var_4','Var_5','Var_6']
nomer_voprosa = 0
sum_ballov = 0
def f_nomer_voprosa(message):
    try:
        #Открываем базу данных
        conn = sqlite3.connect('test_base.db')
        c = conn.cursor()
        user_n_id = message.chat.id
        request = """select max(user_vopros) from result_otvet where result_otvet.user_id = 
                
                """ + str(user_n_id)
        c.execute(request)
        max_nomer = c.fetchall()[0][0]
        # print(max_nomer)
        nomer_voprosa = max_nomer + 1
        print('f_nomer_voprosa - try - nomer_voprosa =' + str(nomer_voprosa))
    except:
        nomer_voprosa = 0
        print('f_nomer_voprosa - except - nomer_voprosa =' + str(nomer_voprosa))
    return nomer_voprosa

def get_test(message):
    # global nomer_voprosa
    nomer_voprosa = f_nomer_voprosa(message)
    if nomer_voprosa <=18:
        cleanedList = [x for x in list(voprosi.loc[nomer_voprosa])[2:] if str(x) != 'nan']
        keyboard_test = types.InlineKeyboardMarkup(); #наша клавиатура
        nomer = 1
        for var in cleanedList:
            callback_text = 'Var_' + str(nomer)
            nomer +=1
            key_test = types.InlineKeyboardButton(text=var, callback_data=callback_text); #кнопка «Get_text»
            keyboard_test.add(key_test);
        bot.send_message(message.chat.id, text=voprosi.loc[nomer_voprosa]['vopros'], reply_markup=keyboard_test)
    elif nomer_voprosa > 18: #20
        bot.register_next_step_handler(message, get_result(message))    
    # nomer_voprosa += 1
    # print(message)
    # print('callback_text - ' + callback_text)


def get_result(message): # Нужно переделать под базуданных и сделать уникальными записи ответов, чтобы
# не было разных ответов одного пользователя на один вопрос. Нужно сформировать список ответов из базы 
    global sum_ballov #, nomer_otveta, nomer_voprosa
    try:
        #Открываем базу данных
        conn = sqlite3.connect('test_base.db')
        c = conn.cursor()
        user_n_id = message.chat.id
        request = """select user_otvet from result_otvet where result_otvet.user_id = 
                
                """ + str(user_n_id)
        c.execute(request)
        nomer_otveta = c.fetchall()
        print('get_result - try - nomer_otveta =' + str(nomer_otveta))
    except:
        print('get_result - except - nomer_otveta =')
    print('Количество ответов - ' + str(len(nomer_otveta)))
    for row in range(len(nomer_otveta)):
        print(str(results.loc[row][nomer_otveta[row][0]]))
        sum_ballov += results.loc[row][nomer_otveta[row][0]]
    bot.send_message(message.chat.id, text='Сумма баллов - ' + str(sum_ballov))
    if sum_ballov <= 14:
        bot.send_message(message.chat.id, text='Если сумма набранных баллов 14 и менее, то данный человек \
считается человеком со слабой волей.')
    if sum_ballov >= 15 and sum_ballov <= 25:
        bot.send_message(message.chat.id, text='При сумме баллов от 15 до 25 характер и воля человека \
считаются достаточно твердыми, а поступки в основном реалистичными и взвешенными.')
    if sum_ballov >= 26 and sum_ballov <= 38:
        bot.send_message(message.chat.id, text='При общей сумме баллов от 26 до 38 характер человека и \
его воля считаются очень твердыми, а его поведение в большинстве случаев — достаточно \
ответственным. Есть, правда, опасность увлечения силой воли с целью самолюбования.')
    if sum_ballov >= 39:
        bot.send_message(message.chat.id, text='При сумме баллов выше 38 воля и характер человека считаются \
близкими к идеальнымЁ но иногда возникает сомнение в том, достаточно ли правильно и \
объективно человек себя оценил.')
    nomer_voprosa = 0
    sum_ballov = 0
    nomer_otveta = []
    message.from_user.id = message.chat.id # Меня id бота на id пользователя, в start id берётся из from_user
    bot.register_next_step_handler(message, start(message))


bot = telebot.TeleBot(config_bot.TOKEN)
print('Бот запущен!')

@bot.message_handler(commands=["start"])
def start(message):
    keyboard_start = types.InlineKeyboardMarkup(); #наша клавиатура
#    key_reg = types.InlineKeyboardButton(text='Регистрация', callback_data='reg'); #кнопка «Регистрация»
#    keyboard_start.add(key_reg); #добавляем кнопку в клавиатуру
    key_test = types.InlineKeyboardButton(text='Тест силы воли', callback_data='get_test'); #кнопка «Get_text»
    keyboard_start.add(key_test);
    question = 'Выберите необходимое действие';
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard_start)
    print('Start нажал - ' + str(message.from_user.id))

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # print(call)
    # print('callback_text - ' + call.data)
    global var_otveta
    if call.data == "get_test":
        print('Ответ get_test от - ' + str(call.from_user.id))
        get_test(call.message)
    elif call.data in var_otveta:
        # global nomer_otveta, nomer_voprosa
        nomer_voprosa = f_nomer_voprosa(call.message)
        # try:
        #     #Открываем базу данных
        #     conn = sqlite3.connect('test_base.db')
        #     c = conn.cursor()
        #     user_n_id = call.message.chat.id
        #     request = """select max(user_vopros) from result_otvet where result_otvet.user_id = 
                    
        #             """ + str(user_n_id)
        #     c.execute(request)
        #     max_nomer = c.fetchall()[0][0]
        #     print(max_nomer)
        #     nomer_voprosa = max_nomer + 1
        #     print('callback_worker - call.data in var_otveta - try - nomer_voprosa =' + str(nomer_voprosa))
        # except:
        #     nomer_voprosa = 0
        #     print('callback_worker - call.data in var_otveta - except - nomer_voprosa =' + str(nomer_voprosa))
 
        print('Ответ var от - ' + str(call.from_user.id))

        user_otvet = (call.from_user.id, nomer_voprosa, call.data) # Подготовим кортеж для записи в базу данных
        #Открываем базу данных
        conn = sqlite3.connect('test_base.db')
        c = conn.cursor()
        # Create table
        try:
            c.execute('''create table result_otvet
       (user_id integer, user_vopros integer, user_otvet text)''')
        except:
            pass
        # Insert a row of data
        c.execute("insert into result_otvet values (?,?,?)", user_otvet)
        # Save (commit) the changes
        conn.commit()
        c.close()

        # nomer_otveta.append(call.data)
        if nomer_voprosa <= 18: # 19
            bot.register_next_step_handler(call.message, get_test(call.message))
        elif nomer_voprosa == 19: #20
            bot.register_next_step_handler(call.message, get_result(call.message))
        # print(nomer_otveta)


if __name__ == '__main__':
    bot.infinity_polling()
