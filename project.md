# Projeto: Sistema de Recomendação de Produtos Agrícolos do DF

## 1. Objetivo do Projeto

O objetivo central deste projeto é desenvolver um sistema de recomendação para conectar consumidores a associações e cooperativas de produtores rurais no Distrito Federal. O sistema visa facilitar a busca e descoberta de produtos locais com base nas preferências do usuário, como localização, produtos específicos, características nutricionais e outros critérios relevantes.

## 2. Ferramentas Utilizadas (Bibliotecas Python)

Para a construção do sistema, foram utilizadas as seguintes bibliotecas principais:

* **Pandas:** Para manipulação e organização dos dados em formato de tabelas (DataFrames).
* **NumPy:** Para operações numéricas e trabalho com arrays.
* **Geopy:** Para calcular distâncias geográficas precisas (geodésicas) entre coordenadas.
* **Folium:** Para a criação de mapas interativos para visualização das recomendações.

## 3. Fontes e Preparação dos Dados

A base do sistema é construída a partir de diferentes fontes de dados foram processadas e integradas:

### 3.1. Associações e Cooperativas (Localização e Produtos)

* **Coleta de Dados:** As informações sobre as 17 associações/cooperativas (nome, coordenadas de latitude e longitude, e produtos oferecidos) foram levantadas manualmente. As coordenadas foram obtidas via Google Maps, CNPJ ou outras fontes online (ex: redes sociais). Para associações com múltiplos locais, uma única coordenada foi assumida. A lista de produtos que cada uma comercializa foi extraída de fontes como editais do GDF, resultando no arquivo `associacao_vende.txt`.
* **Estruturação:** Esses dados foram organizados em um DataFrame, incluindo um ID para cada associação, nome, latitude, longitude, uma lista padronizada de produtos, uma avaliação média simulada (para fins de exemplo) e uma indicação se o foco principal é em produtos orgânicos.
* **Padronização (`produtos_escopo`, `mapeamento_produtos`):** Foi definida uma lista (`produtos_escopo`) com todos os produtos considerados pelo sistema. Um dicionário de mapeamento (`mapeamento_produtos`) foi usado para padronizar diferentes nomes de um mesmo produto (ex: "Limão Tahiti" para "Limão").

### 3.2. Informações Nutricionais (TACO)

* **Coleta de Dados:** Os dados nutricionais (calorias, vitaminas, fibras, etc.) foram extraídos da Tabela Brasileira de Composição de Alimentos (TACO). Para alimentos não presentes na TACO (como Abóbora Cabotiá, Coentro, Hortelã, Limão Tahiti, Repolho Verde), as informações foram complementadas manualmente com base em pesquisas em tabelas do IBGE ou equivalentes.
* **Utilização:** Estes dados permitem que o sistema filtre ou classifique produtos com base em critérios nutricionais definidos pelo usuário. Foram calculados scores normalizados para alguns nutrientes (ex: `score_vitamina_c`, `score_baixa_caloria`) para facilitar comparações.

### 3.3. Dados de Produção Regional (EMATER-DF)

* **Coleta de Dados:** Informações sobre a produção agrícola por região administrativa do DF (área plantada, volume de produção por cultura) foram estruturadas.
* **Utilização:** A partir desses dados, foi calculada a `relevancia_regiao_percent` para cada produto em cada região. Este indicador mostra a participação percentual da produção de uma região em relação ao total do DF para um item específico. Ele é usado como um critério de "qualidade" ou especialização produtiva da região.

## 4. Base para Recomendações Colaborativas: Matriz de Utilidade

Para implementar a filtragem colaborativa, que sugere itens com base no comportamento de outros usuários, foi criada uma matriz de utilidade.

### 4.1. Criação e Propósito da Matriz

* A matriz de utilidade representa as interações (neste caso, avaliações simuladas) entre "consumidores" (usuários) e "itens" (associações/cooperativas).

### 4.2. Simulação das Avaliações

* **Motivação:** Devido à ausência de um histórico real de avaliações e ao requisito do projeto de ter uma matriz com pelo menos 5.000 linhas (interações), as avaliações foram geradas artificialmente.
* **Processo:** Um número definido de `consumidores_simulados` foi criado. Cada um "avaliou" um subconjunto aleatório de associações com notas de 1 a 5. A simulação atribuiu notas com uma leve tendência a seguir a `avaliacao_media` pré-existente (e também simulada) da associação, adicionando também um componente de aleatoriedade para variar as opiniões. O resultado é o DataFrame `df_utility_pivot`.

## 5. Componente Central: A Classe `SistemaRecomendacaoDF`

Esta classe Python encapsula toda a lógica de processamento e geração de recomendações.

### 5.1. Inicialização e Matriz de Similaridade Item-Item

* Ao ser instanciada, a classe recebe todos os DataFrames preparados (associações, nutrientes, produção EMATER, matriz de utilidade).
* Um passo crucial na inicialização é o cálculo da `item_similarity_df`. Esta matriz de similaridade item-item é gerada aplicando a `cosine_similarity` à transposta da `utility_matrix_filled` (matriz de utilidade com NaNs preenchidos por 0). Ela indica o quão "similares" duas associações são, com base nos padrões de avaliação dos usuários.

### 5.2. Método Principal de Recomendação (`recomendar`)

* Este método é o motor que gera as sugestões personalizadas.
    * **5.2.1. Entradas do Usuário (Localização, Preferências):** Recebe o `id_consumidor` (para a parte colaborativa), as coordenadas de `lat_usuario` e `lon_usuario`, e um dicionário de `preferencias` contendo os critérios de busca.
    * **5.2.2. Processo de Filtragem Inicial:** As associações são inicialmente filtradas por:
        * **Distância:** Apenas aquelas dentro da `distancia_max_km` especificada.
        * **Orgânicos:** Se `apenas_organicos` for `True`.
        * **Produtos:** Apenas aquelas que oferecem pelo menos um dos `produtos_desejados`.
    * **5.2.3. Cálculo de Scores para Ranking (Abordagem Híbrida):** Para as associações restantes, diversos sub-scores são calculados. O `score_final` é uma soma ponderada destes, refletindo uma abordagem híbrida:
        * **Score de Distância (`s_dist`):** Prioriza associações mais próximas ao usuário.
        * **Score de Avaliação da Associação (`s_aval`):** Considera a avaliação média da associação.
        * **Score Nutricional (`s_nutri`):** Avalia o quão bem os produtos da associação atendem ao `objetivo_nutricional` do usuário (ex: baixa caloria, alta vitamina C, etc., conforme item 6.5 da sua lista).
        * **Score de Relevância Produtiva Regional (`s_relev_prod`):** Bonifica associações em regiões com alta `relevancia_regiao_percent` para os produtos desejados (critério de "qualidade" regional, conforme item 6.5).
        * **Score Colaborativo Item-Item (`s_collab`):** Utiliza a `item_similarity_df` para encontrar associações similares àquelas que o `id_consumidor` já avaliou positivamente.
        * **Score Final Ponderado:** Cada sub-score é multiplicado por um peso (definido nas `preferencias`) e somados para obter o `score_final`, que ordena as recomendações.

## 6. Utilizando o Sistema: Personalizando as Buscas

A personalização das recomendações é feita através do dicionário `preferencias` passado ao método `recomendar`.

### 6.1. Definindo Localização do Usuário

* Altere as variáveis `user_lat_ex...` e `user_lon_ex...` no script de teste (Nova Célula 7 do Jupyter Notebook) com as coordenadas desejadas.

### 6.2. Especificando Produtos Desejados

* Modifique a lista `preferencias['produtos_desejados']` com os nomes dos produtos de interesse (ex: `['Morango', 'Alface']`). Os nomes devem corresponder aos definidos na lista `produtos_escopo`.

### 6.3. Ajustando Filtros (Distância Máxima, Orgânicos, etc.)

* `preferencias['distancia_max_km']`: Define o raio de busca em km.
* `preferencias['apenas_organicos']`: `True` para filtrar por orgânicos, `False` para não filtrar.

### 6.4. Objetivos Nutricionais

* `preferencias['objetivo_nutricional']`: Pode ser `'alta_vitamina_c'`, `'alta_fibra'`, `'baixa_caloria'`, ou `None`. O sistema considera as informações nutricionais dos alimentos (item 6.5 da sua lista) para este score.

### 6.5. Controlando a Importância dos Critérios (Pesos dos Scores)

* No dicionário `preferencias`, chaves como `peso_distancia`, `peso_avaliacao`, `peso_nutricional`, `peso_relevancia_prod`, `peso_colaborativo` permitem ajustar a importância relativa de cada fator no `score_final`. Alterar esses pesos permite calibrar o sistema para diferentes prioridades de recomendação.

## 7. Visualização dos Resultados: Mapa Interativo

A Nova Célula 8 (do Jupyter Notebook) utiliza a função `criar_mapa_recomendacoes_folium_v2` para gerar um mapa interativo:

* Exibe a localização do usuário e um círculo representando o raio de busca.
* Marca as associações recomendadas no mapa.
* Popups em cada marcador mostram detalhes da associação, incluindo o score final, distância, e os sub-scores que contribuíram para a recomendação.

## 8. Conclusão e Possíveis Próximos Passos

O sistema desenvolvido implementa uma abordagem híbrida para recomendação de produtos agrícolas, combinando características dos itens e preferências do usuário (baseada em conteúdo) com padrões de avaliação (colaborativa). Ele permite uma busca personalizada e geolocalizada por produtores no DF.

**Possíveis Próximos Passos e Melhorias:**

* **Coleta de Dados Reais:** Substituir os dados simulados (avaliações de usuários) por dados reais para aumentar a precisão.
* **Aprimoramento da Simulação:** Refinar a simulação da matriz de utilidade para gerar padrões mais complexos.
* **Mais Critérios de Filtragem/Score:** Incluir outros fatores como horários de funcionamento, tipos de entrega, etc.
* **Algoritmos de Machine Learning Avançados:**
    * Implementar técnicas como Fatoração de Matrizes (ex: SVD) para a filtragem colaborativa.
    * Treinar modelos de regressão para prever ratings baseados em conteúdo.
* **Interface de Usuário:** Desenvolver uma interface web ou mobile.
* **Sistema de Feedback:** Permitir que usuários reais avaliem associações e produtos.
* **Tratamento de "Cold Start":** Melhorar estratégias para novos usuários ou novas associações.