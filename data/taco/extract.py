import pandas as pd

# 1. Lista original dos alimentos que você deseja encontrar (base para a busca)
alimentos_usuario_original = [
    "Abacate",
    "Abóbora Japonesa",
    "Abobrinha Italiana",
    "Acelga",
    "Alface Americana",
    "Alho",
    "Batata Doce",
    "Beterraba",
    "Brócolis",
    "Cebola",
    "Cebolinha Comum",
    "Cenoura",
    "Chuchu",
    "Coentro",
    "Couve-Flor",
    "Couve Manteiga",
    "Espinafre",
    "Goiaba",
    "Hortelã",
    "Inhame",
    "Limão Tahiti",
    "Manjericão",
    "Maracujá",
    "Milho Verde",
    "Morango",
    "Pepino Comum",
    "Pimentão Verde",
    "Repolho Verde",
    "Repolho Roxo",
    "Salsa",
    "Tangerina Ponkan",
    "Tomate",
    "Vagem",
    "Banana Prata",
]

# 2. Dicionário para adaptar os nomes da sua lista para os termos de busca mais prováveis na TACO
#    Baseado no seu CSV e padrões comuns.
termos_busca_adaptados = {
    "Abacate": "Abacate",
    "Abóbora Japonesa": "Abóbora",  # Buscar genérico, depois filtrar por "crua"
    "Abobrinha Italiana": "Abobrinha, italiana",
    "Acelga": "Acelga",
    "Alface Americana": "Alface, americana",
    "Alho": "Alho",
    "Batata Doce": "Batata, doce",  # Seu CSV mostra "Batata, doce, crua"
    "Beterraba": "Beterraba",
    "Brócolis": "Brócolis",
    "Cebola": "Cebola",
    "Cebolinha Comum": "Cebolinha",
    "Cenoura": "Cenoura",
    "Chuchu": "Chuchu",
    "Coentro": "Coentro",  # Será filtrado para "crua"
    "Couve-Flor": "Couve-flor",
    "Couve Manteiga": "Couve, manteiga",
    "Espinafre": "Espinafre",  # Será filtrado para "crua"
    "Goiaba": "Goiaba",
    "Hortelã": "Hortelã",
    "Inhame": "Inhame",
    "Limão Tahiti": "Limão",  # Buscar genérico, depois filtrar por "crua" e "Taiti"
    "Manjericão": "Manjericão",
    "Maracujá": "Maracujá",
    "Milho Verde": "Milho, verde",  # Tentar encontrar "Milho, verde, cru"
    "Morango": "Morango",
    "Pepino Comum": "Pepino",
    "Pimentão Verde": "Pimentão, verde",
    "Repolho Verde": "Repolho, verde",
    "Repolho Roxo": "Repolho, roxo",
    "Salsa": "Salsa",
    "Tangerina Ponkan": "Tangerina",  # Buscar genérico, depois filtrar por "crua" e "Ponkan"
    "Tomate": "Tomate",
    "Vagem": "Vagem",
    "Banana Prata": "Banana, prata",
}

# Palavras-chave em descrições "cruas" que indicam processamento ou forma não primária
# Estas serão evitadas ao escolher a "melhor" opção crua, se uma alternativa mais simples existir.
palavras_chave_evitar_em_cru = [
    "polpa",
    "suco",
    "extrato",
    "salada",
    "doce",
    "pasta",
    "mistura",
    "curau",
    "biscoito",
    "iogurte",
    "queijo",
    "molho",
    "purê",
    "desidratada",
    "folhas desidratadas",
    "industrializado",
]


# Nomes dos arquivos
arquivo_entrada_csv = "taco_nutritional_data.csv"
arquivo_saida_csv = "valores_nutricionais_selecionados_crus.csv"

coluna_alimento_identificada = None
df_original = None

print(f"📝 Iniciando o processo de extração e seleção de dados nutricionais...")

try:
    # Carregar o arquivo CSV
    # Adicionado `decimal=','` por causa de valores como "83,8"
    # `header=0` assume que a primeira linha é o cabeçalho. Se seu CSV começa com 0,1,2,.. como header, está OK.
    # Se a primeira linha do seu arquivo for `0,1,2,3...` e essa for a linha de cabeçalho,
    # então os nomes das colunas serão '0', '1', '2', etc. (strings).
    # Se o arquivo não tiver cabeçalho e a primeira linha for dados, use `header=None`.
    try:
        df_original = pd.read_csv(arquivo_entrada_csv, encoding="utf-8", decimal=",")
    except UnicodeDecodeError:
        print(f"⚠️ Falha ao ler com UTF-8. Tentando com encoding 'latin1'...")
        df_original = pd.read_csv(arquivo_entrada_csv, encoding="latin1", decimal=",")

    print(f"✅ Arquivo '{arquivo_entrada_csv}' carregado com sucesso.")

    # Identificar a coluna de nome do alimento
    # O trecho do seu CSV sugere que a descrição do alimento está na segunda coluna.
    # Se a primeira linha do CSV for '0,1,2,...', o nome da segunda coluna será '1'.
    possiveis_colunas_alimento = [
        "1",
        df_original.columns[1] if len(df_original.columns) > 1 else None,
        "Alimento",
        "Descrição do Alimento",
        "description",
        "food_name",
    ]
    possiveis_colunas_alimento = [
        col for col in possiveis_colunas_alimento if col is not None
    ]  # Remover Nones

    for col_name in possiveis_colunas_alimento:
        if col_name in df_original.columns:
            # Verificar se a coluna parece conter descrições de texto longas
            if (
                df_original[col_name].dtype == "object"
                and df_original[col_name].str.len().mean() > 10
            ):
                coluna_alimento_identificada = col_name
                print(
                    f"🔍 Coluna de alimentos identificada como: '{coluna_alimento_identificada}'"
                )
                break

    if coluna_alimento_identificada is None:
        print(
            f"❌ Erro: Não foi possível encontrar automaticamente a coluna com os nomes dos alimentos."
        )
        print(f"   Colunas disponíveis: {df_original.columns.tolist()}")
        print(
            f"   Por favor, verifique se o arquivo CSV tem um cabeçalho adequado ou ajuste o script."
        )
        exit()

    resultados_finais_lista_df = []
    alimentos_encontrados_log = []

    print("\n🔎 Processando cada alimento da sua lista:")
    for alimento_original_usuario in alimentos_usuario_original:
        termo_busca = termos_busca_adaptados.get(
            alimento_original_usuario, alimento_original_usuario
        )
        print(f"  -----------------------------------------------------")
        print(
            f"  Buscando por: '{alimento_original_usuario}' (usando termo: '{termo_busca}')"
        )

        # Etapa 1: Filtrar pelo termo de busca adaptado
        df_alimento_base = df_original[
            df_original[coluna_alimento_identificada].str.contains(
                termo_busca, case=False, na=False
            )
        ]

        if df_alimento_base.empty:
            print(f"    ⚠️ Nenhuma correspondência inicial para '{termo_busca}'.")
            alimentos_encontrados_log.append(
                f"{alimento_original_usuario}: Não encontrado (sem correspondência inicial)"
            )
            continue

        # Etapa 2: Filtrar por "cru" ou "crua"
        df_cru = df_alimento_base[
            df_alimento_base[coluna_alimento_identificada].str.contains(
                ", crua", case=False, na=False
            )
            | df_alimento_base[coluna_alimento_identificada].str.contains(
                ", cru", case=False, na=False
            )
        ]

        if df_cru.empty:
            print(f"    ⚠️ Encontrado '{termo_busca}', mas nenhuma versão 'cru(a)'.")
            alimentos_encontrados_log.append(
                f"{alimento_original_usuario}: Não encontrado (sem versão crua)"
            )
            continue

        print(
            f"    ✔️ Encontradas {len(df_cru)} versão(ões) 'cru(a)' para '{termo_busca}'."
        )

        # Etapa 3: Selecionar a melhor opção "de mercado"
        candidatos_selecionados = []
        for index, row in df_cru.iterrows():
            descricao = row[coluna_alimento_identificada].lower()
            is_clean = True
            for palavra_evitar in palavras_chave_evitar_em_cru:
                if palavra_evitar in descricao:
                    is_clean = False
                    break

            # Lógica específica para termos genéricos que precisam de refinamento
            # (Ex: para "Limão" buscamos "Taiti"; para "Abóbora" buscamos "japonesa" ou "cabotiá")
            refinamento_ok = True
            if (
                alimento_original_usuario == "Limão Tahiti" and "taiti" not in descricao
            ):  # Seu CSV usa "Taiti"
                refinamento_ok = False
            if alimento_original_usuario == "Abóbora Japonesa" and not (
                "japonesa" in descricao
                or "cabotiá" in descricao
                or "kabocha" in descricao
            ):
                refinamento_ok = False
            if (
                alimento_original_usuario == "Tangerina Ponkan"
                and "ponkan" not in descricao
            ):  # Ou "poncã"
                if "poncã" not in descricao:  # Adicionando verificação para "poncã"
                    refinamento_ok = False

            if refinamento_ok:
                if is_clean:
                    candidatos_selecionados.append(
                        row.to_frame().T
                    )  # Adicionar como DataFrame de uma linha
                elif (
                    not candidatos_selecionados
                ):  # Se não houver limpos ainda, adicionar o primeiro "não tão limpo" como fallback
                    candidatos_selecionados.append(row.to_frame().T)

        if candidatos_selecionados:
            # Se houver "limpos", priorizar o primeiro deles.
            # Se não, já teremos o primeiro "não tão limpo" como fallback.
            df_escolhido = candidatos_selecionados[
                0
            ]  # Pegar o primeiro da lista de candidatos (prioriza os "clean")

            descricao_escolhida = df_escolhido[coluna_alimento_identificada].iloc[0]
            print(f"    ➡️ Opção 'cru(a)' selecionada: \"{descricao_escolhida}\"")
            resultados_finais_lista_df.append(df_escolhido)
            alimentos_encontrados_log.append(
                f'{alimento_original_usuario}: Encontrado ("{descricao_escolhida}")'
            )
        else:
            print(
                f"    ⚠️ Nenhuma versão 'cru(a)' atendeu aos critérios de refinamento para '{alimento_original_usuario}'."
            )
            alimentos_encontrados_log.append(
                f"{alimento_original_usuario}: Não encontrado (não atendeu refinamento cru)"
            )

    if not resultados_finais_lista_df:
        print(f"\n❌ Nenhum alimento foi selecionado após todos os filtros.")
    else:
        df_final_selecionado = (
            pd.concat(resultados_finais_lista_df)
            .drop_duplicates()
            .reset_index(drop=True)
        )
        df_final_selecionado.to_csv(
            arquivo_saida_csv, index=False, encoding="utf-8-sig"
        )
        print(
            f"\n🎉 Sucesso! Os dados nutricionais para os alimentos selecionados foram salvos em '{arquivo_saida_csv}'."
        )
        print(
            f"   Total de {len(df_final_selecionado)} linhas de dados finais extraídas."
        )

    print("\n📋 Resumo do Processamento:")
    for log_entry in alimentos_encontrados_log:
        print(f"   {log_entry}")

except FileNotFoundError:
    print(f"❌ Erro: O arquivo de entrada '{arquivo_entrada_csv}' não foi encontrado.")
except pd.errors.EmptyDataError:
    print(
        f"❌ Erro: O arquivo CSV de entrada '{arquivo_entrada_csv}' está vazio ou corrompido."
    )
except Exception as e:
    print(f"❌ Ocorreu um erro inesperado durante a execução do script:")
    print(e)
    if (
        df_original is not None
        and coluna_alimento_identificada
        and coluna_alimento_identificada not in df_original.columns
    ):
        print(
            f"   A coluna '{coluna_alimento_identificada}' (identificada ou definida) não existe no arquivo CSV."
        )
        print(f"   Colunas disponíveis: {df_original.columns.tolist()}")
    elif df_original is not None:
        print(f"   Verifique as colunas do seu CSV: {df_original.columns.tolist()}")
