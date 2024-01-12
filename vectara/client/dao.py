from vectara.client.domain import Corpus
from abc import ABC
import sqlite3
import logging
from typing import List, Any
from dataclasses import asdict


"""
SQLite implementation of persistence

"""

class BaseDao(ABC):

    def __init__(self, database_location: str = "test.db", enabled: bool = True):
        self.enabled = enabled
        self.database_location = database_location
        self.logger = logging.getLogger(__class__.__name__)

    def _runSql(self, sql:str):
        if self.enabled:
            self.logger.info("Setting up database")
        else:
            self.logger.info("Skipping as database persistence disabled")
            return

        with sqlite3.connect(self.database_location) as conn:
            cur = conn.cursor()
            try:
                return cur.execute(sql)
            except Exception as e:
                self.logger.error(f"Exception in database code running statement {sql}, safely closing cursor")
                cur.close()
                raise e from None

    def _runSqlWithParams(self, sql:str, params: dict[str,Any]):
        temp = sql

        temp_kwargs = {}
        for key in params.keys():
            if not ("{" + key + "}") in temp:
                self.logger.info(f"Key [{key}] not in template [{temp}]")
                continue

            self.logger.info(f"Replacing [{key}] in template [{temp}]")
            value = params[key]
            if value is None:
                temp_kwargs[key] = 'NULL'
            elif isinstance(value, str):
                temp_kwargs[key] = f'"{value}"'
            else:
                temp_kwargs[key] = value

        formatted = sql.format(**temp_kwargs)
        self.logger.info(f"SQL After params injected is [{formatted}]")
        self._runSql(formatted)

class CoreDao(BaseDao):

    def setupDatabase(self):
        self._runSql("CREATE TABLE IF NOT EXISTS files (id text, source_location text, sha1_hash text)")
        self._runSql("CREATE TABLE IF NOT EXISTS corpus (id int, name text, description text)")
        self._runSql("CREATE TABLE IF NOT EXISTS uploads (id text, file_id text, corpus_id text)")
        self._runSql("CREATE TABLE IF NOT EXISTS questions (id integer primary key autoincrement, question_text text, tags text)")

    def dropDatabase(self):
        self._runSql("DROP TABLE IF EXISTS files")
        self._runSql("DROP TABLE IF EXISTS uploads")
        self._runSql("DROP TABLE IF EXISTS corpus")
        self._runSql("DROP TABLE IF EXISTS files")

class CorpusDao(BaseDao):

    def registerCorpus(self, corpus:Corpus):
        params = asdict(corpus)
        self._runSqlWithParams('INSERT INTO corpus VALUES ({id}, {name}, {description})', params)



    #def getLocalDefinition(self, id: int):




class ManagerDao(BaseDao):

    def addQuestion(self, question_text, tags: List[str] = None):
        if tags:
            tags_text = '|' + '|'.join(tags) + '|'
        else:
            tags_text = ""

        self._runSql(f'INSERT INTO questions (question_text, tags) VALUES ("{question_text}","{tags_text}")')
