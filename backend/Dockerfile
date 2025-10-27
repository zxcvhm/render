FROM python:3.13-slim

WORKDIR /backend

# 시스템 의존성 설치 (psycopg2 빌드에 필요)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --no-cache-dir --upgrade pip

# 의존성 파일만 먼저 복사 (캐싱 최적화)
COPY requirements.txt ./

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]