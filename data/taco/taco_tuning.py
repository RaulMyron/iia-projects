import pandas as pd

alimentos_desejados = [
    "Abóbora, cabotiá",
    "Abacate",
    "Abobrinha, italiana",
    "Acelga",
    "Alface, americana",
    "Alho",
    "Batata, doce",
    "Beterraba",
    "Brócolis",
    "Cebola",
    "Cebolinha",
    "Cenoura",
    "Chuchu",
    "Coentro",
    "Couve-flor",
    "Couve, manteiga",
    "Espinafre",
    "Goiaba",
    "Hortelã",
    "Inhame",
    "Limão, Taiti",
    "Manjericão",
    "Maracujá",
    "Milho verde",
    "Morango",
    "Pepino",
    "Pimentão, verde",
    "Repolho, verde",
    "Repolho, roxo",
    "Salsa",
    "Tangerina, Ponkan",
    "Tomate",
    "Vagem",
    "Banana, prata",
]

arquivo_entrada_csv = "taco_nutritional_data.csv"
arquivo_saida_csv = "valores_nutricionais_filtrados.csv"

coluna_alimento_identificada = None

try:
    try:
        df = pd.read_csv(arquivo_entrada_csv, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(arquivo_entrada_csv, encoding="latin1")

    possiveis_colunas_alimento = [
        "Alimento",
        "Descrição do Alimento",
        "description",
        "food_name",
        "Nome do Alimento",
        "Descricao Alimento",
    ]
    if len(df.columns) > 1:
        possiveis_colunas_alimento.append(df.columns[1])

    for col in possiveis_colunas_alimento:
        if col in df.columns:
            coluna_alimento_identificada = col
            break

    if coluna_alimento_identificada is None:
        print(
            f"Não foi possível encontrar automaticamente a coluna com os nomes dos alimentos."
        )
        print(f"Colunas disponíveis: {df.columns.tolist()}")
        exit()

    lista_dfs_filtrados = []
    alimentos_encontrados_nomes = set()

    for alimento_busca in alimentos_desejados:
        df_alimento_encontrado = df[
            df[coluna_alimento_identificada].str.contains(
                alimento_busca, case=False, na=False
            )
        ]

        if not df_alimento_encontrado.empty:
            lista_dfs_filtrados.append(df_alimento_encontrado)
            alimentos_encontrados_nomes.add(alimento_busca)

    if not lista_dfs_filtrados:
        print(
            f"Nenhum dos alimentos desejados foi encontrado na tabela '{arquivo_entrada_csv}'."
        )
        print(
            f"Primeiros exemplos de alimentos na coluna '{coluna_alimento_identificada}':"
        )
        print(df[coluna_alimento_identificada].head().to_list())
    else:
        df_final_filtrado = (
            pd.concat(lista_dfs_filtrados).drop_duplicates().reset_index(drop=True)
        )
        df_final_filtrado.to_csv(arquivo_saida_csv, index=False, encoding="utf-8-sig")

except FileNotFoundError:
    print(f"Erro: O arquivo de entrada '{arquivo_entrada_csv}' não foi encontrado.")
except pd.errors.EmptyDataError:
    print(
        f"Erro: O arquivo CSV de entrada '{arquivo_entrada_csv}' está vazio ou corrompido."
    )
except Exception as e:
    print(e)
    if (
        "df" in locals()
        and coluna_alimento_identificada
        and coluna_alimento_identificada not in df.columns
    ):
        print(f"A coluna '{coluna_alimento_identificada}' não existe no arquivo CSV.")
        print(f"Colunas disponíveis: {df.columns.tolist()}")
    elif "df" in locals():
        print(f"Colunas do seu CSV: {df.columns.tolist()}")
