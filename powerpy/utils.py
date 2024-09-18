from flask import flash
import re
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
import os

from typing import List, Union
from flask_wtf import FlaskForm


class Flash:
    @staticmethod
    def _escape(message):
        """Escape some characters in a message to make them HTML friendly.

        Args:
            message (str): The string to process.

        Returns:
            str: Escaped string.
        """
        translations = {
            '"': '&quot;',
            "'": '&#39;',
            '`': '&lsquo;',
            '\n': '<br>',
        }
        for k, v in translations.items():
            message = message.replace(k, v)
        return message

    @classmethod
    def default(cls, message):
        return flash(cls._escape(message), 'default')

    @classmethod
    def success(cls, message):
        return flash(cls._escape(message), 'success')

    @classmethod
    def info(cls, message):
        return flash(cls._escape(message), 'info')

    @classmethod
    def warning(cls, message):
        return flash(cls._escape(message), 'warning')

    @classmethod
    def danger(cls, message):
        return flash(cls._escape(message), 'danger')

    @classmethod
    def well(cls, message):
        return flash(cls._escape(message), 'well')

    @classmethod
    def modal(cls, message):
        return flash(cls._escape(message), 'modal')
    










class CustomValidator:
    """
    A class containing custom validators for form fields.

    This class includes methods for validating field data based on allowed character sets.
    You can use these validators to enforce rules such as allowing only letters, numbers,
    underscores, hyphens, etc., in a form field.

    Methods
    -------
    regex(form: FlaskForm, field: object, characters: List[str]) -> None
        Validates that the field data contains only the allowed characters based on the provided list.
    """

    @staticmethod
    def regex(field: object, characters: List[str]) -> None:
        """
        Custom validator to check if a field contains only allowed characters.

        Parameters
        ----------
        field : object
            The field instance being validated. Typically, this would be an instance of a specific
            field type from wtforms, such as StringField.
        characters : List[str]
            A list of strings specifying which characters are allowed. The possible values are:
            - 'letters': Allows both lowercase and uppercase letters.
            - 'numbers': Allows digits (0-9).
            - 'underscores': Allows underscores (_).
            - 'hyphens': Allows hyphens (-).
            - Any combination of these values can be passed in the list.

        Raises
        ------
        ValidationError
            If the field contains characters that are not in the allowed set.
        """

        # Define character sets based on the input list
        count=0
        allowed_chars = ''
        if 'letters' in characters:
            allowed_chars += 'a-zA-Z'
            count +=1
        if 'numbers' in characters:
            allowed_chars += '0-9'
            count +=1
        if 'underscores' in characters:
            allowed_chars += '_'
            count +=1
        if 'hyphens' in characters:
            allowed_chars += '-'
            count +=1
        
        # Build the regex pattern dynamically
        pattern = f'^[{allowed_chars}]+$'

        # Validate the field data
        if not re.match(pattern, field.data):
                if count > 1:
                    raise ValidationError(f"This field can only contain {', '.join(characters[0:-1])} and {characters[-1]}.")
                else:
                    raise ValidationError(f"This field can only contain {characters[0]}.")





import duckdb

class GigaDuck():
    def __init__(self, database=None, user_id=None, default_db=None, default_schema= None):
        """
        Initializes a GigaDuck object. If a database is provided, it connects to that DuckDB database.
        Otherwise, it creates a GigaDuck object without an active connection.

        Args:
            database (str, unnecessary): Path to a DuckDB database file. If None, no connection is initialized.
            user_id (int, mandatory): User's id
            schema_id (int, mandatory): User's selected schema
            database_id (int, mandatory):User's selected database
        """
        if database is not None:
            # Establish a connection to the provided DuckDB database
            self.connection = duckdb.connect(database=database)
        else:
            # No connection is initialized yet
            self.connection = None

        self.user_id = user_id
        self.default_db = default_db
        self.default_schema = default_schema

    @staticmethod
    def transform_query_for_parquet(query, user_id, default_db, default_schema):
        """
        Transforms SQL queries by adding '.parquet' to table names after 'FROM' or 'JOIN' clauses.
        Handles table names with optional aliases and adds single quotes around paths.
        Skips transformation for CTEs.
        
        Args:
            query (str): The original SQL query.
            user_id (str): The user-specific directory path.
            default_db (str): The default database name.
            default_schema (str): The default schema name.
        
        Returns:
            str: The transformed query with '.parquet' added to table names.
        """
    
        def replace_table(match):
            """
            Replaces table names in the query with their corresponding '.parquet' suffix.
            Handles table names with optional aliases and adds single quotes around paths.
            """
            clause = match.group(1)  # FROM or JOIN
            tables = match.group(2)  # List of tables, possibly separated by commas
            
            # List to store tables with '.parquet' added
            table_list = []
            for table in tables.split(','):
                parts = table.strip().split()  # Separate table name and alias
                table_name = parts[0]  # Original table name
                alias = " ".join(parts[1:])  # Keep any alias
                
                # Skip CTEs from being transformed
                if table_name in cte_names:
                    table_list.append(f"{table_name} {alias}".strip())
                    continue
                
                # Determine if the table name already includes database/schema
                if '.' in table_name:
                    parts = table_name.split('.')
                    if len(parts) == 3:
                        database, schema, table_name = parts
                        table_name = f"uploads/{user_id}/{database}/{schema}/{table_name}.parquet"
                    elif len(parts) == 2:
                        schema, table_name = parts
                        table_name = f"uploads/{user_id}/{default_db}/{schema}/{table_name}.parquet"
                    else:
                        # Handle additional dots if necessary
                        table_name = f"uploads/{user_id}/{default_db}/{default_schema}/{table_name}.parquet"
                else:
                    table_name = f"uploads/{user_id}/{default_db}/{default_schema}/{table_name}.parquet"
    
                # Add single quotes around the table name
                table_list.append(f"'{table_name}' {alias}".strip())
    
            # Return the replaced clause with '.parquet' added to all table names
            return f"{clause} {', '.join(table_list)}"
    
        def join_check(query):
            """
            Checks for JOIN clauses and ensures proper formatting.
            """
            join_pattern = r'\bJOIN\s+(\w+(?:\.\w+)?(?:\.\w+)?)'
    
            def replace_join(match):
                table_name = match.group(1)
    
                # Skip CTEs from being transformed
                if table_name in cte_names:
                    return f"JOIN {table_name}"
    
                # Transform table name
                if '.' in table_name:
                    parts = table_name.split('.')
                    if len(parts) == 3:
                        database, schema, table_name = parts
                        transformed_table_name = f"'uploads/{user_id}/{database}/{schema}/{table_name}.parquet'"
                    elif len(parts) == 2:
                        schema, table_name = parts
                        transformed_table_name = f"'uploads/{user_id}/{default_db}/{schema}/{table_name}.parquet'"
                    else:
                        transformed_table_name = f"'uploads/{user_id}/{default_db}/{default_schema}/{table_name}.parquet'"
                else:
                    transformed_table_name = f"'uploads/{user_id}/{default_db}/{default_schema}/{table_name}.parquet'"
    
                return f"JOIN {transformed_table_name}"
    
            # Apply transformation globally
            transformed_query = re.sub(join_pattern, replace_join, query, flags=re.IGNORECASE | re.DOTALL)
            return transformed_query
    
        def extract_cte_names(query):
            """
            Extracts CTE names from the query. CTE names are collected to begin with. When transforming table names we simply check
            if they've been identified as a cte. if so, no transformation is made.
            """
            cte_pattern = r'(\w+)\s+AS\s+\('
            return re.findall(cte_pattern, query, flags=re.IGNORECASE)
    
        # Step 1: Extract CTE names
        cte_names = extract_cte_names(query)
    
        # Step 2: Apply transformations for FROM and JOIN clauses
        table_pattern = r'\b(FROM|JOIN)\s+((?:\w+(?:\.\w+)?(?:\.\w+)?\s*(?:,\s*)?)+)(?!\()'
        transformed_query = re.sub(table_pattern, replace_table, query, flags=re.IGNORECASE | re.DOTALL)
    
        # Step 3: Apply JOIN specific transformations
        transformed_query = join_check(transformed_query)
    
        return transformed_query

    def query(self, query):
        """
        Executes a transformed SQL query (with '.parquet' table names) using the DuckDB connection.
        If no database connection is active, an in-memory DuckDB connection is used.

        Args:
            query (str): The original SQL query.

        Returns:
            duckdb.DuckDBPyRelation: The result of the query as a DuckDB relation object.
        """
        # Transform the query to replace table names with '.parquet' suffix
        transformed_query = self.transform_query_for_parquet(query, user_id= self.user_id, default_db = self.default_db, default_schema=self.default_schema)
        print(transformed_query)

        # Execute the query using the current connection or an in-memory DuckDB connection
        if self.connection:
            return self.connection.query(transformed_query)
        else:
            # Use in-memory DuckDB connection if no database is connected
            return duckdb.query(transformed_query)

    def execute_df(self, query):
        """
        Executes a transformed SQL query and fetches the results as a DataFrame-like structure.
        If no database connection is active, it returns a warning message.

        Args:
            query (str): The original SQL query.

        Returns:
            DataFrame-like: The result of the query as a DataFrame (default DuckDB format).
        """
        # Transform the query to replace table names with '.parquet' suffix
        transformed_query = self.transform_query_for_parquet(query, user_id= self.user_id, default_db = self.default_db, default_schema=self.default_schema)

        if self.connection:
            # Execute the query and return results as a DuckDB DataFrame
            return self.connection.execute(transformed_query).fetch_df()
        else:
            # If no connection is available, print a warning message
            print('No database connection found. Use connect(database) to establish a connection.')
            return None
        
    def execute(self, query):
        """
        Executes a transformed SQL query.
        If no database connection is active, it returns a warning message.

        Args:
            query (str): The original SQL query.

        Returns:
            DataFrame-like: The result of the query as a DataFrame (default DuckDB format).
        """
        # Transform the query to replace table names with '.parquet' suffix
        transformed_query = self.transform_query_for_parquet(query, user_id= self.user_id, default_db = self.default_db, default_schema=self.default_schema)

        if self.connection:
            # Execute the query and return results as a DuckDB DataFrame
            return self.connection.execute(transformed_query)
        else:
            # If no connection is available, print a warning message
            print('No database connection found. Use connect(database) to establish a connection.')
            return None

    def connect(self, database):
        """
        Connects to a DuckDB database, replacing the existing connection if one already exists.

        Args:
            database (str): Path to the DuckDB database file.
        """
        # Establish a new connection to the provided DuckDB database
        self.connection = duckdb.connect(database)

