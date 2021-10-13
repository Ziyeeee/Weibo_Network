import requests
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
    user_ids.put(3479691367)
    queue_len = user_ids.qsize()
    search_depth = 0

    cache_files = get_file_list('../data/cache/relatives')
    user_cache, last_data = read_json_files(cache_files)

    while search_depth <= 5:
        if user_ids.empty():
            # 本层遍历结束
            user_ids = temp_user_ids
            queue_len = user_ids.qsize()
            temp_user_ids = Queue()
            # 保存数据
            with open('../data/fans-depth{}.json'.format(search_depth), 'w') as f:
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
                if str(user_id) in user_cache.keys():
                    # 如果该用户信息已被缓存
                    print('{}/{}:\t{} in cache'.format(queue_len - user_ids.qsize(), queue_len, user_id))
                    for fan in user_cache[str(user_id)]:
                        temp_user_ids.put(fan['fan_id'])
                    visited_users.append(user_id)
                    relatives_info.append({'user_id': user_id, 'relatives_info': user_cache[str(user_id)]})
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

                    last_data[user_id] = fans_list
                    if len(last_data) > item_num:
                        cache_files.append('../data/cache/fans/fans_user_cache{:0>3d}.json'.format(len(cache_files)))
                        last_data = {}
                        last_data[user_id] = fans_list
                    relatives_info.append({'user_id': user_id, 'relatives_info': fans_list})
                    # 缓存已经获取到的所有用户信息
                    with open('../data/cache/fans/fans_user_cache{:0>3d}.json'.format(len(cache_files)-1), 'w') as cache_f:
                        json.dump(last_data, cache_f)