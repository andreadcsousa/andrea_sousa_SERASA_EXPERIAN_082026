import os
import json
import pandas as pd

# Garantir resolução de caminho independente do diretório de execução
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTRACT_PATH = os.path.join(BASE_DIR, "data_contract.json")

# Carregar contrato em JSON
with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
    contract = json.load(f)

# Dataset de simulação (inclui cenários de borda: valor negativo, outlier e nulo)
data = pd.DataFrame(
    {
        "user_id": ["u1", "u2", "u3"],
        "qtd_transacoes_24h": [10, -5, 600],
        "timestamp": ["2026-08-27 12:00:00", None, "2026-08-27 13:00:00"],
    }
)


def validate_data(df: pd.DataFrame, contract_config: dict) -> list:
    """
    Aplica as regras de qualidade do Data Contract sobre o DataFrame.
    Retorna uma lista de violações encontradas.
    """
    errors = []
    rules = contract_config.get("quality_rules", [])

    for rule_item in rules:
        rule_expr = rule_item.get("rule", "")

        # Validação 1: Limite inferior (Valores Negativos)
        if "qtd_transacoes_24h >= 0" in rule_expr:
            # Preenche NAs temporariamente para evitar falhas na comparação booleana
            invalid = df[df["qtd_transacoes_24h"].fillna(0) < 0]
            if not invalid.empty:
                errors.append(
                    f"Valores negativos encontrados: {invalid['qtd_transacoes_24h'].tolist()}"
                )

        # Validação 2: Limite superior (Outliers)
        if "qtd_transacoes_24h <= 500" in rule_expr:
            invalid = df[df["qtd_transacoes_24h"].fillna(0) > 500]
            if not invalid.empty:
                errors.append(
                    f"Outliers acima do limite de 500: {invalid['qtd_transacoes_24h'].tolist()}"
                )

        # Validação 3: Nulidade do Timestamp
        if "timestamp não pode ser nulo" in rule_expr:
            invalid = df[df["timestamp"].isnull()]
            if not invalid.empty:
                affected_users = invalid["user_id"].tolist()
                errors.append(
                    f"Timestamp nulo encontrado para os usuários: {affected_users}"
                )

    return errors


# Execução da Validação
if __name__ == "__main__":
    violations = validate_data(data, contract)

    if violations:
        print("⚠️ Violações de Data Contract detectadas:")
        for v in violations:
            print(f"  - {v}")
    else:
        print("✅ Dados conformes com o Data Contract.")
