from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from token_bot_vk import bot_token, token_user
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_find_users import VkBotFunc
import requests
from io import BytesIO
from vk_api.upload import VkUpload


token = bot_token

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
upload = VkUpload(vk)

number_photo = 0


def photo_switch(count_photo, number_global):
    if (count_photo <= len(persons) - 1) and (count_photo >= 0):
        correct_number_photo = count_photo
    elif count_photo < 0:
        correct_number_photo = len(persons) - 1
        number_global = len(persons) - 1
    elif count_photo > len(persons) - 1:
        correct_number_photo = 0
        number_global = 0
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
    users_data = master_user.get_users(sex_to_search, home_town_to_search)
    users_selected = master_user.select_users(users_data, sex_to_search, home_town_to_search, int(bdate_to_search))
    photos_data = master_user.get_photos(users_selected)
    return photos_data


def photo_upload(url):
    img = requests.get(url).content
    f = BytesIO(img)

    response = upload.photo_messages(f)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key


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
                correct_photo = photo_switch(number_photo, number_photo)[0]
                new_photo = photo_upload(persons[correct_photo]['user_photo_data'][0])
                send_photo(event.user_id, new_photo[0], new_photo[1], new_photo[2], keyboard_photo_vk())
            elif request == 'next':
                number_photo += 1
                correct_photo = photo_switch(number_photo, number_photo)[0]
                number_photo = photo_switch(number_photo, number_photo)[1]
                new_photo = photo_upload(persons[correct_photo]['user_photo_data'][0])
                send_photo(event.user_id, new_photo[0], new_photo[1], new_photo[2], keyboard_photo_vk())
            elif request == 'back':
                number_photo -= 1
                correct_photo = photo_switch(number_photo, number_photo)[0]
                number_photo = photo_switch(number_photo, number_photo)[1]
                new_photo = photo_upload(persons[correct_photo]['user_photo_data'][0])
                send_photo(event.user_id, new_photo[0], new_photo[1], new_photo[2], keyboard_photo_vk())
            elif request == 'favorite':
                write_msg(event.user_id, 'Эта функция еще не реализованана')
            elif request == 'find':
                persons = data_research()
                write_msg(event.user_id, 'Нашел подходящих людей')
            else:
                write_msg(event.user_id, 'Не поняла вашего ответа. Вот список команд', keyboard_start())
