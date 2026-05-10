#!/usr/bin/env python3
"""
蛇类数据实时爬虫脚本
从维基百科爬取蛇类数据并添加到数据库
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
import sys
from urllib.parse import urljoin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models.snake import Snake


WIKI_BASE_URL = "https://zh.wikipedia.org"


def get_page(url: str) -> BeautifulSoup | None:
    """获取网页内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            print(f"  ✓ 成功获取页面: {url}")
            return BeautifulSoup(response.text, 'html.parser')
        else:
            print(f"  ✗ 获取页面失败: {url}, 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ✗ 请求出错: {url}, 错误: {e}")
    return None


def get_image_url(page_url: str) -> str | None:
    """获取蛇类页面的图片URL"""
    soup = get_page(page_url)
    if not soup:
        return None

    infobox = soup.find('table', {'class': 'infobox'})
    if infobox:
        img = infobox.find('img')
        if img:
            img_url = img.get('src')
            if img_url:
                if not img_url.startswith('http'):
                    img_url = 'https:' + img_url
                print(f"    📷 找到图片: {img_url}")
                return img_url

    content = soup.find('div', {'id': 'mw-content-text'})
    if content:
        img = content.find('img')
        if img:
            img_url = img.get('src')
            if img_url:
                if not img_url.startswith('http'):
                    img_url = 'https:' + img_url
                print(f"    📷 找到图片: {img_url}")
                return img_url

    return None


def parse_snake_page(url: str, is_venomous: bool = None) -> dict | None:
    """解析单个蛇类页面"""
    soup = get_page(url)
    if not soup:
        return None

    data = {
        'name': '',
        'scientific_name': '',
        'description': '',
        'temperament': '',
        'treatment': '',
        'is_venomous': is_venomous if is_venomous is not None else False,
        'image': None
    }

    title = soup.find('h1', {'id': 'firstHeading'})
    if title:
        data['name'] = title.get_text(strip=True)
        print(f"  正在解析: {data['name']}")

    infobox = soup.find('table', {'class': 'infobox'})
    if infobox:
        rows = infobox.find_all('tr')
        for row in rows:
            header = row.find('th')
            cell = row.find('td')
            if header and cell:
                header_text = header.get_text(strip=True)
                cell_text = cell.get_text(strip=True)

                if '学名' in header_text or ' scientific name' in header_text.lower():
                    data['scientific_name'] = cell_text
                elif '分布' in header_text or '分布区域' in header_text:
                    if not data['description']:
                        data['description'] = cell_text
                elif '毒性' in header_text:
                    data['is_venomous'] = '毒' in cell_text or '有' in cell_text
                elif '习性' in header_text or '行为' in header_text:
                    data['temperament'] = cell_text

    content = soup.find('div', {'id': 'mw-content-text'})
    if content:
        paragraphs = content.find_all('p')
        description_parts = []
        for p in paragraphs[:3]:
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                description_parts.append(text)
                if len(' '.join(description_parts)) > 200:
                    break
        if description_parts:
            data['description'] = ' '.join(description_parts)[:500]

    time.sleep(0.3)
    data['image'] = get_image_url(url)

    return data if data['name'] else None


def get_common_snakes_list() -> list:
    """获取常见蛇类列表"""
    print("\n" + "="*60)
    print("获取常见蛇类列表")
    print("="*60)

    common_snakes = [
        {'name': '眼镜王蛇', 'wiki': '眼镜王蛇', 'is_venomous': True},
        {'name': '眼镜蛇', 'wiki': '眼镜蛇', 'is_venomous': True},
        {'name': '银环蛇', 'wiki': '银环蛇', 'is_venomous': True},
        {'name': '金环蛇', 'wiki': '金环蛇', 'is_venomous': True},
        {'name': '竹叶青', 'wiki': '竹叶青', 'is_venomous': True},
        {'name': '尖吻蝮', 'wiki': '尖吻蝮', 'is_venomous': True},
        {'name': '原矛头蝮', 'wiki': '原矛头蝮', 'is_venomous': True},
        {'name': '蝮蛇', 'wiki': '蝮蛇', 'is_venomous': True},
        {'name': '蝰蛇', 'wiki': '蝰蛇', 'is_venomous': True},
        {'name': '青环海蛇', 'wiki': '青环海蛇', 'is_venomous': True},
        {'name': '玉米蛇', 'wiki': '玉米蛇', 'is_venomous': False},
        {'name': '球蟒', 'wiki': '球蟒', 'is_venomous': False},
        {'name': '王锦蛇', 'wiki': '王锦蛇', 'is_venomous': False},
        {'name': '黑眉锦蛇', 'wiki': '黑眉锦蛇', 'is_venomous': False},
        {'name': '赤链蛇', 'wiki': '赤链蛇', 'is_venomous': False},
        {'name': '乌梢蛇', 'wiki': '乌梢蛇', 'is_venomous': False},
        {'name': '翠青蛇', 'wiki': '翠青蛇', 'is_venomous': False},
        {'name': '滑鼠蛇', 'wiki': '滑鼠蛇', 'is_venomous': False},
        {'name': '白条锦蛇', 'wiki': '白条锦蛇', 'is_venomous': False},
        {'name': '虎斑颈槽蛇', 'wiki': '虎斑颈槽蛇', 'is_venomous': False},
    ]

    result = []
    for snake in common_snakes:
        url = f"https://zh.wikipedia.org/wiki/{snake['wiki']}"
        result.append({
            'name': snake['name'],
            'url': url,
            'is_venomous': snake['is_venomous']
        })

    return result


def scrape_all_snakes() -> list:
    """爬取所有蛇类数据"""
    snake_list = get_common_snakes_list()

    print("\n" + "="*60)
    print(f"开始爬取 {len(snake_list)} 个蛇类的详细信息")
    print("="*60)

    results = []
    for i, snake in enumerate(snake_list):
        print(f"\n[{i+1}/{len(snake_list)}] 爬取中...")
        data = parse_snake_page(snake['url'], snake['is_venomous'])
        if data:
            if not data.get('treatment'):
                if data['is_venomous']:
                    data['treatment'] = '1. 保持冷静，避免恐慌\n2. 尽快拨打急救电话\n3. 保持伤口低于心脏位置\n4. 避免剧烈运动\n5. 尽快就医，使用抗蛇毒血清'
                else:
                    data['treatment'] = '无毒，咬伤后清洁消毒伤口即可。如有不适请就医。'

            if not data.get('temperament'):
                if data['is_venomous']:
                    data['temperament'] = '野生毒蛇，性格凶猛，有领地意识'
                else:
                    data['temperament'] = '性格温顺，一般不主动攻击人'

            results.append(data)
            print(f"  ✓ 成功获取: {data['name']}")
        else:
            print(f"  ✗ 爬取失败")

        time.sleep(0.5)

    return results


def save_to_database(snakes_data: list):
    """保存到数据库"""
    print("\n" + "="*60)
    print("保存到数据库")
    print("="*60)

    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    existing_count = session.query(Snake).count()
    if existing_count > 0:
        print(f"\n数据库中已有 {existing_count} 条数据")
        response = input("是否清空并重新导入？(y/n): ").strip().lower()
        if response == 'y':
            session.query(Snake).delete()
            session.commit()
            print("已清空现有数据")
        else:
            print("跳过数据导入")
            return

    for i, snake in enumerate(snakes_data):
        print(f"[{i+1}/{len(snakes_data)}] 保存: {snake['name']} (图片: {'有' if snake['image'] else '无'})")
        try:
            snake_model = Snake(
                name=snake['name'],
                scientific_name=snake.get('scientific_name', ''),
                description=snake.get('description', ''),
                temperament=snake.get('temperament', ''),
                treatment=snake.get('treatment', ''),
                is_venomous=snake.get('is_venomous', False),
                image=snake.get('image')
            )
            session.add(snake_model)
            session.commit()
            print(f"  ✓ 保存成功")
        except Exception as e:
            print(f"  ✗ 保存失败: {e}")
            session.rollback()

    session.close()
    print(f"\n数据库导入完成！共导入 {len(snakes_data)} 条数据")


def main():
    """主函数"""
    print("="*60)
    print("🐍 蛇类百科数据爬虫")
    print("="*60)
    print("从维基百科实时抓取蛇类数据...")
    print()

    snakes_data = scrape_all_snakes()

    if snakes_data:
        print(f"\n成功爬取 {len(snakes_data)} 条蛇类数据")
        save_to_database(snakes_data)
    else:
        print("\n爬取失败，请检查网络连接后重试")
        sys.exit(1)


if __name__ == "__main__":
    main()
