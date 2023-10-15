"""Change uuid_jti column data type

Revision ID: 0004_db8df3d4425c
Revises: 0003_810e096646b1
Create Date: 2023-10-16 00:41:29.321674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '0004_db8df3d4425c'
down_revision: Union[str, None] = '0003_810e096646b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('admin', 'uuid_jti',
               existing_type=mysql.CHAR(length=32),
               type_=sa.String(length=256),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('admin', 'uuid_jti',
               existing_type=sa.String(length=256),
               type_=mysql.CHAR(length=32),
               existing_nullable=True)
    # ### end Alembic commands ###