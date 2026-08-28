# Case Técnico: Engenheira de Analytics Plena

Este case apresenta a evolução da arquitetura de dados de uma fintech de crédito que já possui um modelo de propensão à inadimplência em produção. O objetivo foi propor uma solução capaz de lidar com picos de volume em datas críticas, garantindo **latência reduzida**, **governança de dados** e **observabilidade**.

A narrativa segue quatro etapas:

1. **Problema:** contexto e desafios atuais;
2. **Arquitetura:** proposta híbrida (batch + near-real-time);
3. **Execução:** SQL, EDA, CI/CD e pipeline orquestrado;
4. **Impacto:** ganhos de performance, confiabilidade e clareza analítica.

📑 Conteúdo:

- [Case Técnico: Engenheira de Analytics Plena](#case-técnico-engenheira-de-analytics-plena)
  - [1 Arquitetura de Dados](#1-arquitetura-de-dados)
    - [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
    - [Data Contract: Feature Near‑Real‑Time](#data-contract-feature-nearrealtime)
    - [Observabilidade e SLAs por Camada](#observabilidade-e-slas-por-camada)
    - [Validação Automática](#validação-automática)
    - [Fluxo de Validação Automática](#fluxo-de-validação-automática)
    - [Principais Pontos](#principais-pontos)
  - [2 SQL](#2-sql)
    - [Estratégia](#estratégia)
    - [Resultado](#resultado)
  - [3 Análise Exploratória de Dados](#3-análise-exploratória-de-dados)
    - [Estratégia](#estratégia-1)
    - [Anatomia do Comportamento de Valor (Boxplot e Outliers)](#anatomia-do-comportamento-de-valor-boxplot-e-outliers)
    - [Feature Engineering](#feature-engineering)
    - [Resultado](#resultado-1)
  - [4 CI/CD para Databricks](#4-cicd-para-databricks)
    - [Estratégia](#estratégia-2)
    - [Resultado](#resultado-2)
  - [5 Pipeline Orquestrado](#5-pipeline-orquestrado)
    - [Estratégia](#estratégia-3)
    - [Resultado](#resultado-3)

## 1 Arquitetura de Dados

> [!IMPORTANT]
> **Contexto:** fintech de crédito com modelo de propensão à inadimplência em produção, hoje consumindo features em batch diário — o que degrada a performance em janelas de alto volume (vésperas de feriado, datas de pagamento).

### Visão Geral da Arquitetura

![](/mermaid-diagram-1.png)

A arquitetura proposta é **híbrida**, combinando processamento _near-real-time_ para features críticas e _batch diário_ para features históricas. Organiza-se nas camadas **bronze → silver → gold**, com integração à **Feature Store** e consumo por modelos de ML e dashboards analíticos.

---

### Data Contract: Feature Near‑Real‑Time

O contrato está disponível em dois formatos:

- [contracts/data_contract.yaml](contracts/data_contract.yaml)
- [contracts/data_contract.json](contracts/data_contract.json)

Mais detalhes sobre uso e governança estão em [contracts/README.md](contracts/README.md).

**Definições principais:**

- Schema, SLA, owner e regras de qualidade bem definidos.
- Monitoramento automático e reação a violações.
- Governança e rastreabilidade da feature crítica.

<br>

```yaml
# Data Contract - Feature: qtd_transacoes_24h
feature_name: qtd_transacoes_24h
description: Quantidade total de transações realizadas por um cliente nas últimas 24 horas.

schema:
  - name: user_id
    type: string
    nullable: false
  - name: qtd_transacoes_24h
    type: integer
    nullable: false
  - name: timestamp
    type: datetime
    nullable: false

sla:
  update_latency: "5 minutos"
  freshness_check: "a cada 5 minutos"
  max_delay_tolerance: "10 minutos"

owner:
  team: dados_risco
  contact: dados_risco@fintech.com

quality_rules:
  - rule: "qtd_transacoes_24h >= 0"
    description: "Valores negativos são inválidos."
  - rule: "qtd_transacoes_24h <= 500"
    description: "Valores acima de 500 são considerados outliers."
  - rule: "timestamp não pode ser nulo"
    description: "Garantir integridade temporal."

violation_policy:
  alert_channel: "Slack #monitoramento-dados"
  action_on_violation:
    - "Gerar alerta automático"
    - "Marcar feature como inválida"
    - "Bloquear consumo pelo modelo até correção"
```

### Observabilidade e SLAs por Camada

Para garantir confiabilidade na tomada de decisão e no consumo pelo modelo de ML, a pipeline foi projetada com regras claras de observabilidade:

- **SLA de Features Near-Real-Time:** Latência máxima de atualização de **5 minutos** e tolerancia máxima de delay de 10 minutos. Falhas disparam alertas imediatos via Slack e bloqueiam o consumo da feature pelo modelo;
- **SLA de Dashboards Analíticos:** Atualização em janela batch de **1 hora**;
- **Estratégia de Testes por Camada:**
  - **Camada Bronze:** Validação de schema, nulos e conformidade com o Data Contract via `validate_contract.py` / `.sql`;
  - **Camada Silver:** Quality Gates aplicados no pipeline (ex.: validação da taxa de fraude em limites aceitáveis entre 0,1% e 20%);
  - **Camada Gold:** Monitoramento de frescor dos dados (_freshness_) e métricas de agregação.

### Validação Automática

Exemplos de validação de dados contra o contrato:

- [contracts/validate_contract.py](contracts/validate_contract.py) → validação em Python
- [contracts/validate_contract.sql](contracts/validate_contract.sql) → validação em SQL

Esses scripts aplicam as regras de qualidade e monitoram violações de SLA.

### Fluxo de Validação Automática

![](/mermaid-diagram-2.png)

### Principais Pontos

- Separação clara entre streaming (_near-real-time_) e batch diário.
- Camadas bronze → silver → gold bem definidas.
- Feature Store híbrida para consumo do modelo.
- Dashboards analíticos com SLA de 1 hora.
- Estratégia de qualidade e observabilidade com alertas e testes por camada.
- Trade-off: complexidade do streaming vs custo/latência → mitigado com arquitetura híbrida.

## 2 SQL

Nessa parte do case, o objetivo foi resolver um desafio técnico inspirado em entrevistas na plataforma HackerRank. Link de acesso ao README do desafio na pasta [/desafio2](/desafio2/README.md).

> [!IMPORTANT]
> Exige múltiplos JOINs e funções de agregação para consolidar métricas de diferentes tabelas em uma única consulta. É esperado o uso de CTEs ou subqueries para organizar a lógica.

### Estratégia

- Conectar as tabelas com **JOIN** e **LEFT JOIN**;
- Usar **SUM()** para consolidar métricas;
- Usar **COALESCE()** para tratar valores nulos;
- Usar **CTEs** para organizar a lógica e manter o código legível;
- Filtrar contests com **HAVING** em que todas as métricas fossem zero.

<br>

```sql
WITH view_totals AS (
    SELECT
        challenge_id,
        SUM(total_views) AS total_views,
        SUM(total_unique_views) AS total_unique_views
    FROM View_Stats
    GROUP BY challenge_id
),
submission_totals AS (
    SELECT
        challenge_id,
        SUM(total_submissions) AS total_submissions,
        SUM(total_accepted_submissions) AS total_accepted_submissions
    FROM Submission_Stats
    GROUP BY challenge_id
)
SELECT
    ct.contest_id, ct.hacker_id, ct.name,
    SUM(COALESCE(ss.total_submissions, 0)) AS total_submissions,
    SUM(COALESCE(ss.total_accepted_submissions, 0)) AS total_accepted_submissions,
    SUM(COALESCE(vs.total_views, 0)) AS total_views,
    SUM(COALESCE(vs.total_unique_views, 0)) AS total_unique_views
FROM Contests ct
JOIN Colleges cl ON ct.contest_id = cl.contest_id
JOIN Challenges ch ON cl.college_id = ch.college_id
LEFT JOIN submission_totals ss ON ch.challenge_id = ss.challenge_id
LEFT JOIN view_totals vs ON ch.challenge_id = vs.challenge_id
GROUP BY ct.contest_id, ct.hacker_id, ct.name
HAVING
    SUM(COALESCE(ss.total_submissions, 0)) +
    SUM(COALESCE(ss.total_accepted_submissions, 0)) +
    SUM(COALESCE(vs.total_views, 0)) +
    SUM(COALESCE(vs.total_unique_views, 0)) > 0
ORDER BY ct.contest_id;
```

### Resultado

- Consulta final disponível em: [/desafio2/interviews_hackerrank.sql](/desafio2/interviews_hackerrank.sql);
- Saída retornando: contest_id, hacker_id, name e as somas de submissões, aceites, views e views únicas.

## 3 Análise Exploratória de Dados

Nessa parte do case, o objetivo foi realizar uma análise exploratória de dados em um dataset de transações financeiras com indicação de fraude. Link de acesso ao README do desafio na pasta [/desafio3](/desafio3/README.md).

> [!IMPORTANT]
> Exige exploração estatística, visualização gráfica e criação de novas features para identificar padrões que diferenciam transações legítimas de fraudulentas. É esperado o uso de pandas para manipulação, matplotlib/seaborn para visualização e feature engineering para enriquecer o dataset.

### Estratégia

- Explorar colunas, tipos e volume de dados; tratar nulos, duplicados e inconsistências;
- Analisar a distribuição de fraudes e avaliar impacto em modelos de ML;
- Identificar padrões temporais e de valor (amount) entre transações legítimas e fraudulentas;
- Criar novas features (idade do cliente, distância cliente–merchant, flag de horário crítico);
- Executar query analítica para identificar categorias com maior taxa de fraude e valor médio das transações fraudulentas.

<br>

![Proporção de Transações Fraudulentas vs Legítimas](/desafio3/proporcao_transacoes.png)

### Anatomia do Comportamento de Valor (Boxplot e Outliers)

A análise comparativa da distribuição de valores entre transações legítimas e fraudulentas revelou um padrão crítico de camuflagem:

- **Transações Legítimas (Valores Baixos + Outliers no Topo):** O comportamento padrão da população ocorre em valores baixos a moderados (mediana de R$ 66,81). Os outliers legítimos (compras caras como eletrodomésticos) sobem a régua, mas são eventos isolados;
- **Transações Fraudulentas (Padrão Concentrado no Topo):** O ticket médio das fraudes é radicalmente superior (R$ 518,07). Como os criminosos buscam extrair o valor máximo antes do bloqueio do cartão, não há interesse em golpes de valor baixo. O "normal" da fraude é o valor alto;
- **O Ponto de Intersecção (Desafio de ML):** Em escala logarítmica, a caixa do boxplot de fraudes mimetiza a área de outliers das transações legítimas. O grande desafio do modelo de detecção é diferenciar um cliente de alta renda realizando uma compra cara legítima de um fraudador estourando o limite do cartão.

### Feature Engineering

Para enriquecer a detecção de anomalias, foram criadas 4 features preditivas:

- **`is_night_transaction`**: Flag binária isolando o horário de pico crítico (22h às 03h, em que a taxa de fraude atinge até 28,92%);
- **`distance_merch_user`**: Distância em km (fórmula de Haversine) entre a localização do cliente e do estabelecimento;
- **`amt_to_cat_avg_ratio`**: Razão do valor gasto sobre a média da categoria para destacar transações atípicas em segmentos de menor ticket;
- **`customer_age`**: Idade do titular para análise demográfica de vulnerabilidade.

### Resultado

- Notebook final disponível em: [/desafio3/fraud_analysis.ipynb](/desafio3/fraud_analysis.ipynb);
- Saídas incluem gráficos e tabelas que mostram:
  - Dataset desbalanceado (transações fraudulentas são ~12% da amostra);
  - Fraudes concentradas no topo da tabela de preços e em horários noturnos;
  - Features enriquecidas prontas para modelagem preditiva;
  - Top 5 categorias mais vulneráveis, lideradas por `shopping_net` e `grocery_pos`.

## 4 CI/CD para Databricks

Nessa parte do case, o objetivo foi configurar um pipeline de CI/CD para Databricks utilizando Databricks Asset Bundles (DAB) e GitHub Actions, com workflows separados para produção e pull requests. Link de acesso ao README do desafio na pasta [/desafio4](/desafio4/README.md).

> [!IMPORTANT]
> Exige definição de workflow com múltiplas tasks, separação de ambientes (dev e prod) e pipelines automatizados para validação, deploy e execução de jobs. A autenticação é feita via secrets configurados no repositório.

### Estratégia

- Definição do workflow no **databricks.yml** utilizando Databricks Asset Bundles (DAB v2) sob resources.jobs e Job Clusters parametrizados dinamicamente por ambiente (dev vs prod);
- **Tasks encadeadas:** Ingestão → Transformação → Quality Gate (com passagem de parâmetro threshold);
- **Pipeline de Produção (deploy.yml) disparado em push na main:** Testes Unitários (pytest) → Validate → Deploy → Run em prod;
- **Pipeline de Pull Request (ci.yml) disparado em PRs:** Testes Unitários → Validate em dev (sem alterar o ambiente de produção).

### Resultado

- Arquivos criados:
  - [/desafio4/databricks.yml](/desafio4/databricks.yml)
  - [/.github/workflows/deploy.yml](/.github/workflows/deploy.yml)
  - [/.github/workflows/ci.yml](/.github/workflows/ci.yml)

## 5 Pipeline Orquestrado

Nesta etapa foi implementado um pipeline orquestrado em **Apache Airflow**, simulando o fluxo diário de ingestão, transformação e validação de dados de transações financeiras, com notificação de sucesso ou falha. Link de acesso ao README do desafio na pasta [/desafio5](/desafio5/README.md).

### Estratégia

O **DAG** foi estruturado com dependências explícitas entre as tarefas:

`ingestão → transformação → quality gate → notificação`

Durante a execução, alguns ajustes foram necessários:

- Inicialização do banco de metadados (**airflow db init**) e criação de usuário admin;
- Correção da leitura da coluna **is_fraud**, convertendo valores para numérico;
- Renomeação do arquivo para **fraud_data.csv** (evitando espaços no nome);
- Ajuste do **docker-compose.yml** para manter o webserver e scheduler ativos.

### Resultado

Após as correções acima, a DAG rodou com sucesso, validando a taxa de fraude e concluindo com notificação positiva.

![DAG rodando com sucesso no Airflow](/desafio5/fraud_pipeline_dag_success.jpg)

- Arquivos criados:
  - [/desafio5/fraud_pipeline_dag.py](/desafio5/fraud_pipeline_dag.py)
  - [/desafio5/docker-compose.yml](/desafio5/docker-compose.yml)
