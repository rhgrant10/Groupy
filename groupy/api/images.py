from . import base
from groupy import utils


class Images(base.Manager):
    base_url = 'https://image.groupme.com/'

    def upload(self, fp):
        url = utils.urljoin(self.url, 'pictures')
        response = self.session.post(url, files={'file': fp})
        image_urls = response.data['payload']
        return image_urls

    def download(self, url):
        response = self.session.get(url)
        return response.content
