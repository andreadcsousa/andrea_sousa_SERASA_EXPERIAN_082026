from datetime import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
import pandas as pd


def ingestao():
    path = Variable.get(
        "fraud_data_path", default_var="/opt/airflow/dags/fraud_data.csv"
    )
    print(f"Simulando ingestão do arquivo em: {path}")


def transformacao():
    path = Variable.get(
        "fraud_data_path", default_var="/opt/airflow/dags/fraud_data.csv"
    )
    df = pd.read_csv(path)
    df["is_fraud"] = pd.to_numeric(df["is_fraud"], errors="coerce")
    df = df.dropna(subset=["is_fraud"])
    print(f"Transformação concluída: {len(df)} registros válidos após limpeza.")


def quality_gate():
    path_csv = "/opt/airflow/dags/fraud_data.csv"
    df = pd.read_csv(path_csv)

    # Tratamento preventivo e validação do indicador
    df["is_fraud"] = pd.to_numeric(df["is_fraud"], errors="coerce")
    taxa_fraude = df["is_fraud"].mean()

    threshold_min, threshold_max = 0.001, 0.20

    if pd.isna(taxa_fraude):
        raise ValueError("A coluna 'is_fraud' não possui valores numéricos válidos.")

    if not (threshold_min <= taxa_fraude <= threshold_max):
        raise ValueError(
            f"Quality Gate Rejeitado: Taxa de fraude fora do intervalo ({taxa_fraude:.2%})"
        )

    print(f"Quality Gate Aprovado! Taxa de fraude apurada: {taxa_fraude:.2%}")


def notificar_sucesso():
    print("Pipeline executado com sucesso!")


def notificar_falha(context):
    task_id = context.get("task_instance").task_id
    print(f"❌ Falha detectada na task: {task_id}")


default_args = {
    "owner": "airflow",
    "on_failure_callback": notificar_falha,
}

with DAG(
    dag_id="fraud_pipeline_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,  # Aplica o callback de falha em todas as tasks
) as dag:

    ingestao_task = PythonOperator(
        task_id="ingestao",
        python_callable=ingestao,
    )

    transformacao_task = PythonOperator(
        task_id="transformacao",
        python_callable=transformacao,
    )

    quality_gate_task = PythonOperator(
        task_id="quality_gate",
        python_callable=quality_gate,
    )

    notificar_task = PythonOperator(
        task_id="notificacao",
        python_callable=notificar_sucesso,
    )

    ingestao_task >> transformacao_task >> quality_gate_task >> notificar_task
