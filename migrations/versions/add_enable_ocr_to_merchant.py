"""add enable_ocr to merchant

Revision ID: 003_add_enable_ocr
Revises: 002_add_language
Create Date: 2025-12-04 21:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_enable_ocr'
down_revision = '002_add_language'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 enable_ocr 列
    op.add_column('merchants', sa.Column('enable_ocr', sa.Boolean(), nullable=False, server_default='1', comment='是否启用OCR图片识别'))


def downgrade() -> None:
    # 删除 enable_ocr 列
    op.drop_column('merchants', 'enable_ocr')

