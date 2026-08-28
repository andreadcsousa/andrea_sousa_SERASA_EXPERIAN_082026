import pandas as pd
import json
import yaml

# Carregar contrato em JSON
with open("contracts/data_contract.json", "r") as f:
    contract = json.load(f)

# Exemplo de dataset (simulação)
data = pd.DataFrame(
    {
        "user_id": ["u1", "u2", "u3"],
        "qtd_transacoes_24h": [10, -5, 600],  # contém valores inválidos
        "timestamp": ["2026-08-27 12:00:00", None, "2026-08-27 13:00:00"],
    }
)


# Função de validação
def validate_data(df, contract):
    errors = []
    rules = contract["quality_rules"]

    for rule in rules:
        if "qtd_transacoes_24h >= 0" in rule["rule"]:
            invalid = df[df["qtd_transacoes_24h"] < 0]
            if not invalid.empty:
                errors.append(
                    f"Valores negativos encontrados: {invalid['qtd_transacoes_24h'].tolist()}"
                )

        if "qtd_transacoes_24h <= 500" in rule["rule"]:
            invalid = df[df["qtd_transacoes_24h"] > 500]
            if not invalid.empty:
                errors.append(
                    f"Outliers encontrados: {invalid['qtd_transacoes_24h'].tolist()}"
                )

        if "timestamp não pode ser nulo" in rule["rule"]:
            invalid = df[df["timestamp"].isnull()]
            if not invalid.empty:
                errors.append("Timestamp nulo encontrado.")

    return errors


# Executar validação
violations = validate_data(data, contract)

if violations:
    print("⚠️ Violações detectadas:")
    for v in violations:
        print("-", v)
else:
    print("✅ Dados conformes ao contrato.")
