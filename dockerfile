# 使用官方 Python 3.10 精简版镜像作为基础
FROM python:3.10-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    UPLOAD_FOLDER=/home/docs/uploads \
    OUTPUT_FOLDER=/home/docs/output \
    HOME=/home
    
# 安装必要的软件包
RUN apt-get update && apt-get install -y \
    flatpak \
    && rm -rf /var/lib/apt/lists/*

# 添加 Flathub 远程仓库
RUN flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# 安装 PrusaSlicer
RUN flatpak install -y flathub com.prusa3d.PrusaSlicer

# Allow PrusaSlicer access to the documents folder inside /home
RUN flatpak override --filesystem=/home/docs --user com.prusa3d.PrusaSlicer

# 设置工作目录为 /home/docs
WORKDIR /home/docs

# 复制当前目录（包含 app.py 和 config.ini）中的所有文件到 /home/docs
COPY . /home/docs

# 安装 Python 依赖
RUN pip install --no-cache-dir -r /home/docs/requirements.txt

# 确保上传和输出目录存在
RUN mkdir -p $UPLOAD_FOLDER $OUTPUT_FOLDER

# 暴露 Flask 端口
EXPOSE 5000

# 运行应用程序
CMD ["python", "app.py"]
