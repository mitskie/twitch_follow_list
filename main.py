#!/usr/bin/python

import argparse

from Main import get_info


def parser():
    parser_args = argparse.ArgumentParser(description='Узнай, кто сейчас онлайн из списка зафоловленных каналов')
    parser_args.add_argument('--user', '-u', default=None, nargs='+', help='Логин или список логинов через пробел')

    return parser_args


if __name__ == '__main__':
    parser = parser()
    parse_login = parser.parse_args()

    if parse_login.user is not None:
        for login in parse_login.user:
            live_list = get_info.GetInfo(login).get_result()
            get_info.print_result_terminal(live_list)

    else:
        parser.print_help()
