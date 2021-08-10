#coding: utf-8
import os
import time
import queue
import multiprocessing
import threading
import threadpool
import win32file
import win32con

import log
import marco
import exception


LOG = log.get_logger()


class QueryFileAttrs():
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
        result = dict()
        atime = self.stat_info.st_atime
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(atime))
        result.update({"CreationTime": time_str})
        return result

    def get_access_time(self):
        result = dict()
        atime = self.stat_info.st_atime
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(atime))
        result.update({"LastAccessTime": time_str})
        return result

    def get_modify_time(self):
        result = dict()
        mtime = self.stat_info.st_mtime
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        result.update({"LastModifyTime": time_str})
        return result

    def get_alloc_size(self):
        result = dict()
        sz = os.path.getsize(self.file_name)
        result.update({"AllocationSize": sz})
        return result

    def get_file_size(self):
        result = dict()
        sz = self.stat_info.st_size
        result.update({"EndOfFile": sz})
        return result

    def is_read_only(self):
        result = dict()
        is_read_only = os.access(self.file_name, os.W_OK)
        result.update({"ReadOnly": is_read_only})
        return result

    def is_hide(self):
        result = dict()
        file_flag = win32file.GetFileAttributesW(self.file_name)
        is_hide = file_flag & win32con.FILE_ATTRIBUTE_HIDDEN
        result.append({"Hide": is_hide})
        return result
        

    def get_all_attrs(self):
        result = dict()
        for attr,func in self.execute_func.items():
            if attr == "AllAttributes":
                continue
            res = func()
            result.update(res)
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
            return dict()

    def query_file_attrs(self):
        """
        @查询单个文件的用户所需的所有属性
        """
        attrs = dict()
        result = {self.file_name: attrs}
        result.append("The attributes of the file ({}) are as follows:".format(self.file_name))
        if "AllAttributes" in self.attrs:
            result.update(self.get_all_attrs())
            return result

        for attr in self.attrs:
            res = self.query_file_attrs(attr)
            attrs.update(res)
        return result


class QueryFileThread(threading.Thread):
    def __init__(self, query_file_info):
        threading.Thread.__init__(self)
        self.query_file_info = query_file_info
        self.query_file_worker = QueryFileAttrs(query_file_info)
        self.result = dict()

    def run(self):
        try:
            self.result = self.query_file_worker.query_file_attrs()
        except Exception as ex:
            raise ex

    def get_result(self):
        return self.result


class ThreadPool(object):
    def __init__(self, max_thread=None) -> None:
        if max_thread:
            self.max_thread = max_thread
        else:
            self.max_thread = multiprocessing.cpu_count() * 2
        self.thread_queue = queue.Queue(self.max_thread)
        for i in range(self.max_thread):
            self.thread_queue.put(QueryFileThread)

    def get_thread(self):
        return self.thread_queue.get()

    def add_thread(self):
        self.thread_queue.put(QueryFileThread)

    def is_queue_full(self):
        return len(self.thread_queue) == self.max_thread


class ParseAndCheckArg():
    def __init__(self, file_name) -> None:
        self.file_name = file_name

    def parse_one_item(self, query_one_file):
        """
        解析一个文件及其所需要查询的属性
        """
        result = list()
        # 检查参数个数是否正确
        split_arg = query_one_file.split("|")
        if len(split_arg) < 2:
            raise exception.FileAttrBaseException()

        # 检查文件名是否正确
        file_name = split_arg[0].split("=", 1)
        if not os.path.isfile(file_name):
            raise exception.FileNotExist()

        # 检查文件属性是否正确
        file_attrs = split_arg[1:]
        diff = set(file_attrs).difference(set(marco.Attribute.ATTRIBUTES.value))
        if diff:
            raise exception.AttrNotSupport()

        result.append(file_name)
        result.extend(set(file_attrs))
        return result

    def parse_file_data(self):
        """
        从文件中获取查询信息
        """
        result = list()
        if not os.path.isfile(self.file_name):
            raise

        with open(self.file_name, "r") as fd:
            arg_list = fd.readlines()
            for arg in arg_list:
                res = self.parse_one_item(arg)
                if not res:
                    LOG("check parm {} error".format(arg))
                    return list()
                result.append(res)
        return result


class QueryFilesAttr():
    def __init__(self, call_back=None) -> None:
        # 回调函数用于返回
        self.call_back = call_back
        self.thread_pool = ThreadPool()

    def _do_finish(self):
        if self.call_bacK:
            self.call_back()

    @staticmethod
    def _is_can_query(query_file_list):
        for query_file in query_file_list:
            if not os.path.isfile(query_file[0]):
                raise exception.FileNotExist()

            diff = set(query_file[1:]).difference(set(marco.Attribute.ATTRIBUTES.value))
            if diff:
                raise exception.AttrNotSupport()

    def _query_file_attrs(self, file_attrs):
        """
        @parm: [filename, attrs]
        @return: {filename: {attrname: attr}, ...}
        """
        thread = self.thread_pool.get_thread()(file_attrs)
        thread.start()
        thread.join()
        return thread.get_result()

    def query_files_attrs(self, query_file_list):
        """
        @function 查询参数列表中的各个文件属性
        @parm: [[filename, attrs], [filename, attrs], ...]
        @return: {filename: {attrname: attr}, ...}
        """
        result = dict()
        for query_file in query_file_list:
            one_file_res = self._query_file_attrs(query_file)
            result.update(one_file_res)
        self._do_finish()

    def query_file_from_file(self, file_name):
        """
        @function: 从指定文件中读取需要查询的文件的数据
        @parm: 数据文件全名称
        @return: {filename: {attrname: attr}, ...}
        """
        query_file_list = ParseAndCheckArg().parse_file_data()
        self.query_files_attrs(query_file_list)




           