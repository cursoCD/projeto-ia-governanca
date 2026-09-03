import os
import sys
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def selecionar_arquivo():
    """Abre uma janela para o usuário selecionar o arquivo CSV."""
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal do Tkinter
    root.attributes("-topmost", True)

    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione o arquivo CSV do Dataset",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os Arquivos", "*.*")],
    )

    return caminho_arquivo


def processar_e_modificar_dataset(caminho_csv):
    """Lê, aplica modificações para correção de viés e salva um novo CSV."""
    print(f"\n[INFO] Lendo arquivo: {caminho_csv}")
    df = pd.read_csv(caminho_csv)

    print("\n--- Visualização do Dataset Original ---")
    print(df.head())

    # =========================================================================
    # MODIFICAÇÃO DO DATASET (GOVERNANÇA E MITIGAÇÃO DE VIÉS)
    # =========================================================================
    # Criamos uma cópia para preservar os dados originais
    df_modificado = df.copy()

    # 1. Regra de Negócio Ética: Correção da decisão para solicitantes
    # da Periferia sem histórico de inadimplência (historico_inadimplencia == 0).
    condicao_correcao = (df_modificado["cep_regiao"] == "Periferia") & (
        df_modificado["historico_inadimplencia"] == 0
    )
    df_modificado.loc[condicao_correcao, "credito_aprovado"] = 1

    # 2. Remoção/Anonimização da variável proxy "cep_regiao" para evitar
    # que o modelo futuro utilize a localização geográfica de forma discriminatória.
    # df_modificado = df_modificado.drop(columns=['cep_regiao'])

    print(
        "\n--- Dataset Modificado (Viés Corrigido em Periferia/Inadimplência Zero) ---"
    )
    print(df_modificado.head())

    # =========================================================================
    # EXPORTAÇÃO DO NOVO ARQUIVO CSV
    # =========================================================================
    pasta_destino = os.path.dirname(caminho_csv)
    caminho_saida = os.path.join(
        pasta_destino, "dados_credito_corrigido.csv"
    )
    df_modificado.to_csv(caminho_saida, index=False)
    print(f"\n[SUCESSO] Novo arquivo modificado salvo em: {caminho_saida}")

    # =========================================================================
    # VISUALIZAÇÃO COMPARATIVA DOS DADOS
    # =========================================================================
    gerar_grafico_comparativo(df, df_modificado)


def gerar_grafico_comparativo(df_original, df_modificado):
    """Gera um gráfico comparativo antes e depois da modificação."""
    taxa_orig = (
        df_original.groupby("cep_regiao")["credito_aprovado"]
        .mean()
        .reset_index()
    )
    taxa_orig["Status"] = "Original (Com Viés)"

    taxa_mod = (
        df_modificado.groupby("cep_regiao")["credito_aprovado"]
        .mean()
        .reset_index()
    )
    taxa_mod["Status"] = "Modificado (Fairness Aplicado)"

    df_comparativo = pd.concat([taxa_orig, taxa_mod])
    df_comparativo["Taxa (%)"] = df_comparativo["credito_aprovado"] * 100

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(9, 5))

    ax = sns.barplot(
        data=df_comparativo,
        x="cep_regiao",
        y="Taxa (%)",
        hue="Status",
        palette="Set2",
    )

    plt.title(
        "Impacto da Modificação no Dataset: Taxa de Aprovação por Região",
        fontsize=12,
        fontweight="bold",
    )
    plt.xlabel("Região", fontsize=10)
    plt.ylabel("Taxa de Aprovação (%)", fontsize=10)
    plt.ylim(0, 110)

    plt.tight_layout()
    plt.show()


# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    caminho_selecionado = selecionar_arquivo()

    if caminho_selecionado:
        processar_e_modificar_dataset(caminho_selecionado)
    else:
        print("\n[AVISO] Nenhum arquivo foi selecionado. Operação cancelada.")