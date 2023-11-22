

# airflow-sandbox

## Cloning the repository 

Before getting started, create a new folder on your desktop. If you already have a place where you like to store git repos or personal projects, feel free to clone the repo there. 

After installing git, open a terminal session and execute this command. 

```zsh
git clone https://github.com/larsonaj/airflow-sandbox.git {FOLDER-NAME}
```

## Getting the airflow containers started on your machine
*Note: this section assumes you have docker installed*

After cloning the repo and installing docker, before starting airflow you need to prepare your environment variables.

First we need to add the *.env* file to the top level directory which contains authentication information for connections with Snowflake. 

Sample *.env* file:

```yaml
AIRFLOW_UID=50000  
SNOWFLAKE_CONNECTION='{
	"conn_type": "snowflake",
	"login": "username",
	"password": "password",
	"host": "captech_partner.snowflakecomputing.com",
	"port": 443,
	"schema": "F1",
	"extra": {
		"account": "captech_partner",
		"database": "TEST_DB",
		"region": "us-east-1",
		"warehouse": "XS_WH"
		}
	}'
```


## Writing your first DAG

## Configuration and experimentation