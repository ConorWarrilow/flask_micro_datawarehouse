# Flask Micro Data Warehouse

A lightweight, secure microdata warehouse solution built with DuckDB and Flask.


<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20194530.jpg" alt="Description of image 1">
</div>





## How it works
The project uses DuckDB as its core SQL engine, efficiently handling all database operations. User queries from the front end are received, parsed, analyzed, and executed based on specified logic, and .duckdb database files are used to store databases, schemas, and tables. Since DuckDB is optimization for its native file type, it provides rapid query execution for small to medium sized datasets without the need for a powerful server or other expensive data-warehousing solutions. Datasets of up to 50gb were tested and performed well on my local machine running 32gb ddr5 6000mhz + ryzen 5 7600X.

The front end uses vanilla JS, CSS, and HTML. CodeMirror is used for the query editor, with JavaScript allowing users to write and execute multiple queries independently within each worksheet. These worksheets are automatically saved to the backend periorically or upon page refresh/exit. An adjacency list model is used to create a hierarchical file system for the organization of worksheets. Users can also visualize their databases, schemas and tables on the front end, making it easy to work with .duckdb files. 
User authentication, data encryption, and email verification processes for account creation and password resets are also implemented.
  
The backend uses flask, with SQLAlchemy as the ORM and Sqlite to store user data. Whenever a user manipulates an existing database (whether it be creating/deleting a schema, or creating/altering/updating a table etc), their actions are tracked and stored within the SQLite database. In addition, each query is stored with a status as to whether the query was successful or unsuccessful. 

## Notable Features
- **Full DuckDB Query Functionality**: Utilizes DuckDB on the backend and supports full sql functionality (with transactions to be added in the future)
- **Cross-Database Queries**: Full support for cross-database queries. By parsing and analyzing queries, connections are made to several databases automatically, allowing for queries across multiple databases without any need to manage connections manually.
- **User Authentication**: Secure login system to manage access.
- **Email Authentication**: Verify user identities through email.
- **Sensitive Data Encryption**: Ensures data security at rest.
- **adjacency list File System**: Heirarchical file system including directories and SQL worksheets using an adjacency list model. 
- **Hierarchical Database Organization**: User databases can be visualized on the front end in a heierarchical Database > Schema > Table structure.
- **Historic Query Analytics**: All queries are saved and can be viewed later on. Users can also see which queries were executed successfully or unsuccessfully. 



## To-Do
- Finish adding support for querying and pulling in data contained in S3/Blob.
- Add Account heirarchies (Organization, Account, User, Role)
- Extend SQLGlot library to allow for GRANT and REVOKE functionalities.
- Add full RBAC functionalities, similar to snowflakes.



## Limitations
- Duckdb is limited regarding concurrency. Conflicts would occur should multiple users/processes perform operations on a database at the same time.
- Duckdb is running as a single node, which is limited in scalability, and will never compete with distributed compute when it comes to large workloads.
- Does not support transactional queries at the moment
- Yet to implement RBAC controls (currently my main focus)
- Everything is currently stored locally. For personal use or a small team this is okay, however it isn't scalable.




## Extra Images
<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20194646.jpg" alt="Description of image 1">
</div>

Both the table container and database/worksheets menu are resizeable. Unlike snowflake, the table container was placed at the bottom and stretches the entire width of the interface, wasting far less space and allowing you to visualize more columns without collapsing the menu. 
<br/>
<br/>



<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20190707.jpg" alt="Description of image 1">
</div>


<div style="display: flex; justify-content: center; gap: 10px;">
  <img src="https://github.com/ConorWarrilow/flask_micro_datawarehouse/blob/main/assets/Screenshot%202024-10-04%20191210.jpg" alt="Description of image 1">
</div>
The project also features pages for viewing your databases/worksheets, with information such as the date created and any comments (if given). Functionality for filtering and sorting (whether by name or date) is also included.
