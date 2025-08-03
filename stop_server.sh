#!/bin/bash

# MRGQ2025 웹서버 종료 스크립트

PROJECT_DIR="/home/jikhanjung/projects/MRGQ2025"
PID_FILE="$PROJECT_DIR/server.pid"
PORT=8080

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== MRGQ2025 웹서버 종료 스크립트 ===${NC}"

# PID 파일에서 서버 프로세스 종료
if [ -f "$PID_FILE" ]; then
    SERVER_PID=$(cat "$PID_FILE")
    echo -e "${YELLOW}PID 파일에서 서버 프로세스 확인: $SERVER_PID${NC}"
    
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}서버 프로세스 (PID: $SERVER_PID) 종료 중...${NC}"
        kill $SERVER_PID
        sleep 2
        
        # 강제 종료가 필요한 경우
        if ps -p $SERVER_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}강제 종료 중...${NC}"
            kill -9 $SERVER_PID
            sleep 1
        fi
        
        if ! ps -p $SERVER_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 서버가 성공적으로 종료되었습니다.${NC}"
        else
            echo -e "${RED}❌ 서버 종료에 실패했습니다.${NC}"
        fi
    else
        echo -e "${YELLOW}해당 PID의 프로세스가 이미 종료되어 있습니다.${NC}"
    fi
    
    rm -f "$PID_FILE"
    echo -e "${GREEN}PID 파일을 삭제했습니다.${NC}"
else
    echo -e "${YELLOW}PID 파일을 찾을 수 없습니다.${NC}"
fi

# 포트 사용 중인 다른 프로세스 확인 및 종료
echo -e "${YELLOW}포트 $PORT 사용 중인 프로세스 확인...${NC}"
EXISTING_PROCESSES=$(lsof -ti:$PORT 2>/dev/null)

if [ ! -z "$EXISTING_PROCESSES" ]; then
    echo -e "${YELLOW}포트 $PORT 사용 중인 프로세스들을 종료합니다:${NC}"
    for pid in $EXISTING_PROCESSES; do
        echo -e "${YELLOW}  - PID: $pid${NC}"
        kill $pid 2>/dev/null
    done
    sleep 2
    
    # 강제 종료 확인
    REMAINING_PROCESSES=$(lsof -ti:$PORT 2>/dev/null)
    if [ ! -z "$REMAINING_PROCESSES" ]; then
        echo -e "${YELLOW}강제 종료 중...${NC}"
        for pid in $REMAINING_PROCESSES; do
            kill -9 $pid 2>/dev/null
        done
    fi
    echo -e "${GREEN}포트 $PORT 정리 완료.${NC}"
else
    echo -e "${GREEN}포트 $PORT 사용 중인 프로세스가 없습니다.${NC}"
fi

echo -e "${GREEN}웹서버 종료 완료!${NC}"