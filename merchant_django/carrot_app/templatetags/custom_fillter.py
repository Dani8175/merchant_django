from django import template
from django.utils import timezone


# from bs4 import BeautifulSoup
import re


register = template.Library()


# # 글 미리보기 기능
# @register.filter
# def text_only(value):
#     soup = BeautifulSoup(value, "html.parser")

#     # img 태그 제거
#     for img in soup.find_all('img'):
#         img.decompose()

#     # 텍스트만 추출, 첫 20글자만 반환
#     text_content = soup.get_text()
#     if len(text_content) >= 200:
#         text_content = text_content[:200] + '...'
#     return text_content


# 첫 번째 img 태그의 src 속성 값 찾아 반환함
@register.filter(name="get_img_src")
def get_img_src(value):
    match = re.search(r'<img [^>]*src="([^"]+)', value)
    if match:
        return match.group(1)
    return ""


@register.filter
def format_upload_date(upload_date):
    now = timezone.now()
    time_since = now - upload_date

    if time_since.days >= 365:
        return f"{time_since.days // 365}년 전"
    elif time_since.days >= 30:
        return f"{time_since.days // 30}달 전"
    elif time_since.days >= 7:
        return f"{time_since.days // 7}주 전"
    elif time_since.days > 0:
        return f"{time_since.days}일 전"
    elif time_since.seconds >= 3600:
        return f"{time_since.seconds // 3600}시간 전"
    elif time_since.seconds >= 60:
        return f"{time_since.seconds // 60}분 전"
    else:
        return "방금 전"


@register.filter
def add_commas(number):
    original_str = str(number)
    parts = []
    while len(original_str) > 3:
        parts.append(original_str[-3:])
        original_str = original_str[:-3]
    parts.append(original_str)
    return ",".join(reversed(parts))


@register.filter(name="mask_and_truncate_password")
def mask_and_truncate_password(password, length=8):
    masked_password = "*" * len(password)
    return masked_password[:length]
