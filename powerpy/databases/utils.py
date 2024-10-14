""" This is more or less the brain of the backend. It enables us to extract all necessary information from a user's query, 
such as the databases, schemas, and tables specified. We can also extract the type of query (SELECT, CREATE, ALTER etc), 
allowing us to implement RBAC permissions later. It's still a work in progress and isn't finished 
(USE, DELETE and transactions still havent even been implemented). A lot of changes were made from when I began, 
and so there's quite a few inconsistencies in how things are done, and a lot of repetitive code, but I'll be fixing them in the real project."""



import secrets
import os
from PIL import Image
from powerpy import mail
from flask import url_for, current_app, jsonify
from flask_mail import Message
import re
from powerpy.models import DataFile, Database, Schema, SchemaTable
from flask_login import current_user
from powerpy import db
import json
from datetime import datetime, timezone
import sqlglot
from sqlglot.errors import ParseError
from sqlglot.expressions import Create, Table, Identifier, Drop, Delete, Use, Select, CTE, Subquery, Insert, Update, Alter, Command, Transaction, RenameTable
from sqlglot import exp
import duckdb
import os
from sqlglot import parse_one
import shutil
import logging
from sqlglot.errors import ParseError
import duckdb
from typing import Union, List, Dict, Any
import logging

logging.basicConfig(
    filename=os.path.join('logs', 'query_logs.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


#output_type - message (successful, warning, unsuccessful, denial), table, plot
#output - the actual output for the selected category
#operation (select, create, drop etc)
#objects (list of included databases, schemas, tables etc involved in a query)
# fix error message when trying to query a table which doesn't exist e.g. select * from db.schema.table;



from abc import ABC, abstractmethod


class SqlQueryBase(ABC):
    def __init__(self, parsed_query, user_id, default_db, default_schema):
        self.user_id = user_id
        self.default_db = default_db
        self.default_schema = default_schema
        self.all_databases = set()
        self.parsed_query = parsed_query
        self.default_db_name = default_db.database_name

    @abstractmethod
    def execute_query(self):
        pass

    def _extract_all_tables():
        """ Yet to be implemented """
        pass


    def _database_file_path(self, database_name):
        return f"uploads/{self.user_id}/{database_name}.db"

    def _query_result_formatter(self, status_code: int = 200, status_message: str = "successful request", status_type: str = "success", data_type: str = 'message', data_contents: Union[Dict[str, List[Any]], str] = 'no contents') -> Dict[str, Any]:
        """ Formats query results into json to be sent to the front end. Default values assume a successful request """
        output = {
            "status": {
                "code": status_code,
                "message": status_message,
                "type": status_type
            },
            "data": {
                "type": data_type,
                "contents": data_contents
            }
        }
        return output
    
    def _table_results(self, table):
        """ Returns Table results formatted as json using the _query_result_formatter() function """
        for column in table.select_dtypes(include=['datetime64']):
            table[column] = table[column].astype(str)
        return self._query_result_formatter(
            status_code=200,
            status_message="table data returned successfully",
            status_type="success",
            data_type="table",
            data_contents={
                "columns": table.columns.tolist(),
                "values": table.values.tolist()
            }
        )

    def _message_results(self, message, status_code = 200, status_message = "request complete", status_type = 'success'):
        return self._query_result_formatter(
            status_code=status_code, 
            status_message=status_message,
            status_type=status_type,
            data_type="message",
            data_contents=str(message)
        )
    
    def _update_sqlite_databases(self, database=None, schema=None, table=None):
        """ yet to be implemented """
        pass

    def _extract_db_schema_table(self):
        """ Extracts the names of the database (if exists), schema (if exists) and table from any query containing a table. 
        This can range from a simple select query, CTAS, Update queries, Alter queries etc. 
        If a database is specified we'll need to connect to it, which is why we extract it. 
        Currently, extracting the schema serves no purpose, however it'll be important in the future when RBAC permissions are involved."""

        db_schema_table = self.parsed_query.find(sqlglot.exp.Table)
        table_name = str(db_schema_table.name)
        table_schema = str(db_schema_table.args.get("db")) if isinstance(db_schema_table.args.get("db"), Identifier) else self.default_schema.name
        table_database = str(db_schema_table.args.get("catalog")) if isinstance(db_schema_table.args.get("catalog"), Identifier) else self.default_db.database_name
        return table_database, table_schema, table_name

    def _extract_extra_databases(self):
        """ Extracts all databases specified in a query which aren't the default database. """
        all_ctes = {cte.alias_or_name for cte in self.parsed_query.find_all(sqlglot.exp.CTE)}
        all_tables = {table for table in self.parsed_query.find_all(sqlglot.exp.Table)}

        for table in all_tables:
            print(f"all tables: {table}")
            table_name = table.name
            if table_name not in all_ctes: 
                schema = table.args.get("catalog", None)
                database = table.args.get("catalog", None)
                if database:
                    self.all_databases.add(str(database))
        extra_databases = [database for database in self.all_databases if database != self.default_db.database_name]
        logging.info(f"Extra Databases: {extra_databases}")
        return extra_databases




    def _duckdb_execution(self, output_type: str, extra_databases: set = None, output_message: str = None):
        """Executes the query and returns various outputs based on the inputoutput_type is a message or a table. 
        if it's a messsage you need to supply the query action being performed (created, updated, deleted, dropped etc), and the 
        object being acted on (table, database, schema) some queries will involve databases other than 
        the default selected database on the interface, which need to be supplied if they exist."""
        
        try:
            with duckdb.connect(f"uploads/{self.user_id}/{self.default_db.database_name}.db") as conn:
                conn.execute(f"""use {self.default_db.database_name}.{self.default_schema.name}""")
                if extra_databases:
                    for database in extra_databases:
                        if os.path.exists(f"uploads/{self.user_id}/{str(database)}.db"):
                            print(f"attaching database: {database}")
                            conn.execute(f"ATTACH 'uploads/{self.user_id}/{str(database)}.db' AS {str(database)}")
                        else:
                            return {"output_type": "message", "output": f"Database '{database}' not found."}
                if output_type == 'table':
                    table = conn.execute(str(self.parsed_query)).df()
                    conn.close()
                    return self._table_results(table)
                else:
                    conn.execute(str(self.parsed_query))
                    conn.close()
                    return self._message_results(message = output_message, status_type='success')
        except Exception as e:
            conn.close()
            return self._message_results(message = str(e), status_type='unsuccessful')
        
    def _duckdb_table_execution(self, extra_databases: set = None):
        try:
            with duckdb.connect(f"uploads/{self.user_id}/{self.default_db.database_name}.db") as conn:
                conn.execute(f"""use {self.default_db.database_name}.{self.default_schema.name}""")
                if extra_databases:
                    for database in extra_databases: 
                        if os.path.exists(f"uploads/{self.user_id}/{str(database)}.db"):
                            print(f"attaching database: {database}")
                            conn.execute(f"ATTACH 'uploads/{self.user_id}/{str(database)}.db' AS {str(database)}")
                        else:
                            return self._message_results(message = f"Database '{database}' not found.", status_type='unsuccessful')

                table = conn.execute(str(self.parsed_query)).df()
                conn.close()
                return self._table_results(table)
        except Exception as e:
            conn.close()
            return self._message_results(message = str(e), status_type='unsuccessful')
    




class SelectQuery(SqlQueryBase):
    def execute_query(self):
        select_table_database, select_table_schema, select_table_name = self._extract_db_schema_table()
        extra_databases = self._extract_extra_databases()
        return self._duckdb_table_execution(extra_databases = extra_databases)

class InsertQuery(SqlQueryBase):
    def execute_query(self):
        insert_table_database, insert_table_schema, insert_table_name = self._extract_db_schema_table()
        self.all_databases.add(insert_table_database)
        extra_databases = self._extract_extra_databases()
        return self._duckdb_execution(output_type = 'message', extra_databases = extra_databases, output_message= f"Insert successful for table {insert_table_name}")

class UpdateQuery(SqlQueryBase):
    def execute_query(self):
        update_table_database, update_table_schema, update_table_name = self._extract_db_schema_table()
        self.all_databases.add(update_table_database)
        if self.parsed_query.args.get('expressions'):
            extra_databases = self._extract_extra_databases()
        return self._duckdb_execution(output_type = 'message', extra_databases = extra_databases, output_message= f"Update successful for table {update_table_name}")

class DeleteQuery(SqlQueryBase):
    def execute_query(self):
        print(f"Executing DELETE query for user {self.user_id} on DB {self.default_db.database_name}.{self.default_schema.name}")

class UseQuery(SqlQueryBase):
    def execute_query(self):
        print(f"Executing DELETE query for user {self.user_id} on DB {self.default_db.database_name}.{self.default_schema.name}")

class AlterQuery(SqlQueryBase):
    def execute_query(self):
        alter_table_database, alter_table_schema, alter_table_name = self._extract_db_schema_table()
        try:
            with duckdb.connect(f"uploads/{self.user_id}/{alter_table_database}.db") as conn:
                conn.execute(f"""use {self.default_db.database_name}.{self.default_schema.name}""")
                conn.execute(str(self.parsed_query))
                conn.close()
        except Exception as e:
            return self._message_results(message = f"Unable to alter table '{alter_table_name}': {str(e)} - fkbndj4j583", status_type='unsuccessful')
        if isinstance(self.parsed_query.args.get('actions')[0], RenameTable):
            sqlite_database = Database.query.filter_by(database_name=alter_table_database.upper(), owner=current_user).first()
            sqlite_schema = Schema.query.filter_by(database_id=sqlite_database.id, name=alter_table_schema.upper()).first()
            altered_table = SchemaTable.query.filter_by(schema_id=sqlite_schema.id, name=alter_table_name.upper()).first()
            altered_table.name = self.parsed_query.args.get('actions')[0].this.this.this.upper()
            db.session.commit()
        return self._message_results(message = f"table '{alter_table_name}' successfully altered.", status_type='success')

class TransactionQuery(SqlQueryBase):
    def execute_query(self):
        print(f"Executing DELETE query for user {self.user_id} on DB {self.default_db.database_name}.{self.default_schema.name}")

class DropQuery(SqlQueryBase):
    def execute_query(self):
        object_type = self.parsed_query.kind.lower()
        if object_type == "table":
            return self._drop_table()
        elif object_type == 'schema':
            return self._drop_schema()
        elif object_type == 'database':
            return self._drop_database()
        
    def _drop_table(self):
        drop_table_database, drop_table_schema, drop_table_name = self._extract_db_schema_table()
        try:
            with duckdb.connect(f"uploads/{self.user_id}/{drop_table_database}.db") as conn:
                conn.execute(f"""use {self.default_db.database_name}.{self.default_schema.name}""")


                conn.execute(str(self.parsed_query))
                conn.close()
                sqlite_database = Database.query.filter_by(database_name=drop_table_database.upper(), owner=current_user).first()
                sqlite_schema = Schema.query.filter_by(database_id=sqlite_database.id, name=drop_table_schema.upper()).first()
                dropped_table = SchemaTable.query.filter_by(schema_id=sqlite_schema.id, name=drop_table_name.upper()).first()
                db.session.delete(dropped_table)
                db.session.commit()
                return self._message_results(message = f"table '{drop_table_name}' successfully dropped.", status_type='success')
        except Exception as e:
            conn.close()
            return self._message_results(message = f"Unable to delete table '{drop_table_name}': {str(e)} - sdf2342sssdhj43", status_type='unsuccessful')
            
    def _drop_schema(self):
        schema = str(self.parsed_query.this.db)
        database = str(self.parsed_query.this.catalog)
        database = self.parsed_query.this.catalog or self.default_db.database_name
        ##### NEED TO IMPLEMENT THIS ^^ OR STATEMENT EVERYWHERE, WILL CLEAN UP THE CODE 100x
        print(f"database being used: {database}")

        file_path = f"uploads/{self.user_id}/{str(database)}.db"
        if os.path.exists(file_path):
            try:
                with duckdb.connect(file_path) as conn:
                    conn.execute(str(self.parsed_query))
                    conn.close()
            except Exception as e:
                conn.close()
                return self._message_results(message = f"Unable to delete schema '{schema}': {str(e)} - sdfsdfjklsdhj43", status_type='unsuccessful')
        else:
            print(f"Database '{database}' does not exist")
            return self._message_results(message = f"Database '{database}' does not exist.", status_type='unsuccessful')
        sqlite_database = Database.query.filter_by(database_name=database.upper(), owner=current_user).first()
        dropped_schema = Schema.query.filter_by(database_id=sqlite_database.id, name=schema.upper()).first()
        dropped_schema_tables = SchemaTable.query.filter_by(schema_id=dropped_schema.id).all()
        for table in dropped_schema_tables:
            db.session.delete(table)
        db.session.delete(dropped_schema)
        db.session.commit()

        return self._message_results(message = f"Schema '{schema}' successfully dropped.", status_type='success')
            
    def _drop_database(self):
        database = self.parsed_query.this.this.this
        database_file_path = self._database_file_path(str(database))
        if os.path.exists(database_file_path):
            try:
                os.remove(database_file_path)
                dropped_database = Database.query.filter_by(database_name=database.upper(), owner=current_user).first()
                if dropped_database:
                    dropped_db_schemas = Schema.query.filter_by(database_id=dropped_database.id).all()
                    dropped_db_tables = SchemaTable.query.filter_by(database_id=dropped_database.id).all()
                    for schema in dropped_db_schemas:
                        db.session.delete(schema)
                    for table in dropped_db_tables:
                        db.session.delete(table)
                    db.session.delete(dropped_database)
                    db.session.commit()

                return self._message_results(message = f"Database '{database}' successfully dropped.", status_type='success')
            except Exception as e:
                return self._message_results(message = f"Unable to delete database '{database}': {str(e)} - sgjhn3456790egrh.", status_type='unsuccessful')
        else:
            return self._message_results(message = f"Database '{database}' does not exist.", status_type='unsuccessful')

class CreateQuery(SqlQueryBase):
    def execute_query(self):
        object_type = self.parsed_query.kind.lower()

        if object_type == "table":
            return self._create_table()
        elif object_type == 'schema':
            return self._create_schema()
        elif object_type == 'database':
            return self._create_database()
        
    def _duckdb_table_creation(self, extra_databases, create_table_database, create_table_schema, create_table_name, has_replace = False, has_exists = False):
        try:
            sqlite_database = Database.query.filter_by(owner=current_user, database_name=create_table_database.upper()).first()
            sqlite_schema = Schema.query.filter_by(name=create_table_schema.upper(), database_id = sqlite_database.id).first()
            existing_table = SchemaTable.query.filter_by(name = create_table_name.upper(), schema_id= sqlite_schema.id).first()
        except Exception as e:
            return self._message_results(message = f"{str(e)} - fssdf543234", status_type='unsuccessful')
        if existing_table:
            if has_exists:
                return self._message_results(message = f"table '{create_table_name}' already exists.", status_type='success')
            if not has_replace:
                return self._message_results(message = f"table '{create_table_name}' already exists.", status_type='unsuccessful')
        try:
            with duckdb.connect(f"uploads/{self.user_id}/{self.default_db.database_name}.db") as conn:
                print('moreeeeeeeee')
                conn.execute(f"""use {self.default_db.database_name}.{self.default_schema.name}""")
                print('attached')
                if extra_databases:
                    print('extra datbases apparently')
                    for database in extra_databases:
                        if os.path.exists(f"uploads/{self.user_id}/{str(database)}.db"):
                            conn.execute(f"ATTACH 'uploads/{self.user_id}/{str(database)}.db' AS {str(database)}")
                        else:
                            print('database not foundddddddd')
                            return self._message_results(message = f"Database '{database}' not found.", status_type='unsuccessful')
                conn.execute(str(self.parsed_query))
                conn.close()
                print('WOWOWWWWW')
                if existing_table and has_replace:
                    print('existing table exists')
                    existing_table.date_created = datetime.now(timezone.utc)
                    db.session.commit()
                else:
                    print('holy shit')
                    created_table = SchemaTable(name=create_table_name.upper(), database_id = sqlite_database.id, schema_id = sqlite_schema.id, table_columns = 'leaving this here for now', owner=current_user)
                    db.session.add(created_table)
                    db.session.commit()
                return self._message_results(message = f"table '{create_table_name}' created successfully.", status_type='success')
        except Exception as e:
            conn.close()
            print(f"THE ERORRRRRRRRRRR :{e}")
            return self._message_results(message = f"{str(e)} - fgjgfdhf7rt634", status_type='unsuccessful')

    def _create_table(self):
        create_table_database, create_table_schema, create_table_name = self._extract_db_schema_table()
        print(f" create table schema: {create_table_schema}")
        self.all_databases.add(create_table_database)
        if self.parsed_query.args.get('expression'):
            extra_databases = self._extract_extra_databases()
        else:
            extra_databases = [database for database in self.all_databases if database != self.default_db.database_name]
        return self._duckdb_table_creation(extra_databases, create_table_database, create_table_schema, create_table_name, has_replace = self.parsed_query.args.get('replace'), has_exists = self.parsed_query.args.get('exists'))

    def _create_schema(self):
        schema = self.parsed_query.this.db
        # If Database Specified
        if self.parsed_query.this.catalog:
            database = self.parsed_query.this.catalog
            file_path = f"uploads/{self.user_id}/{database}.db"
            if os.path.exists(file_path):
                try:
                    with duckdb.connect(file_path) as conn:
                        conn.execute(str(self.parsed_query))
                        conn.close()
                        sqlite_database = Database.query.filter_by(owner=current_user, database_name=database.upper()).first()
                        created_schema = Schema(name=schema.upper(), database_id = sqlite_database.id, owner=current_user)
                        db.session.add(created_schema)
                        db.session.commit()
                        conn.close()

                except duckdb.CatalogException as e:
                    conn.close()
                    error_message = str(e).split(': ', 1)[-1].strip("'")
                    return self._message_results(message = f"error: {error_message}", status_type='unsuccessful')
            else:
                return self._message_results(message = f"Database '{database}' doesn't exist.", status_type='unsuccessful')
        else:
            conn = duckdb.connect(f"uploads/{self.user_id}/{self.default_db.database_name}.db")
            try:
                conn.execute(str(self.parsed_query)) 
                conn.close()
                sqlite_database = Database.query.filter_by(owner=current_user, database_name=self.default_db.database_name.upper()).first()
                created_schema = Schema(name=schema.upper(), database_id = sqlite_database.id, owner=current_user)
                db.session.add(created_schema)
                db.session.commit()
            except duckdb.CatalogException as e:
                conn.close()
                error_message = str(e).split(': ', 1)[-1].strip("'")
                return self._message_results(message = f"error: {error_message}", status_type='unsuccessful')
        return self._message_results(message = f"schema '{schema}' successfully created.", status_type='success')

    def _create_database(self):
        print('recieved query to create a database')
        database = self.parsed_query.this.this.this
        replace = self.parsed_query.args.get('replace')
        database_file_path = self._database_file_path(database)
        if replace and os.path.exists(database_file_path):
            try:
                os.remove(database_file_path) 
            except Exception as e:
                return self._message_results(message = f"Unable to remove existing database.", status_type='unsuccessful')
            sqlite_database = Database.query.filter_by(owner=current_user, database_name=database.upper()).first()
            db.session.delete(sqlite_database)
            conn = duckdb.connect(database_file_path)
            conn.close()
            return self._message_results(message = f"database '{str(database)}' successfully replaced.", status_type='success')
        elif os.path.exists(database_file_path):
            print(f"database path {self.user_id}/{database} exists")
            return self._message_results(message = f"database '{str(database)}' already exists", status_type='fail')
        print('path doesnt exist, creating database')
        conn = duckdb.connect(database_file_path)
        conn.close()
        sqlite_database = Database(database_name=(database).upper(), owner=current_user)
        db.session.add(sqlite_database)
        db.session.commit()
        sqlite_schema = Schema(name = 'MAIN', database_id = sqlite_database.id, owner=current_user)
        db.session.add(sqlite_schema)
        db.session.commit()
        return self._message_results(message = f"database '{str(database)}' successfully created.", status_type='success')


query_classes = {
    Select: SelectQuery,
    Insert: InsertQuery,
    Update: UpdateQuery,
    Delete: DeleteQuery,
    Create: CreateQuery,
    Drop: DropQuery,
    Use: UseQuery,
    Alter: AlterQuery,
    Transaction: TransactionQuery
}


def get_query_object(query, user_id, default_db, default_schema):
    """ Uses SQLGlot to parse the query and determine the type of query passed. If a valid query is passed, the query class dictionary will
    be called, and if a valid key is found, the respective child class of SqlQueryBase will be created."""
    try:
        parsed_query = parse_one(query, read="duckdb")
    except ParseError as e:
        return {"output_type": "error", "output": str(e)}
    query_type = type(parsed_query)
    if isinstance(parsed_query, Command):
        return {"output_type": "warning", "output": f"Unsupported Query syntax."}
    query_class = query_classes.get(query_type)
    if query_class:
        try:
            return query_class(parsed_query, user_id, default_db, default_schema)
        except Exception as e:
            return {'output_type': 'syntax error', 'output': str(e)}
    else:
        return {"output_type": "warning", "output": f"Unsupported Query syntax."}



def get_global_db_query_object(query, user_id, default_db, default_schema):
    """ Currently not in use. """
    try:
        parsed_query = parse_one(query, read="duckdb")
    except ParseError as e:
        return {"output_type": "error", "output": str(e)}
    query_type = type(parsed_query)
    if isinstance(parsed_query, Command):
        return {"output_type": "warning", "output": f"Unsupported Query syntax."}
    query_class = query_classes.get(query_type)
    if query_class:
        try:
            return query_class(parsed_query, user_id, default_db, default_schema)
        except Exception as e:
            return {'output_type': 'syntax error', 'output': str(e)}
    else:
        return {"output_type": "warning", "output": f"Unsupported Query syntax."}
