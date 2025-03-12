# Data-Product-Kit
A guide to acquire, install and deploy the search capability via API, for SQL and OpenSearch.

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
    * Certain issues with Docker may be resolved by uninstalling and reinstalling using homebrew:
    ```bash
    brew uninstall --cask docker --force

    brew uninstall --formula docker --force

    brew install --cask docker
    ```
    * This will work even if you did not install Docker with homebrew originally.

- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python](https://www.python.org/downloads/)
- [libpq](https://www.postgresql.org/docs/current/libpq.html#:~:text=libpq%20is%20the%20C%20application,the%20results%20of%20these%20queries.)
    - libpq can be installed via homebrew
    ```bash
    brew install libpq
    brew link --force libpq
    ```

## Initial Setup

Clone the `Data-Product-Kit` Repository: 
```bash
git clone https://github.com/mirrulations/Data-Product-Kit.git
```

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

**NOTE:** Including a `$` or a `!` in the password as a special character may lead to issues when running docker compose later on (the following text gets interpreted as a shell variable), so avoid using them in your password.

**NOTE:** When running locally, you can set the username and password to any desired credentials. **Example credentials are included below:**

```bash
OPENSEARCH_INITIAL_ADMIN_PASSWORD=C4nzUMkFu^e4N2
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
S3_BUCKET_NAME=presentationbucketcs334s25
```
**NOTE:** <ins>The S3 Bucket we are using for sample data is `docket-samples`</ins>. You can use your own bucket by changing the value of S3_BUCKET_NAME in the `.env` file.

Run `source .env` to load the environment variables into the current shell session in case of any credential issues.

3. Run the docker-compose file (make sure docker is running on your machine)
```bash
docker compose up -d
```

4. Confirm that the OpenSearch container is running and is accessible by running the following commands:
```bash
docker compose ps
```
**Note:** There should be 3 opensearch containers running upon successful execution. If you are having issues, you may want to revisit your password as the containers will not start with a low strength password. [Visit the OpenSearch troubleshooting guide for further assistance.](opensearch/opensearch_troubleshoot.md)


```bash
curl https://localhost:9200 -ku admin:<your-admin-password>
```


## Using OpenSearch

1. In the virtual environment, run the following command to create the index and ingest the data:
```bash
python ingest.py
```
**NOTE:** This may take a few minutes to complete. It will produce one line of output for each document ingested.

2. To query the data, run the following command:
```bash
python query.py <search term>
```
NOTE: Only dockets that have matching comments will appear as output


## Cleanup 

1. To delete data from the OpenSearch instance, run the following command:
```bash
python delete_index.py
```
2. To stop the OpenSearch container, run the following command:
```bash
docker compose down
```

# SQL

### **Troubleshooting tips are available in the <u>[SQL Troubleshooting Guide](sql/sql_troubleshoot.md](https://github.com/mirrula**tions/Data-Product-Kit/blob/main/sql/sql_troubleshoot.md))</u>**

## Installation of SQL

1. Navigate to the `sql` directory:
```bash
cd sql
```

2. Create an `.env` file in the `sql` directory containing the following:
```bash
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```
**NOTE:** When running locally, you can set the username and password to any desired credentials. Example credentials are displayed above.

Run `source .env` to load the environment variables into the current shell session in case of any credential issues.

## Using SQL
1. To start the SQL container, run the following command:
```bash
docker compose up -d
```

* You can run the following command to create the table and insert data:
```bash
python CreateTables.py
```

To ingest all the sample data from the S3 bucket, you can run the following command:
```bash
python IngestFromBucket.py presentationbucketcs334s25
```
**NOTE:** This may take a few minutes to complete.

* *Optional:* To ingest an individual docket with all its contents from the Mirrulations S3 bucket, you can run the following command:
```bash
python IngestFromS3.py <docket_id>
```
**NOTE:** Example docket: *DOS-2022-0004*


**IMPORTANT:** Additional documentation for all the scripts for SQL can be found [here](sql/syntax.md)

### Querying

Queries can be made through the database connection or by running the `Query.py` script:

1. <u>**PSQL Interface**</u>
* You can connect to the database using the following command:

 ```bash
psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB
 ```

You can begin querying once the connection has been established. 

**NOTE:** You can enhance readability of query output by toggling expanded display mode with this command:
```bash
\x
```

* To exit psql, type:
```bash
\q
```
or press `CTRL+D`


2. <u>**Query.py script**</u>
    * This command allows the user to input a SQL query:
```bash
python Query.py "SELECT docket_id FROM dockets;"
```
 An example query is provided above. 

**NOTE:** Queries are limited to SELECT statements and must be written within the quotation marks.The script must be rerun per query issued; output is returned in JSON format.

## Cleanup

**Note**: You can run the following command to drop the tables if you want to empty the database:
```bash
python DropTables.py
```

1. To stop the SQL container, run the following command:
```bash
docker compose down
```

If you have any further questions or need help, please reach out to a member of the Data Product team.
