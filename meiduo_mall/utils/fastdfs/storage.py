from django.core.files.storage import Storage

class FastDFSStorage(Storage):
    """自定义文件存储系统"""

    def _save(self, name, content, max_length=None):
        pass

    def _open(self, name, mode='rb'):
        pass

    def url(self, name):
        # name=Remote file_id
        #'Remote file_id': 'group1/M00/00/02/wKjllFzhEE6AFbTWAALd0X8OZb4408.jpg',
        #http://192.168.229.148:8888/+group1/M00/00/02/wKjllFzhEE6AFbTWAALd0X8OZb4408.jpg
        # return 'http://192.168.229.148:8888/' + name

        return 'http://image.meiduo.site:8888/' + name