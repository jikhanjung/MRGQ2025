#!/usr/bin/env python3
"""
QR 코드에 웹페이지 컬러 스킴에 맞는 그라데이션 적용
"""

from PIL import Image, ImageDraw
import numpy as np

def hex_to_rgb(hex_color):
    """헥스 컬러를 RGB 튜플로 변환"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def apply_gradient_to_qr(input_path, output_path):
    """QR 코드에 그라데이션 적용"""
    
    # 웹페이지에서 사용하는 주요 컬러들 (채도 높은 빨강, 넓은 영역)
    color1 = hex_to_rgb('#1e3a8a')  # 진한 파랑
    color2 = hex_to_rgb('#3b82f6')  # 밝은 파랑  
    color3 = hex_to_rgb('#ff0040')  # 채도 높은 빨강
    
    # 원본 QR 코드 로드
    qr_img = Image.open(input_path).convert('RGBA')
    width, height = qr_img.size
    
    # 그라데이션 이미지 생성 (대각선 그라데이션)
    gradient = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(gradient)
    
    # NumPy 배열로 변환하여 그라데이션 생성
    arr = np.zeros((height, width, 4), dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            # 대각선 그라데이션 계산 (붉은 영역 확장)
            diagonal_pos = (x + y) / (width + height)
            
            if diagonal_pos <= 0.3:
                # color1에서 color2로 (짧은 구간)
                t = diagonal_pos / 0.3  # 0~1로 정규화
                r = int(color1[0] * (1-t) + color2[0] * t)
                g = int(color1[1] * (1-t) + color2[1] * t)
                b = int(color1[2] * (1-t) + color2[2] * t)
            else:
                # color2에서 color3으로 (긴 구간 - 붉은 영역 확장)
                t = (diagonal_pos - 0.3) / 0.7  # 0~1로 정규화
                r = int(color2[0] * (1-t) + color3[0] * t)
                g = int(color2[1] * (1-t) + color3[1] * t)
                b = int(color2[2] * (1-t) + color3[2] * t)
            
            arr[y, x] = [r, g, b, 255]
    
    gradient = Image.fromarray(arr, 'RGBA')
    
    # 원본 QR 코드의 알파 채널을 사용하여 마스크 생성
    qr_array = np.array(qr_img)
    
    # 검은색 픽셀(QR 코드 부분)을 찾아서 마스크 생성
    # 흰색이 아닌 모든 픽셀을 QR 코드로 간주
    if len(qr_array.shape) == 3 and qr_array.shape[2] == 4:  # RGBA
        # 알파 채널이 있는 경우
        mask = qr_array[:,:,3] > 128  # 알파값이 128보다 큰 픽셀
        # 동시에 검은색에 가까운 픽셀만 선택
        is_dark = (qr_array[:,:,0] < 128) & (qr_array[:,:,1] < 128) & (qr_array[:,:,2] < 128)
        mask = mask & is_dark
    else:  # RGB
        qr_array = np.array(qr_img.convert('RGB'))
        # 검은색에 가까운 픽셀 찾기 (RGB 값이 모두 128 미만)
        mask = (qr_array[:,:,0] < 128) & (qr_array[:,:,1] < 128) & (qr_array[:,:,2] < 128)
    
    # 결과 이미지 생성
    result = Image.new('RGBA', (width, height), (255, 255, 255, 0))  # 투명 배경
    result_array = np.array(result)
    gradient_array = np.array(gradient)
    
    # 마스크된 부분에만 그라데이션 적용
    result_array[mask] = gradient_array[mask]
    
    # 투명하지 않은 부분의 알파값을 255로 설정
    result_array[mask, 3] = 255
    
    result = Image.fromarray(result_array, 'RGBA')
    
    # 배경을 흰색으로 설정하여 최종 이미지 생성
    final_img = Image.new('RGB', (width, height), 'white')
    final_img.paste(result, mask=result.split()[3])  # 알파 채널을 마스크로 사용
    
    # 저장
    final_img.save(output_path, 'PNG')
    print(f"그라데이션 QR 코드가 저장되었습니다: {output_path}")

if __name__ == "__main__":
    input_file = "mrgq2025_qr.png"
    output_file = "mrgq2025_qr_gradient.png"
    
    try:
        apply_gradient_to_qr(input_file, output_file)
        print("✅ QR 코드 그라데이션 적용 완료!")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")