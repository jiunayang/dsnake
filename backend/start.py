#!/usr/bin/env python3
"""
后端启动脚本
自动检测并执行数据库迁移，导入初始数据，然后启动服务
"""

import sys
import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.snake import Snake
from app.models.admin import Admin


INITIAL_SNAKE_DATA = [
    {"name": "眼镜王蛇", "scientific_name": "Ophiophagus hannah", "description": "眼镜王蛇是世界上最大的毒蛇，体长可达5米。头部呈椭圆形，颈部可膨扁，背部有\"∧\"形黄白色斑纹。分布于南亚和东南亚地区。", "temperament": "领地意识强，行动敏捷，遇到威胁时会立起身体前部并展开颈部的皮褶进行警告。", "treatment": "1. 保持冷静，避免恐慌\n2. 尽快拨打急救电话\n3. 保持伤口低于心脏位置\n4. 避免剧烈运动\n5. 尽快就医，使用抗眼镜蛇毒血清", "is_venomous": True, "image": None},
    {"name": "眼镜蛇", "scientific_name": "Naja", "description": "眼镜蛇是眼镜蛇科眼镜蛇属的毒蛇，上颌骨较短，前端有沟牙。头部呈椭圆形。", "temperament": "性格较为警觉，受惊时颈部会膨扁进行警告。一般不主动攻击人。", "treatment": "1. 保持冷静，减少活动\n2. 尽快就医\n3. 抗蛇毒血清是特效治疗", "is_venomous": True, "image": None},
    {"name": "银环蛇", "scientific_name": "Bungarus multicinctus", "description": "银环蛇是眼镜蛇科环蛇属的一种，俗称过基峡、白节黑、金钱白花蛇等。体背黑白相间环纹，脊棱突出。", "temperament": "性格胆小，常在夜间活动，一般不主动攻击人。但毒性极强。", "treatment": "1. 立即就医\n2. 保持静止\n3. 不要使用止血带\n4. 抗银环蛇毒血清治疗", "is_venomous": True, "image": None},
    {"name": "金环蛇", "scientific_name": "Bungarus fasciatus", "description": "金环蛇是环蛇属的一种，俗称金甲带、金包铁等。特征是黄黑相间宽环纹。", "temperament": "性格温和，夜行性蛇类。毒性很强，但一般不主动攻击人。", "treatment": "1. 保持冷静\n2. 立即就医\n3. 抗蛇毒血清治疗", "is_venomous": True, "image": None},
    {"name": "竹叶青", "scientific_name": "Trimeresurus stejnegeri", "description": "竹叶青是蝰科竹叶青蛇属的管牙类毒蛇，又名翠青蛇。通体绿色，尾背及尾尖焦红色。", "temperament": "性格较神经质，容易被惊扰。昼夜均活动。", "treatment": "1. 保持冷静\n2. 尽快就医\n3. 抗蝮蛇毒血清治疗", "is_venomous": True, "image": None},
    {"name": "尖吻蝮", "scientific_name": "Deinagkistrodon", "description": "尖吻蝮又称百步蛇、五步蛇。背部有灰褐色菱形斑块，头呈三角形。是中国特有的毒蛇。", "temperament": "性格凶猛，攻击性强。有\"坐土\"习性。", "treatment": "1. 保持冷静，避免恐慌\n2. 固定伤肢\n3. 尽快就医\n4. 抗五步蛇毒血清治疗", "is_venomous": True, "image": None},
    {"name": "原矛头蝮", "scientific_name": "Trimeresurus mucrosquamatus", "description": "原矛头蝮又称龟壳花蛇、烙铁头。头呈长三角形，颈部细，形似烙铁。", "temperament": "夜行性蛇类，喜欢夜里出来活动。", "treatment": "1. 保持冷静\n2. 尽快就医\n3. 抗蝮蛇毒血清", "is_venomous": True, "image": None},
    {"name": "蝮蛇", "scientific_name": "Gloydius brevicaudus", "description": "蝮蛇是中国常见的毒蛇，头部呈三角形，背部有深色圆斑。", "temperament": "性格凶猛，行动迅速。有颊窝，能感知温血动物。", "treatment": "1. 保持冷静\n2. 固定伤肢\n3. 尽快就医\n4. 抗蝮蛇毒血清", "is_venomous": True, "image": None},
    {"name": "蝰蛇", "scientific_name": "Daboia russelii", "description": "蝰蛇又称黑斑蝰蛇，体长0.9～1.3米。背面暗褐色，有淡褐色链状椭圆斑。", "temperament": "性格凶猛，昼夜都活动。", "treatment": "1. 立即就医\n2. 抗蛇毒血清", "is_venomous": True, "image": None},
    {"name": "青环海蛇", "scientific_name": "Hydrophis cyanocinctus", "description": "青环海蛇体长橄榄色或黄色，背深灰色，有青黑色环纹达腹部。", "temperament": "海蛇多性格温和，但毒性很强。", "treatment": "1. 立即就医\n2. 抗海蛇毒血清", "is_venomous": True, "image": None},
    {"name": "玉米蛇", "scientific_name": "Pantherophis guttatus", "description": "玉米蛇是最受欢迎的宠物蛇之一，原产于北美洲。体色丰富多变。", "temperament": "性格温顺，很少主动攻击人类。", "treatment": "无毒，咬伤后清洁伤口即可。", "is_venomous": False, "image": None},
    {"name": "球蟒", "scientific_name": "Python regius", "description": "球蟒是最小的蟒蛇之一，因受到惊吓时会缩成一团而得名。", "temperament": "性格温和，非常温顺，一般不会咬人。", "treatment": "无毒，咬伤后清洁消毒即可。", "is_venomous": False, "image": None},
    {"name": "王锦蛇", "scientific_name": "Elaphe carinata", "description": "王锦蛇又称菜花蛇、大王蛇。体背黄绿色，有黑色斑纹。是中国常见的无毒蛇。", "temperament": "性格凶猛，动作迅速。无毒但会通过缠绕猎物进行捕食。", "treatment": "无毒蛇，咬伤后清洁消毒伤口即可。", "is_venomous": False, "image": None},
    {"name": "黑眉锦蛇", "scientific_name": "Orthriophis taeniurus", "description": "黑眉锦蛇因眼后有黑色眉纹而得名。体型较大，是中国常见的无毒蛇。", "temperament": "性格相对温和，行动较缓慢。", "treatment": "无毒蛇，咬伤后清洁消毒伤口即可。", "is_venomous": False, "image": None},
    {"name": "赤链蛇", "scientific_name": "Lycodon rufozonatum", "description": "赤链蛇体背红黑色相间，有红色环纹。是中国常见的无毒蛇。", "temperament": "性格较胆小，受到威胁时会分泌有臭味的物质。", "treatment": "无毒，咬伤后清洁消毒即可。", "is_venomous": False, "image": None},
    {"name": "乌梢蛇", "scientific_name": "Zaocys dhumnades", "description": "乌梢蛇体背棕褐色或黑褐色，是中国传统的药用蛇类。体型较大。", "temperament": "性格温和，行动迅速。善攀爬。", "treatment": "无毒蛇，咬伤后清洁消毒伤口即可。", "is_venomous": False, "image": None},
    {"name": "翠青蛇", "scientific_name": "Cyclura_phaps", "description": "翠青蛇通体翠绿色，外观与竹叶青相似，但无毒。", "temperament": "性格温顺，以蚯蚓、昆虫为主食。无攻击性。", "treatment": "完全无毒，咬伤后清洁消毒即可。", "is_venomous": False, "image": None},
    {"name": "滑鼠蛇", "scientific_name": "Ptyas mucosa", "description": "滑鼠蛇又称水律蛇，是体型较大的无毒蛇。背部棕褐色。", "temperament": "性格凶猛，动作敏捷。无毒但会通过缠绕进行捕食。", "treatment": "无毒蛇，咬伤后清洁消毒伤口即可。", "is_venomous": False, "image": None},
    {"name": "白条锦蛇", "scientific_name": "Elaphe dione", "description": "白条锦蛇是中国常见的无毒蛇，体背灰褐色或棕黄色。", "temperament": "性格温和，适应能力强。", "treatment": "无毒蛇，咬伤后清洁消毒伤口即可。", "is_venomous": False, "image": None},
    {"name": "虎斑颈槽蛇", "scientific_name": "Rhabdophis tigrinus", "description": "虎斑颈槽蛇又称野鸡脖子。颈部有红黑相间的斑纹。性情温和。", "temperament": "平时性格温和，受威胁时可能会咬人。", "treatment": "1. 清洁伤口\n2. 观察症状\n3. 如有不适，及时就医", "is_venomous": False, "image": None},
]


def get_existing_migrations(engine):
    """获取已执行的迁移版本"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if 'alembic_version' in tables:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            return [row[0] for row in result]
    return []


def run_migration(engine, migration_name: str, sql_statements: list) -> bool:
    """执行单个迁移"""
    existing_migrations = get_existing_migrations(engine)

    if migration_name in existing_migrations:
        return True

    print(f"[MIGRATION] 执行迁移: {migration_name}")
    try:
        with engine.connect() as conn:
            for sql in sql_statements:
                conn.execute(text(sql))
            conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{migration_name}')"))
            conn.commit()
        print(f"[MIGRATION] ✓ 迁移 {migration_name} 执行成功")
        return True
    except Exception as e:
        print(f"[MIGRATION] ✗ 迁移 {migration_name} 执行失败: {e}")
        return False


def auto_migrate():
    """自动执行所有待执行的迁移和初始数据"""
    engine = create_engine(settings.DATABASE_URL)

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if 'alembic_version' not in tables:
        print("[MIGRATION] 初始化数据库...")
        from app.models.base import Base
        Base.metadata.create_all(engine)

        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                )
            """))
            conn.commit()
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('0001')"))
            conn.commit()
        print("[MIGRATION] ✓ 数据库初始化完成")

    all_migrations = [
        ('0002_add_scientific_name', [
            "ALTER TABLE snakes ADD COLUMN IF NOT EXISTS scientific_name VARCHAR(200)"
        ]),
        ('0003_add_indexes', [
            "CREATE INDEX IF NOT EXISTS idx_snakes_name ON snakes(name)",
            "CREATE INDEX IF NOT EXISTS idx_snakes_venomous ON snakes(is_venomous)"
        ]),
    ]

    for migration_name, sqls in all_migrations:
        if not run_migration(engine, migration_name, sqls):
            print(f"[MIGRATION] 迁移 {migration_name} 失败，继续启动...")

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        existing_admin = session.query(Admin).filter(Admin.username == 'admin').first()
        if not existing_admin:
            admin = Admin(
                username='admin',
                password_hash=get_password_hash('admin123')
            )
            session.add(admin)
            session.commit()
            print("[MIGRATION] ✓ 默认管理员账号已创建 (admin/admin123)")
        else:
            print("[MIGRATION] ℹ 管理员账号已存在")
    except Exception as e:
        print(f"[MIGRATION] 检查管理员账号时出错: {e}")
        session.rollback()
    finally:
        session.close()

    snake_count = session.query(Snake).count()
    if snake_count == 0:
        print("[DATA] 导入初始蛇类数据...")
        session = Session()
        try:
            for snake_data in INITIAL_SNAKE_DATA:
                snake = Snake(**snake_data)
                session.add(snake)
            session.commit()
            print(f"[DATA] ✓ 已导入 {len(INITIAL_SNAKE_DATA)} 条初始数据")
        except Exception as e:
            print(f"[DATA] ✗ 导入初始数据失败: {e}")
            session.rollback()
        finally:
            session.close()
    else:
        print(f"[DATA] ℹ 数据库已有 {snake_count} 条蛇类数据，跳过初始数据导入")

    print("[MIGRATION] ✓ 数据库迁移检查完成\n")


if __name__ == "__main__":
    print("="*50)
    print("🐍 蛇类百科后端服务")
    print("="*50)

    auto_migrate()

    print("正在启动服务...")
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
