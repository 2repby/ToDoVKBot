import vk_api
import pymysql
import os
import random
import threading
import dateparser
import re
from timefhuman import timefhuman
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('token')
vk = vk_api.VkApi(token=token)
from vk_api.longpoll import VkLongPoll, VkEventType
longpoll = VkLongPoll(vk)

host = os.getenv('host')
port = os.getenv('port')
user = os.getenv('user')
password = os.getenv('password')
database = os.getenv('database')
charset = os.getenv('charset')

print(dateparser.parse('через месяц в 12:15'))

connection = pymysql.connect(host=host, user=user, password=password, db=database, charset=charset, cursorclass=pymysql.cursors.DictCursor)

# Таймер для выполнения
#
# def (i):
#     threading.Timer(2.0, printit, [i+1]).start()
#     vk.method('messages.send', {'user_id': 4591935, 'message': 'Привет ' + str(i),
#                                 'random_id': random.randint(0, 1000)})
#     print("Hello ", i)
#
# printit(1)

# Основной цикл программы
for event in longpoll.listen():
    print(event.type)
    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            user = vk.method("users.get", {"user_ids": event.user_id,
                                           "fields": "photo_id, verified, sex, bdate, city, country, home_town, "
                                                     "has_photo, photo_50, photo_100, photo_200_orig, photo_200, "
                                                     "photo_400_orig, photo_max, photo_max_orig, online, domain, "
                                                     "has_mobile, contacts, site, education, universities, schools, "
                                                     "status, last_seen, followers_count, occupation, nickname, "
                                                     "relatives, relation, personal, connections, exports, activities, "
                                                     "interests, music, movies, tv, books, games, about, quotes, "
                                                     "can_post, can_see_all_posts, can_see_audio, "
                                                     "can_write_private_message, can_send_friend_request, "
                                                     "is_favorite, is_hidden_from_feed, timezone, screen_name, "
                                                     "maiden_name, crop_photo, is_friend, friend_status, career, "
                                                     "military, blacklisted, blacklisted_by_me, "
                                                     "can_be_invited_group"})[0]
            print(user["first_name"])
            cur = connection.cursor()
            # Выбираем из таблицы users пользователя, отправивишего сообщение
            cur.execute("SELECT * FROM users WHERE vk_id=" + str(event.user_id))
            # Получаем количество выбранных строк (0 или 1)
            n = cur.rowcount
            cur.close()
            # Если пользователя нет в таблице
            if n == 0:
                cur = connection.cursor()
                # Добавляем пользователя в таблицу
                cur.execute("INSERT INTO users (first_name, last_name, vk_id, login) VALUES (%s, %s, %s, %s)",
                            (user["first_name"], user["last_name"], user["id"], user['screen_name']))
                connection.commit()
                cur.close()
            # Получение id пользователя - добавленного или имеющегося
            cur = connection.cursor()
            cur.execute("SELECT * FROM users WHERE vk_id=" + str(user["id"]))
            rows = cur.fetchall()
            for row in rows:
                id_user = row['id']
            print(id_user)
            vk.method('messages.send', {'peer_id': event.user_id, 'message': 'Привет, ' + user["first_name"] + '! Я бот!',
                                        'random_id': random.randint(0, 1000)})
            # Текст сообщения пользователя
            request = str(event.text)
            # Массив элементов команды
            params = re.split(";|,",request)
            if params[0] in {'задача', 'task', 'add', 'добавить'}:
                cur = connection.cursor()
                # Добавляем задачу в таблицу
                cur.execute("INSERT INTO tasks (name, deadline, tags, id_user) VALUES (%s, %s, %s, %s)",
                            (params[1], params[2], params[3], id_user))
                connection.commit()
                cur.close()

