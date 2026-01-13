from sqlalchemy.orm import Session
from sqlalchemy import select, text
from finance_data_models import TransactionCategory


class CategoryMapper:
    def __init__(self):
        pass

    def do_category_mapping(self, source_value, session):

        # Use default as placeholder
        stmt = select(TransactionCategory).where(TransactionCategory.name == "default")
        default_cat = session.scalars(stmt).one()

        ###################################
        # 'contains' rule. TODO: Could convert to ORM query

        sql = text("""
            SELECT cat.id
            FROM TransactionCategory cat
                INNER JOIN CategoryMapping cmap
                    ON cat.id = cmap.category_id
            WHERE cmap.mapping_rule = 'contains'
                AND :value LIKE concat('%',cmap.param1,'%')
            ORDER BY cat.priority ASC, name ASC
            limit 1
                ;
        """)

        result = session.execute(sql,{"value":source_value})
        if result.rowcount > 0:
            id = result.scalar_one()
            print(id)
            return id


        # TODO: Run all rules. use hierarchy.

        # TODO: Remove
        print(f'!!No Mapped Category found for {source_value}. Using Default!')
        return default_cat.id
