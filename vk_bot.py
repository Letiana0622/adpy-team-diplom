from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from token_bot_vk import bot_token, token_user
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_find_users import VkBotFunc
import requests
from io import BytesIO
from vk_api.upload import VkUpload
from data_base import add_favorite, select_photo, select_user, select_user_count


token = bot_token

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
upload = VkUpload(vk)

number_photo = 1


def photo_switch(count_photo, number_global):
    persons_count = select_user_count()
    if (count_photo <= len(persons_count)) and (count_photo > 0):
        correct_number_photo = count_photo
    elif count_photo <= 1:
        correct_number_photo = len(persons_count)
        number_global = len(persons_count)
    elif count_photo > len(persons_count):
        correct_number_photo = 1
        number_global = 1
    return correct_number_photo, number_global


def keyboard_start():
    keyboard_main = VkKeyboard()
    keyboard_main.add_button('Hi', VkKeyboardColor.PRIMARY)
    keyboard_main.add_button('Photo', VkKeyboardColor.PRIMARY)
    keyboard_main.add_button('Find', VkKeyboardColor.PRIMARY)
    keyboard_main.add_button('Bye', VkKeyboardColor.PRIMARY)
    return keyboard_main


def keyboard_photo_vk():
    keyboard_photo = VkKeyboard(inline=True)
    keyboard_photo.add_button('Back', VkKeyboardColor.PRIMARY)
    keyboard_photo.add_button('Favorite', VkKeyboardColor.PRIMARY)
    keyboard_photo.add_button('Next', VkKeyboardColor.PRIMARY)
    return keyboard_photo


def write_msg(user_id, message, keyboard=None):
    parameter = {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7),
    }
    if keyboard != None:
        parameter['keyboard'] = keyboard.get_keyboard()
    else:
        parameter = parameter

    vk.method('messages.send', parameter)


def send_photo(user_id, owner_id, url_photo, access_key, keyboard=None):
    parameter = {
        'peer_id': user_id,
        'attachment': f'photo{owner_id}_{url_photo}_{access_key}',
        'random_id': randrange(10 ** 7),
    }

    if keyboard != None:
        parameter['keyboard'] = keyboard.get_keyboard()
    else:
        parameter = parameter
    vk.method('messages.send', parameter)


def data_research():
    master_user = VkBotFunc(token, token_user, event.user_id)
    find_params = master_user.user_info()
    sex_to_search = find_params['response'][0]['sex']
    home_town_to_search = find_params['response'][0]['city']['id']
    bdate_main = find_params['response'][0]['bdate'].split('.')
    bdate_to_search = bdate_main[2]
    master_user.get_users(sex_to_search, home_town_to_search, int(bdate_to_search))


def photo_upload(url):
    img = requests.get(url).content
    f = BytesIO(img)

    response = upload.photo_messages(f)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key


def find_user_info(correct_user_id):
    params = {'access_token': token, 'v': '5.131', 'user_ids': correct_user_id, 'fields': 'domain'}
    url_get = 'https://api.vk.com/method/users.get'
    response = requests.get(url_get, params)
    return response.json()


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text.lower()
            keyboard_start()
            if request == 'hi':
                write_msg(event.user_id, f'Хай, {event.user_id}')
            elif request == 'bye':
                write_msg(event.user_id, 'Пока((')
            elif request == 'photo':
                start_photo = 1
                correct_photo = photo_switch(number_photo, number_photo)[0]
                number_photo = photo_switch(number_photo, number_photo)[1]
                person_id = select_user(start_photo)
                nickname = find_user_info(person_id)
                write_msg(event.user_id, f'{nickname["response"][0]["first_name"]} {nickname["response"][0]["last_name"]}')
                write_msg(event.user_id, f'https://vk.com/{nickname["response"][0]["domain"]}')
                new_photo = photo_upload(select_photo(start_photo)[0][0])
                send_photo(event.user_id, new_photo[0], new_photo[1], new_photo[2], keyboard_photo_vk())
            elif request == 'next':
                number_photo += 1
                correct_photo = photo_switch(number_photo, number_photo)[0]
                number_photo = photo_switch(number_photo, number_photo)[1]
                person_id = select_user(number_photo)
                nickname = find_user_info(person_id)
                write_msg(event.user_id, f'{nickname["response"][0]["first_name"]} {nickname["response"][0]["last_name"]}')
                write_msg(event.user_id, f'https://vk.com/{nickname["response"][0]["domain"]}')
                new_photo = photo_upload(select_photo(number_photo)[0][0])
                send_photo(event.user_id, new_photo[0], new_photo[1], new_photo[2], keyboard_photo_vk())
            elif request == 'back':
                number_photo -= 1
                correct_photo = photo_switch(number_photo, number_photo)[0]
                number_photo = photo_switch(number_photo, number_photo)[1]
                person_id = select_user(number_photo)
                nickname = find_user_info(person_id)
                write_msg(event.user_id, f'{nickname["response"][0]["first_name"]} {nickname["response"][0]["last_name"]}')
                write_msg(event.user_id, f'https://vk.com/{nickname["response"][0]["domain"]}')
                new_photo = photo_upload(select_photo(number_photo)[0][0])
                send_photo(event.user_id, new_photo[0], new_photo[1], new_photo[2], keyboard_photo_vk())
            elif request == 'favorite':
                add_favorite(person_id)
                write_msg(event.user_id, 'Успешно добавлено в избранное')
            elif request == 'find':
                data_research()
                write_msg(event.user_id, 'Нашел подходящих людей')
            else:
                write_msg(event.user_id, 'Не поняла вашего ответа. Вот список команд', keyboard_start())
