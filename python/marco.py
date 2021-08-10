#coding: utf-8
from enum import Enum


class Exception(Enum):
    """异常返回信息"""
    LACK_ARGVS_ERROR = "缺少参数"
    ARGVS_FORMAT_ERROR = "文件路径参数格式不正确，请以File=路径为格式"
    FILE_PATH_ERROR = "文件路径不正确，请确认路径合理性,路径中不可包含空格"
    ATTRIBUTE_ERROR = "参数格式不正确"


class Attribute(Enum):
    """属性类"""
    ATTRIBUTES = ["CreationTime", "LastAccessTime", "AllocationSize", "EndOfFile", "ReadOnly", "Hide", "AllAttributes"]


class CheckFileType(Enum):
    File = "File.txt"
    Files = "Files.txt"