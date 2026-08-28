-- CTE que consolida métricas de visualizações por challenge
WITH view_totals AS (
    SELECT
        challenge_id,
        SUM(total_views) AS total_views,
        SUM(total_unique_views) AS total_unique_views
    FROM View_Stats
    GROUP BY challenge_id
),
-- CTE que consolida métricas de submissões por challenge
submission_totals AS (
    SELECT
        challenge_id,
        SUM(total_submissions) AS total_submissions,
        SUM(total_accepted_submissions) AS total_accepted_submissions
    FROM Submission_Stats
    GROUP BY challenge_id
)
-- Consulta principal: consolida métricas por contest
SELECT
    ct.contest_id,
    ct.hacker_id,
    ct.name,
    SUM(COALESCE(ss.total_submissions, 0)) AS total_submissions,
    SUM(COALESCE(ss.total_accepted_submissions, 0)) AS total_accepted_submissions,
    SUM(COALESCE(vs.total_views, 0)) AS total_views,
    SUM(COALESCE(vs.total_unique_views, 0)) AS total_unique_views
FROM Contests ct
JOIN Colleges cl ON ct.contest_id = cl.contest_id
JOIN Challenges ch ON cl.college_id = ch.college_id
LEFT JOIN submission_totals ss ON ch.challenge_id = ss.challenge_id
LEFT JOIN view_totals vs ON ch.challenge_id = vs.challenge_id
GROUP BY
    ct.contest_id,
    ct.hacker_id,
    ct.name
-- Só mostra contests em que pelo menos uma métrica é > 0
HAVING
       SUM(COALESCE(ss.total_submissions, 0))
    +  SUM(COALESCE(ss.total_accepted_submissions, 0))
    +  SUM(COALESCE(vs.total_views, 0))
    +  SUM(COALESCE(vs.total_unique_views, 0)) > 0
ORDER BY ct.contest_id;