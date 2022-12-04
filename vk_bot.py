from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from token_bot_vk import bot_token
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_find_users import VkBotFunc


token = bot_token

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

number_photo = 0
list_photo = ['photo-201557715_457267588', 'photo-201557715_457267749', 'photo-201557715_457267830']


def photo_switch(count_photo, number_global):
    if (count_photo <= len(list_photo) - 1) and (count_photo >= 0):
        correct_number_photo = count_photo
    elif count_photo < 0:
        correct_number_photo = len(list_photo) - 1
        number_global = len(list_photo) - 1
    elif count_photo > len(list_photo) - 1:
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


def send_photo(user_id, url_photo, keyboard=None):
    parameter = {
        'user_id': user_id,
        'attachment': url_photo,
        'random_id': randrange(10 ** 7),
    }

    if keyboard != None:
        parameter['keyboard'] = keyboard.get_keyboard()
    else:
        parameter = parameter
    vk.method('messages.send', parameter)


def data_research():
    master_user = VkBotFunc(token, event.user_id)
    find_params = master_user.user_info()
    users_data = master_user.get_users()
    sex_to_search = find_params['response'][0]['sex']
    home_town_to_search = find_params['response'][0]['city']['id']
    bdate_main = find_params['response'][0]['bdate'].split('.')
    bdate_to_search = bdate_main[2]
    users_selected = master_user.select_users(users_data, sex_to_search, home_town_to_search, int(bdate_to_search))
    return users_selected


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
                send_photo(event.user_id, list_photo[correct_photo], keyboard_photo_vk())
            elif request == 'next':
                number_photo += 1
                correct_photo = photo_switch(number_photo, number_photo)[0]
                number_photo = photo_switch(number_photo, number_photo)[1]
                send_photo(event.user_id, list_photo[correct_photo], keyboard_photo_vk())
            elif request == 'back':
                number_photo -= 1
                correct_photo = photo_switch(number_photo, number_photo)[0]
                number_photo = photo_switch(number_photo, number_photo)[1]
                send_photo(event.user_id, list_photo[correct_photo], keyboard_photo_vk())
            elif request == 'favorite':
                write_msg(event.user_id, 'Эта функция еще не реализованана')
            elif request == 'find':
                persons = data_research()
                write_msg(event.user_id, f'Your data {persons}')
            else:
                write_msg(event.user_id, 'Не поняла вашего ответа. Вот список команд', keyboard_start())
