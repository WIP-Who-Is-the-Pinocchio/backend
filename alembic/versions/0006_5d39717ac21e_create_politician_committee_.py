"""Create Politician, Committee, PromiseCountDetail, Constituency, Jurisdiction table

Revision ID: 0006_5d39717ac21e
Revises: 0005_c024c5eacb27
Create Date: 2023-10-22 22:46:14.202764

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0006_5d39717ac21e"
down_revision: Union[str, None] = "0005_c024c5eacb27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "constituency",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("assembly_term", sa.Integer(), nullable=False, comment="국회 회기"),
        sa.Column("region", sa.String(length=256), nullable=False, comment="지역구"),
        sa.Column("district", sa.String(length=256), nullable=True, comment="세부 지역구"),
        sa.Column("section", sa.String(length=256), nullable=True, comment="분구"),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            default=datetime.now(),
            onupdate=datetime.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_constituency_id"), "constituency", ["id"], unique=False)
    op.create_table(
        "politician",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False, comment="의원 이름"),
        sa.Column(
            "profile_url", sa.String(length=256), nullable=True, comment="프로필 주소"
        ),
        sa.Column(
            "political_party", sa.String(length=256), nullable=False, comment="소속 정당"
        ),
        sa.Column("elected_count", sa.Integer(), nullable=False, comment="당선 횟수"),
        sa.Column("total_promise_count", sa.Integer(), nullable=True, comment="총 공약수"),
        sa.Column(
            "completed_promise_count", sa.Integer(), nullable=True, comment="완료 공약수"
        ),
        sa.Column(
            "in_progress_promise_count",
            sa.Integer(),
            nullable=True,
            comment="추진 중인 공약수",
        ),
        sa.Column(
            "pending_promise_count", sa.Integer(), nullable=True, comment="보류 공약수"
        ),
        sa.Column(
            "discarded_promise_count", sa.Integer(), nullable=True, comment="폐기 공약수"
        ),
        sa.Column("other_promise_count", sa.Integer(), nullable=True, comment="기타 공약수"),
        sa.Column(
            "resolve_required_promise_count",
            sa.Integer(),
            nullable=True,
            comment="필요 입법 공약 총 수",
        ),
        sa.Column(
            "resolved_promise_count",
            sa.Integer(),
            nullable=True,
            comment="입법 의결 완료 공약 총 수",
        ),
        sa.Column(
            "total_required_funds", sa.Integer(), nullable=True, comment="필요 재정 총액"
        ),
        sa.Column(
            "total_secured_funds", sa.Integer(), nullable=True, comment="확보 재정 총액"
        ),
        sa.Column(
            "total_executed_funds", sa.Integer(), nullable=True, comment="집행 재정 총액"
        ),
        sa.Column("notes", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            default=datetime.now(),
            onupdate=datetime.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_politician_id"), "politician", ["id"], unique=False)
    op.create_table(
        "committee",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("politician_id", sa.Integer(), nullable=False, comment="의원 id"),
        sa.Column("is_main", sa.Boolean(), nullable=False, comment="해당 의원의 대표 위원회 여부"),
        sa.Column("name", sa.String(length=256), nullable=False, comment="위원회 명칭"),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            default=datetime.now(),
            onupdate=datetime.now(),
        ),
        sa.ForeignKeyConstraint(
            ["politician_id"],
            ["politician.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_committee_id"), "committee", ["id"], unique=False)
    op.create_table(
        "jurisdiction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("politician_id", sa.Integer(), nullable=False, comment="의원 id"),
        sa.Column("constituency_id", sa.Integer(), nullable=False, comment="지역구 id"),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            default=datetime.now(),
            onupdate=datetime.now(),
        ),
        sa.ForeignKeyConstraint(
            ["constituency_id"],
            ["constituency.id"],
        ),
        sa.ForeignKeyConstraint(
            ["politician_id"],
            ["politician.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jurisdiction_id"), "jurisdiction", ["id"], unique=False)
    op.create_table(
        "promise_count_detail",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("politician_id", sa.Integer(), nullable=False, comment="의원 id"),
        sa.Column(
            "completed_national_promise_count",
            sa.Integer(),
            nullable=True,
            comment="완료 국정 공약수",
        ),
        sa.Column(
            "total_national_promise_count",
            sa.Integer(),
            nullable=True,
            comment="총 국정 공약수",
        ),
        sa.Column(
            "completed_local_promise_count",
            sa.Integer(),
            nullable=True,
            comment="완료 지역 공약수",
        ),
        sa.Column(
            "total_local_promise_count", sa.Integer(), nullable=True, comment="총 지역 공약수"
        ),
        sa.Column(
            "completed_legislative_promise_count",
            sa.Integer(),
            nullable=True,
            comment="완료 입법 공약수",
        ),
        sa.Column(
            "total_legislative_promise_count",
            sa.Integer(),
            nullable=True,
            comment="총 입법 공약수",
        ),
        sa.Column(
            "completed_financial_promise_count",
            sa.Integer(),
            nullable=True,
            comment="완료 재정 공약수",
        ),
        sa.Column(
            "total_financial_promise_count",
            sa.Integer(),
            nullable=True,
            comment="총 재정 공약수",
        ),
        sa.Column(
            "completed_in_term_promise_count",
            sa.Integer(),
            nullable=True,
            comment="완료 임기 내 공약수",
        ),
        sa.Column(
            "total_in_term_promise_count",
            sa.Integer(),
            nullable=True,
            comment="총 임기 내 공약수",
        ),
        sa.Column(
            "completed_after_term_promise_count",
            sa.Integer(),
            nullable=True,
            comment="완료 임기 후 공약수",
        ),
        sa.Column(
            "total_after_term_promise_count",
            sa.Integer(),
            nullable=True,
            comment="총 임기 후 공약수",
        ),
        sa.Column(
            "completed_ongoing_business_promise_count",
            sa.Integer(),
            nullable=True,
            comment="완료 지속 사업 공약수",
        ),
        sa.Column(
            "total_ongoing_business_promise_count",
            sa.Integer(),
            nullable=True,
            comment="총 지속 사업 공약수",
        ),
        sa.Column(
            "completed_new_business_promise_count",
            sa.Integer(),
            nullable=True,
            comment="완료 신규 사업 공약수",
        ),
        sa.Column(
            "total_new_business_promise_count",
            sa.Integer(),
            nullable=True,
            comment="총 신규 사업 공약수",
        ),
        sa.Column("notes", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            default=datetime.now(),
            onupdate=datetime.now(),
        ),
        sa.ForeignKeyConstraint(
            ["politician_id"],
            ["politician.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_promise_count_detail_id"), "promise_count_detail", ["id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_promise_count_detail_id"), table_name="promise_count_detail")
    op.drop_table("promise_count_detail")
    op.drop_index(op.f("ix_jurisdiction_id"), table_name="jurisdiction")
    op.drop_table("jurisdiction")
    op.drop_index(op.f("ix_committee_id"), table_name="committee")
    op.drop_table("committee")
    op.drop_index(op.f("ix_politician_id"), table_name="politician")
    op.drop_table("politician")
    op.drop_index(op.f("ix_constituency_id"), table_name="constituency")
    op.drop_table("constituency")
    # ### end Alembic commands ###
