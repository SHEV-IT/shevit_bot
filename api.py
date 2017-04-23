import requests
import constants as c


class VkApi:
    @staticmethod
    def send_msg(user, data):
        url = 'https://api.vk.com/method/messages.send'
        post_data = {'access_token': c.VK_TOKEN, 'user_id': user, 'attachment': []}

        if type(data) is str or type(data) is unicode:
            post_data['message'] = data
        elif 'message' in data:
            post_data['message'] = data['text']
            for attachment in ['photo', 'video', 'audio', 'doc', 'wall', 'market']:
                if attachment in data:
                    post_data['attachment'].append(data[attachment])
            post_data['attachment'] = ','.join(post_data['attachment'])

        r = requests.post(url, data=post_data)
        # TODO: check r.status
