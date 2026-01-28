# 部署步骤

1. 本地，把代码推到远程仓库

```
git init
git add .
git commit -m "init deploy"
git remote add origin <仓库地址>
git push -u origin main
```

> 如果已经是 Git 仓库，直接 git push 即可。

2. 终端 SSH 到服务器

```
ssh username@server_ip
```

3. 在服务器上拉代码

```
# 找一个放项目的目录
cd /opt
git clone <仓库地址> CarbonCount
cd CarbonCount
```

4. 在服务器上启动或更新服务

```
# 第一次部署会根据 Dockerfile 构建镜像，然后启动容器。
docker compose up -d --build

cd /opt/CarbonCount
# 拉取最新代码
git pull
docker compose up -d --build
```
