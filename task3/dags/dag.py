from datetime import datetime, timedelta
import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.reqifTojson import reqifTojson
from src.jsonTorst import jsonToRst
from src.uploadRST import uploadFile
from src.updateIndexRST import updateIndexRST
from src.addPipeline import addPipeLine

default_args = {
    'owner': 'thiendsu',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id = 'oneplustwo_work_flow',
    default_args = default_args,
    description = 'This is our work flow dag building ',
    start_date = datetime(2023,6,15,12),
    schedule_interval=timedelta(1)
) as dag:
    task1 = PythonOperator(
        task_id = 'CovertReqifToJson',
        python_callable = reqifTojson,
    )
    task2 = PythonOperator(
        task_id = 'ConvertJsonToRst',
        python_callable = jsonToRst,
    )
    task3 = PythonOperator(
        task_id = 'UploadRSTFile',
        python_callable = uploadFile,
    )
    task4 = PythonOperator(
        task_id = 'UpdateIndexRstFile' , 
        python_callable = updateIndexRST
    )
    task5 = PythonOperator(
        task_id = 'AddPipeline' , 
        python_callable = addPipeLine
    )
    task1 >> task2 >> task3 >> task4 >> task5