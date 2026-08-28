# Databricks notebook source
dbutils.widgets.text("threshold", "0.95")
threshold = dbutils.widgets.get("threshold")

print(f"Etapa 3: Quality Gate executado com threshold {threshold}.")
