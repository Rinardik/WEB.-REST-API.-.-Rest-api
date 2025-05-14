from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

SqlAlchemyBase = declarative_base()
__factory = None


def global_init(db_file):
    """
    Инициализация подключения к базе данных
    :param db_file: путь к файлу базы данных
    """
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    
    print(f"Подключение к базе данных по адресу {conn_str}")
    engine = create_engine(conn_str, echo=False)
    __factory = sessionmaker(bind=engine)
    from . import jobs
    from . import users
    from . import categories
    SqlAlchemyBase.metadata.create_all(engine)


def create_session():
    """
    Создает новую сессию для работы с базой данных
    :return: объект сессии
    """
    global __factory
    if not __factory:
        raise Exception("Сначала вызовите global_init()")
    
    return __factory()