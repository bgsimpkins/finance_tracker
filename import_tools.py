import pandas as pd
import numpy as np
from datetime import datetime
from finance_data_models import Account, account_exists
from sqlalchemy.orm import Session
from sqlalchemy import select


def import_accounts(filepath, engine):
    df = pd.read_csv(filepath)
    df = df.replace({np.nan}, None)     # Pandas converts empty cells to NAN. Covert to None/NULL
    session = Session(engine)
    for i, row in df.iterrows():

        if not account_exists(row["name"], engine):
            account = Account(
                account_number=row["account_number"],
                name=row["name"],
                debt_entity=row["debt_entity"],
                description=row["description"],
                date_created=datetime.strptime(row["date_created"], "%Y-%m-%d")
            )
            session.add(account)
            session.commit()
        else:
            print(f"account {row['name']} exists!")
