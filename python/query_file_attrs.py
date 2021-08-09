import os
import time
import sys
import win32file
import win32con

import public_marco


class ParseAndCheckArg():
    def __init__(self) -> None:
        pass
        
    def parse_and_check(self):
        arg_count = len(sys.argv)
        if (arg_count < 2):
            print(public_marco.Exception.LACK_ARGVS_ERROR)
            self.usage_info()
            return list()

        arg_head = sys.argv[1].strip()
        if arg_head.startswith("Files="):
            return self.parse_from_string()
        elif arg_head == public_marco.CONFIG_FILE:
            return self.parse_from_file()
        else:
            print(public_marco.Exception.LACK_ARGVS_ERROR.value)
            self.usage_info()
            return list()

    def usage_info(self):
        # TODO程序的使用方法
        pass

    def parse_one_item(self, one_file):
        """
        解析一个文件及其所需要查询的属性
        """
        result = list()
        # 检查参数个数是否正确
        split_arg = one_file.split("|")
        if len(split_arg) < 2:
            print(public_marco.Exception.LACK_ARGVS_ERROR.value)
            self.usage_info()
            return result

        # 检查文件名是否正确
        file_name = split_arg[0].split("=", 1)
        if not os.path.isfile(file_name):
            print(public_marco.Exception.FILE_PATH_ERROR.value)
            return result

        # 检查文件属性是否正确
        file_attrs = split_arg[1:]
        diff = set(file_attrs).difference(set(public_marco.Attribute.ATTRIBUTES.value))
        if diff:
            print(public_marco.Exception.ATTRIBUTE_ERROR.value)
            return result

        result.append(file_name)
        result.extend(set(file_attrs))
        return result

    def parse_from_file(self):
        """
        从文件中获取查询信息
        """
        result = list()
        arg_info = sys.argv
        arg_count = len(sys.argv)

        if arg_count != 2:
            self.usage_info()

        with open(sys.argv[1], "r") as fd:
            arg_list = fd.readlines()
            # 日志记录在哪出错
            for arg in arg_list:
                res = self.parse_one_item(arg)
                if not res:
                    return list()
                result.append(res)
        return result

    def parse_from_string(self):
        """
        从参数中读取查询信息
        """
        # TODO系统参数在最外层定义
        result = list()
        arg_info = sys.argv[1:]

        for arg in arg_info:
            res = self.parse_one_item(arg)
            if not res:
                return list()
            result.append(res)
        return result


class QueryFileAttrs:
    """
    @查询文件参数类
    @parm:
        构造函数参数为一个列表，列表的第一个元素为文件名，后面是需要查询的文件属性
    """
    def __init__(self, args):
        self.file_name = args[0]
        self.attrs = args[1:]
        self.execute_func = dict()
        self.init_attr_map()
        self.stat_info = self._get_stat_info()
    
    def init_attr_map(self):
        """
        @用于初始化不同文件属性到属性查询方法的映射
        """
        self.execute_func["CreationTime"] = self.get_creat_time
        self.execute_func["LastAccessTime"] = self.get_access_time
        self.execute_func["LastModifyTime"] = self.get_modify_time
        self.execute_func["AllocationSize"] = self.get_alloc_size
        self.execute_func["EndOfFile"] = self.get_file_size
        self.execute_func["ReadOnly"] = self.is_read_only
        self.execute_func["Hide"] = self.is_hide
        self.execute_func["AllAttributes"] = self.get_all_attrs

    def _get_stat_info(self):
        """
        @获取文件的stat
        """
        stat_info = os.stat(self.file_name)
        return stat_info

    def get_creat_time(self):
        result = list()
        atime = self.stat_info.st_atime
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(atime))
        result.append("CreationTime: " + time_str)
        return result

    def get_access_time(self):
        result = list()
        atime = self.stat_info.st_atime
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(atime))
        result.append("LastAccessTime: " + time_str)
        return result

    def get_modify_time(self):
        result = list()
        mtime = self.stat_info.st_mtime
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        result.append("LastModifyTime: " + time_str)
        return result

    def get_alloc_size(self):
        result = list()
        sz = os.path.getsize(self.file_name)
        result.append("AllocationSize: " + str(sz) + " B")
        return result

    def get_file_size(self):
        result = list()
        sz = self.stat_info.st_size
        result.append("EndOfFile: " + str(sz) + " B")
        return result

    def is_read_only(self):
        result = list()
        is_read_only = os.access(self.file_name, os.W_OK)
        result.append("ReadOnly: " + str(is_read_only))
        return result

    def is_hide(self):
        result = list()
        file_flag = win32file.GetFileAttributesW(self.file_name)
        is_hide = file_flag & win32con.FILE_ATTRIBUTE_HIDDEN
        result.append("Hide: " + str(is_hide))
        return result
        

    def get_all_attrs(self):
        result = list()
        for attr,func in self.execute_func.items():
            if attr == "AllAttributes":
                continue
            res = func()
            result.extend(res)
        return result

    def query_file_attr(self, attr):
        """
        @查询单个文件的一个属性
        @ return: 
            failed: 返回空列表
        """
        if attr in self.execute_func.keys():
            return (self.execute_func[attr])()
        else:
            return list()

    def query_file_attrs(self):
        """
        @查询单个文件的用户所需的所有属性
        """
        result = list()
        result.append("The attributes of the file ({}) are as follows:".format(self.file_name))
        if "AllAttributes" in self.attrs:
            result.extend(self.get_all_attrs())
            return result

        for attr in self.attrs:
            res = self.query_file_attrs(attr)
            result.extend(res)
        return result