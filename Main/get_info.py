import requests
import sys
import os
import fileinput
from enum import auto
from concurrent.futures import ThreadPoolExecutor, as_completed

import config


class Style:
    BOLD = '\033[1m'
    END = '\033[0m'


class URLs(auto):
    TOKEN = config.TWITCH_TOKEN_URL
    MAIN = config.TWITCH_URL
    USER = MAIN + '/users'
    FOLLOW = USER + '/follows'
    STREAM = MAIN + '/streams'


class STATUS(auto):
    OK = 200
    BAD_TOKEN = 401


SESSION = requests.Session()

TOKEN_DATA = {'client_id': config.TWITCH_CLIENT_ID,
              'client_secret': config.TWITCH_CLIENT_SECRET,
              'grant_type': 'client_credentials'}

HEADERS = {'client-id': config.TWITCH_CLIENT_ID,
           'authorization': 'Bearer ' + config.TWITCH_OAUTH_TOKEN}


class GetToken:
    @staticmethod
    def get_token():
        try:
            with requests.post(URLs.TOKEN, data=TOKEN_DATA) as get_response:
                status = get_response.status_code

                if status == STATUS.OK:
                    get_data = get_response.json()
                    token = get_data['access_token']

                    return token

                else:
                    sys.exit(f'[get_token] Что-то пошло не так :( Код ошибки: {status}')

        except Exception as error:
            sys.exit('[get_token] Что-то пошло не по плану -_-' + '\nСистемная ошибка: ' + str(error))

    @staticmethod
    def update_token(token):
        old_token = config.TWITCH_OAUTH_TOKEN
        new_token = token

        path_to_config = os.path.join(config.PATH_TO_FILE, 'config.py')
        with fileinput.FileInput(path_to_config, inplace=True, backup='.bak') as open_file:
            for line in open_file:
                print(line.replace(old_token, new_token), end='')


class GetInfo:
    def __init__(self, login):
        self.login = login

    def get_user(self):
        try:
            with SESSION.get(URLs.USER, headers=HEADERS, params={'login': self.login}) as get_response:
                status = get_response.status_code

                if status == STATUS.OK:
                    get_data = get_response.json()
                    user_id = get_data['data'][0]['id']

                    return user_id

                elif status == STATUS.BAD_TOKEN:
                    print('Токен устарел. \nОбновляю... ', end='')
                    new_token = GetToken.get_token()
                    GetToken.update_token(new_token)
                    print('OK')
                    os.execv(sys.argv[0], sys.argv)

                else:
                    sys.exit(f'[get_user] Что-то пошло не так :( Код ошибки: {status}')

        except Exception as error:
            sys.exit('[get_user] Что-то пошло не по плану -_-' + '\nСистемная ошибка: ' + str(error))

    def get_follow(self):
        user_id = self.get_user()
        count = 100

        try:
            with SESSION.get(URLs.FOLLOW, headers=HEADERS, params={'first': count, 'from_id': user_id}) as get_response:
                status = get_response.status_code

                if status == STATUS.OK:
                    get_data = get_response.json()
                    total = get_data['total']

                    streamer_list = [get_data['data'][n]['to_id'] for n in range(0, total)]

                    return streamer_list

                else:
                    sys.exit(f'[get_follow] Что-то пошло не так :( Код ошибки: {status}')

        except Exception as error:
            sys.exit('[get_follow] Что-то пошло не по плану -_-' + '\nСистемная ошибка: ' + str(error))

    @staticmethod
    def get_streamer_online(streamer_id):
        try:
            with SESSION.get(URLs.STREAM, headers=HEADERS, params={'user_id': streamer_id}) as get_response:
                status = get_response.status_code

                if status == STATUS.OK:
                    get_data = get_response.json()

                    if get_data['data']:
                        streamer_name = get_data['data'][0]['user_name']
                        game_name = get_data['data'][0]['game_name']
                        title = get_data['data'][0]['title']

                        streamer_info = {'streamer_name': streamer_name, 'game_name': game_name, 'title': title}

                        return streamer_info

        except Exception as error:
            sys.exit('[get_streamer_online] Что-то пошло не по плану -_-' + '\nСистемная ошибка: ' + str(error))

    def get_result(self):
        streamer_list = self.get_follow()
        result_list = []

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.get_streamer_online, streamer) for streamer in streamer_list]

            for result in as_completed(futures):
                if result.result() is not None:
                    result_list.append(result.result())

            return result_list


def print_result_terminal(live_list):
    print('-' * 60)

    for streamer in live_list:
        streamer_name = streamer["streamer_name"]
        game_name = streamer["game_name"]
        title = streamer["title"]

        print(Style.BOLD + f'{streamer_name}' + Style.END + ' сейчас стримит ' + Style.BOLD +
              f'{game_name}' + Style.END + f' - {title}')

    print('-' * 60)


def message_result_telegram(live_list):
    message = []

    for streamer in live_list:
        streamer_name = streamer['streamer_name']
        game_name = streamer['game_name']
        text = f'<a href="https://twitch.tv/{streamer_name}">{streamer_name}</a> сейчас стримит <b>{game_name}</b>' + \
               '\n'
        message.append(text)

    complete_message = '\n'.join(message)
    return complete_message
