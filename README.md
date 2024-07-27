# Company-Reimbursement-Management-System-Mysql
Using mysql as backend and streamlit as frontend.

## Setup Instructions

### Files

- `all_tables.sql` - Creates tables, contains code for trigger and procedure
- `populate.sql` - Populates the required tables
- `crms.py` - Streamlit frontend code which calls upon different queries

### Open MySQL Command Line:

```sql
CREATE DATABASE crms;
USE crms;
SOURCE <path of all_tables.sql>;
SOURCE <path of populate.sql>;
CREATE USER 'abc'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON crms.* TO 'abc'@'localhost';
```
Make sure all_tables.sql, populate.sql, and crms.py are in the same directory.


### Open the Terminal Where You Run Python:
1. Change directory to where crms.py exists.
2. Run the following command:

```
streamlit run crms.py
```

