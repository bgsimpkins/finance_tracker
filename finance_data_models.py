from datetime import date, datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Integer, String, Numeric, Boolean, Date, DateTime, create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# Account through which transactions are done (e.g., bank account)
class Account(Base):
    __tablename__ = "Account"

    id: Mapped[int] = mapped_column(primary_key=True)

    account_number: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(100))

    # E.g. bank (PNC, 5/3, Wells Fargo)
    debt_entity: Mapped[str] = mapped_column(String(50))

    description: Mapped[str] = mapped_column(String(200), nullable=True)

    date_created: Mapped[date] = mapped_column(Date)

    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"         ##TODO: is there a way to NULL out orphans here? Just remove the foreign key constraint?
    )


# Category of transaction. Allows higher-order analytics/tracking
class TransactionCategory(Base):
    __tablename__ = "TransactionCategory"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    description: Mapped[str] = mapped_column(String(200), nullable=True)

    parent: Mapped[str] = mapped_column(String(100), nullable=True)

    need_flag: Mapped[bool] = mapped_column(Boolean)

    priority: Mapped[int] = mapped_column(Integer)

    date_created: Mapped[date] = mapped_column(Date)

    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"         ##TODO: is there a way to NULL out orphans here? Just remove the foreign key constraint?
    )

    category_mappings: Mapped[List["CategoryMapping"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )


# Encapsulate logic to map TransactionCategory to Transactions (e.g., 1:1, keywords, more complex matching rules)
class CategoryMapping (Base):
    __tablename__ = "CategoryMapping"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Value to be mapped to category (e.g., Transaction to description)
    source_value: Mapped[str] = mapped_column(String(200))

    # Indicator for rule/operato used to map source_value to category
    # TODO: Could snowflake mapping rules out into their own table..
    mapping_rule: Mapped[str] = mapped_column(String(100))

    #Parameters
    param1: Mapped[str] = mapped_column(String(200), nullable=True)
    param2: Mapped[str] = mapped_column(String(200), nullable=True)

    category_id = mapped_column(ForeignKey(TransactionCategory.id))
    category: Mapped["TransactionCategory"] = relationship(back_populates="category_mappings")

    description: Mapped[str] = mapped_column(String(200), nullable=True)

    date_created: Mapped[date] = mapped_column(Date)


# Financial transaction
# (credit or debit)
class Transaction(Base):
    __tablename__ = "Transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))

    # Source of transaction (e.g, store, Amazon, work)
    source: Mapped[str] = mapped_column(String(50), nullable=True)

    # Account
    account_id = mapped_column(ForeignKey(Account.id))
    account: Mapped["Account"] = relationship(back_populates="transactions")

    # Category
    category_id = mapped_column(ForeignKey(TransactionCategory.id))
    category: Mapped["TransactionCategory"] = relationship(back_populates="transactions")

    # Description in transaction (required)
    description: Mapped[str] = mapped_column(String(100))
    notes: Mapped[str] = mapped_column(String(200), nullable=True)

    # Dates relevant to transaction
    date_created: Mapped[date] = mapped_column(Date)
    date_processed: Mapped[date] = mapped_column(Date, nullable=True)

    date_imported:Mapped[datetime] = mapped_column(DateTime)


def db_connect(config_vals):
    return create_engine(f"mysql+pymysql://{config_vals['user']}:{config_vals['password']}@{config_vals['host']}:3306/{config_vals['database']}",
                         echo=False)


def create_db_from_models(engine, drop_all=False):
    if drop_all:
        print("Purging DB objects...")
        Base.metadata.drop_all(engine)

    # Create DB schema from models
    print("Creating DB objects from models...")
    Base.metadata.create_all(engine)

    return Base

# TODO: Should just return account?
def account_exists(account_name, session):
    stmt = select(Account).where(Account.name == account_name).exists()
    return session.scalar(select(stmt))


def get_category_for_name(category_name, session) -> TransactionCategory:
    stmt = select(TransactionCategory).where(TransactionCategory.name == category_name)
    return session.scalar(stmt)


def test_create_account(engine):
    session = Session(engine)
    fifth_third = Account(
        account_number='66666666',
        name='Fifth Third Checking',
        debt_entity="Fifth Third Bank",
        description="routing no=434q3452456",
        date_created=date.today()
    )
    session.add_all([fifth_third])
    session.commit()


def test_add_transaction(engine):
    session = Session(engine)
    stmt = select(Account).where(Account.name=="Fifth Third Checking")
    account = session.scalars(stmt).one()

    trans = Transaction(
        amount="69.24",
        source="Amazon",
        account=account,
        date_created=datetime.strptime("2024-01-01", "%Y-%m-%d"),
        date_imported=datetime.strptime("2024-01-03 02:34:00", "%Y-%m-%d %H:%M:%S")

    )
    session.add_all([trans])
    session.commit()
