# 빌드 스테이지: 애플리케이션을 빌드하는 단계
FROM node:22-alpine AS builder

# 작업 디렉토리 설정 (빌드 스테이지에서 사용)
WORKDIR /frontend

# 🔑 빌드 시점에 환경변수 받기 (중요!)
# React는 빌드 타임에 환경변수를 정적 파일에 포함시킴
# 따라서 Docker 빌드할 때 반드시 환경변수를 전달해야 함

# ARG: docker 이미지를 빌드 할때만 사용하는 변수 
# ENV: 컨테이너 실행시 사용할 환경 변수 
ARG VITE_FASTAPI_HOST
ENV VITE_FASTAPI_HOST=$VITE_FASTAPI_HOST

# package.json과 package-lock.json만 먼저 복사 
COPY package*.json ./

# package-lock.json을 기준으로 정확한 버전의 패키지 설치
RUN npm ci 

# 소스 코드 전체를 컨테이너로 복사
COPY . .

# 빌드 실행 (dist 또는 build 폴더에 결과물 생성)
# Vite의 경우 /frontend/dist에 빌드 결과가 생성됨 (npm create vite@latest frontend 명령어에서 vite는 빌드 도구)
RUN npm run build

# 프로덕션 스테이지: 실제로 실행될 최종 이미지
FROM node:22-alpine

# 작업 디렉토리 설정 (프로덕션 스테이지에서 사용)
WORKDIR /frontend

# serve 패키지를 전역으로 설치
# serve는 빌드된 정적 파일(dist)를 브라우저에서 확인하기 위한 웹 서버
RUN npm install -g serve

# 📦 빌드 스테이지에서 빌드된 결과물만 복사
# /frontend/dist (builder 스테이지) → /frontend/dist (현재 스테이지)
# 이렇게 하면 node_modules, 소스 코드 등 불필요한 파일은 제외됨
COPY --from=builder /frontend/dist ./dist

# serve 패키지의 기본 포트는 3000번 포트
EXPOSE 3000

# 🚀 컨테이너 시작 시 실행할 명령어
# -s dist: dist 폴더를 SPA(Single Page Application) 모드로 서빙
# -l 3000: 3000번 포트에서 실행
CMD ["serve", "-s", "dist", "-l", "3000"]