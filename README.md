# Data-Product-Kit
A guide to acquire, install and deploy the search capability via API, for SQL and OpenSearch.

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python](https://www.python.org/downloads/)

Create a virtual environment, activate it, and install the requirements.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# OpenSearch

## Installation of OpenSearch

1. Navigate to the `opensearch` directory:
```bash
cd opensearch
```

2. Create an `.env` file in the `opensearch` directory containing the following:

**NOTE:** When running locally, you can set the username and password to any desired credentials.

**NOTE:** Including a `$` or a `!` in the password as a special character may lead to issues when running docker compose later on (the following text gets interpreted as a shell variable), so avoid using them in your password.

```bash
OPENSEARCH_INITIAL_ADMIN_PASSWORD=<password>
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
S3_BUCKET_NAME=<bucket-name> 
```
**NOTE:** <ins>The S3 Bucket we are using for sample data is `docket-samples`</ins>. You can use your own bucket by changing the value of S3_BUCKET_NAME in the `.env` file.

3. Run the docker-compose file (make sure docker is running on your machine)
```bash
docker compose -f docker-compose.yml up -d 
```

4. Confim that the OpenSearch container is running and is accessible by running the following command:
```bash
docker -f docker-compose.yml ps
```
and 
```bash
curl https://localhost:9200 -ku admin:<custom-admin-password>
```

## Using OpenSearch

1. In the virtual environment, run the following command to create the index and ingest the data:
```bash
python ingest.py
```
NOTE: This may take a few minutes to complete. It will produce one line of output for each document ingested.

2. To query the data, run the following command:
```bash
python query.py
```
NOTE: `query.py` is currently hard coded to search for the term "<ins>drug</ins>", but you can change this to any term you would like to search for.

## Cleanup 

1. To delete data from the OpenSearch instance, run the following command:
```bash
python delete_index.py
```
2. To stop the OpenSearch container, run the following command:
```bash
docker compose -f docker-compose.yml down
```

# SQL

Troubleshooting tips are available in the <u>[SQL Troubleshooting Guide](sql/sql_troubleshoot.md](https://github.com/mirrulations/Data-Product-Kit/blob/main/sql/sql_troubleshoot.md))</u>

## Installation of SQL

1. Navigate to the `sql` directory:
```bash
cd sql
```

2. Create an `.env` file in the `sql` directory containing the following:
```bash
POSTGRES_DB=<database name>
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```
NOTE: When running locally, you can set the username and password to any desired credentials.

## Using SQL
1. To start the SQL container, run the following command:
```bash
docker compose -f docker-compose.yml up -d
```

* You can run the following command to create the table and insert data:
```bash
python CreateTables.py
```

* To ingest a docket with all its contents from the Mirrulations S3 bucket, you can run the following command:
```bash
python IngestFromS3.py <docket_id>
```

* *Optional:* You can run the following command to ingest dockets, comments, and documents respectively:
```bash
    python IngestDocket.py
    python IngestComment.py 
    python IngestDocument.py
```

### Querying

Queries can be made through the database connection or by running the `Query.py` script:

1. <u>**PSQL Interface**</u>
* You can connect to the database using the following command:

 ```bash
psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB
 ```

You can begin querying once the connection has been established. 

* To exit psql, type:
```bash
\q
```

2. <u>**Query.py script**</u>
    * This command allows the user to input a SQL query:
```bash
python Query.py "<User Query>"
```
NOTE: Queries are limited to SELECT statements and must be written within the quotation marks.The script must be rerun per query issued; output is returned in JSON format.

## Cleanup

**Note**: You can run the following command to drop the tables if you want to empty the database:
```bash
python DropTables.py
```

1. To stop the SQL container, run the following command:
```bash
docker compose -f docker-compose.yml down
```

If you have any further questions or need help, please reach out to a member of the Data Product team.