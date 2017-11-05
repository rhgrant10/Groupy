import time
import sys

from groupy.client import Client


def read_token_from_file(filename):
    with open(filename) as f:
        return f.read().strip()


def test_groups(groups):
    for group in groups:
        print(group)

        print('Members:')
        for member in group.members[:5]:
            print(member)

        print('Recent messages:')
        for message in group.messages.list()[:5]:
            print(message)

        print('Leaderboard (day):')
        for message in group.leaderboard.list_day()[:5]:
            print(message.favorited_by)

        print('Gallery:')
        for message in group.gallery.list()[:5]:
            print(message.attachments)

        print()


def test_messages(messages):
    for message in messages:
        print(message)
        print(message.attachments)
        print('Liking...', message.like())
        time.sleep(1)  # you get rate limited by liking/unliking too fast
        print('Unliking...', message.unlike())


def test_chats(chats):
    for chat in chats:
        print(chat)
        print('Recent messages:')
        for message in chat.messages.list():
            print(message)


def main(*args):
    token_file = args[0]
    token = read_token_from_file(token_file)
    client = Client.from_token(token)

    groups = list(client.groups.list().autopage())
    test_group_ids = ('12268264', '27205597', '27205784', '35799100')
    target_groups = []
    for group in groups:
        if group.id in test_group_ids:
            print('Found {0} (id={0.group_id})'.format(group))
            target_groups.append(group)
    if len(target_groups) < len(test_group_ids):
        raise Exception('could not find group test groups')

    chats = list(client.chats.list())
    test_chat_ids = ('14529712+14612048',)
    target_chats = []
    for chat in chats:
        if chat.last_message['conversation_id'] in test_chat_ids:
            print('Found {}'.format(chat))
            target_chats.append(group)
    if len(target_chats) < len(test_chat_ids):
        raise Exception('could not find group test chats')

    target_messages = []
    for group in target_groups:
        target_messages.append(group.messages.list()[0])
    for chat in target_chats:
        target_messages.append(chat.messages.list()[0])

    print_header('test groups')
    test_groups(target_groups)

    print_header('test chats')
    test_chats(target_chats)

    print_header('test messages')
    test_messages(target_messages)


def print_header(header):
    print('\n')
    print('=' * 50)
    print('|  {}'.format(header))
    print('=' * 50)
    print()


if __name__ == '__main__':
    main(*sys.argv[1:])
