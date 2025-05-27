#!/usr/bin/env python
# coding: utf-8

# 
# Sistema de Recomendação de Produtos Agrícolas do DF
# Projeto 1 - Introdução à Inteligência Artificial
# Professor Díbio - UnB 2025/1
# 
# Raul Myron Silva Amorim - 200049712
# Lucca Santos Aguilar - 241024221
# Thais Aragão Bianchini - 
# 
# Este notebook implementa um sistema de recomendação para
# pequenos produtores rurais a consumidores no Distrito Federal.
# 

# In[2]:


import pandas as pd
import numpy as np
from geopy.distance import geodesic
import folium
import json
from datetime import datetime
import random
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
import warnings
warnings.filterwarnings('ignore')


# In[3]:


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# In[4]:


"""
Dados extraídos manualmente dos documentos fornecidos:
- 17 Associações/Cooperativas com coordenadas geográficas
- Produtos oferecidos por cada uma (baseado nos editais do GDF)
- Regiões de atuação no DF
"""

# Lista completa de produtos do escopo do projeto
produtos_escopo = [
    'Alface', 'Mandioca', 'Tomate', 'Repolho', 'Batata', 'Cebola', 'Couve',
    'Chuchu', 'Morango', 'Pimentão', 'Brócolis', 'Abóbora', 'Berinjela',
    'Beterraba', 'Pepino', 'Cenoura', 'Quiabo', 'Agrião', 'Jiló', 'Gengibre',
    'Abacate', 'Goiaba', 'Banana', 'Limão', 'Tangerina', 'Maracujá', 'Manga',
    'Lichia', 'Uva', 'Atemóia', 'Cajamanga', 'Graviola', 'Coco', 'Pitaia', 'Mamão'
]

# Mapeamento entre nomes dos produtos nos documentos e produtos do escopo
mapeamento_produtos = {
    'Abóbora Japonesa': 'Abóbora',
    'Abobrinha Italiana': 'Abóbora',
    'Acelga': 'Couve',
    'Alface Americana': 'Alface',
    'Cebolinha Comum': 'Cebola',
    'Coentro': 'Couve',
    'Couve-Flor': 'Brócolis',
    'Couve Manteiga': 'Couve',
    'Espinafre': 'Couve',
    'Hortelã': 'Agrião',
    'Manjericão': 'Agrião',
    'Pepino Comum': 'Pepino',
    'Pimentão Verde': 'Pimentão',
    'Repolho Verde': 'Repolho',
    'Repolho Roxo': 'Repolho',
    'Salsa': 'Agrião',
    'Batata Doce': 'Batata',
    'Brócolis Cabeça Única (Japonês)': 'Brócolis',
    'Inhame': 'Batata',
    'Limão Tahiti': 'Limão',
    'Milho Verde': 'Pepino',
    'Tangerina Ponkan': 'Tangerina',
    'Vagem': 'Pepino',
    'Banana Prata': 'Banana',
    'Alho': 'Cebola'
}

# Dados das 17 associações/cooperativas
associacoes_data = [
    {
        'id': 1,
        'nome': 'AFECA - Assentamento 15 de Agosto',
        'latitude': -15.911319,
        'longitude': -47.721311,
        'regioes': ['São Sebastião'],
        'produtos_originais': ['Abóbora Japonesa', 'Abobrinha Italiana', 'Acelga', 'Alface Americana', 
                              'Cebolinha Comum', 'Chuchu', 'Coentro', 'Couve-Flor', 'Couve Manteiga', 
                              'Espinafre', 'Hortelã', 'Manjericão', 'Maracujá', 'Pepino Comum', 
                              'Pimentão Verde', 'Repolho Verde', 'Repolho Roxo', 'Salsa', 'Tomate']
    },
    {
        'id': 2,
        'nome': 'AGRIFAM - Agricultura Familiar DF',
        'latitude': -15.932992,
        'longitude': -48.040909,
        'regioes': ['Taguatinga', 'Gama', 'Santa Maria'],
        'produtos_originais': ['Abacate', 'Abóbora Japonesa', 'Abobrinha Italiana', 'Acelga', 
                              'Alface Americana', 'Alho', 'Batata Doce', 'Beterraba', 
                              'Brócolis Cabeça Única (Japonês)', 'Cebola', 'Cebolinha Comum', 
                              'Cenoura', 'Chuchu', 'Coentro', 'Couve-Flor', 'Couve Manteiga', 
                              'Espinafre', 'Goiaba', 'Hortelã', 'Inhame', 'Limão Tahiti', 
                              'Manjericão', 'Maracujá', 'Milho Verde', 'Pepino Comum', 
                              'Pimentão Verde', 'Repolho Verde', 'Repolho Roxo', 'Salsa', 
                              'Tangerina Ponkan', 'Tomate', 'Vagem', 'Banana Prata']
    },
    {
        'id': 3,
        'nome': 'AMISTA - Agricultores Orgânicos',
        'latitude': -15.782057,
        'longitude': -47.470923,
        'regioes': ['Santa Maria'],
        'produtos_originais': ['Abacate', 'Abóbora Japonesa', 'Abobrinha Italiana', 'Batata Doce', 
                              'Beterraba', 'Brócolis Cabeça Única (Japonês)', 'Cebolinha Comum', 
                              'Cenoura', 'Chuchu', 'Coentro', 'Couve-Flor', 'Couve Manteiga', 
                              'Inhame', 'Limão Tahiti', 'Maracujá', 'Pepino Comum', 'Pimentão Verde', 
                              'Repolho Verde', 'Repolho Roxo', 'Salsa', 'Tomate', 'Vagem']
    },
    {
        'id': 4,
        'nome': 'ASPAF - Produtores Agricultura Familiar',
        'latitude': -15.940404,
        'longitude': -47.737964,
        'regioes': ['Guará', 'Núcleo Bandeirante', 'Plano Piloto'],
        'produtos_originais': ['Goiaba', 'Morango', 'Tangerina Ponkan', 'Abacate', 'Abóbora Japonesa', 
                              'Abobrinha Italiana', 'Acelga', 'Alface Americana', 'Batata Doce', 
                              'Beterraba', 'Brócolis Cabeça Única (Japonês)', 'Cebola', 
                              'Cebolinha Comum', 'Cenoura', 'Chuchu', 'Coentro', 'Couve-Flor', 
                              'Couve Manteiga', 'Espinafre', 'Hortelã', 'Inhame', 'Limão Tahiti', 
                              'Manjericão', 'Maracujá', 'Milho Verde', 'Pepino Comum', 
                              'Pimentão Verde', 'Repolho Verde', 'Repolho Roxo', 'Salsa', 
                              'Tomate', 'Vagem', 'Banana Prata']
    },
    {
        'id': 5,
        'nome': 'ASPAG - Alexandre Gusmão',
        'latitude': -15.726869,
        'longitude': -48.189019,
        'regioes': ['Alexandre Gusmão', 'Brazlândia'],
        'produtos_originais': ['Abacate', 'Abóbora Japonesa', 'Abobrinha Italiana', 'Acelga', 
                              'Alface Americana', 'Batata Doce', 'Beterraba', 
                              'Brócolis Cabeça Única (Japonês)', 'Cebolinha Comum', 'Cenoura', 
                              'Chuchu', 'Coentro', 'Couve-Flor', 'Couve Manteiga', 'Espinafre', 
                              'Goiaba', 'Hortelã', 'Inhame', 'Limão Tahiti', 'Manjericão', 
                              'Maracujá', 'Milho Verde', 'Pepino Comum', 'Pimentão Verde', 
                              'Repolho Verde', 'Repolho Roxo', 'Salsa', 'Tangerina Ponkan', 
                              'Tomate', 'Vagem', 'Banana Prata']
    },
    {
        'id': 6,
        'nome': 'ASPHOR - Hortigranjeiros DF',
        'latitude': -15.791442,
        'longitude': -47.948464,
        'regioes': ['Plano Piloto', 'Gama', 'Santa Maria'],
        'produtos_originais': ['Abacate', 'Abóbora Japonesa', 'Abobrinha Italiana', 'Acelga', 
                              'Alface Americana', 'Batata Doce', 'Beterraba', 
                              'Brócolis Cabeça Única (Japonês)', 'Cebola', 'Cebolinha Comum', 
                              'Cenoura', 'Chuchu', 'Coentro', 'Couve-Flor', 'Couve Manteiga', 
                              'Espinafre', 'Goiaba', 'Hortelã', 'Inhame', 'Limão Tahiti', 
                              'Manjericão', 'Maracujá', 'Milho Verde', 'Morango', 'Pepino Comum', 
                              'Pimentão Verde', 'Repolho Verde', 'Repolho Roxo', 'Salsa', 
                              'Tomate', 'Vagem']
    },
    {
        'id': 7,
        'nome': 'ASPROC - Orgânicos e Convencionais',
        'latitude': -15.777904,
        'longitude': -48.120988,
        'regioes': ['Ceilândia', 'Recanto das Emas', 'Samambaia', 'Paranoá', 'Planaltina'],
        'produtos_originais': ['Goiaba', 'Tangerina Ponkan', 'Morango']
    },
    {
        'id': 8,
        'nome': 'ASPRONTE - Novo Horizonte',
        'latitude': -15.603130,
        'longitude': -48.113516,
        'regioes': ['Brazlândia', 'Ceilândia', 'Recanto Das Emas'],
        'produtos_originais': ['Morango', 'Abacate', 'Abobrinha Italiana', 'Acelga', 
                              'Alface Americana', 'Batata Doce', 'Beterraba', 
                              'Brócolis Cabeça Única (Japonês)', 'Cebolinha Comum', 'Cenoura', 
                              'Chuchu', 'Coentro', 'Couve-Flor', 'Couve Manteiga', 'Espinafre', 
                              'Goiaba', 'Hortelã', 'Pepino Comum', 'Pimentão Verde', 
                              'Repolho Verde', 'Salsa', 'Tomate', 'Vagem']
    },
    {
        'id': 9,
        'nome': 'ASTRAF - Assentamento Chapadinha',
        'latitude': -15.542238,
        'longitude': -48.029995,
        'regioes': ['PAD-DF', 'Planaltina'],
        'produtos_originais': ['Abacate', 'Abóbora Japonesa', 'Abobrinha Italiana', 'Acelga', 
                              'Alface Americana', 'Alho', 'Batata Doce', 'Beterraba', 
                              'Brócolis Cabeça Única (Japonês)', 'Cebola', 'Cebolinha Comum', 
                              'Cenoura', 'Chuchu', 'Coentro', 'Couve-Flor', 'Couve Manteiga', 
                              'Espinafre', 'Hortelã', 'Inhame', 'Limão Tahiti', 'Manjericão', 
                              'Maracujá', 'Milho Verde', 'Pepino Comum', 'Pimentão Verde', 
                              'Repolho Verde', 'Repolho Roxo', 'Salsa', 'Tomate', 'Vagem', 
                              'Banana Prata']
    },
    {
        'id': 10,
        'nome': 'COOPBRASIL - Agricultura Familiar',
        'latitude': -15.918585,
        'longitude': -48.082794,
        'regioes': ['Recanto das Emas', 'Gama', 'Samambaia', 'Núcleo Bandeirante', 
                   'Planaltina', 'Brazlândia', 'Ceilândia'],
        'produtos_originais': ['Alho', 'Abóbora Japonesa', 'Cebola', 'Inhame', 'Limão Tahiti', 
                              'Manjericão', 'Maracujá', 'Milho Verde', 'Repolho Roxo', 
                              'Banana Prata', 'Abacate', 'Abobrinha Italiana', 'Acelga', 
                              'Alface Americana', 'Batata Doce', 'Beterraba', 
                              'Brócolis Cabeça Única (Japonês)', 'Cebolinha Comum', 'Cenoura', 
                              'Chuchu', 'Coentro', 'Couve-Flor', 'Couve Manteiga', 'Espinafre', 
                              'Goiaba', 'Hortelã', 'Pepino Comum', 'Pimentão Verde', 
                              'Repolho Verde', 'Salsa', 'Tomate', 'Vagem', 'Morango']
    },
    {
        'id': 11,
        'nome': 'Cooper-Horti - Buriti Vermelho',
        'latitude': -15.898749,
        'longitude': -47.409203,
        'regioes': ['Paranoá', 'PAD-DF'],
        'produtos_originais': ['Abacate', 'Abóbora Japonesa', 'Abobrinha Italiana', 'Batata Doce', 
                              'Beterraba', 'Cenoura', 'Chuchu', 'Couve Manteiga', 'Inhame', 
                              'Limão Tahiti', 'Maracujá', 'Pepino Comum', 'Pimentão Verde', 
                              'Repolho Verde', 'Tangerina Ponkan']
    },
    {
        'id': 12,
        'nome': 'Prorural - Planaltina GO',
        'latitude': -15.445505,
        'longitude': -47.619013,
        'regioes': ['Planaltina', 'Plano Piloto', 'Paranoá'],
        'produtos_originais': ['Abacate', 'Abóbora Japonesa', 'Abobrinha Italiana', 'Acelga', 
                              'Alface Americana', 'Alho', 'Batata Doce', 'Beterraba', 
                              'Brócolis Cabeça Única (Japonês)', 'Cebola', 'Cebolinha Comum', 
                              'Cenoura', 'Chuchu', 'Coentro', 'Couve-Flor', 'Couve Manteiga', 
                              'Espinafre', 'Goiaba', 'Hortelã', 'Inhame', 'Limão Tahiti', 
                              'Manjericão', 'Maracujá', 'Milho Verde', 'Pepino Comum', 
                              'Pimentão Verde', 'Repolho Verde', 'Repolho Roxo', 'Salsa', 
                              'Tomate', 'Vagem', 'Banana Prata']
    },
    {
        'id': 13,
        'nome': 'Coopebraz - Brazlândia',
        'latitude': -15.602622,
        'longitude': -48.113771,
        'regioes': ['Brazlândia', 'Taguatinga', 'Samambaia', 'Recanto Das Emas'],
        'produtos_originais': ['Morango']
    },
    {
        'id': 14,
        'nome': 'Coopermista - Agricultura Familiar',
        'latitude': -15.764000,
        'longitude': -47.493246,
        'regioes': ['Planaltina'],
        'produtos_originais': ['Abacate', 'Abóbora Japonesa', 'Abobrinha Italiana', 'Batata Doce', 
                              'Beterraba', 'Cenoura', 'Couve Manteiga', 'Limão Tahiti', 
                              'Maracujá', 'Pepino Comum', 'Repolho Verde', 'Repolho Roxo', 
                              'Tangerina Ponkan']
    },
    {
        'id': 15,
        'nome': 'Rede Terra - Ecológicos do Cerrado',
        'latitude': -16.784921,
        'longitude': -47.600542,
        'regioes': ['Santa Maria', 'Gama'],
        'produtos_originais': ['Acelga', 'Alface Americana', 'Alho', 'Cebola', 'Espinafre', 
                              'Goiaba', 'Hortelã', 'Manjericão', 'Milho Verde']
    },
    {
        'id': 16,
        'nome': 'Cootaquara - Planaltina',
        'latitude': -15.632824,
        'longitude': -47.522650,
        'regioes': ['Planaltina', 'Ceilândia'],
        'produtos_originais': ['Abacate', 'Abóbora Japonesa', 'Abobrinha Italiana', 
                              'Alface Americana', 'Batata Doce', 'Beterraba', 
                              'Brócolis Cabeça Única (Japonês)', 'Cebolinha Comum', 'Cenoura', 
                              'Chuchu', 'Coentro', 'Couve-Flor', 'Couve Manteiga', 'Espinafre', 
                              'Inhame', 'Limão Tahiti', 'Maracujá', 'Milho Verde', 'Pepino Comum', 
                              'Pimentão Verde', 'Repolho Verde', 'Repolho Roxo', 'Salsa', 
                              'Tomate', 'Vagem', 'Banana Prata']
    },
    {
        'id': 17,
        'nome': 'Cooperbrasília - Serviços Ambientais',
        'latitude': -15.918543,
        'longitude': -48.082816,
        'regioes': ['Sobradinho', 'São Sebastião'],
        'produtos_originais': ['Abacate', 'Abóbora Japonesa', 'Abobrinha Italiana', 'Acelga', 
                              'Alface Americana', 'Alho', 'Batata Doce', 'Beterraba', 
                              'Brócolis Cabeça Única (Japonês)', 'Cebola', 'Cebolinha Comum', 
                              'Cenoura', 'Chuchu', 'Coentro', 'Couve-Flor', 'Couve Manteiga', 
                              'Espinafre', 'Goiaba', 'Hortelã', 'Inhame', 'Limão Tahiti', 
                              'Manjericão', 'Maracujá', 'Milho Verde', 'Morango', 'Pepino Comum', 
                              'Pimentão Verde', 'Repolho Verde', 'Repolho Roxo', 'Salsa', 
                              'Tangerina Ponkan', 'Tomate', 'Vagem', 'Banana Prata']
    }
]


# In[5]:


# Converter para DataFrame e mapear produtos
df_associacoes = pd.DataFrame(associacoes_data)

# Função para mapear produtos originais para produtos do escopo
def mapear_produtos(produtos_lista):
    produtos_mapeados = []
    for produto in produtos_lista:
        if produto in mapeamento_produtos:
            produto_mapeado = mapeamento_produtos[produto]
            if produto_mapeado in produtos_escopo and produto_mapeado not in produtos_mapeados:
                produtos_mapeados.append(produto_mapeado)
        elif produto in produtos_escopo and produto not in produtos_mapeados:
            produtos_mapeados.append(produto)
    return produtos_mapeados

# Aplicar mapeamento
df_associacoes['produtos'] = df_associacoes['produtos_originais'].apply(mapear_produtos)

# Adicionar características adicionais
np.random.seed(101)
df_associacoes['organico_principal'] = np.random.choice([True, False], size=len(df_associacoes), p=[0.3, 0.7])
df_associacoes['avaliacao_media'] = np.random.uniform(3.5, 5.0, size=len(df_associacoes))
df_associacoes['num_avaliacoes'] = np.random.randint(20, 200, size=len(df_associacoes))
df_associacoes['preco_medio_relativo'] = np.random.choice(['Baixo', 'Médio', 'Alto'], 
                                                          size=len(df_associacoes), 
                                                          p=[0.3, 0.5, 0.2])

# Ajustar algumas associações específicas como orgânicas
df_associacoes.loc[df_associacoes['nome'].str.contains('Orgânicos|Ecológicos'), 'organico_principal'] = True

print(f"✅ Dados de {len(df_associacoes)} associações/cooperativas carregados com sucesso!")
print(f"\n📊 Total de produtos únicos no escopo: {len(produtos_escopo)}")
print(f"📊 Total de produtos após mapeamento: {df_associacoes['produtos'].apply(len).sum()}")
print("\n🏢 Primeiras 3 associações:")
print(df_associacoes[['id', 'nome', 'regioes', 'produtos']].head(3))


# In[6]:


dados_taco = {
    'Abacate': {'id': 163, 'umidade': 83.8, 'energia_kcal': 96, 'proteina_g': 1.2, 
                'lipidios_g': 8.4, 'carboidratos_g': 6.0, 'fibra_g': 6.3, 'calcio_mg': 8, 
                'vitamina_c_mg': 15},
    'Abóbora': {'id': 71, 'umidade': 93.9, 'energia_kcal': 19, 'proteina_g': 1.1, 
                'lipidios_g': 0.1, 'carboidratos_g': 4.3, 'fibra_g': 1.4, 'calcio_mg': 15, 
                'vitamina_c_mg': 20},
    'Agrião': {'id': 74, 'umidade': 93.2, 'energia_kcal': 21, 'proteina_g': 1.4, 
                'lipidios_g': 0.1, 'carboidratos_g': 4.6, 'fibra_g': 1.1, 'calcio_mg': 43, 
                'vitamina_c_mg': 10},
    'Alface': {'id': 77, 'umidade': 97.2, 'energia_kcal': 9, 'proteina_g': 0.6, 
               'lipidios_g': 0.1, 'carboidratos_g': 1.7, 'fibra_g': 1.0, 'calcio_mg': 14, 
               'vitamina_c_mg': 6},
    'Batata': {'id': 89, 'umidade': 69.5, 'energia_kcal': 118, 'proteina_g': 1.3, 
               'lipidios_g': 0.1, 'carboidratos_g': 28.2, 'fibra_g': 2.6, 'calcio_mg': 21, 
               'vitamina_c_mg': 17},
    'Beterraba': {'id': 98, 'umidade': 86.0, 'energia_kcal': 49, 'proteina_g': 1.9, 
                  'lipidios_g': 0.1, 'carboidratos_g': 11.1, 'fibra_g': 3.4, 'calcio_mg': 18, 
                  'vitamina_c_mg': 24},
    'Brócolis': {'id': 101, 'umidade': 91.2, 'energia_kcal': 25, 'proteina_g': 3.6, 
                 'lipidios_g': 0.3, 'carboidratos_g': 4.0, 'fibra_g': 2.9, 'calcio_mg': 86, 
                 'vitamina_c_mg': 30},
    'Cebola': {'id': 107, 'umidade': 88.9, 'energia_kcal': 39, 'proteina_g': 1.7, 
               'lipidios_g': 0.1, 'carboidratos_g': 8.9, 'fibra_g': 2.2, 'calcio_mg': 14, 
               'vitamina_c_mg': 12},
    'Cenoura': {'id': 110, 'umidade': 90.1, 'energia_kcal': 34, 'proteina_g': 1.3, 
                'lipidios_g': 0.2, 'carboidratos_g': 7.7, 'fibra_g': 3.2, 'calcio_mg': 23, 
                'vitamina_c_mg': 11},
    'Chuchu': {'id': 113, 'umidade': 94.8, 'energia_kcal': 17, 'proteina_g': 0.7, 
               'lipidios_g': 0.1, 'carboidratos_g': 4.1, 'fibra_g': 1.3, 'calcio_mg': 12, 
               'vitamina_c_mg': 7},
    'Couve': {'id': 115, 'umidade': 90.9, 'energia_kcal': 27, 'proteina_g': 2.9, 
              'lipidios_g': 0.5, 'carboidratos_g': 4.3, 'fibra_g': 3.1, 'calcio_mg': 131, 
              'vitamina_c_mg': 35},
    'Goiaba': {'id': 197, 'umidade': 85.7, 'energia_kcal': 52, 'proteina_g': 0.9, 
              'lipidios_g': 0.5, 'carboidratos_g': 12.4, 'fibra_g': 6.3, 'calcio_mg': 5, 
              'vitamina_c_mg': 7},
   'Limão': {'id': 9004, 'umidade': 91.0, 'energia_kcal': 29, 'proteina_g': 1.1, 
             'lipidios_g': 0.3, 'carboidratos_g': 9.3, 'fibra_g': 2.8, 'calcio_mg': 26, 
             'vitamina_c_mg': 53},  # Limão Tahiti
   'Manga': {'id': 133, 'umidade': 83.5, 'energia_kcal': 65, 'proteina_g': 0.5, 
             'lipidios_g': 0.3, 'carboidratos_g': 15.0, 'fibra_g': 1.6, 'calcio_mg': 12, 
             'vitamina_c_mg': 43},
   'Maracujá': {'id': 232, 'umidade': 82.9, 'energia_kcal': 68, 'proteina_g': 2.0, 
                'lipidios_g': 2.1, 'carboidratos_g': 12.3, 'fibra_g': 1.1, 'calcio_mg': 5, 
                'vitamina_c_mg': 28},
   'Morango': {'id': 239, 'umidade': 91.5, 'energia_kcal': 30, 'proteina_g': 0.9, 
               'lipidios_g': 0.3, 'carboidratos_g': 6.8, 'fibra_g': 1.7, 'calcio_mg': 11, 
               'vitamina_c_mg': 10},
   'Pepino': {'id': 142, 'umidade': 96.8, 'energia_kcal': 10, 'proteina_g': 0.9, 
              'lipidios_g': 0.0, 'carboidratos_g': 2.0, 'fibra_g': 1.1, 'calcio_mg': 10, 
              'vitamina_c_mg': 9},
   'Pimentão': {'id': 144, 'umidade': 93.5, 'energia_kcal': 21, 'proteina_g': 1.1, 
                'lipidios_g': 0.2, 'carboidratos_g': 4.9, 'fibra_g': 2.6, 'calcio_mg': 9, 
                'vitamina_c_mg': 8},
   'Repolho': {'id': 150, 'umidade': 90.1, 'energia_kcal': 31, 'proteina_g': 1.9, 
               'lipidios_g': 0.1, 'carboidratos_g': 7.2, 'fibra_g': 2.0, 'calcio_mg': 44, 
               'vitamina_c_mg': 18},
   'Tangerina': {'id': 251, 'umidade': 89.2, 'energia_kcal': 38, 'proteina_g': 0.8, 
                 'lipidios_g': 0.1, 'carboidratos_g': 9.6, 'fibra_g': 0.9, 'calcio_mg': 13, 
                 'vitamina_c_mg': 8},
   'Tomate': {'id': 157, 'umidade': 95.1, 'energia_kcal': 15, 'proteina_g': 1.1, 
              'lipidios_g': 0.2, 'carboidratos_g': 3.1, 'fibra_g': 1.2, 'calcio_mg': 7, 
              'vitamina_c_mg': 11},
   'Banana': {'id': 182, 'umidade': 71.9, 'energia_kcal': 98, 'proteina_g': 1.3, 
              'lipidios_g': 0.1, 'carboidratos_g': 26.0, 'fibra_g': 2.0, 'calcio_mg': 8, 
              'vitamina_c_mg': 26},
   'Berinjela': {'id': 9006, 'umidade': 92.5, 'energia_kcal': 24, 'proteina_g': 1.0, 
                 'lipidios_g': 0.2, 'carboidratos_g': 5.7, 'fibra_g': 3.4, 'calcio_mg': 9, 
                 'vitamina_c_mg': 2},
   'Quiabo': {'id': 9007, 'umidade': 90.0, 'energia_kcal': 33, 'proteina_g': 2.0, 
              'lipidios_g': 0.1, 'carboidratos_g': 7.0, 'fibra_g': 3.2, 'calcio_mg': 81, 
              'vitamina_c_mg': 21},
   'Jiló': {'id': 9008, 'umidade': 92.0, 'energia_kcal': 27, 'proteina_g': 1.4, 
            'lipidios_g': 0.2, 'carboidratos_g': 6.2, 'fibra_g': 4.8, 'calcio_mg': 20, 
            'vitamina_c_mg': 6},
   'Gengibre': {'id': 9009, 'umidade': 78.9, 'energia_kcal': 80, 'proteina_g': 1.8, 
                'lipidios_g': 0.8, 'carboidratos_g': 17.8, 'fibra_g': 2.0, 'calcio_mg': 16, 
                'vitamina_c_mg': 5},
   'Uva': {'id': 9010, 'umidade': 80.5, 'energia_kcal': 69, 'proteina_g': 0.7, 
           'lipidios_g': 0.2, 'carboidratos_g': 17.1, 'fibra_g': 0.9, 'calcio_mg': 10, 
           'vitamina_c_mg': 4},
   'Lichia': {'id': 9011, 'umidade': 81.8, 'energia_kcal': 66, 'proteina_g': 0.8, 
              'lipidios_g': 0.4, 'carboidratos_g': 16.5, 'fibra_g': 1.3, 'calcio_mg': 5, 
              'vitamina_c_mg': 72},
   'Pitaia': {'id': 9012, 'umidade': 87.0, 'energia_kcal': 50, 'proteina_g': 1.1, 
              'lipidios_g': 0.4, 'carboidratos_g': 11.0, 'fibra_g': 3.0, 'calcio_mg': 9, 
              'vitamina_c_mg': 21},
   'Mamão': {'id': 9013, 'umidade': 88.6, 'energia_kcal': 43, 'proteina_g': 0.5, 
             'lipidios_g': 0.3, 'carboidratos_g': 10.8, 'fibra_g': 1.8, 'calcio_mg': 20, 
             'vitamina_c_mg': 62},
   'Coco': {'id': 9014, 'umidade': 47.0, 'energia_kcal': 354, 'proteina_g': 3.3, 
            'lipidios_g': 33.5, 'carboidratos_g': 15.2, 'fibra_g': 9.0, 'calcio_mg': 14, 
            'vitamina_c_mg': 3},
   'Graviola': {'id': 9015, 'umidade': 81.2, 'energia_kcal': 66, 'proteina_g': 1.0, 
                'lipidios_g': 0.3, 'carboidratos_g': 16.8, 'fibra_g': 3.3, 'calcio_mg': 14, 
                'vitamina_c_mg': 21},
   'Cajamanga': {'id': 9016, 'umidade': 91.0, 'energia_kcal': 31, 'proteina_g': 0.6, 
                 'lipidios_g': 0.1, 'carboidratos_g': 7.6, 'fibra_g': 0.9, 'calcio_mg': 3, 
                 'vitamina_c_mg': 34},
   'Atemóia': {'id': 9017, 'umidade': 72.9, 'energia_kcal': 94, 'proteina_g': 1.7, 
               'lipidios_g': 0.3, 'carboidratos_g': 23.6, 'fibra_g': 2.4, 'calcio_mg': 24, 
               'vitamina_c_mg': 36},
   'Mandioca': {'id': 9018, 'umidade': 61.8, 'energia_kcal': 151, 'proteina_g': 1.0, 
                'lipidios_g': 0.3, 'carboidratos_g': 36.2, 'fibra_g': 1.9, 'calcio_mg': 19, 
                'vitamina_c_mg': 17}
}

# Criar DataFrame de nutrientes
df_nutrientes = pd.DataFrame.from_dict(dados_taco, orient='index')

# Adicionar categorias aos alimentos
categorias_alimentos = {
   'folhosas': ['Alface', 'Couve', 'Agrião'],
   'frutos_hortalicas': ['Tomate', 'Pimentão', 'Berinjela', 'Jiló', 'Quiabo', 'Chuchu', 'Pepino'],
   'raizes_tuberculos': ['Batata', 'Mandioca', 'Beterraba', 'Cenoura'],
   'bulbos': ['Cebola'],
   'cruciferas': ['Brócolis', 'Repolho'],
   'frutas_doces': ['Banana', 'Manga', 'Mamão', 'Uva', 'Lichia', 'Atemóia'],
   'frutas_acidas': ['Limão', 'Tangerina', 'Maracujá', 'Cajamanga'],
   'frutas_berries': ['Morango'],
   'frutas_gordurosas': ['Abacate', 'Coco'],
   'frutas_tropicais': ['Goiaba', 'Graviola', 'Pitaia'],
   'temperos': ['Gengibre'],
   'leguminosas': ['Abóbora']
}

# Inverter o dicionário para facilitar a atribuição
categoria_por_alimento = {}
for categoria, alimentos in categorias_alimentos.items():
   for alimento in alimentos:
       categoria_por_alimento[alimento] = categoria

df_nutrientes['categoria'] = df_nutrientes.index.map(categoria_por_alimento)

# Calcular scores nutricionais normalizados
df_nutrientes['score_vitamina_c'] = df_nutrientes['vitamina_c_mg'] / df_nutrientes['vitamina_c_mg'].max()
df_nutrientes['score_fibras'] = df_nutrientes['fibra_g'] / df_nutrientes['fibra_g'].max()
df_nutrientes['score_baixa_caloria'] = 1 - (df_nutrientes['energia_kcal'] / df_nutrientes['energia_kcal'].max())
df_nutrientes['score_proteina'] = df_nutrientes['proteina_g'] / df_nutrientes['proteina_g'].max()

print("📊 Dados nutricionais carregados com sucesso!")
print(f"Total de alimentos com dados nutricionais: {len(df_nutrientes)}")
print("\n🥗 Categorias de alimentos:")
for categoria, count in df_nutrientes['categoria'].value_counts().items():
   print(f"  - {categoria}: {count} alimentos")
print("\n💊 Top 5 alimentos por vitamina C:")
print(df_nutrientes.nlargest(5, 'vitamina_c_mg')[['vitamina_c_mg', 'categoria']])


# In[7]:


"""
Dados reais de produção por região do DF
Fonte: Informações Agropecuárias do Distrito Federal - 2024 (EMATER-DF)
"""

# Dados de produção por escritório/região
producao_emater = {
    'ALEXANDRE GUSMÃO': {
        'Abacate': {'area_ha': 23.08, 'producao_t': 18.0, 'participacao_df': 23.08},
        'Alface': {'area_ha': 24.25, 'producao_t': 9.51, 'participacao_df': 24.25},
        'Banana': {'area_ha': 9.5, 'producao_t': 6.83, 'participacao_df': 9.5},
        'Chuchu': {'area_ha': 32.99, 'producao_t': 14.52, 'participacao_df': 32.99},
        'Couve': {'area_ha': 35.66, 'producao_t': 9.39, 'participacao_df': 35.66},
        'Goiaba': {'area_ha': 42.2, 'producao_t': 38.56, 'participacao_df': 42.2},
        'Limão': {'area_ha': 13.15, 'producao_t': 12.04, 'participacao_df': 13.15},
        'Mandioca': {'area_ha': 18.29, 'producao_t': 6.17, 'participacao_df': 18.29},
        'Manga': {'area_ha': 13.67, 'producao_t': 1.66, 'participacao_df': 13.67},
        'Maracujá': {'area_ha': 12.19, 'producao_t': 10.26, 'participacao_df': 12.19},
        'Pimentão': {'area_ha': 14.73, 'producao_t': 4.13, 'participacao_df': 14.73},
        'Repolho': {'area_ha': 24.68, 'producao_t': 8.87, 'participacao_df': 24.68},
        'Tangerina': {'area_ha': 21.44, 'producao_t': 6.96, 'participacao_df': 21.44},
        'Tomate': {'area_ha': 14.62, 'producao_t': 11.67, 'participacao_df': 14.62},
        'Uva': {'area_ha': 4.16, 'producao_t': 0.77, 'participacao_df': 4.16}
    },
    'BRAZLÂNDIA': {
        'Abacate': {'area_ha': 19.45, 'producao_t': 18.6, 'participacao_df': 19.45},
        'Alface': {'area_ha': 8.87, 'producao_t': 5.95, 'participacao_df': 8.87},
        'Banana': {'area_ha': 4.35, 'producao_t': 3.61, 'participacao_df': 4.35},
        'Chuchu': {'area_ha': 27.72, 'producao_t': 13.09, 'participacao_df': 27.72},
        'Couve': {'area_ha': 9.43, 'producao_t': 3.24, 'participacao_df': 9.43},
        'Goiaba': {'area_ha': 53.62, 'producao_t': 57.58, 'participacao_df': 53.62},
        'Limão': {'area_ha': 9.3, 'producao_t': 9.48, 'participacao_df': 9.3},
        'Mandioca': {'area_ha': 6.88, 'producao_t': 4.08, 'participacao_df': 6.88},
        'Manga': {'area_ha': 4.4, 'producao_t': 0.6, 'participacao_df': 4.4},
        'Maracujá': {'area_ha': 3.94, 'producao_t': 1.38, 'participacao_df': 3.94},
        'Morango': {'area_ha': 76.51, 'producao_t': 17.36, 'participacao_df': 76.51},
        'Pimentão': {'area_ha': 15.89, 'producao_t': 6.18, 'participacao_df': 15.89},
        'Repolho': {'area_ha': 23.53, 'producao_t': 10.6, 'participacao_df': 23.53},
        'Tangerina': {'area_ha': 11.42, 'producao_t': 5.63, 'participacao_df': 11.42},
        'Tomate': {'area_ha': 8.66, 'producao_t': 10.33, 'participacao_df': 8.66},
        'Uva': {'area_ha': 3.29, 'producao_t': 0.24, 'participacao_df': 3.29}
    },
    'CEILÂNDIA': {
        'Abacate': {'area_ha': 3.61, 'producao_t': 9.77, 'participacao_df': 3.61},
        'Alface': {'area_ha': 24.1, 'producao_t': 12.04, 'participacao_df': 24.1},
        'Banana': {'area_ha': 12.33, 'producao_t': 29.03, 'participacao_df': 12.33},
        'Chuchu': {'area_ha': 29.16, 'producao_t': 17.64, 'participacao_df': 29.16},
        'Couve': {'area_ha': 22.59, 'producao_t': 7.41, 'participacao_df': 22.59},
        'Goiaba': {'area_ha': 0.37, 'producao_t': 1.44, 'participacao_df': 0.37},
        'Limão': {'area_ha': 10.43, 'producao_t': 23.69, 'participacao_df': 10.43},
        'Mandioca': {'area_ha': 16.23, 'producao_t': 9.48, 'participacao_df': 16.23},
        'Manga': {'area_ha': 5.92, 'producao_t': 3.63, 'participacao_df': 5.92},
        'Maracujá': {'area_ha': 7.96, 'producao_t': 20.18, 'participacao_df': 7.96},
        'Repolho': {'area_ha': 17.83, 'producao_t': 8.75, 'participacao_df': 17.83},
        'Tangerina': {'area_ha': 6.03, 'producao_t': 9.55, 'participacao_df': 6.03},
        'Tomate': {'area_ha': 3.22, 'producao_t': 3.47, 'participacao_df': 3.22}
    },
    'GAMA': {
        'Abacate': {'area_ha': 6.98, 'producao_t': 20.49, 'participacao_df': 6.98},
        'Alface': {'area_ha': 19.58, 'producao_t': 32.92, 'participacao_df': 19.58},
        'Banana': {'area_ha': 5.59, 'producao_t': 15.58, 'participacao_df': 5.59},
        'Couve': {'area_ha': 9.74, 'producao_t': 8.83, 'participacao_df': 9.74},
        'Lichia': {'area_ha': 5.86, 'producao_t': 1.21, 'participacao_df': 5.86},
        'Limão': {'area_ha': 12.17, 'producao_t': 27.56, 'participacao_df': 12.17},
        'Mandioca': {'area_ha': 9.66, 'producao_t': 16.37, 'participacao_df': 9.66},
        'Manga': {'area_ha': 13.1, 'producao_t': 6.94, 'participacao_df': 13.1},
        'Maracujá': {'area_ha': 3.06, 'producao_t': 7.6, 'participacao_df': 3.06},
        'Pimentão': {'area_ha': 2.24, 'producao_t': 3.26, 'participacao_df': 2.24},
        'Pitaia': {'area_ha': 16.31, 'producao_t': 1.71, 'participacao_df': 16.31},
        'Repolho': {'area_ha': 1.85, 'producao_t': 2.31, 'participacao_df': 1.85},
        'Tangerina': {'area_ha': 9.07, 'producao_t': 10.7, 'participacao_df': 9.07}
    },
    'PLANALTINA': {
        'Abacate': {'area_ha': 4.26, 'producao_t': 8.23, 'participacao_df': 4.26},
        'Alface': {'area_ha': 1.13, 'producao_t': 3.94, 'participacao_df': 1.13},
        'Banana': {'area_ha': 7.35, 'producao_t': 10.82, 'participacao_df': 7.35},
        'Chuchu': {'area_ha': 1.94, 'producao_t': 4.52, 'participacao_df': 1.94},
        'Couve': {'area_ha': 0.96, 'producao_t': 1.69, 'participacao_df': 0.96},
        'Goiaba': {'area_ha': 0.8, 'producao_t': 2.57, 'participacao_df': 0.8},
        'Lichia': {'area_ha': 61.0, 'producao_t': 7.17, 'participacao_df': 61.0},
        'Limão': {'area_ha': 15.68, 'producao_t': 27.24, 'participacao_df': 15.68},
        'Mandioca': {'area_ha': 7.19, 'producao_t': 30.89, 'participacao_df': 7.19},
        'Manga': {'area_ha': 13.01, 'producao_t': 3.23, 'participacao_df': 13.01},
        'Maracujá': {'area_ha': 7.53, 'producao_t': 11.02, 'participacao_df': 7.53},
        'Pimentão': {'area_ha': 2.1, 'producao_t': 2.39, 'participacao_df': 2.1},
        'Repolho': {'area_ha': 1.68, 'producao_t': 3.74, 'participacao_df': 1.68},
        'Tangerina': {'area_ha': 10.55, 'producao_t': 8.73, 'participacao_df': 10.55},
        'Tomate': {'area_ha': 3.49, 'producao_t': 16.83, 'participacao_df': 3.49},
        'Uva': {'area_ha': 15.24, 'producao_t': 11.13, 'participacao_df': 15.24}
    },
    'SOBRADINHO': {
        'Abacate': {'area_ha': 5.78, 'producao_t': 11.67, 'participacao_df': 5.78},
        'Alface': {'area_ha': 11.79, 'producao_t': 12.59, 'participacao_df': 11.79},
        'Banana': {'area_ha': 27.36, 'producao_t': 43.04, 'participacao_df': 27.36},
        'Berinjela': {'area_ha': 14.33, 'producao_t': 4.35, 'participacao_df': 14.33},
        'Chuchu': {'area_ha': 2.32, 'producao_t': 3.22, 'participacao_df': 2.32},
        'Couve': {'area_ha': 9.15, 'producao_t': 5.88, 'participacao_df': 9.15},
        'Limão': {'area_ha': 7.6, 'producao_t': 11.29, 'participacao_df': 7.6},
        'Mandioca': {'area_ha': 15.39, 'producao_t': 14.95, 'participacao_df': 15.39},
        'Manga': {'area_ha': 25.42, 'producao_t': 10.15, 'participacao_df': 25.42},
        'Maracujá': {'area_ha': 8.8, 'producao_t': 3.45, 'participacao_df': 8.8},
        'Pimentão': {'area_ha': 5.13, 'producao_t': 6.43, 'participacao_df': 5.13},
        'Repolho': {'area_ha': 11.8, 'producao_t': 12.24, 'participacao_df': 11.8},
        'Tangerina': {'area_ha': 7.6, 'producao_t': 6.44, 'participacao_df': 7.6},
        'Tomate': {'area_ha': 4.5, 'producao_t': 8.75, 'participacao_df': 4.5},
        'Uva': {'area_ha': 22.17, 'producao_t': 5.35, 'participacao_df': 22.17}
    },
    'SÃO SEBASTIÃO': {
        'Abacate': {'area_ha': 0.1, 'producao_t': 1.86, 'participacao_df': 0.1},
        'Abóbora': {'area_ha': 4.14, 'producao_t': 0.19, 'participacao_df': 4.14},
        'Agrião': {'area_ha': 0.94, 'producao_t': 0.1, 'participacao_df': 0.94},
        'Alface': {'area_ha': 0.46, 'producao_t': 0.34, 'participacao_df': 0.46},
        'Banana': {'area_ha': 1.5, 'producao_t': 28.78, 'participacao_df': 1.5},
        'Cebola': {'area_ha': 66.0, 'producao_t': 95.49, 'participacao_df': 66.0},
        'Couve': {'area_ha': 0.59, 'producao_t': 0.22, 'participacao_df': 0.59},
        'Limão': {'area_ha': 1.05, 'producao_t': 11.77, 'participacao_df': 1.05},
        'Mandioca': {'area_ha': 2.6, 'producao_t': 1.98, 'participacao_df': 2.6},
        'Manga': {'area_ha': 5.63, 'producao_t': 20.2, 'participacao_df': 5.63},
        'Maracujá': {'area_ha': 8.45, 'producao_t': 28.31, 'participacao_df': 8.45},
        'Morango': {'area_ha': 2.41, 'producao_t': 0.46, 'participacao_df': 2.41},
        'Pitaia': {'area_ha': 0.37, 'producao_t': 0.31, 'participacao_df': 0.37},
        'Quiabo': {'area_ha': 1.16, 'producao_t': 0.09, 'participacao_df': 1.16},
        'Repolho': {'area_ha': 0.1, 'producao_t': 0.09, 'participacao_df': 0.1},
        'Tangerina': {'area_ha': 0.27, 'producao_t': 1.36, 'participacao_df': 0.27},
        'Tomate': {'area_ha': 0.17, 'producao_t': 0.18, 'participacao_df': 0.17}
    }
}

# Converter para DataFrame
lista_producao = []
for regiao, produtos_dict in producao_emater.items(): # Renomeado para produtos_dict para clareza
    for produto, dados in produtos_dict.items():
        lista_producao.append({
            'regiao': regiao,
            'produto': produto,
            'area_ha': dados['area_ha'],
            'producao_t': dados['producao_t']
        })


# In[8]:


df_producao = pd.DataFrame(lista_producao)

# Mapear os nomes dos produtos da EMATER para os nomes do nosso escopo

df_producao['produto'] = df_producao['produto'].replace(mapeamento_produtos)
df_producao['produto'] = df_producao['produto'].str.strip()

# Filtrar apenas produtos que estão no nosso escopo
df_producao = df_producao[df_producao['produto'].isin(produtos_escopo)].copy()

# Calcular a produção total por produto no DF para ponderação
df_producao_total_produto = df_producao.groupby('produto', as_index=False)['producao_t'].sum()
df_producao_total_produto.rename(columns={'producao_t': 'producao_total_df_t'}, inplace=True)

# Adicionar a produção total ao df_producao
df_producao = pd.merge(df_producao, df_producao_total_produto, on='produto', how='left')

# Calcular a relevância da região para cada produto (porcentagem da produção do DF naquela região)
df_producao['relevancia_regiao_percent'] = 0.0
mask_total_prod_gt_0 = df_producao['producao_total_df_t'] > 0
df_producao.loc[mask_total_prod_gt_0, 'relevancia_regiao_percent'] = \
    (df_producao['producao_t'][mask_total_prod_gt_0] / df_producao['producao_total_df_t'][mask_total_prod_gt_0]) * 100
df_producao['relevancia_regiao_percent'].fillna(0, inplace=True)


#  Análise dos dados EMATER

# In[9]:


print("\n\nDados de produção da EMATER-DF processados (com dados do usuário)!")
print(f"Total de registros de produção regional (após filtro de escopo): {len(df_producao)}")
print(f"Total de produtos distintos na EMATER (no escopo): {df_producao['produto'].nunique()}")

print("\nTop regiões produtoras de Alface (por participação %):")
alface_prod = df_producao[df_producao['produto'] == 'Alface'].nlargest(5, 'relevancia_regiao_percent')
print(alface_prod[['regiao', 'producao_t', 'relevancia_regiao_percent']])

print("\nTop produtos mais produzidos no DF (toneladas):")
top_5_produtos = df_producao.groupby('produto')['producao_t'].sum().nlargest()
print(top_5_produtos)

print("\nExemplo de dados de produção para a região de BRAZLÂNDIA (ordenado por produção):")
brazlandia_data = df_producao[df_producao['regiao'] == 'BRAZLÂNDIA'].sort_values(by='producao_t', ascending=False)
print(brazlandia_data[['produto', 'area_ha', 'producao_t', 'relevancia_regiao_percent']].head())

df_producao.head()


# In[10]:


"""
Criar uma matriz de utilidade Usuário-Item (Consumidor-Associação).
Esta matriz simula avaliações de consumidores para as associações.
O objetivo é ter pelo menos 5.000 avaliações (linhas na forma longa).
"""
np.random.seed(101)

num_consumidores_simulados = 500
min_avaliacoes_por_consumidor = 10
max_avaliacoes_por_consumidor = 25

consumidores_ids = [f'Consumidor_{i+1:03d}' for i in range(num_consumidores_simulados)]

if 'df_associacoes' not in locals() or df_associacoes.empty:
    print("⚠️ df_associacoes não definido ou vazio. Célula 2 precisa ser executada.")
    df_associacoes = pd.DataFrame({'id': range(1,18), 'avaliacao_media': np.random.uniform(3.0,5.0,17), 'produtos': [[] for _ in range(17)]})


associacoes_ids_avaliadas = df_associacoes['id'].unique()
if len(associacoes_ids_avaliadas) == 0:
    raise ValueError("Nenhuma ID de associação encontrada. Verifique o df_associacoes.")

utility_matrix_list = []
for consumidor_id in consumidores_ids:
    num_avaliacoes_a_fazer = np.random.randint(min_avaliacoes_por_consumidor,
                                               min(max_avaliacoes_por_consumidor, len(associacoes_ids_avaliadas)) + 1)
    if num_avaliacoes_a_fazer == 0 and len(associacoes_ids_avaliadas) > 0 : # Garante pelo menos 1 se possível
        num_avaliacoes_a_fazer = 1
    if num_avaliacoes_a_fazer == 0 : continue # Pula se não há associações para avaliar

    associacoes_escolhidas_ids = np.random.choice(associacoes_ids_avaliadas, size=num_avaliacoes_a_fazer, replace=False)

    for assoc_id in associacoes_escolhidas_ids:
        assoc_info = df_associacoes[df_associacoes['id'] == assoc_id].iloc[0]
        avaliacao_base = assoc_info['avaliacao_media']
        if np.random.rand() < 0.6: # 60% de chance da avaliação ser próxima da média
            avaliacao = np.clip(round(np.random.normal(loc=avaliacao_base, scale=0.5)), 1, 5)
        else: # 40% de chance de uma avaliação mais aleatória
            avaliacao = np.random.randint(1, 6)
        utility_matrix_list.append({
            'id_consumidor': consumidor_id,
            'id_associacao': assoc_id,
            'avaliacao': int(avaliacao)
        })

df_utility_long = pd.DataFrame(utility_matrix_list)
print(f"✅ Matriz de utilidade em formato longo criada com {len(df_utility_long)} avaliações.")
if len(df_utility_long) < 5000:
    print(f"⚠️ Atenção: Foram geradas {len(df_utility_long)} avaliações. Ajuste os parâmetros de simulação se o alvo é 5000+.")

if not df_utility_long.empty:
    df_utility_pivot = df_utility_long.pivot(
        index='id_consumidor',
        columns='id_associacao',
        values='avaliacao'
    )
    print("\n↔️ Matriz de Utilidade Pivotada (amostra - NaN significa sem avaliação):")
    print(df_utility_pivot.head())
    print(f"\nDimensões da matriz pivotada: {df_utility_pivot.shape}")
    print(f"Esparsidade da matriz: {1.0 - (df_utility_pivot.count().sum() / float(df_utility_pivot.shape[0] * df_utility_pivot.shape[1])):.4f}")
else:
    print("⚠️ Matriz de utilidade longa está vazia. Pivot não pode ser criado.")
    # Criar um df_utility_pivot vazio para evitar erros subsequentes, mas o sistema não será funcional
    df_utility_pivot = pd.DataFrame()


# In[11]:


"""
Esta classe encapsulará toda a lógica para gerar recomendações híbridas.
"""
class SistemaRecomendacaoDF:
    def __init__(self, df_associacoes, df_nutrientes, df_producao, df_utility_pivot):
        self.df_associacoes = df_associacoes.copy()
        self.df_nutrientes = df_nutrientes.copy()
        self.df_producao = df_producao.copy()
        self.df_utility_pivot = df_utility_pivot.copy()
        self.utility_matrix_filled = self.df_utility_pivot.fillna(0)

        self.item_similarity_df = pd.DataFrame()
        if not self.utility_matrix_filled.empty and self.utility_matrix_filled.shape[1] > 1:
            similarity_matrix = cosine_similarity(self.utility_matrix_filled.T)
            self.item_similarity_df = pd.DataFrame(
                similarity_matrix,
                index=self.utility_matrix_filled.columns,
                columns=self.utility_matrix_filled.columns
            )
            print(f"Matriz de similaridade item-item calculada ({self.item_similarity_df.shape}).")
        else:
            print("Matriz de utilidade vazia ou com poucos itens, similaridade item-item não calculada.")
        print("SistemaRecomendacaoDF inicializado.")

    def _calcular_distancia_km(self, lat1, lon1, lat2, lon2):
        if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2): return float('inf')
        return geodesic((lat1, lon1), (lat2, lon2)).km

    def _get_item_collab_score(self, id_consumidor, id_item_candidato):
        score_collab = 0.0; num_itens_sim_usados = 0
        if id_consumidor not in self.utility_matrix_filled.index or \
           id_item_candidato not in self.item_similarity_df.index or self.item_similarity_df.empty:
            return 0.0
        avaliacoes_consumidor = self.utility_matrix_filled.loc[id_consumidor]
        itens_avaliados_bem = avaliacoes_consumidor[avaliacoes_consumidor >= 3.5].index
        for id_item_gostou in itens_avaliados_bem:
            if id_item_gostou in self.item_similarity_df.columns and id_item_gostou != id_item_candidato:
                similaridade = self.item_similarity_df.loc[id_item_candidato, id_item_gostou]
                score_collab += similaridade * avaliacoes_consumidor[id_item_gostou]
                num_itens_sim_usados +=1
        return (score_collab / num_itens_sim_usados) if num_itens_sim_usados > 0 else 0.0

    def recomendar(self, id_consumidor, lat_usuario, lon_usuario, preferencias):
        print(f"\n🔄 Gerando recomendações para '{id_consumidor}' em ({lat_usuario:.4f}, {lon_usuario:.4f}) com prefs: {preferencias.get('produtos_desejados', 'N/A')}")
        cand_df = self.df_associacoes.copy()
        cand_df['dist_km'] = cand_df.apply(lambda r: self._calcular_distancia_km(lat_usuario, lon_usuario, r['latitude'], r['longitude']), axis=1)
        cand_df = cand_df[cand_df['dist_km'] <= preferencias.get('distancia_max_km', 30)].copy()
        if preferencias.get('apenas_organicos', False): cand_df = cand_df[cand_df['organico_principal'] == True].copy()
        prods_des = preferencias.get('produtos_desejados', [])
        if prods_des: cand_df = cand_df[cand_df['produtos'].apply(lambda p_list: any(p_d in p_list for p_d in prods_des))].copy()

        if cand_df.empty: print("⚠️ Nenhuma candidata após filtros iniciais."); return pd.DataFrame()
        print(f"🔎 {len(cand_df)} candidatas após filtros iniciais.")

        cand_df['score_final'] = 0.0
        max_d = cand_df['dist_km'].max(); min_d = cand_df['dist_km'].min()
        cand_df['s_dist'] = (1 - (cand_df['dist_km'] - min_d) / (max_d - min_d)) if max_d > min_d else 1.0
        cand_df['score_final'] += cand_df['s_dist'] * preferencias.get('peso_distancia', 0.25)

        cand_df['s_aval'] = cand_df['avaliacao_media'] / 5.0
        cand_df['score_final'] += cand_df['s_aval'] * preferencias.get('peso_avaliacao', 0.20)

        obj_nutri = preferencias.get('objetivo_nutricional'); cand_df['s_nutri'] = 0.0
        if obj_nutri and prods_des:
            for idx, row in cand_df.iterrows():
                sc_n_assoc = 0; ct_p_n = 0
                for p_n in [p for p in row['produtos'] if p in prods_des]:
                    if p_n in self.df_nutrientes.index:
                        col_sc = {'alta_vitamina_c': 'score_vitamina_c', 'alta_fibra': 'score_fibras', 'baixa_caloria': 'score_baixa_caloria'}.get(obj_nutri)
                        if col_sc and col_sc in self.df_nutrientes.columns: sc_n_assoc += self.df_nutrientes.loc[p_n, col_sc]; ct_p_n +=1
                if ct_p_n > 0: cand_df.loc[idx, 's_nutri'] = sc_n_assoc / ct_p_n
        cand_df['score_final'] += cand_df['s_nutri'] * preferencias.get('peso_nutricional', 0.15) # Peso ajustado

        cand_df['s_relev_prod'] = 0.0
        if preferencias.get('considerar_relevancia_produtiva_regiao', True) and prods_des:
            for idx, row in cand_df.iterrows():
                sc_r_p_assoc = 0; ct_p_r = 0
                for p_r in [p for p in row['produtos'] if p in prods_des]:
                    relev_max = 0
                    for reg_a in row['regioes']:
                        d_emater = self.df_producao[(self.df_producao['regiao'] == reg_a.upper()) & (self.df_producao['produto'] == p_r)]
                        if not d_emater.empty: relev_max = max(relev_max, d_emater['relevancia_regiao_percent'].iloc[0])
                    sc_r_p_assoc += (relev_max / 100.0); ct_p_r +=1
                if ct_p_r > 0: cand_df.loc[idx, 's_relev_prod'] = sc_r_p_assoc / ct_p_r
        cand_df['score_final'] += cand_df['s_relev_prod'] * preferencias.get('peso_relevancia_prod', 0.20) # Peso ajustado

        cand_df['s_collab'] = 0.0
        if id_consumidor in self.utility_matrix_filled.index and not self.item_similarity_df.empty:
            cand_df['s_collab'] = cand_df['id'].apply(lambda id_a: self._get_item_collab_score(id_consumidor, id_a))
            if cand_df['s_collab'].max() > 0: cand_df['s_collab'] = cand_df['s_collab'] / cand_df['s_collab'].max()
        cand_df['score_final'] += cand_df['s_collab'] * preferencias.get('peso_colaborativo', 0.20) # Peso ajustado

        rec_finais = cand_df.sort_values(by='score_final', ascending=False).head(preferencias.get('top_n', 5))
        cols_ret = ['id', 'nome', 'dist_km', 'avaliacao_media', 'produtos', 'score_final', 's_dist', 's_aval', 's_nutri', 's_relev_prod', 's_collab']
        return rec_finais[[c for c in cols_ret if c in rec_finais.columns]]


# In[12]:


"""
Instanciar e testar a classe SistemaRecomendacaoDF.
"""
dfs_necessarias_ok_v2 = True

for nome_df_check_v2 in ["df_associacoes", "df_nutrientes", "df_producao", "df_utility_pivot"]:
    if nome_df_check_v2 not in locals() or not isinstance(locals()[nome_df_check_v2], pd.DataFrame) or locals()[nome_df_check_v2].empty:
        print(f"ERRO: DataFrame '{nome_df_check_v2}' não carregada ou vazia. Execute as células anteriores.")
        dfs_necessarias_ok_v2 = False; break

if dfs_necessarias_ok_v2:
    print("Todas as DataFrames necessárias estão carregadas.")
    sistema_rec_v2 = SistemaRecomendacaoDF(df_associacoes, df_nutrientes, df_producao, df_utility_pivot)

    user_lat_ex1_v2, user_lon_ex1_v2 = -15.7632, -47.8706 # unb
    id_cons_ex1_v2 = df_utility_pivot.index[np.random.randint(0, len(df_utility_pivot))] if not df_utility_pivot.empty else "Consumidor_Teste1_v2"
    
    prefs_ex1_v2 = {
        'produtos_desejados': ['Alface', 'Tomate'], 'distancia_max_km': 20, 'apenas_organicos': False,
        'objetivo_nutricional': 'baixa_caloria', 'top_n': 5,
        'considerar_relevancia_produtiva_regiao': True,
        'peso_distancia': 0.25, 'peso_avaliacao': 0.20,
        'peso_nutricional': 0.20,
        'peso_relevancia_prod': 0.20,
        'peso_colaborativo': 0.15
    }
    recs_ex1_v2 = sistema_rec_v2.recomendar(id_cons_ex1_v2, user_lat_ex1_v2, user_lon_ex1_v2, prefs_ex1_v2)
    if not recs_ex1_v2.empty: print(f"\n🏆 Recomendações Cenário 1 v2 (Usuário: {id_cons_ex1_v2}):"); display(recs_ex1_v2)
    else: print(f"❌ Nenhuma recomendação para Cenário 1 v2 (Usuário: {id_cons_ex1_v2}).")

    user_lat_ex2_v2, user_lon_ex2_v2 = -15.7632, -47.8706 # unb
    id_cons_ex2_v2 = df_utility_pivot.index[np.random.randint(0, len(df_utility_pivot))] if not df_utility_pivot.empty else "Consumidor_Teste2_v2"
    prefs_ex2_v2 = {
        'produtos_desejados': ['Abacate'], 'distancia_max_km': 15, 'apenas_organicos': True,
        'objetivo_nutricional': None, 'top_n': 3,
        'considerar_relevancia_produtiva_regiao': False,
        'peso_distancia': 0.30, 'peso_avaliacao': 0.25,
        'peso_nutricional': 0.10,
        'peso_relevancia_prod': 0.10,
        'peso_colaborativo': 0.25
    }
    recs_ex2_v2 = sistema_rec_v2.recomendar(id_cons_ex2_v2, user_lat_ex2_v2, user_lon_ex2_v2, prefs_ex2_v2)
    if not recs_ex2_v2.empty: print(f"\n🏆 Recomendações Cenário 2 v2 (Usuário: {id_cons_ex2_v2}):"); display(recs_ex2_v2)
    else: print(f"❌ Nenhuma recomendação para Cenário 2 v2 (Usuário: {id_cons_ex2_v2}).")
else:
    print("\n🔴 Sistema de recomendação (v2) não pôde ser instanciado devido à falta de DataFrames.")


# In[13]:


"""
Função para criar um mapa interativo com Folium.
"""
def criar_mapa_recomendacoes_folium_v2(user_lat, user_lon, df_recomendacoes, preferencias_mapa):
    if pd.isna(user_lat) or pd.isna(user_lon): print("!!!!! Coords do usuário inválidas !!!!!"); return None
    mapa = folium.Map(location=[user_lat, user_lon], zoom_start=10)
    folium.Marker([user_lat, user_lon], popup="📍 Sua Localização", tooltip="Você", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(mapa)
    dist_max_km = preferencias_mapa.get('distancia_max_km', 100)
    folium.Circle([user_lat, user_lon], radius=dist_max_km * 1000, color='blue', fill=True, fill_opacity=0.1, tooltip=f"Raio: {dist_max_km} km").add_to(mapa)

    if not df_recomendacoes.empty:
        for _, row in df_recomendacoes.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                prods = row.get('produtos', [])
                prods_str = ", ".join(prods[:3]) + ('...' if len(prods) > 3 else '')
                # Removido 's_saz' do popup
                popup_html = f"""<b>⭐ {row['nome']}</b><hr>
                                 <b>Score:</b> {row.get('score_final', 0.0):.2f}<br>
                                 <b>Distância:</b> {row.get('dist_km', 0.0):.1f} km<br>
                                 <b>Avaliação:</b> {row.get('avaliacao_media', 0.0):.1f}/5<br>
                                 <b>Orgânico:</b> {'Sim' if row.get('organico_principal', False) else 'Não'}<br>
                                 <b>Produtos:</b> {prods_str}<br>
                                 <details><summary>Sub-scores</summary><small>
                                 Dist: {row.get('s_dist', 0):.2f} | Aval: {row.get('s_aval', 0):.2f} <br>
                                 Nutri: {row.get('s_nutri', 0):.2f} | Relev: {row.get('s_relev_prod', 0):.2f} | Collab: {row.get('s_collab', 0):.2f}
                                 </small></details>"""
                folium.Marker(
                    [row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_html, max_width=380),
                    tooltip=f"{row['nome']} (Score: {row.get('score_final',0):.2f})",
                    icon=folium.Icon(color='green' if row.get('organico_principal', False) else 'orange', icon='shopping-basket', prefix='fa')
                ).add_to(mapa)
    else: print("Nenhuma recomendação para exibir no mapa.")
    return mapa

if dfs_necessarias_ok_v2: # Executar mapas apenas se o sistema v2 foi instanciado
    if 'recs_ex1_v2' in locals() and isinstance(recs_ex1_v2, pd.DataFrame) and not recs_ex1_v2.empty:
        print("\n🗺️ Gerando mapa para Cenário 1 (v2)...")
        recs_ex1_v2_com_coords = pd.merge(recs_ex1_v2, df_associacoes[['id', 'latitude', 'longitude', 'organico_principal']], on='id', how='left')
        mapa_ex1_v2 = criar_mapa_recomendacoes_folium_v2(user_lat_ex1_v2, user_lon_ex1_v2, recs_ex1_v2_com_coords, prefs_ex1_v2)
        if mapa_ex1_v2: display(mapa_ex1_v2)
    else: print("\nℹ️ Sem recomendações do Cenário 1 (v2) para mapear.")

    if 'recs_ex2_v2' in locals() and isinstance(recs_ex2_v2, pd.DataFrame) and not recs_ex2_v2.empty:
        print("\n🗺️ Gerando mapa para Cenário 2 (v2)...")
        recs_ex2_v2_com_coords = pd.merge(recs_ex2_v2, df_associacoes[['id', 'latitude', 'longitude', 'organico_principal']], on='id', how='left')
        mapa_ex2_v2 = criar_mapa_recomendacoes_folium_v2(user_lat_ex2_v2, user_lon_ex2_v2, recs_ex2_v2_com_coords, prefs_ex2_v2)
        if mapa_ex2_v2: display(mapa_ex2_v2)
    else: print("\nℹ️ Sem recomendações do Cenário 2 (v2) para mapear.")


# In[ ]:





# In[ ]:




