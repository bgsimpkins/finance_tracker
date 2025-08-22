import os
import pandas as pd
import numpy as np
from datetime import datetime
from finance_data_models import Account, Transaction, account_exists
from sqlalchemy.orm import Session
from sqlalchemy import select


def import_accounts(filepath, engine):
    df = pd.read_csv(f"import/{filepath}")
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

        else:
            print(f"account {row['name']} exists!")

    session.commit()


def import_statement_chase_slate(filename, engine):
    # TODO: This is sloppy. Is a copy and paste from a shitty PDF table.
    #  Split row with space. First element is date, last is amount, rest is source

    # Filename should be format "chase_<year>_<month>.txt"
    filepath = f"import/{filename}"
    year = filename[6:10]
    print(f"filename={filename}")

    session = Session(engine)
    stmt = select(Account).where(Account.name == "Chase Slate")
    account = session.scalars(stmt).one()

    with open(filepath) as file:

        for line in file:

            line_spl = line.split(" ")

            # Date is first element
            date = f"{line_spl[0]}/{year}"
            date = datetime.strptime(date, "%m/%d/%Y")

            # Amount is last
            amount = line_spl[-1]

            #Remove thousands separator
            amount = amount.replace(",","")

            # Everything else is source (including location and city,state) TODO: Could parse these out
            source = " ".join(line_spl[1:-1])

            print(f"date={date} | amount={amount} | source={source}")

            trans = Transaction(
                amount=amount,
                source=source,
                account=account,
                date_created=date,
                date_imported=datetime.now()
            )
            session.add(trans)

        session.commit()

        os.rename(filepath, f"import/archive/{filename}")




