from datetime import datetime
from typing import List

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column

Base = declarative_base()


class DateTimeMixin:
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )


class Admin(Base, DateTimeMixin):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email = Column(String(256), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    nickname = Column(String(256), unique=True, nullable=False)
    hashed_refresh_token = Column(String(256), nullable=True)
    uuid_jti = Column(String(256), nullable=True)

    def __repr__(self):
        return f"Admin(id={self.id}, email={self.email}, nickname={self.nickname})"

    @classmethod
    def create_admin_object(
        cls, email: str, hashed_password: str, nickname: str
    ) -> "Admin":
        return cls(email=email, password=hashed_password, nickname=nickname)

    def update_token(self, hashed_refresh_token: str, uuid_jti: str):
        self.hashed_refresh_token = hashed_refresh_token
        self.uuid_jti = uuid_jti
        return self

    def delete_token_jti_data(self):
        self.hashed_refresh_token = None
        self.uuid_jti = None
        return self


class Politician(Base, DateTimeMixin):
    __tablename__ = "politician"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name = Column(String(10), nullable=False, comment="의원 이름")
    profile_url = Column(String(256), nullable=True, comment="프로필 주소")
    political_party = Column(String(30), nullable=False, comment="소속 정당")
    elected_count = Column(Integer, nullable=False, comment="당선 횟수")
    total_promise_count = Column(Integer, nullable=True, comment="총 공약수")
    completed_promise_count = Column(Integer, nullable=True, comment="완료 공약수")
    in_progress_promise_count = Column(Integer, nullable=True, comment="추진 중인 공약수")
    pending_promise_count = Column(Integer, nullable=True, comment="보류 공약수")
    discarded_promise_count = Column(Integer, nullable=True, comment="폐기 공약수")
    other_promise_count = Column(Integer, nullable=True, comment="기타 공약수")
    resolve_required_promise_count = Column(
        Integer, nullable=True, comment="필요 입법 공약 총 수"
    )
    resolved_promise_count = Column(Integer, nullable=True, comment="입법 의결 완료 공약 총 수")
    total_required_funds = Column(Integer, nullable=True, comment="필요 재정 총액")
    total_secured_funds = Column(Integer, nullable=True, comment="확보 재정 총액")
    total_executed_funds = Column(Integer, nullable=True, comment="집행 재정 총액")
    notes = Column(JSON, nullable=True)

    promise_count_detail: Mapped["PromiseCountDetail"] = relationship(
        back_populates="politician"
    )
    committee: Mapped[List["Committee"]] = relationship(back_populates="politician")
    jurisdiction: Mapped[List["Jurisdiction"]] = relationship(
        back_populates="politician"
    )

    def __repr__(self):
        return f"Politician(id={self.id}, name={self.name}, political_party={self.political_party})"


class PromiseCountDetail(Base, DateTimeMixin):
    __tablename__ = "promise_count_detail"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    politician_id: Mapped[int] = mapped_column(
        ForeignKey("politician.id"), nullable=False, comment="의원 id"
    )
    completed_national_promise_count = Column(
        Integer, nullable=True, comment="완료 국정 공약수"
    )
    total_national_promise_count = Column(Integer, nullable=True, comment="총 국정 공약수")
    completed_local_promise_count = Column(Integer, nullable=True, comment="완료 지역 공약수")
    total_local_promise_count = Column(Integer, nullable=True, comment="총 지역 공약수")
    completed_legislative_promise_count = Column(
        Integer, nullable=True, comment="완료 입법 공약수"
    )
    total_legislative_promise_count = Column(Integer, nullable=True, comment="총 입법 공약수")
    completed_financial_promise_count = Column(
        Integer, nullable=True, comment="완료 재정 공약수"
    )
    total_financial_promise_count = Column(Integer, nullable=True, comment="총 재정 공약수")
    completed_in_term_promise_count = Column(
        Integer, nullable=True, comment="완료 임기 내 공약수"
    )
    total_in_term_promise_count = Column(Integer, nullable=True, comment="총 임기 내 공약수")
    completed_after_term_promise_count = Column(
        Integer, nullable=True, comment="완료 임기 후 공약수"
    )
    total_after_term_promise_count = Column(
        Integer, nullable=True, comment="총 임기 후 공약수"
    )
    completed_ongoing_business_promise_count = Column(
        Integer, nullable=True, comment="완료 지속 사업 공약수"
    )
    total_ongoing_business_promise_count = Column(
        Integer, nullable=True, comment="총 지속 사업 공약수"
    )
    completed_new_business_promise_count = Column(
        Integer, nullable=True, comment="완료 신규 사업 공약수"
    )
    total_new_business_promise_count = Column(
        Integer, nullable=True, comment="총 신규 사업 공약수"
    )
    notes = Column(JSON, nullable=True)

    politician: Mapped["Politician"] = relationship(
        back_populates="promise_count_detail"
    )

    def __repr__(self):
        return f"PromiseCountDetail(id={self.id}, politician_id={self.politician_id})"


class Committee(Base, DateTimeMixin):
    __tablename__ = "committee"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    politician_id: Mapped[int] = mapped_column(
        ForeignKey("politician.id"), nullable=False, comment="의원 id"
    )
    is_main = Column(Boolean, nullable=False, comment="해당 의원의 대표 위원회 여부")
    name = Column(String(30), nullable=False, comment="위원회 명칭")

    politician: Mapped["Politician"] = relationship(back_populates="committee")

    def __repr__(self):
        return f"Committee(id={self.id}, name={self.name}, politician_id={self.politician_id})"


class Region(Base, DateTimeMixin):
    __tablename__ = "region"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    region = Column(String(20), nullable=False, comment="지역구")

    constituency: Mapped[List["Constituency"]] = relationship(back_populates="region")

    def __repr__(self):
        return f"Region(id={self.id}, region={self.region})"


class Constituency(Base, DateTimeMixin):
    __tablename__ = "constituency"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    assembly_term = Column(Integer, nullable=False, comment="국회 회기")
    region_id: Mapped[int] = mapped_column(
        ForeignKey("region.id"), nullable=False, comment="지역구 id"
    )
    district = Column(String(20), nullable=True, comment="세부 지역구")
    section = Column(String(20), nullable=True, comment="분구")

    region: Mapped["Region"] = relationship(back_populates="constituency")
    jurisdiction: Mapped["Jurisdiction"] = relationship(back_populates="constituency")

    def __repr__(self):
        return f"Constituency(id={self.id}, assembly_term={self.assembly_term}, region={self.region}, district={self.district}, section={self.section})"


class Jurisdiction(Base, DateTimeMixin):
    __tablename__ = "jurisdiction"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    politician_id: Mapped[int] = mapped_column(
        ForeignKey("politician.id"), nullable=False, comment="의원 id"
    )
    constituency_id: Mapped[int] = mapped_column(
        ForeignKey("constituency.id"), nullable=False, comment="지역구 id"
    )

    politician: Mapped["Politician"] = relationship(back_populates="jurisdiction")
    constituency: Mapped["Constituency"] = relationship(back_populates="jurisdiction")

    def __repr__(self):
        return f"Constituency(id={self.id}, politician_id={self.politician_id}, constituency_id={self.constituency_id})"
