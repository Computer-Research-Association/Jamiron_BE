FROM python:3.11.13-bookworm
LABEL authors="seyoung"

# 워킹디렉토리
WORKDIR /home/Jamiron_BEFROM python:3.11.13-bookworm
LABEL authors="seyoung"

WORKDIR /home/Jamiron_BE/src/app

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

# 2) requirements.txt 복사 후 설치
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt

# 3) 앱 전체 복사
COPY . /home/Jamiron_BE

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

ENV TZ=Asia/Seoul


# 파이썬 패키지
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# 타임존 - 시간대를 한국시간대로 설정
ENV TZ=Asia/Seoul