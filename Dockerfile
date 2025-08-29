FROM python:3.11.13-bookworm
LABEL authors="seyoung"

# 워킹디렉토리
WORKDIR /home/Jamiron_BE

COPY requirements.txt .
COPY .env .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir --prefer-binary -r requirements.txt \
 && pip install torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install sentence-transformers==5.0.0 --no-deps\
 && pip install --no-cache-dir transformers==4.53.3 scikit-learn==1.6.1


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    libgl1 \
    libglib2.0-0 \
    fonts-nanum fonts-liberation \
    unzip curl \
    chromium \
    chromium-driver \
 && rm -rf /var/lib/apt/lists/*

# Google Chrome 설치
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# ChromeDriver 설치 (Chrome 버전에 맞게)
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+' | head -1) \
    && DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") \
    && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip


ENV TZ=Asia/Seoul


# 타임존 - 시간대를 한국시간대로 설정
ENV TZ=Asia/Seoul