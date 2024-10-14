# MicroDataWarehouse

A lightweight, secure microdata warehouse solution built with DuckDB and Flask.


<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20194530.jpg" alt="Description of image 1">
</div>




<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20194646.jpg" alt="Description of image 1">
</div>


<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20190707.jpg" alt="Description of image 1">
</div>


<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20191210.jpg" alt="Description of image 1">
</div>



MicroDataWarehouse leverages DuckDB as its core SQL engine, handling all database operations with exceptional efficiency. User queries from the front end are received, parsed, analyzed, and executed based on specified logic. The system utilizes .duckdb database files to store databases, schemas, and tables, offering superior data compression compared to CSV and even parquet formats. This storage method, coupled with DuckDB's optimization for its native file type, ensures rapid query execution and efficient data management.
The front end is crafted using vanilla JavaScript, CSS, and HTML, with Bootstrap components enhancing the user interface. CodeMirror is integrated to provide a powerful query editing experience, while custom JavaScript enables users to write and execute multiple queries independently within a single worksheet. These worksheets are saved to the backend, where an ingeniously designed adjacency list model creates a hierarchical file system for organized worksheet management. The system also exposes the structure of databases, schemas, and tables to the front end, providing users with a comprehensive view of their data landscape.
Security and user management are prioritized, with robust user authentication, data encryption, and email verification processes implemented for account creation and password resets. This comprehensive approach ensures a secure, efficient, and user-friendly environment for data warehousing and analysis.
  








## Features
- **Flask Web Server**: Provides a robust and flexible web interface.
- **User Authentication**: Secure login system to manage access.
- **Email Authentication**: Verify user identities through email.
- **Sensitive Data Encryption**: Ensures data security at rest.
- **adjacency list File System**: Heirarchical file system including directories and SQL worksheets using an adjacency list model. 
- **Hierarchical Database Organization**: Data is organized by Database > Schema > Table structure.
- **Full DuckDB Query Functionality**: Leverage the power of DuckDB queries, with transactions to be included in the future.
- **Cross-Database Queries**: Full support for cross-database queries.

## Architecture

The MicroDataWarehouse is designed with a focus on simplicity, security, and performance:

1. **Backend**: Flask serves as the web framework, handling HTTP requests and responses.
2. **Database**: DuckDB is used as the primary database engine, offering fast analytical query processing.
3. **Authentication**: User authentication system with email verification.
4. **Storage**: User databases are stored as .duckdb databases, allowing for data compression and speed.
5. **Query Engine**: Utilizes DuckDB's query capabilities, supporting complex analytical queries.


## Limitations

- Does not support transactional operations
- (Add any other known limitations or constraints)

