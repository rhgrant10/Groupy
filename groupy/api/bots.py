from . import base
from groupy import utils


class Bots(base.Manager):
    """A bot manager."""

    def __init__(self, session):
        super().__init__(session, path='bots')

    def list(self):
        """Return a list of bots.

        :return: all of your bots
        :rtype: :class:`list`
        """
        response = self.session.get(self.url)
        return [Bot(self, **bot) for bot in response.data]

    def create(self, name, group_id, avatar_url=None, callback_url=None,
               dm_notification=None, **kwargs):
        """Create a new bot in a particular group.

        :param str name: bot name
        :param str group_id: the group_id of a group
        :param str avatar_url: the URL of an image to use as an avatar
        :param str callback_url: a POST-back URL for each new message
        :param bool dm_notification: whether to POST-back for direct messages?
        :return: the new bot
        :rtype: :class:`~groupy.api.bots.Bot`
        """
        payload = {
            'bot': {
                'name': name,
                'group_id': group_id,
                'avatar_url': avatar_url,
                'callback_url': callback_url,
                'dm_notification': dm_notification,
            },
        }
        payload['bot'].update(kwargs)
        response = self.session.post(self.url, json=payload)
        bot = response.data['bot']
        return Bot(self, **bot)

    def post(self, bot_id, text, attachments=None):
        """Post a new message as a bot to its room.

        :param str bot_id: the ID of the bot
        :param str text: the text of the message
        :param attachments: a list of attachments
        :type attachments: :class:`list`
        :return: ``True`` if successful
        :rtype: bool
        """
        url = utils.urljoin(self.url, 'post')
        payload = dict(bot_id=bot_id, text=text)

        if attachments:
            payload['attachments'] = [a.to_json() for a in attachments]

        response = self.session.post(url, json=payload)
        return response.ok

    def destroy(self, bot_id):
        """Destroy a bot.

        :param str bot_id: the ID of the bot to destroy
        :return: ``True`` if successful
        :rtype: bool
        """
        url = utils.urljoin(self.url, 'destroy')
        payload = {'bot_id': bot_id}
        response = self.session.post(url, json=payload)
        return response.ok


class Bot(base.ManagedResource):
    """A bot."""

    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(name={!r})>'.format(klass, self.name)

    def __eq__(self, other):
        return self.bot_id == other.bot_id

    def post(self, text, attachments=None):
        """Post a message as the bot.

        :param str text: the text of the message
        :param attachments: a list of attachments
        :type attachments: :class:`list`
        :return: ``True`` if successful
        :rtype: bool
        """
        return self.manager.post(self.bot_id, text, attachments)

    def destroy(self):
        """Destroy the bot.

        :return: ``True`` if successful
        :rtype: bool
        """
        return self.manager.destroy(self.bot_id)
