FROM python:3.11.13-bookworm
LABEL authors="seyoung"

# 워킹디렉토리
WORKDIR /home/Jamiron_BE/src/app

# 파이썬 패키지
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# 타임존 - 시간대를 한국시간대로 설정
ENV TZ=Asia/Seoul