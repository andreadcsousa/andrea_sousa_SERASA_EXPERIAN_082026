# Desafio 1: Data Contract

Este diretório contém os arquivos utilizados para definir e validar um **Data Contract**, ou seja, um conjunto de regras que define como os dados devem ser estruturados e quais condições precisam ser atendidas para serem considerados válidos.

## Objetivo

Garantir interoperabilidade, governança e rastreabilidade das features consumidas em produção, tanto em batch quanto em streaming.
Definir regras para garantir que os dados utilizados pelos sistemas estejam no formato esperado e atendam aos critérios de qualidade estabelecidos.

## Estrutura

- `data_contract.json` → contrato em formato JSON, facilitando seu uso por sistemas;
- `data_contract.yaml` → mesma definição em formato YAML, mais fácil de ler e revisar;
- `fluxo_validacao.png` → diagrama mostrando as etapas da validação;
- `validate_contract.py` → script em Python para verificar se os dados atendem às regras definidas;
- `validate_contract.sql` → versão da validação utilizando SQL.

## Como funciona

1. **Estrutura dos dados:**
   - Verifica se os campos esperados existem e estão no formato definido no contrato.
2. **Prazo de atualização:**
   - Define o tempo máximo esperado para que os dados sejam atualizados;
   - Quando esse prazo não é cumprido, a situação pode ser identificada pela validação.
3. **Qualidade dos dados:**
   - Verifica se os valores estão dentro das regras estabelecidas;
   - Valores inválidos ou fora do esperado são identificados pela validação.

## Interoperabilidade

O contrato foi disponibilizado em `YAML` e `JSON` para mostrar como a mesma definição pode ser utilizada tanto para documentação quanto por sistemas.

## Automação

Os scripts de validação em `Python` e `SQL` mostram como as regras do contrato podem ser verificadas automaticamente, evitando a necessidade de conferir os dados manualmente.
