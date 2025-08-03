#!/bin/bash

# MRGQ2025 웹서버 시작 스크립트
# 포트 8080에서 HTTP 서버를 시작합니다.

PORT=8080
PROJECT_DIR="/home/jikhanjung/projects/MRGQ2025"
LOG_FILE="$PROJECT_DIR/server.log"
PID_FILE="$PROJECT_DIR/server.pid"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== MRGQ2025 웹서버 시작 스크립트 ===${NC}"

# 기존 서버 프로세스 확인 및 종료
echo -e "${YELLOW}기존 서버 프로세스 확인 중...${NC}"
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}기존 서버 프로세스 (PID: $OLD_PID) 종료 중...${NC}"
        kill $OLD_PID
        sleep 2
    fi
    rm -f "$PID_FILE"
fi

# 포트 사용 중인 프로세스 확인
EXISTING_PROCESS=$(lsof -ti:$PORT 2>/dev/null)
if [ ! -z "$EXISTING_PROCESS" ]; then
    echo -e "${YELLOW}포트 $PORT 사용 중인 프로세스 (PID: $EXISTING_PROCESS) 종료 중...${NC}"
    kill $EXISTING_PROCESS 2>/dev/null
    sleep 2
fi

# 프로젝트 디렉토리로 이동
cd "$PROJECT_DIR" || {
    echo -e "${RED}오류: 프로젝트 디렉토리를 찾을 수 없습니다: $PROJECT_DIR${NC}"
    exit 1
}

# 서버 시작
echo -e "${GREEN}포트 $PORT 에서 웹서버 시작 중...${NC}"
nohup python3 -m http.server $PORT --bind 0.0.0.0 > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# PID 파일에 저장
echo $SERVER_PID > "$PID_FILE"

# 서버 시작 확인
sleep 2
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 웹서버가 성공적으로 시작되었습니다!${NC}"
    echo -e "${GREEN}   - PID: $SERVER_PID${NC}"
    echo -e "${GREEN}   - 포트: $PORT${NC}"
    echo -e "${GREEN}   - 로그 파일: $LOG_FILE${NC}"
    echo -e "${GREEN}   - PID 파일: $PID_FILE${NC}"
    echo ""
    echo -e "${BLUE}접속 URL:${NC}"
    echo -e "${BLUE}   - 로컬: http://localhost:$PORT${NC}"
    echo -e "${BLUE}   - 네트워크: http://$(hostname -I | awk '{print $1}'):$PORT${NC}"
    echo ""
    echo -e "${YELLOW}서버 종료: ./stop_server.sh${NC}"
    echo -e "${YELLOW}로그 확인: tail -f $LOG_FILE${NC}"
else
    echo -e "${RED}❌ 웹서버 시작에 실패했습니다.${NC}"
    echo -e "${RED}로그를 확인해주세요: cat $LOG_FILE${NC}"
    exit 1
fi