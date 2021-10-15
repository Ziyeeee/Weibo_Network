import requests
import json
import time
from queue import Queue
from util.spider_fans import get_file_list, read_json_files, item_num

"""
    网址：https://m.weibo.cn/profile/3479691367
"""


def repeat_request(url):
    try:
        response = requests.request("GET", url)
    except:
        time.sleep(5)
        response = requests.request("GET", url)
    data = response.content
    data = json.loads(data)
    if data['ok'] == 0:
        # 未获取到数据
        return data, False
    elif len(data['data']['cards'][-1]['card_group'][0]) == 0:
        # 数据不完整
        return data, False
    elif 'user' not in data['data']['cards'][-1]['card_group'][0].keys():
        # 数据不完整
        return data, False
    else:
        return data, True


def spider_followers(user_id, page):
    followers_info = []
    url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{}&page={}" \
        .format(user_id, page)

    data, success_flag = repeat_request(url)

    # 返回数据为空时，repeat
    wait_time = 0.5
    while not success_flag:
        print("Request Failed!!!\tWait {}s".format(wait_time))
        time.sleep(wait_time)
        data, success_flag = repeat_request(url)
        if wait_time >= 5:
            return [], True
        else:
            wait_time *= 2

    followers_list = data['data']['cards'][-1]['card_group']
    end = False

    for follower in followers_list:
        if follower['user'] is not None and \
                follower['user']['followers_count'].isdigit() and \
                int(follower['user']['followers_count']) <= 500:
        # id、昵称、性别
            followers_info.append({'follower_id': follower['user']['id'], 'follower_name': follower['user']['screen_name'],
                               'follower_gender': follower['user']['gender']})
    return followers_info, end


if __name__ == '__main__':
    user_ids = Queue()
    temp_user_ids = Queue()
    followers_info = []
    visited_user = []
    user_ids.put(3479691367)
    queue_len = user_ids.qsize()
    search_depth = 0

    cache_files = get_file_list('../data/cache/followers')
    user_cache, last_data = read_json_files(cache_files)

    while search_depth <= 2:
        if user_ids.empty():
            # 本层遍历结束
            user_ids = temp_user_ids
            queue_len = user_ids.qsize()
            temp_user_ids = Queue()
            # 保存数据
            with open('../data/followers-depth{}.json'.format(search_depth), 'w') as f:
                json.dump(followers_info, f)
            followers_info = []
            print('Search Depth {} Finished'.format(search_depth))
            search_depth += 1
        else:
            user_id = user_ids.get()
            if user_id in visited_user:
                # 如果该用户已被访问过
                continue
            else:
                if str(user_id) in user_cache.keys():
                    # 如果该用户信息已被缓存
                    print('{}/{}:\t{} in cache'.format(queue_len - user_ids.qsize(), queue_len, user_id))
                    for follower in user_cache[str(user_id)]:
                        temp_user_ids.put(follower['follower_id'])
                    followers_info.append({'user_id': user_id, 'followers_info': user_cache[str(user_id)]})
                else:
                    page = 0
                    followers_list = []
                    while True:
                        # time.sleep(1)
                        followers, end = spider_followers(user_id, page)
                        followers_list += followers
                        print('{}/{}:\t{}'.format(queue_len - user_ids.qsize(), queue_len, followers))
                        for follower in followers:
                            temp_user_ids.put(follower['follower_id'])
                        if end:
                            break
                        else:
                            if page == 0:
                                page += 2
                            elif page == 10:
                                break
                            else:
                                page += 1


                    last_data[user_id] = followers_list
                    if len(last_data) > item_num:
                        cache_files.append('../data/cache/followers/followers_user_cache{:0>3d}.json'.format(len(cache_files)))
                        last_data = {}
                        last_data[user_id] = followers_list
                    followers_info.append({'user_id': user_id, 'followers_info': followers_list})
                    # 缓存已经获取到的所有用户信息
                    with open('../data/cache/followers/followers_user_cache{:0>3d}.json'.format(len(cache_files) - 1),
                              'w') as cache_f:
                        json.dump(last_data, cache_f)
                visited_user.append(user_id)
