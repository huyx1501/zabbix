# encoding=UTF8
import os
import re
import json
import time


class filecache(object):
    
    def __init__(self, cache_file):
        self._cache_file = cache_file
        
    def is_cache_file_exist(self):
        return os.path.exists(self._cache_file)
    
    def get_val_from_json(self, key, seconds=60):
        """
        cache文件的内容，第一行是时间戳，第二行是json数据内容
        return: (value, code)
            code: 
                0: 正常获取数据
                1: 异常
                2: 超时
        """
        if not os.path.exists(self._cache_file):
            return None, 1

        with open(self._cache_file, "r") as fd:
            alllines = fd.readlines()
        if not alllines or len(alllines) < 1:  # 没有数据
            return None, 1
        old_unixtime = int(str(alllines[0]).strip())
        now_unixtime = int(time.time())
        if (now_unixtime - old_unixtime) > seconds:  # 超过60s
            return None, 2
        try:
            resobj = str(alllines[1]).strip()
            resobj = json.loads(resobj)
        except (ValueError, IndexError):  # 数据格式错误
            return None, 1

        keys = re.split(r"\.", key)
        dict_or_val = resobj
        if not isinstance(dict_or_val, dict):  # 缓存文件数据异常
            # return dict_or_val, 0
            return None, 1
        for k in keys:
            k = str(k).strip()
            dict_or_val = dict_or_val.get(k, None)
        return dict_or_val, 0
    
    def get_val_from_lines(self, key, separator=":", seconds=60):
        """
        cache文件的内容，第一行是时间戳，其余行是具体的数据内容
        return: (value, code)
            code: 
                0: 正常获取数据
                1: 异常
                2: 超时
        """
        if not os.path.exists(self._cache_file):
            return None, 1

        with open(self._cache_file, "r") as fd:
            alllines = fd.readlines()
        if not alllines or len(alllines) < 1:  # 没有数据
            return None, 1
        old_unixtime = int(str(alllines[0]).strip())
        now_unixtime = int(time.time())
        if (now_unixtime - old_unixtime) > seconds:  # 超过60秒
            return None, 2

        lines = alllines[1:]
        for line in lines:
            line = str(line).replace(" ", "").strip()
            ln_ary = re.split(separator, line)
            if len(ln_ary) < 2:
                continue
            if ln_ary[0] == key:
                return ln_ary[1], 0
        return None, 1

    def save_to_cache_file(self, content):
        # 如果是dict，则先转换为json字符串再写入
        if isinstance(content, dict):
            content = json.dumps(content)
        now_unixtime = int(time.time())
        with open(self._cache_file, "w") as fd:
            fd.write(str(now_unixtime)+"\n")
            fd.write(content)
