from django.core.files.storage import Storage
from django.conf import settings


class FastDFSStorage(Storage):
    """自定义文件存储类"""
    # def __init__(self, option=None):
    #     """文件存储类的初始化方法"""
    #     if not option:
    #         option = settings.CUSTOM_STORAGE_OPTIONS

    def __init__(self, fdfs_base_url=None):
        """文件存储类的初始化方法"""
        self.fdfs_base_url = fdfs_base_url or settings.FDFS_BASE_URL

    def _open(self, name, mode='rb'):
        """
        :param name: 文件路径
        :param mode: 文件打开方式
        :return: None
        """
        pass

    def _save(self, name, content):
        """
        后台管理系统中，需要在这个方法中实现文件上传到FastDFS服务器
        :param name: 文件路径
        :param content: 文件二进制内容
        """
        pass

    def url(self, name):
        """
        返回文件的全路径
        :param name: 文件相对路径
        """
        return self.fdfs_base_url + name


