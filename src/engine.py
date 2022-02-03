from sqlalchemy import create_engine
from dataclasses import dataclass
import pandas as pd
import sqlalchemy

@dataclass
class Engine:

    server: str
    database: str
    username: str
    password: str

    #post init#

    def __post_init__(self):

        object.__setattr__(self,'engine', 
        create_engine(
            f"mssql+pyodbc://{self.username}:{self.password}@{self.server}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server",
            fast_executemany=True)
        )

    #test if engine is alive
    def test_engine(self):
        """
        test if engine is alive
        """
        with self.engine.begin() as conn:
            conn.execute("SELECT 1")
            return True
        

                        

    def insert_batch_job(self,batch_type : str, 
                         target_file_name : str, src : str,
                         destination_output : str) -> str:
        """
        generates the BatchID prior to starting ETL job - 
        this will be used to update the log upon completion or failure.
        """

        sql_str = f"""
            DECLARE @bid INT
            EXEC @bid = mc_datalayer.[etl].[sp_ins_batchProcess] 
                @batchProcess = 'Merge Government Hosted Publicly Available Addative Content',
                @BatchType = '{batch_type}',
                @src =  '{src}',
                @trf = '{target_file_name}',
                @dst = '{destination_output}'
        """

        with self.engine.begin() as conn:
            job_exec = conn.execute(sql_str)
            
        return pd.read_sql("select max(batchid) as bid from etl.batchprocess", self.engine)['bid'].values[0]


    def update_batch_job(self, bid : str, row_count : str):
        """updates job table after completion"""

        sql_str = f"""EXEC mc_datalayer.[etl].[sp_upd_batchProcess] '{bid}', '{row_count}' """

        with self.engine.begin() as conn:
            conn.execute(sql_str)


