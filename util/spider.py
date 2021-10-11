import requests
import json
import time
from queue import Queue


"""
    网址：https://m.weibo.cn/profile/3479691367
    待完成：
        1.中断后从断点开始爬取
        2.爬取关注的人
"""
def spider_fans(user_id, since_id):
    fans_info = []

    # url = "https://m.weibo.cn/api/container/getIndex"
    url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{}&since_id={}" \
        .format(user_id, since_id)

    # cookie = "WEIBOCN_FROM=1110006030; SUB=_2A25MZdyQDeRhGeFO7VAY9y3EyTqIHXVvqeTYrDV6PUJbkdANLXHNkW1NQU89GizFRnsnG85Yx52afW4ioSYTBWNI; MLOGIN=1; _T_WM=73123320612; XSRF-TOKEN=c8dece; M_WEIBOCN_PARAMS=luicode=10000011&lfid=231051_-_fans_-_3479691367&fid=231051_-_fans_-_3479691367&uicode=10000011"
    # headers = {'cookie': cookie}

    response = requests.request("GET", url)
    data = response.content
    data = json.loads(data)

    # 返回数据为空时，repeat
    wait_time = 0.5859375
    while data['ok'] == 0:
        print("Request Failed!!!\tWait {}s".format(wait_time))
        time.sleep(wait_time)
        response = requests.request("GET", url)
        data = response.content
        data = json.loads(data)
        if wait_time >= 600:
            return [], True
        elif wait_time <= 150:
            wait_time *= 4


    # 获取粉丝列表，当被大V关注时，cards[0]会列举大V信息
    fans_list = data['data']['cards'][-1]['card_group']
    if len(fans_list) != 20:
        end = True
    else:
        end = False

    for fan in fans_list:
        try:
            # 忽略粉丝数>500的用户
            if fan['user'] is not None and int(fan['user']['followers_count']) <= 500:
                try:
                    # id、昵称、性别
                    fans_info.append({'fan_id': fan['user']['id'], 'fan_name': fan['user']['screen_name'],
                                      'fan_gender': fan['user']['gender']})
                except:
                    print("Error!!!", fan)
                    continue
        except ValueError:
            continue
    return fans_info, end


user_ids = Queue()
temp_user_ids = Queue()
fans_info = []
user_info_cache = {}
user_ids.put(3479691367)
queue_len = user_ids.qsize()
search_depth = 0

while search_depth <= 1:
    if user_ids.empty():
        # 本层遍历结束
        user_ids = temp_user_ids
        queue_len = user_ids.qsize()
        temp_user_ids = Queue()
        # 保存数据
        with open('../data/fans-depth{}.json'.format(search_depth), 'w') as f:
            json.dump(fans_info, f)
        # with open('temp_user_ids.json', 'w') as temp_f:
        #     temp_queue = copy.deepcopy(user_ids)
        #     temp_ids = []
        #     while not temp_queue.empty():
        #         temp_ids.append(temp_queue.get())
        #     json.dump(temp_ids, temp_f)
        fans_info = []
        print('Search Depth {} Finished'.format(search_depth))
        search_depth += 1
    else:
        user_id = user_ids.get()
        try:
            fans_list = user_info_cache[user_id]
        except KeyError:
            since_id = 0
            fans_list = []
            while True:
                time.sleep(1)
                fans, end = spider_fans(user_id, since_id)
                fans_list += fans
                print('{}/{}:\t{}'.format(queue_len - user_ids.qsize(), queue_len, fans))
                for fan in fans:
                    temp_user_ids.put(fan['fan_id'])
                if end:
                    break
                else:
                    since_id += 20
            user_info_cache[user_id] = fans_list
        fans_info.append({'user_id': user_id, 'fans_info': fans_list})
        
# https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_3479691367&page=2
