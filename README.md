# MicroDataWarehouse

A lightweight, secure microdata warehouse solution built with DuckDB and Flask.

## Features

- **DuckDB Backend**: Utilizes DuckDB for efficient data storage and querying.
- **Flask Web Server**: Provides a robust and flexible web interface.
- **User Authentication**: Secure login system to manage access.
- **Email Authentication**: Verify user identities through email.
- **Data Encryption**: Ensures data security at rest.
- **Flattened File System**: Optimized storage structure for improved performance.
- **Hierarchical Data Organization**: Database > Schema > Table structure.
- **Full DuckDB Query Functionality**: Leverage the power of DuckDB queries (excluding transactions).
- **Cross-Database Queries**: Ability to query across multiple databases.

## Architecture

The MicroDataWarehouse is designed with a focus on simplicity, security, and performance:

1. **Backend**: Flask serves as the web framework, handling HTTP requests and responses.
2. **Database**: DuckDB is used as the primary database engine, offering fast analytical query processing.
3. **Authentication**: Custom user authentication system with email verification.
4. **Storage**: Implements a flattened file system for efficient data storage and retrieval.
5. **Query Engine**: Utilizes DuckDB's query capabilities, supporting complex analytical queries.

## Setup and Installation

(Add instructions for setting up the project, including dependencies and configuration)

## Usage

(Provide examples of how to use the system, including API endpoints if applicable)

## Security

This project implements several security measures:

- User authentication to control access
- Email verification for new accounts
- Data encryption to protect sensitive information

## Limitations

- Does not support transactional operations
- (Add any other known limitations or constraints)

## Contributing

(Instructions for how others can contribute to the project)

## License

(Specify the license under which this project is released)

## Contact

(Your contact information or how to reach out for support)
