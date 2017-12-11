#!/usr/bin/env python
import sys
import time
import groupy
from itertools import cycle


def main(b_token, r_token):
    print('Creating clients')
    b_client = groupy.Client.from_token(b_token)
    print(b_client)
    r_client = groupy.Client.from_token(r_token)
    print(r_client)

    # bob creates a new group
    print('Creating test group')
    b_group = b_client.groups.create('Just a test')
    print(b_group)

    # bob adds rob to the group
    print('Bob adding Rob to the group')
    result = b_group.memberships.add(nickname='whoknows',
                                     email=r_client.user.me['email'])
    print(result)

    # get the results when ready and ensure all were successful
    print('Waiting for the result')
    members, failures = result.poll()
    if failures:
        raise Exception('failed to add these members: {}'.format(failures))
    print(members)

    # bob makes rob the owner of the group
    print('Bob making Rob onwer of the group')
    result = b_group.change_owners(r_client.user.me['user_id'])
    print(result.reason)

    # wait for server to update
    time.sleep(1)

    # rob get's a reference to the same group
    print('Rob finding the test group')
    test_group_filter = groupy.utils.make_filter(group_id=b_group.group_id)
    r_group = test_group_filter.find(r_client.groups.list_all())
    print(r_group)

    # rob and bob have a conversation
    message_texts = [
        "hey dude",
        "sup",
        "nothing man, just chillin on the couch",
        "aren't you going to that thing?",
        "what thing?",
        "that thing you told me about, like yesterday",
        "oh the convention?",
        "yeah something like that",
        "nah man, I figured I should wait and go next weekend when you can make it",
        "sweet man, that would be awesome",
        "yeah I figure you took me to crochet class, so I'll return the fav",
        "well dang, I still need something to do today...",
        "wanna come over? we can play marble madness",
        "you got the nintendo working?",
        "hellz yeah I did",
        "when? that thing hasn't worked for like a decade",
        "this morning! wanna know something funny?",
        "?",
        "I just unpacked it and plugged it in and it worked",
        "wat",
        "I SAID IT JUST WORKED",
        "lol no but doesn't that suggest that it wasn't ever broken?",
        "yeah... let's not talk about that part ;)",
    ]
    print('Rob and Bob talking in the group')
    messages = []
    groups = cycle([r_group, b_group])
    for group, text in zip(groups, message_texts):
        message = group.post(text=text)
        print(message)
        messages.append(message)

    mid = len(messages) // 2

    # let's list out all the messages
    print('\nAll after mid:')
    for message in r_group.messages.list_all_after(message_id=messages[mid].id, limit=5):
        print('{} @ {}: {}'.format(message.user_id, message.created_at, message.text))

    print('\nAll before mid:')
    for message in r_group.messages.list_all_before(message_id=messages[mid].id, limit=5):
        print('{} @ {}: {}'.format(message.user_id, message.created_at, message.text))

    print('\nSince mid:')
    for message in r_group.messages.list_since(message_id=messages[mid].id, limit=5):
        print('{} @ {}: {}'.format(message.user_id, message.created_at, message.text))

    # rob finds bob in the group
    print('Rob refreshing the group')
    r_group.refresh_from_server()
    print(r_group)

    print('Rob finding Bob in the group')
    bob_filter = groupy.utils.make_filter(user_id=b_client.user.me['user_id'])
    bob = bob_filter.find(r_group.members)
    print(bob)

    # bob find rob in the group
    print('Bob finding Rob in the group')
    b_group.refresh_from_server()
    print(b_group)

    print('Bob finding Rob in the group')
    rob_filter = groupy.utils.make_filter(user_id=r_client.user.me['user_id'])
    rob = rob_filter.find(b_group.members)
    print(rob)

    # let's have a private converstion
    messages = [
        "hey you still there?",
        "yeah but I'm about to cook dinner",
        "oh",
        "what's up?",
        "well, I never came over",
        "yeah, we never got to play CoD",
        "what if I just ordered a pizza and headed over?",
        "bro, that would be awesome!",
        "cool bro, be there in about half and hour",
        "sweet",
        "while I'm on the way maybe you can pick up drinks?",
        "um...",
        "dude I just got us pizza",
        "yeah plus I still owe you",
        "for what?",
        "oh shit, you don't remember?",
        "uh, nope",
        "don't worry about it - I'll bring the drinks"
        "...ok",
        "but I am kicking you out of the group we were just in",
        "k",
        "you're okay with that?",
        "um, sure",
        "k, see you soon",
    ]
    print('Bob and Rob having a private conversation')
    messages = []
    users = cycle([rob, bob])
    for user, message in zip(users, messages):
        message = user.post(text=message)
        print(message)
        messages.append(message)

    # and then remove bob from the group
    print('Remove bob')
    result = bob.remove()
    print(result)

    # now destroy the group
    print('Destroying the test group')
    result = r_group.destroy()
    print(result)

    # but say hi in direct messages
    message = bob.post(text='hey are you there?')
    bob.post(text='hello??')

    # and how about we inspect all messages between us
    print('\n All:')
    all_messages = list(bob.messages.list_all())
    for message in all_messages:
        print(message.user_id, message.created_at, message.text)

    mid = len(all_messages) // 2

    print('\n All before:')
    for message in bob.messages.list_all_before(message_id=all_messages[mid].id):
        print(message.user_id, message.created_at, message.text)

    print('\nSince:')
    message = all_messages[-1]
    for message in bob.messages.list_since(message_id=all_messages[mid].id):
        print(message.user_id, message.created_at, message.text)


if __name__ == '__main__':
    main(*sys.argv[1:])
