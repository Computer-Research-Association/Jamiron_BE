FROM python:3.11.13-bookworm
LABEL authors="seyoung"

# 워킹디렉토리
WORKDIR /home/Jamiron_BE

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

# 1) 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    default-libmysqlclient-dev \
    libpq-dev \
    pkg-config \
    libfreetype6-dev \
    libharfbuzz-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libgl1 \
    libglib2.0-0 \
&& rm -rf /var/lib/apt/lists/*


ENV TZ=Asia/Seoul


# 타임존 - 시간대를 한국시간대로 설정
ENV TZ=Asia/Seoul