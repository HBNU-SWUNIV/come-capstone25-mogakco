#!/bin/bash

# Dyslexia AI 프로젝트 실행 스크립트
# 작성자: Claude Code
# 설명: 프로젝트 설정부터 실행까지 자동화

set -e  # 오류 발생 시 스크립트 종료

echo "🚀 Dyslexia AI 프로젝트 실행 스크립트"
echo "=================================="

# 가상 환경 생성
if [ ! -d ".venv" ]; then
    echo "📦 가상 환경 생성 중..."
    python3 -m venv .venv
else
    echo "✅ 가상 환경이 이미 존재합니다."
fi

# 가상 환경 활성화
echo "🔄 가상 환경 활성화 중..."
source .venv/bin/activate

# pip 업데이트
echo "⬆️ pip 업데이트 중..."
python -m pip install --upgrade pip

# 패키지 설치
echo "📥 패키지 설치 중..."
pip install -r requirements.txt

# 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️ .env 파일이 없습니다. 환경 변수를 설정해주세요."
    echo "필요한 환경 변수:"
    echo "  - ANTHROPIC_API_KEY"
    echo "  - REPLICATE_API_TOKEN"
    echo "  - REDIS_URL (선택사항)"
    exit 1
fi

# 서버 실행
echo "🎯 서버 실행 중..."
echo "접속 URL:"
echo "  - Health test: http://127.0.0.1:10300"
echo "  - API 문서: http://127.0.0.1:10300/docs"
echo "  - ReDoc: http://127.0.0.1:10300/redoc"
echo ""
echo "서버를 중지하려면 Ctrl+C를 누르세요."
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 10300