## this file is no longer used in the project - Simply keeping it for future reference


import sqlglot
from sqlglot.expressions import Create, Table, Identifier, Drop, Delete, Use, Select, CTE, Subquery, Insert, Update
from sqlglot import exp
import duckdb
import os
import logging


def extract_tables(query):
    return [table.name for table in query.find_all(Table)]


def extract_ctes(node):
    return [cte.alias for cte in node.find_all(CTE)]



def create_schema(parsed_query, user_id, default_db):
    schema = parsed_query.this.db
    
    # If Database Specified
    if parsed_query.this.catalog:
        database = parsed_query.this.catalog
        file_path = f"uploads/{user_id}/{database}.db"
        if os.path.exists(file_path):
            conn = duckdb.connect(file_path)
            try:
                conn.execute(str(parsed_query)).fetchone()
                conn.close()
            except duckdb.CatalogException as e:
                conn.close()
                error_message = str(e).split(': ', 1)[-1].strip("'")
                return {"output_type": "error", "error": error_message}
        else:
            return {"output_type": "error", "error": f"Database '{database}' doesn't exist."}
    # No Database Specified
    else:
        conn = duckdb.connect(database=f"uploads/{user_id}/{default_db}.db")
        try:
            conn.execute(str(parsed_query)) 
            conn.close()
        except duckdb.CatalogException as e:
            conn.close()
            error_message = str(e).split(': ', 1)[-1].strip("'")
            return {"output_type": "error", "error": error_message}
    return {"output_type": "message", "message": f"schema '{schema}' successfully created."}


def create_database(parsed_query, user_id):

    ## still need to implement functionality for replacing the database

    print('creating database')
    database = parsed_query.this.this.this
    replace = parsed_query.args.get('replace')
    if replace:
        ## need to make it so that we delete everything within the database not only for the actual file but also for the sqlite tables
        conn = duckdb.connect(database=f"uploads/{user_id}/{database}.db")
        conn.close()
        return {"output_type": "message", "message": f"databsae '{database}' successfully created."}
    elif os.path.exists(f"uploads/{user_id}/{database}.db"):
        print('path exists')
        return {"output_type": "warning", "warning": f"database '{database}' already exists."} 
    print('path doesnt exist')
    conn = duckdb.connect(database=f"uploads/{user_id}/{database}.db")
    conn.close()
    return {"output_type": "message", "message": f"Database '{database}' successfully created."}




def create_table_definition(parsed_query, create_table_name, create_table_database, user_id, default_db):
    if create_table_database:
        #file_path = f"uploads/{user_id}/{create_table_database}.db"
        #if os.path.exists(file_path):
            logging.info(f"created table definition. Database specified ({create_table_database})")
            conn = duckdb.connect(database=f"uploads/{user_id}/{create_table_database}.db")
    else:
        conn = duckdb.connect(database=f"uploads/{user_id}/{default_db}.db")
        logging.info(f"created table definition. No database specified - using default_db")

    try:
        conn.execute(str(parsed_query))
        conn.close()
    except Exception as e:
         conn.close()
         return {"output_type": "error", "error": e}
    return {"output_type": "message", "message": f"table '{create_table_name}' successfully created."}


def drop_database_table(parsed_query, drop_table_name, table_database, user_id):

        #file_path = f"uploads/{user_id}/{create_table_database}.db"
        #if os.path.exists(file_path):
    logging.info(f"created table definition. Database specified ({table_database})")
    conn = duckdb.connect(database=f"uploads/{user_id}/{table_database}.db")
    try:
        conn.execute(str(parsed_query))
        conn.close()
    except Exception as e:
         conn.close()
         return {"output_type": "error", "error": e}
    return {"output_type": "message", "message": f"table '{drop_table_name}' successfully dropped."}
