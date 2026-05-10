#!/usr/bin/env python3
"""
数据库迁移脚本
支持初始化和升级功能，自动检测数据库状态
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


def get_existing_tables(engine):
    """获取数据库中已存在的表"""
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_existing_migrations(engine):
    """获取已执行的迁移版本"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if 'alembic_version' in tables:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            return [row[0] for row in result]
    return []


def init_database():
    """初始化数据库表结构"""
    from app.models.base import Base

    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(engine)
    print("✓ 数据库表结构初始化完成")


def setup_alembic():
    """初始化Alembic版本追踪"""
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if 'alembic_version' not in tables:
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
        print("✓ Alembic版本追踪已初始化")


def create_default_admin():
    """创建默认管理员账号"""
    engine = create_engine(settings.DATABASE_URL)
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
            print("✓ 默认管理员账号已创建 (admin/admin123)")
        else:
            print("ℹ 管理员账号已存在，跳过创建")
    except Exception as e:
        print(f"✗ 创建管理员账号失败: {e}")
        session.rollback()
    finally:
        session.close()


def run_migration(migration_name: str, sql_statements: list):
    """执行单个迁移"""
    engine = create_engine(settings.DATABASE_URL)
    existing_migrations = get_existing_migrations(engine)

    if migration_name in existing_migrations:
        print(f"ℹ 迁移 {migration_name} 已执行，跳过")
        return False

    print(f"执行迁移: {migration_name}")
    try:
        with engine.connect() as conn:
            for sql in sql_statements:
                conn.execute(text(sql))
            conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{migration_name}')"))
            conn.commit()
        print(f"✓ 迁移 {migration_name} 执行成功")
        return True
    except Exception as e:
        print(f"✗ 迁移 {migration_name} 执行失败: {e}")
        return False


def migrate_add_scientific_name():
    """迁移: 添加学名字段"""
    return run_migration('0002_add_scientific_name', [
        "ALTER TABLE snakes ADD COLUMN IF NOT EXISTS scientific_name VARCHAR(200)"
    ])


def migrate_add_indexes():
    """迁移: 添加索引"""
    return run_migration('0003_add_indexes', [
        "CREATE INDEX IF NOT EXISTS idx_snakes_name ON snakes(name)",
        "CREATE INDEX IF NOT EXISTS idx_snakes_venomous ON snakes(is_venomous)"
    ])


def migrate_rename_image_field():
    """迁移: 重命名字段（如果需要）"""
    return run_migration('0004_rename_image_field', [])


def show_status():
    """显示迁移状态"""
    engine = create_engine(settings.DATABASE_URL)
    tables = get_existing_tables(engine)
    existing_migrations = get_existing_migrations(engine)

    print("\n" + "="*50)
    print("数据库迁移状态")
    print("="*50)
    print(f"\n已存在的表: {', '.join(tables) if tables else '无'}")
    print(f"已执行的迁移: {', '.join(existing_migrations) if existing_migrations else '无'}")

    available_migrations = ['0002_add_scientific_name', '0003_add_indexes']
    pending = [m for m in available_migrations if m not in existing_migrations]

    if pending:
        print(f"\n待执行的迁移: {', '.join(pending)}")
    else:
        print("\n✓ 所有迁移已执行完成")

    print()


def main():
    """主函数"""
    print("="*50)
    print("🐍 数据库迁移工具")
    print("="*50)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'status':
            show_status()
        elif command == 'init':
            print("\n初始化数据库...")
            init_database()
            setup_alembic()
            create_default_admin()
            print("\n✓ 数据库初始化完成")
        elif command == 'upgrade':
            print("\n执行升级...")
            migrate_add_scientific_name()
            migrate_add_indexes()
            print("\n✓ 升级完成")
        elif command == 'full':
            print("\n完整初始化（包含升级）...")
            init_database()
            setup_alembic()
            create_default_admin()
            migrate_add_scientific_name()
            migrate_add_indexes()
            print("\n✓ 完整初始化完成")
        else:
            print(f"未知命令: {command}")
            print("\n可用命令:")
            print("  status  - 显示迁移状态")
            print("  init    - 初始化数据库")
            print("  upgrade - 执行升级")
            print("  full    - 完整初始化")
    else:
        show_status()
        print("\n用法:")
        print("  python migrate.py status   - 显示迁移状态")
        print("  python migrate.py init    - 初始化数据库")
        print("  python migrate.py upgrade - 执行升级")
        print("  python migrate.py full    - 完整初始化")


if __name__ == "__main__":
    main()
