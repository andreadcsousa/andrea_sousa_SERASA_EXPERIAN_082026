-- Criação da tabela com constraints baseadas no Data Contract
CREATE TABLE transacoes_24h (
    user_id VARCHAR(50) NOT NULL,
    qtd_transacoes_24h INT NOT NULL CHECK (qtd_transacoes_24h >= 0 AND qtd_transacoes_24h <= 500),
    timestamp TIMESTAMP NOT NULL
);

-- Trigger para monitorar SLA de atualização (simplificado)
-- Aqui, assumimos que existe uma tabela de auditoria para registrar atrasos
CREATE OR REPLACE FUNCTION check_sla()
RETURNS TRIGGER AS $$
BEGIN
    -- SLA: atualização em até 5 minutos
    IF (NOW() - NEW.timestamp) > INTERVAL '10 minutes' THEN
        INSERT INTO auditoria_sla (user_id, violacao, registrado_em)
        VALUES (NEW.user_id, 'Violação de SLA - atraso > 10 min', NOW());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_sla
AFTER INSERT ON transacoes_24h
FOR EACH ROW
EXECUTE FUNCTION check_sla();
