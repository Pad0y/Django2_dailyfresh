# 使用py3fdfs与django项目交互
```text
# 根据pypi中py3fdfs的示例: 在python3命令行执行下面两句
>>> from fdfs_client.client import *
>>> client = Fdfs_client('/etc/fdfs/client.conf')
```
在执行client = Fdfs_client('/etc/fdfs/client.conf')时，
会报错：TypeError: type object argument after ** must be a mapping, not str

解决方法：
1)根据报错位置，定位到xx/lib/python3.6/site-packages/fdfs_client/client.py。
```python
class Fdfs_client(object):
    '''
    Class Fdfs_client implemented Fastdfs client protol ver 3.08.

    It's useful upload, download, delete file to or from fdfs server, etc. It's uses
    connection pool to manage connection to server.
    '''

    def __init__(self, trackers, poolclass=ConnectionPool):
        self.trackers = trackers
        self.tracker_pool = poolclass(**self.trackers)
        self.timeout = self.trackers['timeout']
        return None
```
Fdfs_client的初始化要传递trackers, 而不是'/etc/fdfs/client.conf'字符串。
接着观察到 文件顶部 有如下代码:
```python
def get_tracker_conf(conf_path='client.conf'):
    cf = Fdfs_ConfigParser()
    tracker = {}
    try:
        cf.read(conf_path)
        timeout = cf.getint('__config__', 'connect_timeout')
        tracker_list = cf.get('__config__', 'tracker_server')
        if isinstance(tracker_list, str):
            tracker_list = [tracker_list]
        tracker_ip_list = []
        for tr in tracker_list:
            tracker_ip, tracker_port = tr.split(':')
            tracker_ip_list.append(tracker_ip)
        tracker['host_tuple'] = tuple(tracker_ip_list)
        tracker['port'] = int(tracker_port)
        tracker['timeout'] = timeout
        tracker['name'] = 'Tracker Pool'
    except:
        raise
    return tracker
```
get_tracker_conf(conf_path='client.conf'):不就是 返回一个tracker么，而且其接收的参数是client.conf配置文件的路径。
get_tracker_conf(conf_path='client.conf'):函数的作用是：把配置文件client.conf中信息，提取到一个字典tracker中，并返回该字典tracker。

**解决办法**
```python
trackers = get_tracker_conf('./utils/fdfs/client.conf')
client = Fdfs_client(trackers)
```
