from django.core.files.storage import Storage
from fdfs_client.client import *
from django.conf import settings


class FDFSStorage(Storage):
    """FDFS文件存储"""

    def __init__(self, client_conf=None, domain=None):
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        if domain is None:
            domain = settings.FDFS_STORAGE_URL
        self.domain = domain

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content):
        """
        :param name: 上传文件名字
        :param content: 包含文件内容的File对象
        :return:
        """
        # 实例化对象
        trackers = get_tracker_conf(self.client_conf)
        client = Fdfs_client(trackers)
        res = client.upload_appender_by_buffer(content.read())
        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件失败')
        filename = res.get('Remote file_id')
        return filename.decode()

    def exists(self, name):
        """
        文件是存储在 fastdfs文件系统中的,对于django来说即不存在
        :param name:
        :return:
        """
        return False

    def url(self, name):
        """
        :param name:
        :return:url路径
        """
        return self.domain + name
