import requests
import json
import time
from queue import Queue

"""
    网址：https://m.weibo.cn/profile/3479691367
    待完成：
        1.爬取关注的人
"""


def repeat_request(url):
    response = requests.request("GET", url)
    data = response.content
    data = json.loads(data)
    if data['ok'] == 0:
        # 未获取到数据
        return data, False
    elif 'user' not in data['data']['cards'][-1]['card_group'][0].keys():
        # 数据不完整
        return data, False
    else:
        return data, True


def spider_fans(user_id, since_id):
    fans_info = []

    # url = "https://m.weibo.cn/api/container/getIndex"
    url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{}&since_id={}" \
        .format(user_id, since_id)

    data, success_flag = repeat_request(url)

    # 返回数据为空时，repeat
    wait_time = 0.5859375
    while not success_flag:
        print("Request Failed!!!\tWait {}s".format(wait_time))
        time.sleep(wait_time)
        data, success_flag = repeat_request(url)
        if wait_time >= 18.75:
            return [], True
        elif wait_time <= 18.75:
            wait_time *= 2

    # 获取粉丝列表，当被大V关注时，cards[0]会列举大V信息
    fans_list = data['data']['cards'][-1]['card_group']
    if len(fans_list) != 20:
        end = True
    else:
        end = False

    for fan in fans_list:
        # 忽略粉丝数>500的用户
        if fan['user'] is not None and \
                fan['user']['followers_count'].isdigit() and \
                int(fan['user']['followers_count']) <= 500:
            # id、昵称、性别
            fans_info.append({'fan_id': fan['user']['id'], 'fan_name': fan['user']['screen_name'],
                              'fan_gender': fan['user']['gender']})
    return fans_info, end


user_ids = Queue()
temp_user_ids = Queue()
fans_info = []
visited_user_cache = {}
user_ids.put(3479691367)
queue_len = user_ids.qsize()
search_depth = 0

with open('../data/user_cahce.json', 'r') as cache_f:
    user_cache = json.load(cache_f)

while search_depth <= 5:
    if user_ids.empty():
        # 本层遍历结束
        user_ids = temp_user_ids
        queue_len = user_ids.qsize()
        temp_user_ids = Queue()
        # 保存数据
        with open('../data/fans-depth{}.json'.format(search_depth), 'w') as f:
            json.dump(fans_info, f)
        fans_info = []
        print('Search Depth {} Finished'.format(search_depth))
        search_depth += 1
    else:
        user_id = user_ids.get()
        if user_id in visited_user_cache.keys():
            # 如果该用户已被访问过
            continue
        else:
            if str(user_id) in user_cache.keys():
                # 如果该用户信息已被缓存
                print('{}/{}:\t{} in cache'.format(queue_len - user_ids.qsize(), queue_len, user_id))
                for fan in user_cache[str(user_id)]:
                    temp_user_ids.put(fan['fan_id'])
                visited_user_cache[user_id] = user_cache[str(user_id)]
                fans_info.append({'user_id': user_id, 'fans_info': user_cache[str(user_id)]})
            else:
                since_id = 0
                fans_list = []
                while True:
                    # time.sleep(1)
                    fans, end = spider_fans(user_id, since_id)
                    fans_list += fans
                    print('{}/{}:\t{}'.format(queue_len - user_ids.qsize(), queue_len, fans))
                    for fan in fans:
                        temp_user_ids.put(fan['fan_id'])
                    if end:
                        break
                    else:
                        since_id += 20
                visited_user_cache[user_id] = fans_list
                fans_info.append({'user_id': user_id, 'fans_info': fans_list})
                # 缓存已经获取到的所有用户信息
                with open('../data/user_cahce.json', 'w') as cache_f:
                    json.dump(visited_user_cache, cache_f)

# https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_3479691367&page=2
