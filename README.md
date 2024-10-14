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

