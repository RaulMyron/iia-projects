# Projeto: Sistema de Recomendação de Produtos Agrícolas do DF

## 1. Objetivo do Projeto

O objetivo central deste projeto é desenvolver um sistema de recomendação para conectar consumidores a associações e cooperativas de produtores rurais no Distrito Federal. O sistema visa facilitar a busca e descoberta de produtos locais com base nas preferências do usuário, como localização, produtos específicos, características nutricionais e outros critérios relevantes.

## 2. Ferramentas Utilizadas (Bibliotecas Python)

Para a construção do sistema, foram utilizadas as seguintes bibliotecas principais:

* **Pandas:** Para manipulação e organização dos dados em formato de tabelas (DataFrames).
* **NumPy:** Para operações numéricas e trabalho com arrays.
* **Geopy:** Para calcular distâncias geográficas precisas (geodésicas) entre coordenadas.
* **Folium:** Para a criação de mapas interativos para visualização das recomendações.
* **Scikit-learn:** Especificamente `cosine_similarity` para o cálculo de similaridade na filtragem colaborativa.

## 3. Fontes e Preparação dos Dados

A base do sistema é construída a partir de diferentes fontes de dados que foram processadas e integradas:

### 3.1. Associações e Cooperativas (Localização e Produtos)

* **Coleta de Dados:** As informações sobre 17 associações/cooperativas (nome, coordenadas de latitude e longitude, e produtos oferecidos) foram levantadas manualmente. As coordenadas foram obtidas via Google Maps, CNPJ ou outras fontes online. A lista de produtos que cada uma comercializa foi extraída de fontes como editais do GDF.
* **Estruturação:** Esses dados foram organizados em um DataFrame (`df_associacoes`), incluindo um ID para cada associação, nome, latitude, longitude, uma lista padronizada de produtos (`produtos`), uma indicação se o foco principal é em produtos orgânicos (`organico_principal`), e uma avaliação média simulada (`avaliacao_media`).
* **Padronização (`produtos_escopo`, `mapeamento_produtos`):** Foi definida uma lista (`produtos_escopo`) com todos os produtos considerados pelo sistema. Um dicionário de mapeamento (`mapeamento_produtos`) foi usado para padronizar diferentes nomes de um mesmo produto (ex: "Limão Tahiti" para "Limão").

### 3.2. Informações Nutricionais (TACO)

* **Coleta de Dados:** Os dados nutricionais (calorias, vitaminas, fibras, etc.) foram extraídos da Tabela Brasileira de Composição de Alimentos (TACO) e complementados manualmente quando necessário.
* **Estruturação:** Organizados no DataFrame `df_nutrientes`.
* **Utilização:** Estes dados permitem que o sistema filtre ou classifique produtos com base em critérios nutricionais. Foram calculados scores normalizados para alguns nutrientes (ex: `score_vitamina_c`, `score_fibras`, `score_baixa_caloria`) para facilitar comparações.

### 3.3. Dados de Produção Regional (EMATER-DF)

* **Coleta de Dados:** Informações sobre a produção agrícola por região administrativa do DF (área plantada, volume de produção por cultura) foram estruturadas.
* **Estruturação:** Organizados no DataFrame `df_producao`.
* **Utilização:** A partir desses dados, foi calculada a `relevancia_regiao_percent` para cada produto em cada região. Este indicador mostra a participação percentual da produção de uma região em relação ao total do DF para um item específico e é usado como um critério de "qualidade" ou especialização produtiva da região.

## 4. Base para Recomendações Colaborativas: Matriz de Utilidade

Para implementar a filtragem colaborativa, que sugere itens com base no comportamento de outros usuários, foi criada uma matriz de utilidade.

### 4.1. Criação e Propósito da Matriz

* A matriz de utilidade (`df_utility_pivot`) representa as interações (neste caso, avaliações simuladas) entre "consumidores" (usuários) e "itens" (associações/cooperativas). O índice são os IDs dos consumidores, as colunas são os IDs das associações, e os valores são as avaliações.

### 4.2. Simulação das Avaliações

* **Motivação:** Devido à ausência de um histórico real de avaliações e ao objetivo de ter um volume significativo de interações (o projeto original visava pelo menos 5.000 avaliações no formato longo), as avaliações foram geradas artificialmente.
* **Processo:** Um número definido de `consumidores_simulados` (ex: 500) foi criado. Cada um "avaliou" um subconjunto aleatório de associações com notas de 1 a 5. A simulação atribuiu notas com uma leve tendência a seguir a `avaliacao_media` pré-existente (e também simulada) da associação, adicionando também um componente de aleatoriedade.

## 5. Componente Central: A Classe `SistemaRecomendacaoDF`

Esta classe Python encapsula toda a lógica de processamento e geração de recomendações híbridas.

### 5.1. Inicialização (`__init__`)

O construtor da classe prepara o sistema para fazer recomendações.

**Parâmetros de Entrada:**

* `df_associacoes` (pd.DataFrame): DataFrame contendo os dados das associações.
* `df_nutrientes` (pd.DataFrame): DataFrame com informações nutricionais dos produtos.
* `df_producao` (pd.DataFrame): DataFrame com dados de produção regional.
* `df_utility_pivot` (pd.DataFrame): Matriz de utilidade pivotada.

**Principais Ações na Inicialização:**

1.  **Armazenamento dos Dados**: Os DataFrames de entrada são copiados e armazenados como atributos da instância.
2.  **Preenchimento da Matriz de Utilidade**: `self.utility_matrix_filled` é criada a partir de `self.df_utility_pivot`, onde os valores `NaN` (avaliações ausentes) são preenchidos com `0`.
3.  **Cálculo da Matriz de Similaridade Item-Item (`self.item_similarity_df`)**:
    * Se a `self.utility_matrix_filled` não estiver vazia e tiver mais de um item (associação), uma matriz de similaridade entre os itens é calculada usando a similaridade do cosseno (`cosine_similarity`) sobre a transposta da `self.utility_matrix_filled`.
    * Esta matriz armazena o quão similar cada par de associações é, com base nos padrões de avaliação dos usuários.

### 5.2. Métodos Auxiliares (Privados)

* **`_calcular_distancia_km(self, lat1, lon1, lat2, lon2)`**: Calcula a distância geodésica (em km) entre dois pares de coordenadas.
* **`_get_item_collab_score(self, id_consumidor, id_item_candidato)`**: Calcula um score de filtragem colaborativa item-item. Ele considera os itens que o `id_consumidor` avaliou bem no passado e a similaridade do `id_item_candidato` com esses itens bem avaliados.

### 5.3. Método Principal de Recomendação (`recomendar`)

Este método gera a lista de associações recomendadas.

**Parâmetros de Entrada:**

* `id_consumidor` (str): ID do consumidor.
* `lat_usuario` (float): Latitude da localização do usuário.
* `lon_usuario` (float): Longitude da localização do usuário.
* `preferencias` (dict): Dicionário com as preferências do usuário (detalhado na Seção 6).

**Principais Passos do Processo:**

1.  **Cálculo de Distância Inicial**: A distância entre o usuário e todas as associações é calculada.
2.  **Filtragem Inicial**: As associações são filtradas com base em:
    * `distancia_max_km` (definida nas `preferencias`).
    * `apenas_organicos` (definida nas `preferencias`).
    * `produtos_desejados` (definida nas `preferencias`).
3.  **Cálculo de Sub-Scores**: Para as associações candidatas restantes, são calculados os seguintes scores (normalizados):
    * **`s_dist` (Score de Distância)**: Prioriza associações mais próximas.
    * **`s_aval` (Score de Avaliação)**: Baseado na `avaliacao_media` da associação.
    * **`s_nutri` (Score Nutricional)**: Avalia o quão bem os produtos da associação atendem ao `objetivo_nutricional` especificado, para os `produtos_desejados`.
    * **`s_relev_prod` (Score de Relevância Produtiva Regional)**: Considera a importância da região da associação na produção dos `produtos_desejados`.
    * **`s_collab` (Score Colaborativo Item-Item)**: Score derivado do método `_get_item_collab_score`, usando a `item_similarity_df`.
4.  **Cálculo do `score_final`**: É uma soma ponderada dos sub-scores. Os pesos para cada sub-score são definidos no dicionário `preferencias`.
5.  **Ranking e Seleção**: As associações são ordenadas pelo `score_final`, e as `top_n` melhores (definido em `preferencias`) são retornadas.

**Retorno:**

* Um DataFrame Pandas (`rec_finais`) com as associações recomendadas e colunas detalhando os scores.

## 6. Utilizando o Sistema: Personalizando as Buscas

A personalização das recomendações é feita através do dicionário `preferencias` passado ao método `recomendar` da classe `SistemaRecomendacaoDF`.

### 6.1. Detalhes dos Parâmetros de Preferência do Usuário (`user_preferences`)

O dicionário `user_preferences` customiza a busca. Aqui estão os parâmetros aceitos:

* **`'produtos_desejados'`**:
    * **Descrição**: Lista dos produtos específicos que o consumidor deseja encontrar.
    * **Tipo**: `List[str]` (Lista de strings)
    * **Valores Possíveis**: Cada string deve ser um nome de produto como definido na lista `produtos_escopo`.
    * **Exemplos**: `['Alface', 'Tomate']`, `['Morango']`, `[]` (sem filtro de produto).
    * **Comportamento**: Busca associações com ao menos um dos produtos.

* **`'max_distance_km'`**:
    * **Descrição**: Raio máximo de busca em km.
    * **Tipo**: `int` ou `float`
    * **Valores**: Número positivo (ex: `10`, `25.5`).
    * **Padrão (se não fornecido)**: `30`.

* **`'apenas_organicos'`**: (No seu código original, a chave nas `preferencias` era `apenas_organicos`)
    * **Descrição**: Restringir a associações com foco principal em orgânicos.
    * **Tipo**: `bool`
    * **Valores**: `True` (somente orgânicos) ou `False` (todas).
    * **Padrão (se não fornecido)**: `False`.

* **`'objetivo_nutricional'`**:
    * **Descrição**: Objetivo nutricional principal.
    * **Tipo**: `str` ou `None`
    * **Valores**: `'alta_vitamina_c'`, `'alta_fibra'`, `'baixa_caloria'`, ou `None`.

* **`'top_n'`**:
    * **Descrição**: Número máximo de recomendações a retornar.
    * **Tipo**: `int`
    * **Valores**: Inteiro positivo (ex: `3`, `5`).
    * **Padrão (se não fornecido)**: `5`.

* **`'considerar_relevancia_produtiva_regiao'`**:
    * **Descrição**: Considerar a relevância produtiva da região.
    * **Tipo**: `bool`
    * **Valores**: `True` (considerar) ou `False` (não considerar).
    * **Padrão (se não fornecido)**: `True`.

* **Pesos dos Scores (tipo `float` ou `int`, geralmente não negativos)**:
    Controlam a importância de cada fator no `score_final`.