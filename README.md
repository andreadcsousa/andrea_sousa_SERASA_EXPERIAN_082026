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
    - [Validação Automática](#validação-automática)
    - [Fluxo de Validação Automática](#fluxo-de-validação-automática)
    - [Principais Pontos](#principais-pontos)
  - [2 SQL](#2-sql)
    - [Estratégia](#estratégia)
    - [Resultado](#resultado)
  - [3 Análise Exploratória de Dados](#3-análise-exploratória-de-dados)
    - [Estratégia](#estratégia-1)
    - [Resultado](#resultado-1)
  - [4 CI/CD para Databricks](#4-cicd-para-databricks)
  - [5 Pipeline Orquestrado](#5-pipeline-orquestrado)

## 1 Arquitetura de Dados

> [!IMPORTANT]
> **Contexto:** fintech de crédito com modelo de propensão à inadimplência em produção, hoje consumindo features em batch diário — o que degrada a performance em janelas de alto volume (vésperas de feriado, datas de pagamento).

### Visão Geral da Arquitetura

![Diagrama](https://copilot.microsoft.com/th/id/BCO.ca5ee074-3001-4ca5-b3a4-ef5b577d9812.png)

A arquitetura proposta é **híbrida**, combinando processamento _near-real-time_ para features críticas e _batch diário_ para features históricas.

Organiza-se nas camadas **bronze → silver → gold**, com integração à **Feature Store** e consumo por modelos de ML e dashboards analíticos.

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

### Validação Automática

Exemplos de validação de dados contra o contrato:

- [contracts/validate_contract.py](contracts/validate_contract.py) → validação em Python
- [contracts/validate_contract.sql](contracts/validate_contract.sql) → validação em SQL

Esses scripts aplicam as regras de qualidade e monitoram violações de SLA.

### Fluxo de Validação Automática

![Fluxo de Validação de Dados contra Contrato](https://copilot.microsoft.com/th/id/BCO.b1571369-c414-41e7-ab5e-9eecbd35744d.png)

1. **Leitura do Data Contract**
2. **Checagem de conformidade** (schema, regras, SLA)
3. **Resultado:**
   - ✅ Dados aprovados → seguem para consumo
   - ⚠️ Violação detectada → gera alerta, log e ação corretiva

### Principais Pontos

- Separação clara entre streaming (_near-real-time_) e batch diário.
- Camadas bronze → silver → gold bem definidas.
- Feature Store híbrida para consumo do modelo.
- Dashboards analíticos com SLA de 1 hora.
- Estratégia de qualidade e observabilidade com alertas e testes por camada.
- Trade-off: complexidade do streaming vs custo/latência → mitigado com arquitetura híbrida.

## 2 SQL

Nessa parte do case, o objetivo foi resolver um desafio técnico inspirado em entrevistas na plataforma HackerRank. Link de acesso ao desafio, no README da pasta [/desafio2](/desafio2/README.md).

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

Nessa parte do case, o objetivo foi realizar uma análise exploratória de dados em um dataset de transações financeiras com indicação de fraude.

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

### Resultado

- Notebook final disponível em: [/desafio3/fraud_analysis.ipynb](/desafio3/eda.ipynb);
- Saídas incluem gráficos e tabelas que mostram:
  - Dataset desbalanceado (transações fraudulentas são ~12% da amostra);
  - Fraudes se camuflando de acordo com o comportamento do consumidor;
  - Novas features que aumentam a capacidade de detecção de fraudes;
  - Top 5 categorias mais vulneráveis, com destaque para segmentos digitais.

## 4 CI/CD para Databricks

## 5 Pipeline Orquestrado
