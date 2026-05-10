#!/usr/bin/env python3
"""
后端启动脚本
自动检测并执行数据库迁移，然后启动服务
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
    """自动执行所有待执行的迁移"""
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

    has_changes = False
    for migration_name, sqls in all_migrations:
        if run_migration(engine, migration_name, sqls):
            existing = get_existing_migrations(engine)
            if migration_name in existing:
                pass
            else:
                has_changes = True
        else:
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
