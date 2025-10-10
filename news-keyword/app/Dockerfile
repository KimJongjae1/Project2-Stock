# PySpark와 Java 호환성을 위해 Ubuntu 기반 이미지 사용
FROM ubuntu:20.04

# 비대화형 설치를 위한 환경 변수
ENV DEBIAN_FRONTEND=noninteractive

# Python 3.9와 Java 8 설치 (PySpark 3.3.0과 호환성 최고)
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    python3-pip \
    openjdk-8-jdk \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Python3.9을 기본 python으로 설정
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# pip 업그레이드
RUN python -m pip install --upgrade pip

# 작업 디렉토리 설정
WORKDIR /app

# Java 환경 변수 설정 (Java 8 - PySpark와 완벽 호환)
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# PySpark Java 호환성 설정
ENV PYSPARK_PYTHON=/usr/bin/python
ENV PYSPARK_DRIVER_PYTHON=/usr/bin/python
ENV SPARK_HOME=/usr/local/lib/python3.9/dist-packages/pyspark

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치 (타임아웃 늘림)
RUN pip install --no-cache-dir --timeout 1000 -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# spark/data 디렉토리 생성 (실제 환경에서는 볼륨 마운트 사용)
RUN mkdir -p spark/data

# .env 파일이 있다면 복사 (선택사항)
# COPY .env .env

# 환경 변수 설정 (기본값)
ENV OPENAI_API_KEY=""
ENV LOG_LEVEL="INFO"
ENV DEBUG="False"

# 포트 노출
EXPOSE 8888

# 애플리케이션 실행
CMD ["python", "main.py"]
