
import os
from dotenv import load_dotenv
from finance_data_models import create_db_from_models, db_connect, test_add_transaction
from import_tools import import_accounts, import_categories, import_category_mappings, import_statement_chase_slate, import_statement_fifth_third_checking, import_statement_wells_fargo


def load_creds():
    load_dotenv()

    config_vals = {
        "host": os.getenv('DB_HOST'),
        "user": os.getenv('DB_USER'),
        "password": os.getenv('DB_PASS'),
        "database": os.getenv('DB_DB'),
        "drop_and_recreate": os.getenv('DROP_AND_RECREATE').upper() == "TRUE",
        "import_accounts": os.getenv('IMPORT_ACCOUNTS').upper() == "TRUE",
        "import_categories": os.getenv('IMPORT_CATEGORIES').upper() == "TRUE",
        "import_category_mappings": os.getenv('IMPORT_CATEGORY_MAPPINGS').upper() == "TRUE"

    }

    return config_vals


def do_imports(engine, config_vals):

    # Loop through imports/ dir and process
    for f in os.listdir("import"):

        if f == "accounts.csv" and config_vals["import_accounts"]:
            import_accounts("accounts.csv", engine)
        elif f == "categories.csv" and config_vals["import_categories"]:
            import_categories("categories.csv", engine)
        elif f == "category_mappings.csv" and config_vals["import_category_mappings"]:
            import_category_mappings("category_mappings.csv", engine)
        elif f[0:5] == "chase":
            import_statement_chase_slate(f"{f}", engine)
        elif f[0:11] == "fifth_third":
            import_statement_fifth_third_checking(f"{f}", engine)
        elif f[0:11] == "wells_fargo":
            import_statement_wells_fargo(f"{f}", engine)


if __name__ == '__main__':

    config_vals = load_creds()
    engine = db_connect(config_vals)
    create_db_from_models(engine,
                          drop_all=config_vals["drop_and_recreate"]
                          )


    do_imports(engine, config_vals)

    # TEST
    # test_add_transaction(engine)



