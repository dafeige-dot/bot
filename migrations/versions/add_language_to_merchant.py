"""add language to merchant

Revision ID: 002_add_language
Revises: 001_initial
Create Date: 2025-11-06 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_language'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 language 列
    op.add_column('merchants', sa.Column('language', sa.String(length=10), nullable=False, server_default='zh', comment='用户语言偏好 (zh/en)'))


def downgrade() -> None:
    # 删除 language 列
    op.drop_column('merchants', 'language')


