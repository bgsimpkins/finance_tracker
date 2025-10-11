from sqlalchemy.orm import Session
from sqlalchemy import select
from finance_data_models import TransactionCategory


class CategoryMapper:
    def __init__(self):
        pass

    def do_category_mapping(source_value, session):

        # Use default as placeholder
        stmt = select(TransactionCategory).where(TransactionCategory.name == "default")
        return session.scalars(stmt).one()

        # TODO: Add 'contains' rule

        # TODO: Run all rules. use hierarchy.
