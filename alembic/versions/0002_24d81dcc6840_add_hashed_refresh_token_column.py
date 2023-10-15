"""Add hashed_refresh_token column

Revision ID: 0002_24d81dcc6840
Revises: 0001_c176f828d2e8
Create Date: 2023-10-09 02:48:10.399910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_24d81dcc6840'
down_revision: Union[str, None] = '0001_c176f828d2e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin', sa.Column('hashed_refresh_token', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('admin', 'hashed_refresh_token')
    # ### end Alembic commands ###
