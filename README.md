# Data-Product-Kit
A guide to acquire, install and deploy the search capability via API, for SQL and OpenSearch.

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python](https://www.python.org/downloads/)

## Installation of OpenSearch
1. Clone the repository
```bash
git clone https://github.com/mirrulations/OpenSearch.git
```

2. In the Opensearch directory, create a virtual environment, activate it, and install the requirements.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Set your password as an environment variable for the docker-compose file.
```bash
export OPENSEARCH_INITIAL_ADMIN_PASSWORD=<password>
```
NOTE: including a $ or a ! in the password as a special character may lead to issues when running docker compose later on (the following text gets interpreted as a shell variable), so avoid using them in your password.


4. Create a .env file containing the following:
```bash
OPENSEARCH_INITIAL_PASSWORD=<password>
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
S3_BUCKET_NAME=<bucket-name> 
```
NOTE: The S3 Bucket we are using for sample data is 'docket-samples`. You can use your own bucket by changing the value of S3_BUCKET_NAME in the .env file.

5. Run the docker-compose file (make sure docker is running on your machine)
```bash
docker-compose up -d 
```

6. Confim that the OpenSearch container is running and is accessible by running the following command:
```bash
docker ps
```
and 
```bash
curl https://localhost:9200 -ku admin:<custom-admin-password>
```


## Using OpenSearch

1. In the virutal enviroment run the following command to create the index and ingest the data:
```bash
python ingest.py
```
NOTE: This may take a few minutes to complete. It will produce one line of output for each document ingested.

2. To query the data, run the following command:
```bash
python query.py
```
NOTE: query.py is currently hard coded to search for the temr "drug", but you can change this to any term you would like to search for.

## Cleanup 

1. To delete data from the OpenSearch instance, run the following command:
```bash
python delete_client.py
```
2. To stop the OpenSearch container, run the following command:
```bash
docker-compose down
```

## Installation of SQL

1. Clone the repository
```bash
git clone https://github.com/mirrulations/DatabaseScripts.git
```

2. In the postgres folder of the DatabaseScripts directory, create a virtual environment, activate it, and install the requirements.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create a .env file containing the following:
```bash
POSTGRES_DB=<database name>
POSTGRES_USERNAME=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_HOST=<hostname>
POSTGRES_PORT=5432
```

## Using SQL
1. To start the SQL container, run the following command:
```bash
docker-compose up -d
```

 * You can connect to the database using the following command:
 ```bash
    psql -h localhost -U $POSTGRES_USERNAME -d $POSTGRES_DB
 ```
* You can run the following command to create the table and insert data:
```bash
    python CreateTables.py
```
* You can run the following command to Drop the table:
```bash
    python DropTables.py
```
* You can run the following command to ingest dockets, comments, documents respectively:
```bash
    python IngestDocket.py
    python IngestComment.py 
    python IngestDocument.py
```

## Cleanup
   1. To stop the SQL container, run the following command:
```bash
docker-compose down
```

If you have any questions or need help, please reach out to a member of the Data Product team.
```