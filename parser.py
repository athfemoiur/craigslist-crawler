from bs4 import BeautifulSoup


class AdvertisementParser:

    @staticmethod
    def parse(html_doc):
        soup = BeautifulSoup(html_doc, 'html.parser')
        data = dict(title=None,
                    price=None,
                    body=None,
                    post_id=None,
                    created_time=None,
                    modified_time=None,
                    image=[]
                    )
        title_tag = soup.find('span', {'id': 'titletextonly'})
        if title_tag:
            data['title'] = title_tag.text

        price_tag = soup.find('span', {'class': 'price'})
        if price_tag:
            data['price'] = price_tag.text

        body_tag = soup.find('section', {'id': 'postingbody'})
        if body_tag:
            data['body'] = body_tag.text

        post_id_tag = soup.select_one('body > section > section > section > div.postinginfos > p:nth-child(1)')
        if post_id_tag:
            data['post_id'] = post_id_tag.text.replace('post id: ', '')

        created_time_tag = soup.select_one(
            'body > section > section > section > div.postinginfos > p:nth-child(2) > time')
        if created_time_tag:
            data['created_time'] = created_time_tag['datetime']

        modified_time = soup.select_one('body > section > section > section > div.postinginfos > p:nth-child(3) > time')
        if modified_time:
            data['modified_time'] = modified_time['datetime']
        image_url = soup.find_all('img')
        if image_url:
            image_list = [{'url': img['src'], 'flag': False} for img in image_url]
            data['image'] = image_list
        return data
