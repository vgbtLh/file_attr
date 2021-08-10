import exception


class FileAttrBaseException(exception):
    def __init__(self, msg) -> None:
        super().__init__()
        self.msg = msg


class FileNotExist(FileAttrBaseException):
    msg = _"文件(file)不存在"
        

class AttrNotSupport(FileAttrBaseException):
    msg = _"参数错误(args): 不支持的文件属性(diff)"


class QueryFileParmError(FileAttrBaseException):
    msg = _"文件参数错误：(args)"

