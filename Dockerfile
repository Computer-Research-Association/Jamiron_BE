FROM python:3.11.13-bookworm
LABEL authors="seyoung"

# 워킹디렉토리
WORKDIR /home/Jamiron_BE

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir --prefer-binary -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    fonts-nanum fonts-liberation \   # (한글/문서 깨짐 방지)
    unzip curl \                     # (webdriver-manager 안정화)
 && rm -rf /var/lib/apt/lists/*


ENV TZ=Asia/Seoul


# 타임존 - 시간대를 한국시간대로 설정
ENV TZ=Asia/Seoul