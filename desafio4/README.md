# Desafio 4: CI/CD para Databricks

Este diretório contém a configuração de CI/CD para Databricks utilizando Databricks Asset Bundles (DAB) e GitHub Actions, com workflows separados para produção e pull requests.

## Objetivo

Automatizar a implantação de jobs no Databricks, garantindo qualidade, segurança e separação de ambientes (dev e prod), além de permitir execução manual via CLI.

## Lógica da Solução

### 1. Definição do Job

O arquivo databricks.yml utiliza a estrutura moderna de Databricks Asset Bundles (DAB) declarando os recursos sob a chave resources.jobs:

- **Job Cluster Otimizado:** Utiliza reuso de cluster computacional via job_cluster_key, com dimensionamento e número de workers parametrizados automaticamente por ambiente (dev vs prod);
- Tasks Encadeadas (notebook_task):
  1. **ingestao** → Leitura dos dados brutos;
  2. **transformacao** → Limpeza, enriquecimento e feature engineering (depende de ingestao);
  3. **quality_gate** → Validação de métricas e limites de qualidade (depende de transformacao), recebendo o parâmetro dinâmico threshold via base_parameters.

### 2. Separação de Ambientes

Dois targets distintos:

- **dev** → cluster menor, job `[dev] fraud_pipeline`;
- **prod** → cluster maior, job `fraud_pipeline`.

### 3. Pipeline de CI/CD

Arquivo `deploy.yml` dispara em **push na branch main**.

Etapas:

- Testes unitários (pytest);
- databricks bundle validate;
- databricks bundle deploy --target prod;
- databricks bundle run --target prod;

> [!IMPORTANT]
> O pipeline falha se o job falhar.

### 4. Pipeline de Pull Request (PR)

Arquivo `ci.yml` dispara em **pull requests para main**.

Etapas:

- Testes unitários;
- databricks bundle validate --target dev;

> [!NOTE]
> Não faz deploy em produção.

### 5. Pré-requisitos

- **Databricks CLI v2+** instalado;
- Autenticação via secrets configurados no repositório:
  - DATABRICKS_HOST e DATABRICKS_TOKEN, ou
  - DATABRICKS_CLIENT_ID e DATABRICKS_CLIENT_SECRET (service principal);

> [!TIP]
> Service principal com permissões adequadas no workspace.

> [!NOTE]
> **GitHub Secrets:** Garantir que as variáveis `DATABRICKS_HOST` e `DATABRICKS_TOKEN` (ou credenciais de Service Principal) estejam cadastradas nos secrets do repositório para injeção automática nas etapas de validate, deploy e run.

### Execução Manual via CLI

```bash
# Validar bundle
databricks bundle validate

# Deploy em produção
databricks bundle deploy --target prod

# Executar job
databricks bundle run --target prod
```
