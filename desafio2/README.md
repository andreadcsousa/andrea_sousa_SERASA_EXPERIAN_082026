# Desafio 2: SQL

Desafio de referência: [Interviews — HackerRank](https://www.hackerrank.com/challenges/interviews/problem)

## Objetivo

Gerar uma consulta que retorne, para cada contest:

- contest_id
- hacker_id
- name
- soma de total_submissions
- soma de total_accepted_submissions
- soma de total_views
- soma de total_unique_views

Excluindo contests em que todas as métricas sejam zero.

## Lógica da Solução

### 1. Separação em CTEs

- Uma CTE para consolidar métricas de visualizações (`view_totals`);
- Outra CTE para consolidar métricas de submissões (`submission_totals`);
- Consulta principal utilizando os resultados das consultas temporárias.

```sql
WITH
  view_totals AS (SELECT ... FROM View_Stats ...),
  submission_totals AS (SELECT ... FROM Submission_Stats ...)
SELECT
...
LEFT JOIN submission_totals ss ON ch.challenge_id = ss.challenge_id
LEFT JOIN view_totals vs ON ch.challenge_id = vs.challenge_id
```

> [!NOTE]
> Como o HackerRank não permite testar partes da consulta, precisei ajustar e executar o código várias vezes até chegar a um resultado aceito pela plataforma. E como não tenho experiência profissional com CTEs, apenas conhecimento adquirido em cursos anteriores, tive certa dificuldade com a sintaxe e preferi criar as consultas primeiro para depois envolvê-las nas CTEs.

### 2. Junção das tabelas

- `Contests` → conecta ao criador;
- `Colleges` → conecta contests a colleges;
- `Challenges` → conecta colleges a challenges;
- `view_totals` e `submission_totals` → trazem métricas consolidadas por challenge.

### 3. Agregação final

- Usei `SUM()` junto com `COALESCE()` para somar métricas e tratar nulos simultaneamente.

> [!NOTE]
> Sempre confundo a ordem entre `SUM` e `COALESCE`, mas utilizei a seguinte lógica: para cada linha, se o valor for NULL, substituir por 0; depois, somar os valores. Em vez de considerar 0 apenas se o resultado da soma retornar NULL.

### 4. Filtro de exclusão

- Usei `HAVING` com a soma de todas as métricas:

  ```sql
  HAVING SUM(COALESCE(st.total_submissions, 0))
       + SUM(COALESCE(st.total_accepted_submissions, 0))
       + SUM(COALESCE(vt.total_views, 0))
       + SUM(COALESCE(vt.total_unique_views, 0)) > 0
  ```

> [!NOTE]
> Aqui usei `+` em vez de `AND` porque o requisito é excluir contests em que **todas** as métricas sejam zero. Usar `AND` excluiria contests em que **qualquer** métrica fosse zero, o que não é o esperado. Com `+`, basta que **uma** métrica seja positiva para o contest aparecer.
