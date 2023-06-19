# Aicurriculum-ETL

## Deployment with Docker 🐳

Deployment with docker-compose:

Add oracle_storage_config.prod and private_key.pem to folder configs

```
chmod -R 777 logs resources plugins
docker-compose up -d
```

- Airflow backend - docs: http://0.0.0.0:8080/api/v1/ui/
- Api backend: http://0.0.0.0:8080

## Installation ⚡️

### Requires

- Python: 3.8.16

Install with pip:

```
<!-- Optional: Create venv -->
python -m venv venv
. venv/bin/activate

<!-- Install -->
pip install -r requirements.txt
```

<!-- Optional: Change executor and database -->

Here you can change the executor to LocalExecutor and configure database connection to PostgreSQL.
If use PostgreSQL you can create manual or run in docker
docker run -it --name postgres --env-file=.env.db -p 5432:5432 -d postgres:13

## Run ⚡️

### Run manually

```
<!-- Export working directory -->
export AIRFLOW_HOME=$PWD

<!-- Init database -->
airflow db init
airflow users create --username airflow --firstname {firstname} --lastname {lastname} --role Admin --email {email}

<!-- Run airflow scheduler -->
airflow scheduler

<!-- Open new terminal -->
export AIRFLOW_HOME=$PWD
export PYTHONPATH=$PWD
airflow webserver -p 8080
```

## Connect oracle database ⛄️

In Admin/Connections:

```
Connection id: oracle_default
Connection Type: Oracle
Host: {IP/Domain}. Example: 192.168.x.x
Schema: {username}. Example: AI_team
Login: {username}.  Example: AI_team
Password: {password}. Example: AI_team123
Port: {port number}. Example: 1521
extra: {"dsn":"{IP/Domain}" , "service_name":"{service_name}"}. Example: {"dsn":"192.168.x.x" , "service_name":"xxx.xxx.xxx.oraclevcn.com"}
```

## Login

```
Username: airflow
Password: airflow
```
