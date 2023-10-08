## Script to ingest ny taxi data

import pandas as pd
import os
from sqlalchemy import create_engine
from time import time
import argparse

## Main

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    
    csv_name = 'output.csv'
    parquet_name = 'output.parquet'
    
    os.system(f'wget {url} -O {parquet_name}')
    
    # Convert Parquet to CSV
    df = pd.read_parquet(parquet_name)
    df.to_csv(csv_name, index=False)
    
    # Process CSV
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # Check if table exists
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    for df in df_iter:
        t_start = time()
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        
        df.to_sql(name=table_name, con=engine, if_exists='append')
        t_end = time()
        
        print(f'insert another chunk... took {t_end-t_start} seconds')
        
if __name__ == "__main__":
    ## ArgParse
    parser = argparse.ArgumentParser(
                        description='Ingest CSV data to Postgres')

    parser.add_argument('--user', help='username for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='db name for postgres')
    parser.add_argument('--table_name', help='table name for the postgres db')
    parser.add_argument('--url', help='url of the csv file')

    args = parser.parse_args()

    main(args)