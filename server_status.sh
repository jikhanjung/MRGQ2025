#!/bin/bash

# MRGQ2025 웹서버 상태 확인 스크립트

PROJECT_DIR="/home/jikhanjung/projects/MRGQ2025"
PID_FILE="$PROJECT_DIR/server.pid"
LOG_FILE="$PROJECT_DIR/server.log"
PORT=8080

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== MRGQ2025 웹서버 상태 ===${NC}"

# PID 파일 확인
if [ -f "$PID_FILE" ]; then
    SERVER_PID=$(cat "$PID_FILE")
    echo -e "${BLUE}PID 파일: $PID_FILE${NC}"
    echo -e "${BLUE}저장된 PID: $SERVER_PID${NC}"
    
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 서버가 실행 중입니다 (PID: $SERVER_PID)${NC}"
        
        # 프로세스 정보 표시
        echo -e "${BLUE}프로세스 정보:${NC}"
        ps -p $SERVER_PID -o pid,ppid,cmd,etime,pcpu,pmem
        
    else
        echo -e "${RED}❌ PID 파일은 있지만 해당 프로세스가 실행되지 않습니다.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  PID 파일이 없습니다.${NC}"
fi

# 포트 사용 상태 확인
echo -e "\n${BLUE}포트 $PORT 사용 상태:${NC}"
PORT_PROCESSES=$(lsof -ti:$PORT 2>/dev/null)

if [ ! -z "$PORT_PROCESSES" ]; then
    echo -e "${GREEN}포트 $PORT 사용 중:${NC}"
    lsof -i:$PORT
else
    echo -e "${YELLOW}포트 $PORT 사용 중인 프로세스가 없습니다.${NC}"
fi

# 로그 파일 확인
echo -e "\n${BLUE}로그 파일 상태:${NC}"
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
    LOG_LINES=$(wc -l < "$LOG_FILE")
    echo -e "${GREEN}로그 파일: $LOG_FILE${NC}"
    echo -e "${GREEN}파일 크기: $LOG_SIZE${NC}"
    echo -e "${GREEN}줄 수: $LOG_LINES${NC}"
    
    echo -e "\n${BLUE}최근 로그 (마지막 5줄):${NC}"
    tail -5 "$LOG_FILE"
else
    echo -e "${YELLOW}로그 파일이 없습니다.${NC}"
fi

# 접속 URL 정보
echo -e "\n${BLUE}접속 정보:${NC}"
if [ ! -z "$PORT_PROCESSES" ]; then
    echo -e "${GREEN}로컬 접속: http://localhost:$PORT${NC}"
    echo -e "${GREEN}네트워크 접속: http://$(hostname -I | awk '{print $1}'):$PORT${NC}"
else
    echo -e "${YELLOW}서버가 실행되지 않습니다.${NC}"
fi

# 명령어 안내
echo -e "\n${BLUE}사용 가능한 명령어:${NC}"
echo -e "${YELLOW}서버 시작: ./start_server.sh${NC}"
echo -e "${YELLOW}서버 종료: ./stop_server.sh${NC}"
echo -e "${YELLOW}실시간 로그: tail -f $LOG_FILE${NC}"