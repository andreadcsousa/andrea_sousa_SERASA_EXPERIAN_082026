# Desafio 3: Análise Exploratória de Dados (EDA)

Este diretório contém a Análise Exploratória de Dados (EDA) e a Engenharia de Recursos aplicadas a um ecossistema de transações financeiras com foco na identificação de comportamentos fraudulentos.

## Objetivo

Mapear padrões estatísticos e temporais que diferenciam transações legítimas de fraudulentas, gerando insumos de negócio e novas variáveis (features) para futuros modelos de Machine Learning.

## Lógica da Solução

### 1. Entendimento do dataset

A base possui milhares de registros e colunas numéricas, categóricas e temporais;

- Colunas: **15 variáveis**;
- Linhas: **14.446 registros iniciais**;
- Nulos: **Nenhum valor ausente identificado**;
- Duplicados: **63 registros removidos**;
- Inconsistências: **`is_fraud` ajustado para valores binários (0/1)**.

### 2. Distribuição de fraudes

`Proporção:`

12,4% de transações fraudulentas vs. 87,6% de transações legítimas.

`Balanceamento:`

Dataset desbalanceado.

`Impacto no modelo de ML:`

Modelos treinados sem ajustes tendem a ignorar a classe minoritária (fraude) e apresentar uma acurácia falsamente alta, induzidos pelo viés da maioria.

- **Tratamento**: Adotar técnicas de reamostragem e focar a avaliação em métricas que penalizam falsos negativos.

### 3. Padrões temporais e de valor

`Valor (Amount):`

O valor médio das fraudes (R$ 518,07) é radicalmente superior ao das transações legítimas (R$ 66,81). A análise estatística via IQR (Intervalo Interquartil) comprovou que o limite de compras legítimas normais é de R$ 190,12. Contudo, **75,08% das fraudes ocorrem exatamente acima desse limite**, demonstrando que os criminosos tentam se camuflar fingindo o comportamento de clientes legítimos de alto poder aquisitivo.

`Temporal:`

A incidência de fraudes apresenta um pico crítico no período noturno e na madrugada, atingindo seu ponto máximo às **23h** (onde a taxa de fraudes chega a **28,92%** das transações do horário). As transações legítimas, por outro lado, diluem-se ao longo do horário comercial e diurno.

### 4. Feature engineering

`Idade do cliente:`

Calculada a partir da diferença em anos entre a data de nascimento e o momento da compra.

> [!TIP]
> **Justificativa:**
> A idade influencia diretamente os hábitos de consumo e o perfil de risco do portador do cartão. No dataset, a média de idade dos clientes fraudados (50 anos) é ligeiramente superior à dos usuários comuns (47 anos).

`Distância cliente–merchant:`

Calculada via fórmula geométrica de Haversine utilizando as coordenadas do cliente e do estabelecimento.

> [!TIP]
> **Justificativa:**
> Permite identificar inconsistências geográficas em transações presenciais, mapeando se o cartão foi fisicamente utilizado em um local distante da residência do titular em um intervalo de tempo impossível.

`Horário de Risco:`

Flag binária (0 ou 1) que isola transações ocorridas na janela crítica identificada na EDA (entre 22h e 03h).

> [!TIP]
> **Justificativa:**
> Facilita o aprendizado do modelo de ML ao destacar o indicador temporal mais correlacionado ao comportamento criminoso.

### 5. Query analítica

Resultado da consulta analítica consolidando os 5 segmentos de mercado com maior taxa de incidência de fraude e o respectivo valor médio do prejuízo por transação:

| Categoria     | Total Transações | Total Fraudes | Taxa de Fraude | Média das Transações |
| :------------ | :--------------: | :-----------: | :------------: | -------------------: |
| shopping_net  |      1.393       |      381      |     27,35%     |          R$ 1.001,13 |
| grocery_pos   |      1.591       |      433      |     27,22%     |            R$ 315,23 |
| misc_net      |       815        |      217      |     26,63%     |            R$ 797,16 |
| shopping_pos  |      1.347       |      187      |     13,88%     |            R$ 886,33 |
| gas_transport |      1.424       |      153      |     10,74%     |             R$ 12,65 |

> [!NOTE]
> _Os segmentos digitais (`shopping_net` e `misc_net`) não só estão no topo da taxa de risco, como também concentram os maiores valores médios por golpe, destacando-se como os alvos mais críticos para regras de bloqueio preventivo._
