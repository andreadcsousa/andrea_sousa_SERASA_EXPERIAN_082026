-- =============================================================================
-- DDL & SLA Enforcement via Data Contract (PostgreSQL Dialect)
-- =============================================================================

-- Tabela de destino Silver com Constraints de Qualidade embutidas
CREATE TABLE IF NOT EXISTS transacoes_24h (
    user_id VARCHAR(50) NOT NULL,
    qtd_transacoes_24h INT NOT NULL CHECK (qtd_transacoes_24h >= 0 AND qtd_transacoes_24h <= 500),
    timestamp TIMESTAMP NOT NULL
);

-- Tabela de Auditoria para registrar desvios de SLA
CREATE TABLE IF NOT EXISTS auditoria_sla (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    violacao VARCHAR(255),
    registrado_em TIMESTAMP DEFAULT NOW()
);

-- Função de Trigger para monitorar Latência de Ingestão em Near-Real-Time
CREATE OR REPLACE FUNCTION check_sla()
RETURNS TRIGGER AS $$
BEGIN
    -- Premissa Streaming/Near-Real-Time: Tolerância máxima de delay na ingestão = 10 minutos
    IF (NOW() - NEW.timestamp) > INTERVAL '10 minutes' THEN
        INSERT INTO auditoria_sla (user_id, violacao, registrado_em)
        VALUES (NEW.user_id, 'Violação de SLA - Atraso de ingestão superior a 10 min', NOW());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger ativado na inserção de novos eventos
DROP TRIGGER IF EXISTS trg_check_sla ON transacoes_24h;
CREATE TRIGGER trg_check_sla
AFTER INSERT ON transacoes_24h
FOR EACH ROW
EXECUTE FUNCTION check_sla();