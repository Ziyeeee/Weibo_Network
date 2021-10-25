import json
import time
import os
from queue import Queue
from util.divide_cache import item_num
from util.spider_fans import spider_fans, get_file_list, read_json_files
from util.spider_followers import spider_followers


if __name__ == '__main__':
    user_ids = Queue()
    temp_user_ids = Queue()
    relatives_info = []
    visited_users = []
    fans_list = []
    followers_list = []
    # 填入起始节点的id
    user_ids.put(1234567890)
    queue_len = user_ids.qsize()
    search_depth = 0

    cache_files = get_file_list('../data/cache/fans')
    fans_cache, last_fans_data = read_json_files(cache_files)
    cache_files = get_file_list('../data/cache/followers')
    followers_cache, last_followers_data = read_json_files(cache_files)
    cache_files = get_file_list('../data/cache/relatives')
    relatives_cache, last_relatives_data = read_json_files(cache_files)

    while search_depth <= 3:
        if user_ids.empty():
            # 本层遍历结束
            user_ids = temp_user_ids
            queue_len = user_ids.qsize()
            temp_user_ids = Queue()
            # 保存数据
            with open('../data/relatives-depth{}.json'.format(search_depth), 'w') as f:
                json.dump(relatives_info, f)
            relatives_info = []
            print('Search Depth {} Finished'.format(search_depth))
            search_depth += 1
        else:
            user_id = user_ids.get()
            if user_id in visited_users:
                # 如果该用户已被访问过
                continue
            else:
                if str(user_id) in relatives_cache.keys():
                    print('{}/{}:\t{} in cache'.format(queue_len - user_ids.qsize(), queue_len, user_id))
                    for fan in relatives_cache[str(user_id)]['fans_info']:
                        temp_user_ids.put(fan['fan_id'])
                    for follower in relatives_cache[str(user_id)]['followers_info']:
                        temp_user_ids.put(follower['follower_id'])
                    relatives_info.append({'user_id': user_id, 'fans_info': relatives_cache[str(user_id)]['fans_info'],
                                           'followers_info': relatives_cache[str(user_id)]['followers_info']})
                else:
                    user_relative = {'user_id': user_id}
                    if str(user_id) in fans_cache.keys():
                        # 如果该用户信息已被缓存
                        print('{}/{}:\t{}`s fans in cache'.format(queue_len - user_ids.qsize(), queue_len, user_id))
                        for fan in fans_cache[str(user_id)]:
                            temp_user_ids.put(fan['fan_id'])
                        user_relative['fans_info'] = fans_cache[str(user_id)]
                    else:
                        since_id = 0
                        fans_list = []
                        while True:
                            # time.sleep(1)
                            fans, end = spider_fans(user_id, since_id)
                            fans_list += fans
                            print('{}/{}:\t{}`s fans: {}'.format(queue_len - user_ids.qsize(), queue_len, user_id, fans))
                            for fan in fans:
                                temp_user_ids.put(fan['fan_id'])
                            if end:
                                break
                            else:
                                since_id += 20
                        user_relative['fans_info'] = fans_list

                    if str(user_id) in followers_cache.keys():
                        # 如果该用户信息已被缓存
                        print('{}/{}:\t{}`s followers in cache'.format(queue_len - user_ids.qsize(), queue_len, user_id))
                        for follower in followers_cache[str(user_id)]:
                            temp_user_ids.put(follower['follower_id'])
                        user_relative['followers_info'] = followers_cache[str(user_id)]
                    else:
                        page = 0
                        followers_list = []
                        while True:
                            # time.sleep(1)
                            followers, end = spider_followers(user_id, page)
                            followers_list += followers
                            print('{}/{}:\t{}`s followers: {}'.format(queue_len - user_ids.qsize(), queue_len, user_id, followers))
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
                        user_relative['followers_info'] = followers_list

                    relatives_info.append(user_relative)
                    last_relatives_data[user_id] = {'fans_info': user_relative['fans_info'],
                                                    'followers_info': user_relative['followers_info']}
                    if len(last_relatives_data) > item_num:
                        cache_files.append('../data/cache/relatives/relatives_user_cache{:0>3d}.json'.format(len(cache_files)))
                        last_relatives_data = {}
                        last_relatives_data[user_id] = {'fans_info': fans_list, 'followers_info': followers_list}

                    # 缓存已经获取到的所有用户信息
                    with open('../data/cache/relatives/relatives_user_cache{:0>3d}.json'.format(len(cache_files)-1), 'w') as cache_f:
                        json.dump(last_relatives_data, cache_f)
                visited_users.append(user_id)