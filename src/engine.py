from sqlalchemy import create_engine
from dataclasses import dataclass

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
            f"mssql+pyodbc://{self.username}:{self.password}@{self.server}/{self.database}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server",
            fast_executemany=True)
        )
                        

    def insert_batch_job(self,etl_name : str, target_file_name : str, src : str,
                        destination_output : str) -> str:
        """
        generates the BatchID prior to starting ETL job - this will be used to update the log upon completion or failure.

        """
        sql_str = f"""
            DECLARE @bid INT
            
            EXEC @bid = mc_datalayer.[etl].[sp_ins_batchProcess] 
                @batchProcess = 'Merge Government Hosted Publicly Available Addative Content',
                @BatchType = 'stg1 scrape',
                @src =  {src}
                @trf = {target_file_name},
                @dst = {destination_output}
        """	

        with self.engine.begin() as conn:
            job_exec = conn.execute(sql_str)
            jobkey = job_exec.first()[0]
        return jobkey


    def update_batch_job(self, bid):
        """updates job table after completion"""

        sql_str = f"""EXEC mc_datalayer.[etl].[sp_upd_batchProcess] @{bid}"""

        with self.engine.begin() as conn:

            conn.execute(sql_str)
