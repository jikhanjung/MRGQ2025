#!/usr/bin/env python3
"""
HTML 생성 스크립트
index.html을 템플릿으로 사용하고 program_notes.md에서 내용을 가져와 새로운 index.html을 생성합니다.
"""

import re
import os
from datetime import datetime


def read_file(file_path):
    """파일을 읽어서 내용을 반환합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"오류: '{file_path}' 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None


def parse_markdown_notes(markdown_content):
    """markdown 내용을 파싱하여 프로그램 노트를 추출합니다."""
    notes = []
    
    # ## 로 시작하는 제목으로 구분
    sections = re.split(r'\n## ', markdown_content)
    
    for i, section in enumerate(sections):
        if i == 0:  # 첫 번째 섹션은 제목이므로 건너뛰기
            continue
            
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        title = lines[0].strip()
        content_lines = []
        
        # 제목 다음 줄부터 내용 수집
        for line in lines[1:]:
            line = line.strip()
            if line:  # 빈 줄이 아닌 경우만 추가
                content_lines.append(line)
        
        content = '\n\n'.join(content_lines)
        
        # ID 생성 (특수문자 제거하고 소문자로)
        note_id = re.sub(r'[^a-zA-Z0-9가-힣\s-]', '', title)
        note_id = re.sub(r'\s+', '-', note_id).lower()
        note_id = note_id.replace('--', '-').strip('-')
        
        notes.append({
            'id': note_id,
            'title': title,
            'content': content
        })
    
    return notes


def parse_markdown_invitation(markdown_content):
    """markdown 내용을 파싱하여 초대의 말씀을 추출합니다."""
    # # 제목 제거하고 본문만 추출
    content = re.sub(r'^# .*?\n', '', markdown_content, flags=re.MULTILINE)
    return content.strip()


def parse_markdown_members(markdown_content):
    """markdown 내용을 파싱하여 멤버 정보를 추출합니다."""
    # 한국어/영어 섹션명 매핑
    section_mapping = {
        'Performers': '연주자',
        'Staff': '스태프',
        '연주자': '연주자',
        '스태프': '스태프'
    }
    
    members = {'연주자': [], '스태프': []}
    current_section = None
    current_member = None
    
    lines = markdown_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('## '):
            # 섹션이 바뀔 때 이전 멤버 추가
            if current_member and current_section in members:
                members[current_section].append(current_member)
                current_member = None
            section_name = line[3:].strip()
            current_section = section_mapping.get(section_name, section_name)
        elif line.startswith('### '):
            if current_member and current_section in members:
                members[current_section].append(current_member)
            current_member = {
                'name': line[4:].strip(),
                'description': []
            }
        elif current_member and not line.startswith('#'):
            # HTML div 태그 제거
            clean_line = re.sub(r'<div[^>]*>|</div>', '', line)
            if clean_line:
                current_member['description'].append(clean_line)
    
    # 마지막 멤버 추가
    if current_member and current_section in members:
        members[current_section].append(current_member)
    
    return members


def parse_markdown_program(markdown_content):
    """markdown 내용을 파싱하여 콘서트 프로그램을 추출합니다."""
    program = {'1부': [], '2부': []}
    current_part = None
    current_performers = None
    current_pieces = []
    
    # 섹션명 매핑 (영어 -> 한국어)
    section_mapping = {
        'Part I': '1부',
        'Part II': '2부',
        'Intermission': '인터미션',
        '1부': '1부',
        '2부': '2부',
        '인터미션': '인터미션'
    }
    
    lines = markdown_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('## '):
            # 이전 섹션 저장
            if current_part and current_performers:
                program[current_part].append({
                    'performers': current_performers,
                    'pieces': current_pieces.copy()
                })
                current_pieces = []
            
            section_title = line[3:].strip()
            mapped_section = section_mapping.get(section_title)
            if mapped_section in ['1부', '2부']:
                current_part = mapped_section
            elif mapped_section == '인터미션':
                current_part = '인터미션'
                current_performers = None
            
        elif line.startswith('### '):
            # 이전 연주자 그룹 저장
            if current_part and current_performers and current_part != '인터미션':
                program[current_part].append({
                    'performers': current_performers,
                    'pieces': current_pieces.copy()
                })
                current_pieces = []
            
            # 새 연주자 그룹
            performers_info = line[4:].strip()
            current_performers = performers_info
            
        elif line.startswith('- '):
            # 곡목
            piece = line[2:].strip()
            current_pieces.append(piece)
    
    # 마지막 그룹 저장
    if current_part and current_performers and current_part != '인터미션':
        program[current_part].append({
            'performers': current_performers,
            'pieces': current_pieces
        })
    
    return program


def create_performance_groups():
    """연주 그룹별로 곡을 묶어서 반환합니다."""
    return [
        {
            'name': '4중주 - 오예진, 전예완, 김하진, 조은석',
            'image': '1. 4중주.jpg',
            'pieces': ['조아키노-로시니-도둑까치-서곡']
        },
        {
            'name': '3중주 - 전예완, 오예진, 조은석',
            'image': '2. 3중주.jpg',
            'pieces': ['요한-제바스티안-바흐-토카타와-푸가-d단조-bwv-565']
        },
        {
            'name': '2중주 - 조은석, 오예진',
            'image': '3. 듀오-은석예진.jpg',
            'pieces': ['호르헤-카르도소-밀롱가', '모리스-라벨-죽은-왕녀를-위한-파반느']
        },
        {
            'name': '독주 - 양진호',
            'image': '4. 솔로-진호.jpg',
            'pieces': ['페르난도-소르-마적-주제에-의한-변주곡']
        },
        {
            'name': '2중주 - 전예완, 오예진',
            'image': '5. 듀오-예완예진.jpg',
            'pieces': ['영국-민요-프란시스-커팅-그린슬리브즈', '프란츠-슈베르트-겨울나그네-중-1-안녕히', '에이토르-빌라로부스-브라질풍의-바흐-제5번-1-아리아']
        },
        {
            'name': '2중주 - 김하진, 양진호',
            'image': '6. 듀오-하진진호.jpg',
            'pieces': ['알-디-메올라-그랜드-패션', '마누엘-드-파야-허무한-인생-중-스페인-춤곡-제1번', '이삭-알베니스-카스티야']
        },
        {
            'name': '5중주 - 오예진, 전예완, 김하진, 양진호, 조은석',
            'image': '7. 5중주.jpg',
            'pieces': ['안토닌-드보르자크-교향곡-제9번-신세계로부터-제4악장']
        }
    ]

def create_image_mapping():
    """곡해설 ID와 이미지 파일명을 매핑하는 사전을 생성합니다."""
    return {
        '조아키노-로시니-도둑까치-서곡': '1. 4중주.jpg',
        '요한-제바스티안-바흐-토카타와-푸가-d단조-bwv-565': '2. 3중주.jpg',
        '호르헤-카르도소-밀롱가': '3. 듀오-은석예진.jpg',
        '모리스-라벨-죽은-왕녀를-위한-파반느': '3. 듀오-은석예진.jpg',
        '페르난도-소르-마적-주제에-의한-변주곡': '4. 솔로-진호.jpg',
        '영국-민요-프란시스-커팅-그린슬리브즈': '5. 듀오-예완예진.jpg',
        '프란츠-슈베르트-겨울나그네-중-1-안녕히': '5. 듀오-예완예진.jpg',
        '에이토르-빌라로부스-브라질풍의-바흐-제5번-1-아리아': '5. 듀오-예완예진.jpg',
        '알-디-메올라-그랜드-패션': '6. 듀오-하진진호.jpg',
        '마누엘-드-파야-허무한-인생-중-스페인-춤곡-제1번': '6. 듀오-하진진호.jpg',
        '이삭-알베니스-카스티야': '6. 듀오-하진진호.jpg',
        '안토닌-드보르자크-교향곡-제9번-신세계로부터-제4악장': '7. 5중주.jpg'
    }


def generate_program_notes_html(notes, is_english=False):
    """프로그램 노트들을 HTML로 변환합니다."""
    html_parts = []
    
    # 연주 그룹 정보 가져오기
    performance_groups = create_performance_groups_en() if is_english else create_performance_groups()
    
    # 노트들을 ID로 찾을 수 있도록 딕셔너리로 변환
    notes_dict = {note['id']: note for note in notes}
    
    # 각 연주 그룹별로 섹션 생성
    for group in performance_groups:
        group_html_parts = []
        
        # 그룹 제목과 이미지 추가
        group_html_parts.append(f'''            <div class="performance-group-section">
                <h3 style="color: #2c1810; border-bottom: 2px solid #8b6f3a; padding-bottom: 10px; margin-bottom: 20px;">{group['name']}</h3>
                <div style="text-align: center; margin: 20px 0 30px 0;">
                    <img src="{group['image']}" alt="{group['name']}" style="max-width: 800px; width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); object-fit: cover;">
                </div>''')
        
        # 그룹 내의 각 곡에 대한 해설 추가
        for piece_id in group['pieces']:
            if piece_id not in notes_dict:
                continue
                
            note = notes_dict[piece_id]
            
            # 내용을 문단별로 나누기
            paragraphs = note['content'].split('\n\n')
            paragraph_html = []
            
            # 영어 제목 처리 플래그
            has_english_title = False
            
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    # 첫 번째 문단이 ###으로 시작하면 영어 제목(부제목)으로 처리
                    if i == 0 and paragraph.strip().startswith('###'):
                        # 영어 버전에서는 부제목을 표시하지 않음 (이미 메인 제목이 영어이므로)
                        if not is_english:
                            english_title = paragraph.strip()[3:].strip()
                            if ", " in english_title:
                                e_composer, e_title = english_title.split(", ", 1)
                                paragraph_html.append(f'                    <h5 style="color: #8b6f3a; margin-top: -5px; margin-bottom: 20px; font-weight: 400; font-size: 1.1em;"><span style="color: #4a2c1a;">{e_composer}</span>, <span style="color: #8b6f3a; font-style: italic;">{e_title}</span></h5>')
                            else:
                                paragraph_html.append(f'                    <h5 style="color: #8b6f3a; margin-top: -5px; margin-bottom: 20px; font-weight: 400; font-size: 1.1em;">{english_title}</h5>')
                            has_english_title = True
                    else:
                        # 마크다운 이탤릭 변환: *(by 작성자)* -> <em>(by 작성자)</em>
                        paragraph = re.sub(r'\*(.*?)\*', r'<em>\1</em>', paragraph.strip())
                        paragraph_html.append(f'                    <p>{paragraph}</p>')
            
            # 한국어 제목도 작곡가와 곡명을 분리하여 색상 구분
            if ", " in note['title']:
                k_composer, k_title = note['title'].split(", ", 1)
                korean_title_html = f'<span style="color: #4a2c1a;">{k_composer}</span>, <span style="color: #8b6f3a; font-style: italic;">{k_title}</span>'
            else:
                korean_title_html = note['title']
                
            # 개별 곡 해설 div 생성
            note_html = f'''                <div id="{note['id']}" class="note" style="margin-left: 20px; margin-top: 30px;">
                    <h4 style="font-size: 1.3em; margin-bottom: 5px;">{korean_title_html}</h4>
{chr(10).join(paragraph_html)}
                </div>'''
            
            group_html_parts.append(note_html)
        
        # 그룹 섹션 닫기
        group_html_parts.append('            </div>')
        
        html_parts.append('\n'.join(group_html_parts))
    
    return '\n\n'.join(html_parts)


def generate_invitation_html(invitation_content):
    """초대의 말씀 내용을 HTML로 변환합니다."""
    # div 태그가 포함된 멀티라인 블록을 먼저 찾아서 하나로 합치기
    if '<div' in invitation_content:
        # div 태그의 시작과 끝을 찾아서 그 사이의 모든 내용을 하나의 블록으로 처리
        div_start = invitation_content.find('<div')
        if div_start != -1:
            div_end = invitation_content.find('</div>', div_start)
            if div_end != -1:
                # div 태그 앞의 내용
                before_div = invitation_content[:div_start].rstrip()
                # div 태그 전체 (여러 줄 포함)
                div_block = invitation_content[div_start:div_end + 6]  # </div> 포함
                # div 태그 뒤의 내용
                after_div = invitation_content[div_end + 6:].lstrip()
                
                # 다시 합쳐서 문단 분할
                if after_div:
                    combined_content = before_div + '\n\n' + div_block + '\n\n' + after_div
                else:
                    combined_content = before_div + '\n\n' + div_block
                
                invitation_content = combined_content
    
    # 마크다운 문단을 HTML p 태그로 변환
    paragraphs = invitation_content.split('\n\n')
    paragraph_html = []
    
    for paragraph in paragraphs:
        if paragraph.strip():
            # div 태그가 있는 경우 HTML 블록으로 처리
            if '<div' in paragraph and '</div>' in paragraph:
                # **텍스트** -> <strong>텍스트</strong>
                paragraph = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', paragraph)
                # *텍스트* -> <em>텍스트</em>
                paragraph = re.sub(r'\*(.*?)\*', r'<em>\1</em>', paragraph)
                # 줄바꿈 처리
                paragraph = paragraph.replace('\n', '<br>')
                paragraph_html.append(f'                {paragraph}')
            else:
                # **텍스트** -> <strong>텍스트</strong>
                paragraph = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', paragraph)
                # *텍스트* -> <em>텍스트</em>
                paragraph = re.sub(r'\*(.*?)\*', r'<em>\1</em>', paragraph)
                # 줄바꿈 처리
                paragraph = paragraph.replace('\n', '<br>')
                paragraph_html.append(f'                <p>{paragraph}</p>')
    
    # 모든 문단을 하나의 note div 안에 넣기
    html_content = '            <div class="note">\n' + '\n'.join(paragraph_html) + '\n            </div>'
    
    return html_content


def create_piece_to_id_mapping():
    """곡목을 프로그램 노트 ID로 매핑하는 사전을 생성합니다."""
    return {
        '조아키노 로시니, 《도둑까치》 서곡': '조아키노-로시니-도둑까치-서곡',
        '요한 제바스티안 바흐, 토카타와 푸가 D단조 (BWV 565)': '요한-제바스티안-바흐-토카타와-푸가-d단조-bwv-565',
        '호르헤 카르도소, 밀롱가': '호르헤-카르도소-밀롱가',
        '모리스 라벨, 죽은 왕녀를 위한 파반느': '모리스-라벨-죽은-왕녀를-위한-파반느',
        '페르난도 소르, 《마적》 주제에 의한 변주곡': '페르난도-소르-마적-주제에-의한-변주곡',
        '영국 민요 / 프란시스 커팅, 그린슬리브즈': '영국-민요-프란시스-커팅-그린슬리브즈',
        '프란츠 슈베르트, 《겨울나그네》 중 1. 안녕히': '프란츠-슈베르트-겨울나그네-중-1-안녕히',
        '에이토르 빌라로부스, 브라질풍의 바흐 제5번, 1. 아리아': '에이토르-빌라로부스-브라질풍의-바흐-제5번-1-아리아',
        '알 디 메올라, 그랜드 패션': '알-디-메올라-그랜드-패션',
        '마누엘 드 파야, 《허무한 인생》 중 스페인 춤곡 제1번': '마누엘-드-파야-허무한-인생-중-스페인-춤곡-제1번',
        '이삭 알베니스, 카스티야': '이삭-알베니스-카스티야',
        '안토닌 드보르자크, 교향곡 제9번 "신세계로부터" 제4악장': '안토닌-드보르자크-교향곡-제9번-신세계로부터-제4악장'
    }


def create_performance_groups_en():
    """영어 버전: 연주 그룹별로 곡을 묶어서 반환합니다."""
    return [
        {
            'name': 'Quartet - Oh Yejin, Jeon Yewan, Kim Hajin, Cho Eunseok',
            'image': '1. 4중주.jpg',
            'pieces': ['gioachino-rossini-1792-1868-overture-to-la-gazza-ladra']
        },
        {
            'name': 'Trio - Jeon Yewan, Oh Yejin, Cho Eunseok',
            'image': '2. 3중주.jpg',
            'pieces': ['johann-sebastian-bach-1685-1750-toccata-and-fugue-in-d-minor-bwv-565']
        },
        {
            'name': 'Duo - Cho Eunseok, Oh Yejin',
            'image': '3. 듀오-은석예진.jpg',
            'pieces': ['jorge-cardoso-1949-milonga-from-24-piezas-sudamericanas', 'maurice-ravel-1875-1937-pavane-pour-une-infante-dfunte']
        },
        {
            'name': 'Solo - Yang Jinho',
            'image': '4. 솔로-진호.jpg',
            'pieces': ['fernando-sor-1778-1839-introduction-and-variations-on-a-theme-by-mozart-op9']
        },
        {
            'name': 'Duo - Jeon Yewan, Oh Yejin',
            'image': '5. 듀오-예완예진.jpg',
            'pieces': ['anon-francis-cutting-c1550-1596-greensleeves', 'franz-schubert-1797-1828-winterreise-op89-d911-1-gute-nacht', 'heitor-villa-lobos-1887-1959-bachianas-brasileiras-no5-1-aria-cantilena']
        },
        {
            'name': 'Duo - Kim Hajin, Yang Jinho',
            'image': '6. 듀오-하진진호.jpg',
            'pieces': ['al-di-meola-1954-the-grande-passion', 'manuel-de-falla-18761946-spanish-dance-no1-from-la-vida-breve', 'isaac-albniz-1860-1909-castilla-seguidillas-from-suite-espaola-op47']
        },
        {
            'name': 'Quintet - Oh Yejin, Jeon Yewan, Kim Hajin, Yang Jinho, Cho Eunseok',
            'image': '7. 5중주.jpg',
            'pieces': ['antonn-dvok-1841-1904-symphony-no9-in-e-minor-from-the-new-world-op95-iv-finale-allegro-con-fuoco']
        }
    ]

def create_image_mapping_en():
    """영어 곡해설 ID와 이미지 파일명을 매핑하는 사전을 생성합니다."""
    return {
        'gioachino-rossini-1792-1868-overture-to-la-gazza-ladra': '1. 4중주.jpg',
        'johann-sebastian-bach-1685-1750-toccata-and-fugue-in-d-minor-bwv-565': '2. 3중주.jpg',
        'jorge-cardoso-1949-milonga-from-24-piezas-sudamericanas': '3. 듀오-은석예진.jpg',
        'maurice-ravel-1875-1937-pavane-pour-une-infante-dfunte': '3. 듀오-은석예진.jpg',
        'fernando-sor-1778-1839-introduction-and-variations-on-a-theme-by-mozart-op9': '4. 솔로-진호.jpg',
        'anon-francis-cutting-c1550-1596-greensleeves': '5. 듀오-예완예진.jpg',
        'franz-schubert-1797-1828-winterreise-op89-d911-1-gute-nacht': '5. 듀오-예완예진.jpg',
        'heitor-villa-lobos-1887-1959-bachianas-brasileiras-no5-1-aria-cantilena': '5. 듀오-예완예진.jpg',
        'al-di-meola-1954-the-grande-passion': '6. 듀오-하진진호.jpg',
        'manuel-de-falla-18761946-spanish-dance-no1-from-la-vida-breve': '6. 듀오-하진진호.jpg',
        'isaac-albniz-1860-1909-castilla-seguidillas-from-suite-espaola-op47': '6. 듀오-하진진호.jpg',
        'antonn-dvok-1841-1904-symphony-no9-in-e-minor-from-the-new-world-op95-iv-finale-allegro-con-fuoco': '7. 5중주.jpg'
    }


def create_piece_to_id_mapping_en():
    """영어 곡목을 프로그램 노트 ID로 매핑하는 사전을 생성합니다."""
    return {
        'Gioachino Rossini, Overture to "La Gazza Ladra"': 'gioachino-rossini-1792-1868-overture-to-la-gazza-ladra',
        'Johann Sebastian Bach, Toccata and Fugue in D minor (BWV 565)': 'johann-sebastian-bach-1685-1750-toccata-and-fugue-in-d-minor-bwv-565',
        'Jorge Cardoso, Milonga': 'jorge-cardoso-1949-milonga-from-24-piezas-sudamericanas',
        'Maurice Ravel, Pavane for a Dead Princess': 'maurice-ravel-1875-1937-pavane-pour-une-infante-dfunte',
        'Fernando Sor, Introduction and Variations on a Theme by Mozart': 'fernando-sor-1778-1839-introduction-and-variations-on-a-theme-by-mozart-op9',
        'English Folk Song / Francis Cutting, Greensleeves': 'anon-francis-cutting-c1550-1596-greensleeves',
        'Franz Schubert, "Winterreise" - 1. Gute Nacht': 'franz-schubert-1797-1828-winterreise-op89-d911-1-gute-nacht',
        'Heitor Villa-Lobos, Bachianas Brasileiras No.5, 1. Aria': 'heitor-villa-lobos-1887-1959-bachianas-brasileiras-no5-1-aria-cantilena',
        'Al Di Meola, The Grande Passion': 'al-di-meola-1954-the-grande-passion',
        'Manuel de Falla, Spanish Dance No.1 from "La Vida Breve"': 'manuel-de-falla-18761946-spanish-dance-no1-from-la-vida-breve',
        'Isaac Albéniz, Castilla': 'isaac-albniz-1860-1909-castilla-seguidillas-from-suite-espaola-op47',
        'Antonín Dvořák, Symphony No.9 "From the New World", IV. Finale: Allegro con fuoco': 'antonn-dvok-1841-1904-symphony-no9-in-e-minor-from-the-new-world-op95-iv-finale-allegro-con-fuoco'
    }


def generate_program_html(program, is_english=False):
    """콘서트 프로그램을 HTML로 변환합니다."""
    html_parts = []
    piece_to_id = create_piece_to_id_mapping_en() if is_english else create_piece_to_id_mapping()
    
    # 프로그램 데이터는 항상 한국어 키를 사용하지만 출력은 언어에 따라 다르게
    part1_key = '1부'  # 데이터 키는 항상 한국어
    part1_title = 'Part I' if is_english else '제1부'
    intermission_text = 'Intermission' if is_english else '인터미션'
    part2_key = '2부'  # 데이터 키는 항상 한국어
    part2_title = 'Part II' if is_english else '제2부'
    
    if part1_key in program and program[part1_key]:
        html_parts.append('            <div class="program-section">')
        html_parts.append(f'                <h3>{part1_title}</h3>')
        
        for item in program[part1_key]:
            performers = item['performers']
            pieces = item['pieces']
            
            html_parts.append('                <div class="program-item">')
            html_parts.append(f'                    <h4>{performers}</h4>')
            html_parts.append('                    <ul>')
            
            for piece in pieces:
                # 곡목에 해당하는 ID가 있으면 링크 생성
                piece_id = piece_to_id.get(piece)
                
                # 작곡가와 곡목 분리 (쉼표로 구분)
                if ', ' in piece:
                    composer, title = piece.split(', ', 1)
                    if piece_id:
                        html_parts.append(f'                        <li>• <a href="#{piece_id}" class="program-link"><span style="color: #4a2c1a;">{composer}</span>, <span style="color: #8b6f3a; font-style: italic;">{title}</span></a></li>')
                    else:
                        html_parts.append(f'                        <li>• <span style="color: #4a2c1a;">{composer}</span>, <span style="color: #8b6f3a; font-style: italic;">{title}</span></li>')
                else:
                    if piece_id:
                        html_parts.append(f'                        <li>• <a href="#{piece_id}" class="program-link">{piece}</a></li>')
                    else:
                        html_parts.append(f'                        <li>• {piece}</li>')
            
            html_parts.append('                    </ul>')
            html_parts.append('                </div>')
        
        html_parts.append('            </div>')
    
    # 인터미션
    html_parts.append(f'            <div class="intermission">{intermission_text}</div>')
    
    # 2부
    if part2_key in program and program[part2_key]:
        html_parts.append('            <div class="program-section">')
        html_parts.append(f'                <h3>{part2_title}</h3>')
        
        for item in program[part2_key]:
            performers = item['performers']
            pieces = item['pieces']
            
            html_parts.append('                <div class="program-item">')
            html_parts.append(f'                    <h4>{performers}</h4>')
            html_parts.append('                    <ul>')
            
            for piece in pieces:
                # 곡목에 해당하는 ID가 있으면 링크 생성
                piece_id = piece_to_id.get(piece)
                
                # 작곡가와 곡목 분리 (쉼표로 구분)
                if ', ' in piece:
                    composer, title = piece.split(', ', 1)
                    if piece_id:
                        html_parts.append(f'                        <li>• <a href="#{piece_id}" class="program-link"><span style="color: #4a2c1a;">{composer}</span>, <span style="color: #8b6f3a; font-style: italic;">{title}</span></a></li>')
                    else:
                        html_parts.append(f'                        <li>• <span style="color: #4a2c1a;">{composer}</span>, <span style="color: #8b6f3a; font-style: italic;">{title}</span></li>')
                else:
                    if piece_id:
                        html_parts.append(f'                        <li>• <a href="#{piece_id}" class="program-link">{piece}</a></li>')
                    else:
                        html_parts.append(f'                        <li>• {piece}</li>')
            
            html_parts.append('                    </ul>')
            html_parts.append('                </div>')
        
        html_parts.append('            </div>')
    
    return '\n\n'.join(html_parts)


def generate_members_html(members, is_english=False):
    """멤버 정보를 HTML로 변환합니다."""
    html_parts = []
    
    # 섹션명 번역
    section_translations = {
        '연주자': 'Performers' if is_english else '연주자',
        '스태프': 'Staff' if is_english else '스태프'
    }
    
    for section_name, member_list in members.items():
        if member_list:  # 멤버가 있는 경우에만 섹션 생성
            # 각 섹션(연주자/스태프)을 하나의 카드로
            html_parts.append(f'            <div class="note">')
            html_parts.append(f'                <h3>{section_translations.get(section_name, section_name)}</h3>')
            
            for member in member_list:
                # 첫 번째 설명을 이름 옆에 병기
                if member['description'] and member['description'][0].strip():
                    first_desc = member['description'][0].strip()
                    html_parts.append(f'                <h4 style="margin-top: 30px; color: #4a2c1a;">{member["name"]} | <span style="font-weight: normal;">{first_desc}</span></h4>')
                    # 나머지 설명들을 하나의 문단으로 합치기 (2번째, 3번째 줄을 한 문단으로)
                    remaining_descs = [desc.strip() for desc in member['description'][1:] if desc.strip()]
                    if remaining_descs:
                        combined_desc = '<br>'.join(remaining_descs)
                        html_parts.append(f'                <p>{combined_desc}</p>')
                else:
                    html_parts.append(f'                <h4 style="margin-top: 30px; color: #4a2c1a;">{member["name"]}</h4>')
                    # 모든 설명을 하나의 문단으로 합치기
                    all_descs = [desc.strip() for desc in member['description'] if desc.strip()]
                    if all_descs:
                        combined_desc = '<br>'.join(all_descs)
                        html_parts.append(f'                <p>{combined_desc}</p>')
            
            html_parts.append(f'            </div>')
    
    return '\n\n'.join(html_parts)


def parse_markdown_content(markdown_content):
    """markdown 내용을 HTML로 변환합니다."""
    # 마크다운 파싱 - ## 제목 처리
    html_parts = []
    
    # ## 제목으로 섹션을 나누되, 첫 번째 섹션도 올바르게 처리
    sections = re.split(r'\n(?=## )', markdown_content)
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        if section.startswith('## '):
            # ## 로 시작하는 섹션
            lines = section.split('\n', 1)
            title = lines[0].replace('## ', '').strip()
            content = lines[1].strip() if len(lines) > 1 else ''
            
            html_parts.append('<div class="note">')
            html_parts.append(f'<h3>{title}</h3>')
            
            if content:
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        # 이미지 처리 ![alt](src)
                        if re.match(r'!\[.*?\]\(.*?\)', para.strip()):
                            # 포스터 이미지 처리
                            image_html = re.sub(r'!\[(.*?)\]\((.*?)\)', 
                                             r'<div style="text-align: center; margin: 20px 0;"><img src="\2" alt="\1" style="max-width: 400px; width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);"></div>', 
                                             para.strip())
                            html_parts.append(image_html)
                        # 포스터 정보만 가운데 정렬 처리 (연속된 **텍스트** 줄들)
                        elif ('조유란' in para or 'Cho Yuran' in para) and '**' in para and para.count('\n') >= 3:
                            # 줄바꿈으로 나누기 (markdown의 강제 줄바꿈은 두 칸 다음 줄바꿈)
                            lines = para.split('\n')
                            
                            centered_content = []
                            for line in lines:
                                line = line.strip()
                                if line and '**' in line:
                                    # **텍스트** -> 텍스트 (볼드 제거하고 스타일로 처리)
                                    line_text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                                    centered_content.append(f'<p style="margin: 5px 0; font-weight: bold; text-align: center;">{line_text}</p>')
                            if centered_content:
                                html_parts.append(f'<div style="margin: 20px 0;">{"".join(centered_content)}</div>')
                        else:
                            # **텍스트** -> <strong>텍스트</strong>
                            para = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', para)
                            # *텍스트* -> <em>텍스트</em>  
                            para = re.sub(r'\*(.*?)\*', r'<em>\1</em>', para)
                            # 줄바꿈 처리
                            para = para.replace('  \n', '<br>')
                            para = para.replace('\n', '<br>')
                            html_parts.append(f'<p>{para}</p>')
            
            html_parts.append('</div>')
        else:
            # 제목 없는 일반 내용
            if section.strip():
                html_parts.append('<div class="note">')
                paragraphs = section.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        # 이미지 처리 ![alt](src)
                        if re.match(r'!\[.*?\]\(.*?\)', para.strip()):
                            # 포스터 이미지 처리
                            image_html = re.sub(r'!\[(.*?)\]\((.*?)\)', 
                                             r'<div style="text-align: center; margin: 20px 0;"><img src="\2" alt="\1" style="max-width: 400px; width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);"></div>', 
                                             para.strip())
                            html_parts.append(image_html)
                        # 포스터 정보만 가운데 정렬 처리 (연속된 **텍스트** 줄들)
                        elif ('조유란' in para or 'Cho Yuran' in para) and '**' in para and para.count('\n') >= 3:
                            # 줄바꿈으로 나누기 (markdown의 강제 줄바꿈은 두 칸 다음 줄바꿈)
                            lines = para.split('\n')
                            
                            centered_content = []
                            for line in lines:
                                line = line.strip()
                                if line and '**' in line:
                                    # **텍스트** -> 텍스트 (볼드 제거하고 스타일로 처리)
                                    line_text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                                    centered_content.append(f'<p style="margin: 5px 0; font-weight: bold; text-align: center;">{line_text}</p>')
                            if centered_content:
                                html_parts.append(f'<div style="margin: 20px 0;">{"".join(centered_content)}</div>')
                        else:
                            # **텍스트** -> <strong>텍스트</strong>
                            para = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', para)
                            # *텍스트* -> <em>텍스트</em>
                            para = re.sub(r'\*(.*?)\*', r'<em>\1</em>', para)
                            # 줄바꿈 처리
                            para = para.replace('  \n', '<br>')
                            para = para.replace('\n', '<br>')
                            html_parts.append(f'<p>{para}</p>')
                html_parts.append('</div>')
    
    return '\n'.join(html_parts)


def update_html_template(template_content, notes, invitation_content=None, members=None, program=None, poster_content=None, history_content=None, is_english=False):
    """HTML 템플릿을 업데이트합니다."""
    
    # 프로그램 노트 섹션 찾기 및 교체
    if is_english:
        program_notes_pattern = r'(<section id="program-notes"[^>]*>.*?<h2>Programme Notes</h2>)(.*?)(</section>)'
    else:
        program_notes_pattern = r'(<section id="program-notes"[^>]*>.*?<h2>곡 해설</h2>)(.*?)(</section>)'
    
    def replace_notes(match):
        section_start = match.group(1)
        section_end = match.group(3)
        new_notes_html = generate_program_notes_html(notes, is_english)
        
        return f'''{section_start}
            
{new_notes_html}
        {section_end}'''
    
    updated_content = re.sub(program_notes_pattern, replace_notes, template_content, flags=re.DOTALL)
    
    # 프로그램 섹션 교체
    if program:
        if is_english:
            program_pattern = r'(<section id="program"[^>]*>.*?<h2>Programme</h2>)(.*?)(</section>)'
        else:
            program_pattern = r'(<section id="program"[^>]*>.*?<h2>순서</h2>)(.*?)(</section>)'
        
        def replace_program(match):
            section_start = match.group(1)
            section_end = match.group(3)
            new_program_html = generate_program_html(program, is_english)
            
            return f'''{section_start}
            
{new_program_html}
        {section_end}'''
        
        updated_content = re.sub(program_pattern, replace_program, updated_content, flags=re.DOTALL)
    
    # 초대의 말씀 섹션 교체
    if invitation_content:
        if is_english:
            invitation_pattern = r'(<section id="invitation"[^>]*>.*?<h2>Invitation</h2>.*?<div class="invitation-content">)(.*?)(</div>\s*</section>)'
        else:
            invitation_pattern = r'(<section id="invitation"[^>]*>.*?<h2>초대의 말씀</h2>.*?<div class="invitation-content">)(.*?)(</div>\s*</section>)'
        
        def replace_invitation(match):
            section_start = match.group(1)
            section_end = match.group(3)
            new_invitation_html = generate_invitation_html(invitation_content)
            
            return f'''{section_start}
{new_invitation_html}
            {section_end}'''
        
        updated_content = re.sub(invitation_pattern, replace_invitation, updated_content, flags=re.DOTALL)
    
    # 멤버 소개 섹션 교체
    if members:
        if is_english:
            members_pattern = r'(<section id="members"[^>]*>.*?<h2>Members</h2>)(.*?)(</section>)'
        else:
            members_pattern = r'(<section id="members"[^>]*>.*?<h2>미련 사람들</h2>)(.*?)(</section>)'
        
        def replace_members(match):
            section_start = match.group(1)
            section_end = match.group(3)
            new_members_html = generate_members_html(members, is_english)
            
            return f'''{section_start}
            
{new_members_html}
        {section_end}'''
        
        updated_content = re.sub(members_pattern, replace_members, updated_content, flags=re.DOTALL)
    
    # 포스터 섹션 교체
    if poster_content:
        poster_html = parse_markdown_content(poster_content)
        updated_content = updated_content.replace('{{poster_content}}', poster_html)
    
    # 연혁 섹션 교체
    if history_content:
        history_html = parse_markdown_content(history_content)
        updated_content = updated_content.replace('{{history_content}}', history_html)
    
    # 생성 시간 주석 추가
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    comment = f"<!-- 자동 생성됨: {timestamp} -->\n"
    
    updated_content = updated_content.replace('<!DOCTYPE html>', comment + '<!DOCTYPE html>')
    
    return updated_content


def main():
    """메인 함수"""
    print("HTML 생성 스크립트를 실행합니다...")
    
    # 파일 경로
    template_path = 'template.html'
    notes_path = 'program_notes.md'
    invitation_path = 'invitation.md'
    members_path = 'members.md'
    output_path = 'index_kr.html'
    
    # 템플릿 파일 읽기
    print(f"템플릿 파일 읽는 중: {template_path}")
    template_content = read_file(template_path)
    if template_content is None:
        return
    
    # 프로그램 노트 파일 읽기
    print(f"프로그램 노트 파일 읽는 중: {notes_path}")
    notes_content = read_file(notes_path)
    if notes_content is None:
        return
    
    # 초대의 말씀 파일 읽기
    print(f"초대의 말씀 파일 읽는 중: {invitation_path}")
    invitation_content = read_file(invitation_path)
    
    # 멤버 소개 파일 읽기
    print(f"멤버 소개 파일 읽는 중: {members_path}")
    members_content = read_file(members_path)
    
    # 마크다운 파싱
    print("마크다운 내용을 파싱하는 중...")
    notes = parse_markdown_notes(notes_content)
    print(f"총 {len(notes)}개의 프로그램 노트를 찾았습니다.")
    
    for note in notes:
        print(f"  - {note['title']} (ID: {note['id']})")
    
    # 초대의 말씀 파싱
    invitation_parsed = None
    if invitation_content:
        invitation_parsed = parse_markdown_invitation(invitation_content)
        print("✅ 초대의 말씀 파싱 완료")
    
    # 멤버 소개 파싱
    members_parsed = None
    if members_content:
        members_parsed = parse_markdown_members(members_content)
        total_members = sum(len(members) for members in members_parsed.values())
        print(f"✅ 멤버 소개 파싱 완료 (총 {total_members}명)")
    
    # 콘서트 프로그램 파일 읽기
    program_path = 'concert_program.md'
    print(f"콘서트 프로그램 파일 읽는 중: {program_path}")
    program_content = read_file(program_path)
    
    # 콘서트 프로그램 파싱
    program_parsed = None
    if program_content:
        program_parsed = parse_markdown_program(program_content)
        print("✅ 콘서트 프로그램 파싱 완료")
    
    # 포스터 파일 읽기
    poster_path = 'poster.md'
    print(f"포스터 파일 읽는 중: {poster_path}")
    poster_content = read_file(poster_path)
    
    # 연혁 파일 읽기
    history_path = 'history.md'
    print(f"연혁 파일 읽는 중: {history_path}")
    history_content = read_file(history_path)
    
    # HTML 생성 (한국어)
    print("HTML을 생성하는 중...")
    generated_html = update_html_template(template_content, notes, invitation_parsed, members_parsed, program_parsed, poster_content, history_content)
    
    # 파일 저장 (한국어)
    print(f"결과 파일 저장 중: {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(generated_html)
        print(f"✅ HTML 파일이 성공적으로 생성되었습니다: {output_path}")
    except Exception as e:
        print(f"❌ 파일 저장 중 오류가 발생했습니다: {e}")
        return
    
    # 영어 버전 생성
    print("\n영어 버전 생성을 시작합니다...")
    
    # 영어 템플릿 및 파일 경로
    template_en_path = 'template_en.html'
    notes_en_path = 'program_notes_en.md'
    invitation_en_path = 'invitation_en.md'
    members_en_path = 'members_en.md'
    program_en_path = 'concert_program_en.md'
    output_en_path = 'index_en.html'
    
    # 영어 템플릿 파일 읽기
    print(f"영어 템플릿 파일 읽는 중: {template_en_path}")
    template_en_content = read_file(template_en_path)
    if template_en_content is None:
        print("⚠️ 영어 템플릿 파일을 찾을 수 없어 영어 버전 생성을 건너뜁니다.")
    else:
        # 영어 파일들 읽기
        print(f"영어 프로그램 노트 파일 읽는 중: {notes_en_path}")
        notes_en_content = read_file(notes_en_path)
        
        print(f"영어 초대의 말씀 파일 읽는 중: {invitation_en_path}")
        invitation_en_content = read_file(invitation_en_path)
        
        print(f"영어 멤버 소개 파일 읽는 중: {members_en_path}")
        members_en_content = read_file(members_en_path)
        
        print(f"영어 프로그램 파일 읽는 중: {program_en_path}")
        program_en_content = read_file(program_en_path)
        
        # 영어 포스터 파일 읽기
        poster_en_path = 'poster_en.md'
        print(f"영어 포스터 파일 읽는 중: {poster_en_path}")
        poster_en_content = read_file(poster_en_path)
        
        # 영어 연혁 파일 읽기
        history_en_path = 'history_en.md'
        print(f"영어 연혁 파일 읽는 중: {history_en_path}")
        history_en_content = read_file(history_en_path)
        
        if notes_en_content:
            # 영어 마크다운 파싱
            print("영어 마크다운 내용을 파싱하는 중...")
            notes_en = parse_markdown_notes(notes_en_content)
            print(f"총 {len(notes_en)}개의 영어 프로그램 노트를 찾았습니다.")
            
            # 영어 초대의 말씀 파싱
            invitation_en_parsed = None
            if invitation_en_content:
                invitation_en_parsed = parse_markdown_invitation(invitation_en_content)
                print("✅ 영어 초대의 말씀 파싱 완료")
            
            # 영어 멤버 소개 파싱
            members_en_parsed = None
            if members_en_content:
                members_en_parsed = parse_markdown_members(members_en_content)
                total_members_en = sum(len(members) for members in members_en_parsed.values())
                print(f"✅ 영어 멤버 소개 파싱 완료 (총 {total_members_en}명)")
            
            # 영어 콘서트 프로그램 파싱
            program_en_parsed = None
            if program_en_content:
                program_en_parsed = parse_markdown_program(program_en_content)
                print("✅ 영어 콘서트 프로그램 파싱 완료")
            
            # 영어 HTML 생성
            print("영어 HTML을 생성하는 중...")
            generated_html_en = update_html_template(template_en_content, notes_en, invitation_en_parsed, members_en_parsed, program_en_parsed, poster_en_content, history_en_content, is_english=True)
            
            # 영어 파일 저장
            print(f"영어 결과 파일 저장 중: {output_en_path}")
            try:
                with open(output_en_path, 'w', encoding='utf-8') as f:
                    f.write(generated_html_en)
                print(f"✅ 영어 HTML 파일이 성공적으로 생성되었습니다: {output_en_path}")
                
                # 영어 파일 통계
                file_size_en = os.path.getsize(output_en_path)
                print(f"📊 영어 파일 크기: {file_size_en:,} bytes")
            except Exception as e:
                print(f"❌ 영어 파일 저장 중 오류가 발생했습니다: {e}")
    
    # 통계 출력
    file_size = os.path.getsize(output_path)
    print(f"\n📊 생성된 파일 크기: {file_size:,} bytes")
    print(f"📝 프로그램 노트 개수: {len(notes)}개")
    if members_parsed:
        total_members = sum(len(members) for members in members_parsed.values())
        print(f"👥 멤버 수: {total_members}명")


if __name__ == "__main__":
    main()
