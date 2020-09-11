## docker-compose一键启动
```text
dev分支是docker-compose模式，配置文件需要稍作修改
其中compose文件夹包含着项目和FDFS服务的dockerfile，
有什么配置和具体的配置过程都可以在dockerfile中得到详细的答案，
如有疑问欢迎提出issue。具体的，启动方式如下
```
```bash
# 进入compse文件夹
cd /path/to/project/compose
# 如需要看到详细的控制台输出信息可以取消-d参数
docker-compose up -d
# 访问方式, 具体的映射过程可以看docker-compose.yml
http://ip:8001
```

