import json


def divide_cache(item_num):
    with open('../data/cache/followers/followers_user_cache.json', 'r') as f:
        data = json.load(f)

    cache_f_list = []
    temp_dict = {}
    for id, info in data.items():
        if len(temp_dict) < item_num:
            temp_dict[id] = info
        else:
            cache_f_list.append(temp_dict)
            temp_dict = {}
            temp_dict[id] = info
    cache_f_list.append(temp_dict)

    for i, temp_dict in enumerate(cache_f_list):
        with open('../data/cache/followers_user_cache{:0>3d}.json'.format(i), 'w') as cache_f:
            json.dump(temp_dict, cache_f)


item_num = 100
if __name__ == '__main__':
    divide_cache(item_num)