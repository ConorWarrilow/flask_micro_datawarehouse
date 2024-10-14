# MicroDataWarehouse

A lightweight, secure microdata warehouse solution built with DuckDB and Flask.


## Main GUI
<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20194530.jpg" alt="Description of image 1">
</div>

The main GUI was designed to mimic Snowflake, as snowflake was the original inspiration for the project.


<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20194646.jpg" alt="Description of image 1">
</div>

Both the table container and database/worksheets menu are resizeable. Unlike snowflake, the table container was placed at the bottom, stretching the entire width of the interface, allowing 

<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20190707.jpg" alt="Description of image 1">
</div>


<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20191210.jpg" alt="Description of image 1">
</div>

## How it works
The project uses DuckDB as its core SQL engine, efficiently handling all database operations. User queries from the front end are received, parsed, analyzed, and executed based on specified logic, and .duckdb database files are used to store databases, schemas, and tables. Since DuckDB is optimization for its native file type, it provides rapid query execution for small to medium sized datasets without the need for a powerful server or other expensive data-warehousing solutions. Datasets of up to 50gb were tested and performed well on my local machine running on 32gb ddr5 6000mhz + ryzen 5 7600X.

The front end uses vanilla JS, CSS, and HTML. CodeMirror is used for the query editor, with JavaScript allowing users to write and execute multiple queries independently within each worksheet. These worksheets are automatically saved to the backend periorically or upon page refresh/exit. An adjacency list model is used to create a hierarchical file system for the organization of worksheets. Users can also visualize their databases, schemas and tables on the front end, making it easy to work with .duckdb files. 
User authentication, data encryption, and email verification processes for account creation and password resets are also implemented.
  


## Notable Features
- **Full DuckDB Query Functionality**: Utilizes DuckDB on the backend and supports full sql functionality (with transactions to be added in the future)
- **Cross-Database Queries**: Full support for cross-database queries. By parsing and analyzing queries, connections are made to several databases automatically, allowing for queries across multiple databases without any need to manage connections manually.
- **User Authentication**: Secure login system to manage access.
- **Email Authentication**: Verify user identities through email.
- **Sensitive Data Encryption**: Ensures data security at rest.
- **adjacency list File System**: Heirarchical file system including directories and SQL worksheets using an adjacency list model. 
- **Hierarchical Database Organization**: Data is organized by Database > Schema > Table structure.



## Limitations
- Does not support transactional queries at the moment
- Yet to implement RBAC controls (currently my main focus)





