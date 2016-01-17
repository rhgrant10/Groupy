import factory
import faker
from datetime import datetime

from .. import objects


class GroupMeProvider(faker.providers.BaseProvider):
    def id(self, digits=10):
        if digits < 2:
            return self.numerify('%')
        digits -= 1
        return self.numerify('%{}'.format('#' * digits))


def fake_img_url(o):
    return 'http://i.groupme.com/{}'.format(o.user_id)


fake = faker.Factory.create()
fake.add_provider(GroupMeProvider)


class MessageFactory(factory.Factory):
    class Meta:
        model = objects.responses.Message

    id = factory.Sequence(lambda n: str(n))
    source_guid = factory.Sequence(lambda n: 'GUID-{}'.format(n))
    created_at = factory.Sequence(lambda n: datetime.now().timestamp())
    user_id = factory.Sequence(lambda n: fake.id())
    group_id = factory.Sequence(lambda n: fake.id())
    recipient_id = factory.Sequence(lambda n: fake.id())
    name = factory.Sequence(lambda n: fake.name())
    avatar_url = factory.LazyAttribute(fake_img_url)
    text = factory.Sequence(lambda n: fake.text(max_nb_chars=1000))
    system = False
    favorited_by = []
    attachments = []


class GroupFactory(factory.Factory):
    pass


class PersonFactory(factory.Factory):
    pass


class GroupMessageFactory(MessageFactory):
    recipient = factory.SubFactory(GroupFactory)


class DirectMessageFactory(MessageFactory):
    recipient = factory.SubFactory(PersonFactory)
