from sqlalchemy import create_engine
import config
import platform


def get_db():
    dyna_server = config.dynaServer
    dyna_db = config.dynaDBName
    dyna_user = config.dynaUserName
    dyna_password = config.dynaPassword

    dynacom_conn = f'mssql+pyodbc://{dyna_user}:{dyna_password}@{dyna_server}/{dyna_db}'
    if platform.system() == 'Windows':
        dynacom_driver = 'SQL Server'
    else:
        dynacom_driver = 'ODBC+Driver+17+for+SQL+Server'
    dynacom_eng = create_engine(dynacom_conn+'?driver='+dynacom_driver)
    return dynacom_eng
