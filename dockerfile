# 使用官方 Python 3.10 精简版镜像作为基础
FROM python:3.10-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    UPLOAD_FOLDER=/app/docs/uploads \
    OUTPUT_FOLDER=/app/docs/output

# 设置工作目录
WORKDIR /app

# 复制应用程序文件
COPY . /app

# 安装必要的软件包
RUN apt-get update && apt-get install -y \
    flatpak \
    && rm -rf /var/lib/apt/lists/*

# 添加 Flathub 远程仓库
RUN flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# 安装 PrusaSlicer
RUN flatpak install -y flathub com.prusa3d.PrusaSlicer

# Allow PrusaSlicer access to certain directories
RUN flatpak override --filesystem=/app/docs --user com.prusa3d.PrusaSlicer

# 安装 Python 依赖
RUN pip install --no-cache-dir flask

# 确保上传和输出目录存在
RUN mkdir -p $UPLOAD_FOLDER $OUTPUT_FOLDER

# 暴露 Flask 端口
EXPOSE 5000

# 运行应用程序
CMD ["python", "app.py"]
