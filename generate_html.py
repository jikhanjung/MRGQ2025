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
            current_section = line[3:].strip()
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


def generate_program_notes_html(notes):
    """프로그램 노트들을 HTML로 변환합니다."""
    html_parts = []
    
    for note in notes:
        # 내용을 문단별로 나누기
        paragraphs = note['content'].split('\n\n')
        paragraph_html = []
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                # 첫 번째 문단이 ###으로 시작하면 한국어 제목으로 처리
                if i == 0 and paragraph.strip().startswith('###'):
                    korean_title = paragraph.strip()[3:].strip()
                    paragraph_html.append(f'                <h4 style="color: #6b4423; margin-top: -10px; margin-bottom: 20px; font-weight: 400;">{korean_title}</h4>')
                else:
                    # 마크다운 이탤릭 변환: *(by 작성자)* -> <em>(by 작성자)</em>
                    paragraph = re.sub(r'\*(.*?)\*', r'<em>\1</em>', paragraph.strip())
                    paragraph_html.append(f'                <p>{paragraph}</p>')
        
        note_html = f'''            <div id="{note['id']}" class="note">
                <h3>{note['title']}</h3>
{chr(10).join(paragraph_html)}
            </div>'''
        
        html_parts.append(note_html)
    
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


def generate_members_html(members):
    """멤버 정보를 HTML로 변환합니다."""
    html_parts = []
    
    for section_name, member_list in members.items():
        if member_list:  # 멤버가 있는 경우에만 섹션 생성
            # 각 섹션(연주자/스태프)을 하나의 카드로
            html_parts.append(f'            <div class="note">')
            html_parts.append(f'                <h3>{section_name}</h3>')
            
            for member in member_list:
                html_parts.append(f'                <h4 style="margin-top: 30px; color: #4a2c1a;">{member["name"]}</h4>')
                
                for desc in member['description']:
                    if desc.strip():
                        html_parts.append(f'                <p>{desc}</p>')
            
            html_parts.append(f'            </div>')
    
    return '\n\n'.join(html_parts)


def update_html_template(template_content, notes, invitation_content=None, members=None):
    """HTML 템플릿을 업데이트합니다."""
    
    # 프로그램 노트 섹션 찾기 및 교체
    program_notes_pattern = r'(<section id="program-notes"[^>]*>.*?<h2>프로그램 노트</h2>)(.*?)(</section>)'
    
    def replace_notes(match):
        section_start = match.group(1)
        section_end = match.group(3)
        new_notes_html = generate_program_notes_html(notes)
        
        return f'''{section_start}
            
{new_notes_html}
        {section_end}'''
    
    updated_content = re.sub(program_notes_pattern, replace_notes, template_content, flags=re.DOTALL)
    
    # 초대의 말씀 섹션 교체
    if invitation_content:
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
        members_pattern = r'(<section id="members"[^>]*>.*?<h2>멤버 소개</h2>)(.*?)(</section>)'
        
        def replace_members(match):
            section_start = match.group(1)
            section_end = match.group(3)
            new_members_html = generate_members_html(members)
            
            return f'''{section_start}
            
{new_members_html}
        {section_end}'''
        
        updated_content = re.sub(members_pattern, replace_members, updated_content, flags=re.DOTALL)
    
    # 생성 시간 주석 추가
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    comment = f"<!-- 자동 생성됨: {timestamp} -->\n"
    
    updated_content = updated_content.replace('<!DOCTYPE html>', comment + '<!DOCTYPE html>')
    
    return updated_content


def main():
    """메인 함수"""
    print("HTML 생성 스크립트를 실행합니다...")
    
    # 파일 경로
    template_path = 'index.html'
    backup_path = 'index_backup.html'
    notes_path = 'program_notes.md'
    invitation_path = 'invitation.md'
    members_path = 'members.md'
    output_path = 'index.html'
    
    # 기존 index.html을 백업
    print(f"기존 파일 백업 중: {template_path} -> {backup_path}")
    template_content = read_file(template_path)
    if template_content:
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            print(f"✅ 백업 완료: {backup_path}")
        except Exception as e:
            print(f"❌ 백업 실패: {e}")
            return
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
    
    # HTML 생성
    print("HTML을 생성하는 중...")
    generated_html = update_html_template(template_content, notes, invitation_parsed, members_parsed)
    
    # 파일 저장
    print(f"결과 파일 저장 중: {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(generated_html)
        print(f"✅ HTML 파일이 성공적으로 생성되었습니다: {output_path}")
    except Exception as e:
        print(f"❌ 파일 저장 중 오류가 발생했습니다: {e}")
        return
    
    # 통계 출력
    file_size = os.path.getsize(output_path)
    print(f"📊 생성된 파일 크기: {file_size:,} bytes")
    print(f"📝 프로그램 노트 개수: {len(notes)}개")
    if members_parsed:
        total_members = sum(len(members) for members in members_parsed.values())
        print(f"👥 멤버 수: {total_members}명")


if __name__ == "__main__":
    main()