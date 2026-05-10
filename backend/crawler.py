#!/usr/bin/env python3
"""
蛇类数据爬虫脚本
用于从网络抓取蛇类数据并添加到数据库
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models.snake import Snake
from app.models.admin import Admin
from app.core.security import get_password_hash

SNAKE_DATA = [
    {
        "name": "眼镜王蛇",
        "scientific_name": "Ophiophagus hannah",
        "description": "眼镜王蛇是世界上最大的毒蛇，体长可达5米。头部呈椭圆形，颈部可膨扁，背部有\"∧\"形黄白色斑纹。分布于南亚和东南亚地区。",
        "temperament": "领地意识强，行动敏捷，遇到威胁时会立起身体前部并展开颈部的皮褶进行警告。",
        "treatment": "1. 保持冷静，避免恐慌\n2. 尽快拨打急救电话\n3. 保持伤口低于心脏位置\n4. 避免剧烈运动\n5. 尽快就医，使用抗眼镜蛇毒血清",
        "is_venomous": True,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Ophiophagus_hannah.jpg/1200px-Ophiophagus_hannah.jpg"
    },
    {
        "name": "眼镜蛇",
        "scientific_name": "Naja",
        "description": "眼镜蛇是眼镜蛇科眼镜蛇属的毒蛇，上颌骨较短，前端有沟牙。头部呈椭圆形，从外形看不易与无毒蛇区别且并不是全为黑色。",
        "temperament": "性格较为警觉，受惊时颈部会膨扁进行警告。一般不主动攻击人。",
        "treatment": "1. 保持冷静，减少活动\n2. 尽快就医\n3. 抗蛇毒血清是特效治疗\n4. 对症支持治疗",
        "is_venomous": True,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Indian_Cobra.jpg/1200px-Indian_Cobra.jpg"
    },
    {
        "name": "银环蛇",
        "scientific_name": "Bungarus multicinctus",
        "description": "银环蛇是眼镜蛇科环蛇属的一种，俗称过基峡、白节黑、金钱白花蛇、银甲带、银包铁等。体背黑白相间环纹，脊棱突出。",
        "temperament": "性格胆小，常在夜间活动，一般不主动攻击人。但毒性极强，为陆地第四大毒蛇。",
        "treatment": "1. 立即就医\n2. 保持静止\n3. 不要使用止血带或吸毒\n4. 记录蛇的外观特征\n5. 抗银环蛇毒血清治疗",
        "is_venomous": True,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Bungarus_multicinctus.jpg/1200px-Bungarus_multicinctus.jpg"
    },
    {
        "name": "金环蛇",
        "scientific_name": "Bungarus fasciatus",
        "description": "金环蛇是环蛇属的一种，俗称金甲带、金包铁、金脚带、花扇柄等。特征是黄黑相间宽环纹。",
        "temperament": "性格温和，夜行性蛇类。毒性很强，但一般不主动攻击人。",
        "treatment": "1. 保持冷静\n2. 立即就医\n3. 抗蛇毒血清治疗\n4. 对症支持治疗",
        "is_venomous": True,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Bungarus_fasciatus.jpg/1200px-Bungarus_fasciatus.jpg"
    },
    {
        "name": "竹叶青",
        "scientific_name": "Trimeresurus stejnegeri",
        "description": "竹叶青是蝰科蝮亚科竹叶青蛇属的管牙类毒蛇，又名翠青蛇。体长60-100厘米，通体绿色，眼睛红色、黄色或者绿色，尾背及尾尖焦红色。有\"美女蛇\"之称。",
        "temperament": "性格较神经质，容易被惊扰，有领域性。昼夜均活动，夜间更为频繁。",
        "treatment": "1. 保持冷静\n2. 尽快就医\n3. 固定受伤部位\n4. 避免使用止血带\n5. 抗蝮蛇毒血清治疗",
        "is_venomous": True,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Trimeresurus_stejnegeri.jpg/1200px-Trimeresurus_stejnegeri.jpg"
    },
    {
        "name": "尖吻蝮",
        "scientific_name": "Deinagkistrodon",
        "description": "尖吻蝮又称百步蛇、五步蛇、七步蛇、蕲蛇、山谷虌等。背部有灰褐色菱形斑块，头呈三角形。是中国特有的毒蛇。",
        "temperament": "性格凶猛，攻击性强。有\"坐土\"习性，会长时间保持不动等待猎物。",
        "treatment": "1. 保持冷静，避免恐慌\n2. 固定伤肢，减少活动\n3. 尽快就医\n4. 抗五步蛇毒血清治疗\n5. 注意出血倾向",
        "is_venomous": True,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Deinagkistrodon_acutus.jpg/1200px-Deinagkistrodon_acutus.jpg"
    },
    {
        "name": "原矛头蝮",
        "scientific_name": "Trimeresurus mucrosquamatus",
        "description": "原矛头蝮又称龟壳花蛇、烙铁头。头呈长三角形，颈部细，形似烙铁。体背棕灰褐色，背脊及其两侧有不规则的黑褐色斑块。",
        "temperament": "夜行性蛇类，喜欢夜里出来活动。捕食鼠类等小型哺乳动物。",
        "treatment": "1. 保持冷静\n2. 尽快就医\n3. 抗蝮蛇毒血清\n4. 注意局部组织坏死",
        "is_venomous": True,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Trimeresurus_mucrosquamatus.jpg/1200px-Trimeresurus_mucrosquamatus.jpg"
    },
    {
        "name": "蝮蛇",
        "scientific_name": "Gloydius brevicaudus",
        "description": "蝮蛇是中国常见的毒蛇，头部呈三角形，背部有深色圆斑。体型较小，但毒性较强。",
        "temperament": "性格凶猛，行动迅速。有颊窝，能感知温血动物。",
        "treatment": "1. 保持冷静\n2. 固定伤肢\n3. 尽快就医\n4. 抗蝮蛇毒血清\n5. 注意肾功能损伤",
        "is_venomous": True,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Gloydius_brevicaudus.jpg/1200px-Gloydius_brevicaudus.jpg"
    },
    {
        "name": "蝰蛇",
        "scientific_name": "Daboia russelii",
        "description": "蝰蛇又称黑斑蝰蛇，体长0.9～1.3米。背面暗褐色，有淡褐色链状椭圆斑。毒液以神经性毒为主，也含出血循毒。",
        "temperament": "性格凶猛，昼夜都活动。捕食鼠类等。",
        "treatment": "1. 立即就医\n2. 抗蛇毒血清\n3. 对症支持治疗",
        "is_venomous": True,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Daboia_russelii.jpg/1200px-Daboia_russelii.jpg"
    },
    {
        "name": "青环海蛇",
        "scientific_name": "Hydrophis cyanocinctus",
        "description": "青环海蛇是蛇目眼镜蛇科海蛇属爬行动物。体长橄榄色或黄色，背深灰色，有青黑色环纹达腹部。为前沟牙类毒蛇。",
        "temperament": "海蛇多性格温和，但毒性很强。能麻痹被咬动物的横纹肌。",
        "treatment": "1. 立即就医\n2. 抗海蛇毒血清\n3. 对症支持治疗",
        "is_venomous": True,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Hydrophis_cyanocinctus.jpg/1200px-Hydrophis_cyanocinctus.jpg"
    },
    {
        "name": "玉米蛇",
        "scientific_name": "Pantherophis guttatus",
        "description": "玉米蛇是最受欢迎的宠物蛇之一，原产于北美洲。体色丰富多变，有红色、橙色、黄色等变种。性格温顺，适应能力强。",
        "temperament": "性格温顺，很少主动攻击人类。适应能力强，适合作为宠物饲养。",
        "treatment": "无毒，无需特殊处理。如有咬伤，清洁伤口即可。",
        "is_venomous": False,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Corn_snake.jpg/1200px-Corn_snake.jpg"
    },
    {
        "name": "球蟒",
        "scientific_name": "Python regius",
        "description": "球蟒是最小的蟒蛇之一，因受到惊吓时会缩成一团而得名。它们是非常适合初学者的宠物蛇。",
        "temperament": "性格温和，较为害羞，喜欢温暖的环境。非常温顺，一般不会咬人。",
        "treatment": "无毒，非常温顺，一般不会咬人。",
        "is_venomous": False,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Python_regius.jpg/1200px-Python_regius.jpg"
    },
    {
        "name": "王锦蛇",
        "scientific_name": "Elaphe carinata",
        "description": "王锦蛇又称菜花蛇、大王蛇。体背黄绿色，有黑色斑纹。是中国常见的无毒蛇，也是捕鼠能手。",
        "temperament": "性格凶猛，动作迅速。无毒但会通过缠绕猎物进行捕食。",
        "treatment": "无毒蛇，咬伤后清洁消毒伤口即可。",
        "is_venomous": False,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Elaphe_carinata.jpg/1200px-Elaphe_carinata.jpg"
    },
    {
        "name": "黑眉锦蛇",
        "scientific_name": "Orthriophis taeniurus",
        "description": "黑眉锦蛇因眼后有黑色眉纹而得名。体型较大，可达2米以上。是中国常见的无毒蛇。",
        "temperament": "性格相对温和，行动较缓慢。主要以鼠类为食。",
        "treatment": "无毒蛇，咬伤后清洁消毒伤口即可。",
        "is_venomous": False,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Rat_snake.jpg/1200px-Rat_snake.jpg"
    },
    {
        "name": "赤链蛇",
        "scientific_name": "Lycodon rufozonatum",
        "description": "赤链蛇体背红黑色相间，有红色环纹。是中国常见的无毒蛇，部分个体可能具有微毒性。",
        "temperament": "性格较胆小，受到威胁时会分泌有臭味的物质。无危为逊。",
        "treatment": "无毒或微毒，咬伤后清洁消毒即可，少数过敏体质需就医。",
        "is_venomous": False,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Lycodon_rufozonatum.jpg/1200px-Lycodon_rufozonatum.jpg"
    },
    {
        "name": "乌梢蛇",
        "scientific_name": "Zaocys dhumnades",
        "description": "乌梢蛇体背棕褐色或黑褐色，是中国传统的药用蛇类。体型较大，可达2米以上。",
        "temperament": "性格温和，行动迅速。善攀爬，有一定的观赏价值。",
        "treatment": "无毒蛇，咬伤后清洁消毒伤口即可。",
        "is_venomous": False,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Zaocys_dhumnades.jpg/1200px-Zaocys_dhumnades.jpg"
    },
    {
        "name": "翠青蛇",
        "scientific_name": "Cyclura_phaps",
        "description": "翠青蛇通体翠绿色，外观与竹叶青相似，但无毒。常被误认为竹叶青而被打。",
        "temperament": "性格温顺，以蚯蚓、昆虫为主食。无攻击性。",
        "treatment": "完全无毒，咬伤后清洁消毒即可。",
        "is_venomous": False,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Green_snake.jpg/1200px-Green_snake.jpg"
    },
    {
        "name": "滑鼠蛇",
        "scientific_name": "Ptyas mucosa",
        "description": "滑鼠蛇又称水律蛇，是体型较大的无毒蛇。背部棕褐色，腹部黄白色。是中国南方常见的食用蛇。",
        "temperament": "性格凶猛，动作敏捷。无毒但会通过缠绕进行捕食。",
        "treatment": "无毒蛇，咬伤后清洁消毒伤口即可。",
        "is_venomous": False,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Ptyas_mucosa.jpg/1200px-Ptyas_mucosa.jpg"
    },
    {
        "name": "白条锦蛇",
        "scientific_name": "Elaphe dione",
        "description": "白条锦蛇是中国常见的无毒蛇，体背灰褐色或棕黄色，有3条浅色纵纹。适应能力强。",
        "temperament": "性格温和，适应能力强。主要以小型啮齿动物为食。",
        "treatment": "无毒蛇，咬伤后清洁消毒伤口即可。",
        "is_venomous": False,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Dione_rat_snake.jpg/1200px-Dione_rat_snake.jpg"
    },
    {
        "name": "虎斑颈槽蛇",
        "scientific_name": "Rhabdophis tigrinus",
        "scientific_name": "Rhabdophis tigrinus",
        "description": "虎斑颈槽蛇又称野鸡脖子、红脖颈槽蛇。颈部有红黑相间的斑纹。性情温和，但具有后毒牙。",
        "temperament": "平时性格温和，但在受到威胁时可能会以后沟牙咬人。",
        "treatment": "1. 清洁伤口\n2. 观察症状\n3. 如有中毒症状，及时就医",
        "is_venomous": False,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Tiger_keelback.jpg/1200px-Tiger_keelback.jpg"
    }
]


def download_image(url: str) -> str | None:
    """下载图片并转为base64"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            import base64
            mime_type = response.headers.get('Content-Type', 'image/jpeg')
            b64_data = base64.b64encode(response.content).decode()
            return f"data:{mime_type};base64,{b64_data}"
    except Exception as e:
        print(f"下载图片失败: {url}, 错误: {e}")
    return None


def init_database():
    """初始化数据库连接"""
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()


def seed_snakes():
    """添加蛇类数据到数据库"""
    session = init_database()

    existing_count = session.query(Snake).count()
    if existing_count > 0:
        print(f"数据库中已有 {existing_count} 条蛇类数据，是否清空重新添加？(y/n): ")
        response = input().strip().lower()
        if response == 'y':
            session.query(Snake).delete()
            session.commit()
            print("已清空现有数据")
        else:
            print("跳过数据添加")
            return

    print(f"开始添加 {len(SNAKE_DATA)} 条蛇类数据...")

    for i, data in enumerate(SNAKE_DATA):
        print(f"[{i+1}/{len(SNAKE_DATA)}] 正在处理: {data['name']}")

        image = data.get('image')
        if image:
            print(f"  下载图片: {image}")
            image_data = download_image(image)
            if image_data:
                data['image'] = image_data
            else:
                data['image'] = None

        snake = Snake(**data)
        session.add(snake)
        session.commit()
        print(f"  添加成功: {data['name']}")

        time.sleep(0.5)

    print(f"\n完成！共添加 {len(SNAKE_DATA)} 条数据")


if __name__ == "__main__":
    print("=" * 50)
    print("蛇类数据爬虫")
    print("=" * 50)
    seed_snakes()
