import camelot
import pandas as pd
import re
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

CULTURAS_ALVO_PROJETO = [
    "Alface", "Mandioca", "Tomate", "Repolho", "Batata", "Cebola", "Couve", "Chuchu",
    "Morango", "Pimentão", "Brócolis", "Abóbora", "Berinjela", "Beterraba", "Pepino",
    "Cenoura", "Quiabo", "Agrião", "Jiló", "Gengibre", "Abacate", "Goiaba", "Banana",
    "Limão", "Tangerina", "Maracujá", "Manga", "Lichia", "Uva", "Atemóia", "Cajamanga",
    "Graviola", "Coco", "Pitaia", "Mamão",
]

CULTURA_MAP = {
    "TOMATE (MESA)": "Tomate", "BATATA (INGLESA)": "Batata", "COUVE (MANTEIGA)": "Couve",
    "ALFACE (AMERICANA)": "Alface", "ALFACE (CRESPA)": "Alface", "PIMENTÃO (VERDE)": "Pimentão",
    "PIMENTÃO (VERMELHO)": "Pimentão", "PIMENTÃO (AMARELO)": "Pimentão", "ABÓBORA (JAPONESA)": "Abóbora",
    "ABÓBORA (MENINA)": "Abóbora", "ABÓBORA (MORANGA)": "Abóbora", "BANANA NANICA": "Banana",
    "BANANA PRATA": "Banana", "BANANA MAÇÃ": "Banana", "BANANA DA TERRA": "Banana",
    "GOIABA VERMELHA": "Goiaba", "GOIABA BRANCA": "Goiaba", "MARACUJÁ AZEDO": "Maracujá",
    "MARACUJÁ DOCE": "Maracujá", "MANGA TOMMY": "Manga", "MANGA PALMER": "Manga",
    "MANGA HADEN": "Manga", "MANGA ESPADA": "Manga", "LIMÃO TAHITI": "Limão",
    "LIMÃO (TAHITI)": "Limão", "TANGERINA PONKAN": "Tangerina", "TANGERINA (PONKAN)": "Tangerina",
}

ESCRITORIOS_EMATER_DF = sorted([
    "ALEXANDRE GUSMÃO", "BRAZLÂNDIA", "CEILÂNDIA", "GAMA", "JARDIM", "PAD-DF", "PARANOÁ",
    "PIPIRIPAU", "PLANALTINA", "RIO PRETO", "SÃO SEBASTIÃO", "SOBRADINHO", "TABATINGA",
    "TAQUARA", "VARGEM BONITA", "DISTRITO FEDERAL",
])

def limpar_valor(valor):
    """Converte string de valor para float, tratando formatos brasileiros."""
    if valor is None or str(valor).strip() in ("", "-"):
        return 0.0
    s = str(valor).replace(".", "").replace(",", ".").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0

def normalizar_nome_cultura(nome):
    """Normaliza e mapeia o nome da cultura para o padrão do projeto."""
    nome = nome.upper().strip()
    nome = CULTURA_MAP.get(nome, nome)
    nome = re.sub(r"\s*\(.*\)", "", nome).strip().capitalize()
    return nome

def processar_tabelas_emater(pdf_path, paginas_str, tipo_dados):
    """Extrai dados das tabelas da EMATER-DF para Olericultura ou Fruticultura."""
    dados_secao = {esc: {} for esc in ESCRITORIOS_EMATER_DF if esc != "DISTRITO FEDERAL"}
    dados_secao["TOTAL_DF"] = {}
    try:
        tables = camelot.read_pdf(pdf_path, pages=paginas_str, flavor="lattice", line_scale=30, strip_text="\n")
    except Exception as e:
        logging.warning(f"Erro ao ler PDF (lattice): {e}. Tentando 'stream'.")
        try:
            tables = camelot.read_pdf(pdf_path, pages=paginas_str, flavor="stream", edge_tol=500, row_tol=10)
        except Exception as e2:
            logging.error(f"Erro ao ler PDF (stream): {e2}")
            return dados_secao

    escritorio_atual = None
    for table in tables:
        df = table.df
        for _, row in df.iterrows():
            primeira_coluna = str(row.iloc[0]).strip().upper()
            if primeira_coluna in ESCRITORIOS_EMATER_DF:
                escritorio_atual = primeira_coluna
                continue
            if not escritorio_atual:
                continue
            nome_cultura = row.iloc[0] or row.iloc[1] if len(row) > 1 else ""
            nome_cultura = normalizar_nome_cultura(str(nome_cultura))
            if nome_cultura not in CULTURAS_ALVO_PROJETO:
                continue
            if len(row) > 5:
                area_ha = limpar_valor(row.iloc[3])
                producao_t = limpar_valor(row.iloc[5])
                destino = dados_secao["TOTAL_DF"] if escritorio_atual == "DISTRITO FEDERAL" else dados_secao[escritorio_atual]
                if nome_cultura not in destino:
                    destino[nome_cultura] = {"producao_t": 0.0, "area_ha": 0.0}
                destino[nome_cultura]["producao_t"] += producao_t
                destino[nome_cultura]["area_ha"] += area_ha
    return dados_secao

def combinar_dados(*secoes):
    """Combina os dados de várias seções em um único dicionário."""
    emater_data_final = {esc: {} for esc in ESCRITORIOS_EMATER_DF if esc != "DISTRITO FEDERAL"}
    emater_data_final["TOTAL_DF"] = {}
    for secao in secoes:
        for esc, culturas in secao.items():
            if esc not in emater_data_final:
                emater_data_final[esc] = {}
            for cultura, valores in culturas.items():
                if cultura not in emater_data_final[esc]:
                    emater_data_final[esc][cultura] = {"producao_t": 0.0, "area_ha": 0.0}
                emater_data_final[esc][cultura]["producao_t"] += valores["producao_t"]
                emater_data_final[esc][cultura]["area_ha"] += valores["area_ha"]
    return {k: v for k, v in emater_data_final.items() if v or k == "TOTAL_DF"}

def exportar_para_csv(emater_data_final, filename="emater_data_final.csv"):
    """Exporta os dados combinados para um arquivo CSV."""
    registros = []
    for esc, culturas in emater_data_final.items():
        for cultura, valores in culturas.items():
            registros.append({
                "escritorio": esc,
                "cultura": cultura,
                "area_ha": valores["area_ha"],
                "producao_t": valores["producao_t"],
            })
    df = pd.DataFrame(registros).sort_values(by=["escritorio", "cultura"])
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    logging.info(f"Arquivo '{filename}' salvo com sucesso!")
    return df

if __name__ == "__main__":
    pdf_path = "2024_Relatorio_Informacoes_Agropecuaria_RIA____DF.pdf"
    dados_olericultura = processar_tabelas_emater(pdf_path, "8-9", "Olericultura")
    dados_fruticultura = processar_tabelas_emater(pdf_path, "11-13", "Fruticultura")
    emater_data_final = combinar_dados(dados_olericultura, dados_fruticultura)
    df_final = exportar_para_csv(emater_data_final)
    print(df_final.head(20).to_string(index=False))
    print("\n--- Culturas em Brazlândia ---")
    print(df_final[df_final["escritorio"].str.upper() == "BRAZLÂNDIA"].to_string(index=False))
    tomate_total_df = df_final[(df_final["escritorio"] == "TOTAL_DF") & (df_final["cultura"] == "Tomate")]
    if not tomate_total_df.empty:
        print("\nTomate no TOTAL_DF:", tomate_total_df.to_string(index=False))
    else:
        print("\nDados de Tomate no TOTAL_DF não encontrados.")
