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

    # TODO: group.create_bot
    def create(self, name, group_id, **details):
        """Create a new bot.


        :param str name: name of the bot
        :param str group_id: the ID of the group in which the bot will exist
        :param kwargs details: any additional fields
        :return: the new bot
        :rtype: :class:`~groupy.api.bots.Bot`
        """
        payload = dict(details, name=name, group_id=group_id)
        response = self.session.post(self.url, json=payload)
        return Bot(self, **response.data)

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
        path = '{}/destroy'.format(bot_id)
        url = utils.urljoin(self.url, path)
        response = self.session.post(url)
        return response.ok


class Bot(base.ManagedResource):
    """A bot."""

    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(name={!r})>'.format(klass, self.name)

    def post(self, text, attachments=None):
        """Post a message as the bot.

        :param str text: the text of the message
        :param attachments: a list of attachments
        :type attachments: :class:`list`
        :return: ``True`` if successful
        :rtype: bool
        """
        return self.manager.post(self.bot_id, text, attachments)
