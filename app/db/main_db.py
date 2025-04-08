import os
import threading
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import sqlite3
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.db.models import Base
from app.utils import ExceptionUtils, PathUtils
from config import Config

lock = threading.Lock()
_Engine = create_engine(
    f"sqlite:///{os.path.join(Config().get_config_path(), 'user.db')}?check_same_thread=False",
    echo=False,
    poolclass=QueuePool,
    pool_pre_ping=True,
    pool_size=200,  # 增加连接池大小
    pool_recycle=60 * 10,
    max_overflow=50,  # 允许额外的连接
    connect_args={
        'timeout': 30,  # 设置超时时间
        'isolation_level': 'IMMEDIATE',  # 设置隔离级别
        'journal_mode': 'WAL',  # 使用 WAL 模式
        'synchronous': 'NORMAL',  # 降低同步级别
        'cache_size': -2000,  # 增加缓存大小
        'temp_store': 'MEMORY',  # 使用内存存储临时表
        'mmap_size': 30000000000  # 增加内存映射大小
    }
)
_Session = scoped_session(sessionmaker(bind=_Engine,
                                       autoflush=True,
                                       autocommit=False,
                                       expire_on_commit=False))

def retry_on_db_error(func):
    """
    数据库错误重试装饰器
    处理以下错误：
    1. 数据库锁定错误
    2. 连接超时错误
    3. 其他SQLAlchemy错误
    """
    def wrapper(*args, **kwargs):
        max_retries = 5  # 增加最大重试次数
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except (sqlite3.OperationalError, OperationalError) as e:
                error_msg = str(e).lower()
                if any(err in error_msg for err in ["database is locked", "timeout", "connection"]):
                    retry_count += 1
                    wait_time = 0.5 * (2 ** retry_count)  # 指数退避策略
                    time.sleep(min(wait_time, 10))  # 最大等待10秒
                    last_error = e
                    if retry_count == max_retries:
                        raise SQLAlchemyError(f"数据库操作失败，重试{max_retries}次后仍然失败: {str(last_error)}")
                else:
                    raise
            except SQLAlchemyError as e:
                retry_count += 1
                wait_time = 0.5 * (2 ** retry_count)
                time.sleep(min(wait_time, 10))
                last_error = e
                if retry_count == max_retries:
                    raise SQLAlchemyError(f"数据库操作失败，重试{max_retries}次后仍然失败: {str(last_error)}")
    return wrapper

class MainDb:
    def __init__(self):
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = _Session()
        return self._session

    def close(self):
        """关闭数据库会话"""
        if self._session:
            self._session.close()
            self._session = None

    def init_db(self):
        with lock:
            try:
                Base.metadata.create_all(_Engine)
                self.init_db_version()
            except SQLAlchemyError as e:
                ExceptionUtils.exception_traceback(e)
                raise

    @retry_on_db_error
    def init_db_version(self):
        """
        初始化数据库版本
        """
        try:
            self.excute("delete from alembic_version where 1")
            self.commit()
        except Exception as err:
            print(str(err))

    @retry_on_db_error
    def init_data(self):
        """
        读取config目录下的sql文件，并初始化到数据库，只处理一次
        """
        config = Config().get_config()
        init_files = Config().get_config("app").get("init_files") or []
        config_dir = Config().get_script_path()
        sql_files = PathUtils.get_dir_level1_files(in_path=config_dir, exts=".sql")
        config_flag = False
        for sql_file in sql_files:
            if os.path.basename(sql_file) not in init_files:
                config_flag = True
                with open(sql_file, "r", encoding="utf-8") as f:
                    sql_list = f.read().split(';\n')
                    for sql in sql_list:
                        try:
                            self.excute(sql)
                            self.commit()
                        except Exception as err:
                            print(str(err))
                init_files.append(os.path.basename(sql_file))
        if config_flag:
            config['app']['init_files'] = init_files
            Config().save_config(config)

    @retry_on_db_error
    def insert(self, data):
        """
        插入数据
        """
        if isinstance(data, list):
            self.session.add_all(data)
        else:
            self.session.add(data)

    @retry_on_db_error
    def query(self, *obj):
        """
        查询对象
        """
        return self.session.query(*obj)

    @retry_on_db_error
    def excute(self, sql):
        """
        执行SQL语句
        """
        self.session.execute(text(sql))

    def flush(self):
        """
        刷写
        """
        self.session.flush()

    @retry_on_db_error
    def commit(self):
        """
        提交事务
        """
        self.session.commit()

    def rollback(self):
        """
        回滚事务
        """
        self.session.rollback()

    def __del__(self):
        """析构函数，确保会话被关闭"""
        self.close()

class DbPersist(object):
    """
    数据库持久化装饰器
    """

    def __init__(self, db):
        self.db = db

    def __call__(self, f):
        def persist(*args, **kwargs):
            try:
                ret = f(*args, **kwargs)
                self.db.commit()
                return True if ret is None else ret
            except Exception as e:
                ExceptionUtils.exception_traceback(e)
                self.db.rollback()
                return False

        return persist
