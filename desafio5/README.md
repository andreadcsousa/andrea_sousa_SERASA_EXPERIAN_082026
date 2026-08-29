# Desafio 5: Pipeline Orquestrado

Este diretório contém a implementação de um pipeline orquestrado em **Apache Airflow** para simular o fluxo diário de ingestão, transformação e validação de dados de transações financeiras, com notificação de sucesso ou falha.

## Objetivo

Demonstrar familiaridade com ferramentas de orquestração além de **Databricks**, estruturando um **DAG** com dependências explícitas entre tarefas e regras de qualidade configuráveis.

## Lógica da Solução

- Ingestão: caminho do arquivo configurável via Airflow Variable (`fraud_data_path`), acessível em Admin → Variables na UI do Airflow. Se a variável não estiver cadastrada, usa o caminho padrão como fallback;
- Transformação: aplica a mesma lógica de limpeza do `is_fraud` usada no desafio 3 (conversão para numérico via `pd.to_numeric` e remoção de registros inválidos);
- Quality Gate: falha o DAG se a taxa de fraude estiver fora do intervalo configurável (0,1% a 20%);
- Notificação: `on_failure_callback` aplicado via `default_args`, registrando a task que falhou em caso de erro;
- Dependências: ingestão → transformação → quality gate → notificação.

## Bugs e Ajustes Necessários

Durante a implementação, alguns problemas foram encontrados e resolvidos:

`Webserver encerrando sozinho:`

O Airflow não inicializava porque o banco de metadados não estava criado;

> **Solução:**  
> Rodar **airflow db init** dentro do container e criar um usuário admin com airflow users create.

`Erro na leitura do CSV:`

A coluna is_fraud estava em formato string, causando falha no cálculo da média;

> **Solução:**  
> Forçar conversão para numérico com pd.to_numeric(df["is_fraud"], errors="coerce").

`Nome do arquivo com espaço:`

**"fraud_data 1.csv"** gerava inconsistências;

> **Solução:**  
> Renomear para **fraud_data.csv** e ajustar o caminho no DAG.

`Confusão com nomes de containers:`

O Docker Compose adiciona prefixos aos nomes.

> **Solução:**  
> Necessário usar o nome correto (desafio5-airflow) ao executar os comandos.

Após esses ajustes, a DAG rodou com sucesso, conforme mostrado na imagem:

![DAG rodando com sucesso no Airflow](/desafio5/fraud_pipeline_dag_success.jpg)

## Execução Local

Rodar com Docker Compose simples:

```bash
docker-compose up -d
```

> [!WARNING]
> Necessário ter o Docker Desktop instalado e rodando. Pode testar com `docker ps`.

### Inicialização e Acesso

Ao rodar `docker-compose up -d`, o container automaticamente inicializa o banco de metadados, cria o usuário administrador e sobe o Scheduler + Webserver.

- **URL:** http://localhost:8080
- **Usuário:** `admin`
- **Senha:** `admin`

> [!TIP]
> Ative o toggle da DAG **`fraud_pipeline_dag`** e clique em Play ▶ para testar.

### Configurando a Variable de Ingestão (opcional)

Por padrão, a task de ingestão usa o caminho `/opt/airflow/dags/fraud_data.csv`. Para customizar sem alterar código:

1. Acesse **Admin → Variables** na UI do Airflow;
2. Clique em **+** para adicionar uma nova variável;
3. Preencha:
   - **Key:** `fraud_data_path`
   - **Val:** caminho desejado
4. Salve. A próxima execução da DAG usará o novo caminho automaticamente.
