# Dockerfile
# 指定基础镜像为python:3.8
FROM python:3.8
# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# 将仓库复制到容器里的标准根目录
WORKDIR /app
# 将当前目录下的requirements.txt复制到/app目录下
#COPY requirements.txt requirements.txt
#COPY setup.py setup.py
# 将当前目录下的所有文件复制到/app目录下
COPY . .
# 使用镜像源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
RUN pip config set install.trusted-host mirrors.aliyun.com
RUN pip install -U pip
# 安装依赖包
RUN pip install -r requirements.txt
# 切到后端工作区后启动 gunicorn
WORKDIR /app/apps/backend
CMD ["gunicorn", "web.application:app", "-c", "./web/gunicorn.config.py"]
