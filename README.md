# Datathon 7MLET - Recomendacao Adaptativa de Ofertas

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Dataset](https://img.shields.io/badge/Dataset-Kaggle-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/datasets/henriqueyamahata/bank-marketing)

Projeto de datathon que aplica multi-armed bandit (Thompson Sampling) para recomendar quando priorizar ofertas em canais digitais, usando o historico de contatos anteriores do cliente (`poutcome`).

## Sumario

- [Visao geral](#visao-geral)
- [Problema de negocio](#problema-de-negocio)
- [Base de dados](#base-de-dados)
- [Tratamento de dados](#tratamento-de-dados)
- [Estrategia algoritmica](#estrategia-algoritmica)
- [Resultados](#resultados)
- [Golden set (5 casos)](#golden-set-5-casos)
- [API demonstravel](#api-demonstravel)
- [MLOps](#mlops)
- [Arquitetura alvo em nuvem (AWS)](#arquitetura-alvo-em-nuvem-aws)
- [Como rodar](#como-rodar)
- [Estrutura do repositorio](#estrutura-do-repositorio)
- [Limitacoes e proximos passos](#limitacoes-e-proximos-passos)

## Visao geral

- Objetivo: aumentar taxa de conversao de campanhas sem depender de regras fixas.
- Abordagem: comparar uma politica baseline aleatoria vs. politica adaptativa com Thompson Sampling.
- Entrega: notebook de analise/simulacao + API FastAPI para recomendacao online.

## Problema de negocio

Uma instituicao financeira digital precisa decidir, em diferentes canais, qual oferta, mensagem ou proximo passo apresentar para cada cliente elegivel. Regras fixas e testes A/B longos desperdicam trafego e dificultam a personalizacao responsavel.

Este projeto implementa uma abordagem adaptativa que aprende, com base no historico de contatos anteriores (`poutcome`), qual segmento tem maior probabilidade de conversao, equilibrando exploracao e explotacao.

## Base de dados

Fonte: Kaggle - Bank Marketing (Henrique Yamahata)
https://www.kaggle.com/datasets/henriqueyamahata/bank-marketing

- 41.188 clientes, 21 colunas originais
- Target `y`: cliente subscreveu deposito a prazo (yes/no)
- Taxa de conversao global observada: 11.3%

## Tratamento de dados

- Remocao da coluna `duration` por vazamento temporal (so e conhecida apos a ligacao).
- Valores `"unknown"` em categoricas mantidos como categoria propria.
- Variaveis categoricas transformadas via one-hot encoding (10 colunas categoricas -> 53 colunas no dataset final).
- Target `y` convertido para binario (0 = nao converteu, 1 = converteu).

## Estrategia algoritmica

- Baseline: selecao aleatoria de cliente, sem segmentacao.
- Bandit (Thompson Sampling): os "bracos" sao os segmentos de `poutcome` (`nonexistent`, `failure`, `success`). Para cada braco, mantemos distribuicoes Beta atualizadas por sucesso/falha. A cada rodada, o algoritmo amostra cada Beta e escolhe o maior valor.

Taxas de conversao observadas por segmento:

| Segmento    | Taxa de conversao | N de clientes |
| ----------- | ----------------- | ------------- |
| nonexistent | 8.83%             | 35.563        |
| failure     | 14.23%            | 4.252         |
| success     | 65.11%            | 1.373         |

## Resultados

| Estrategia                              | Taxa de conversao (budget = 5.000 decisoes) |
| --------------------------------------- | ------------------------------------------- |
| Baseline (aleatorio)                    | 11.56%                                      |
| Bandit (Thompson Sampling por segmento) | **66.34%**                                  |

Na simulacao, o bandit converge rapidamente para priorizar o segmento `success`, superando a politica sem estrategia adaptativa.

## Golden set (5 casos)

| Cliente | Idade | Segmento (`poutcome`) | Decisao       |
| ------- | ----- | --------------------- | ------------- |
| 35577   | 32    | nonexistent           | NAO_PRIORIZAR |
| 13950   | 33    | nonexistent           | NAO_PRIORIZAR |
| 29451   | 25    | nonexistent           | NAO_PRIORIZAR |
| 32295   | 34    | nonexistent           | NAO_PRIORIZAR |
| 27477   | 53    | nonexistent           | NAO_PRIORIZAR |

Observacao: este recorte reflete a distribuicao real da base (~86% dos clientes em `nonexistent`).

## API demonstravel

Endpoint `/recomendar` em FastAPI que recebe `poutcome` e retorna decisao em tempo real.

Exemplo de chamada:

```bash
curl -X 'POST' 'http://127.0.0.1:8000/recomendar' \
  -H 'Content-Type: application/json' \
  -d '{"poutcome": "success"}'
```

Resposta exemplo:

```json
{ "cliente_poutcome": "success", "decisao": "OFERTAR" }
```

## MLOps

Parametros e metricas do experimento registrados via MLflow (tracking local em `sqlite:///mlflow.db`), incluindo:

- algoritmo
- segmentos utilizados
- budget de simulacao
- taxa de conversao baseline
- taxa de conversao bandit

## Arquitetura alvo em nuvem (AWS)

- Dados brutos/processados em S3
- Treino agendado com Lambda ou EventBridge
- Registro de modelo e metricas via MLflow em EC2 pequena (ou SageMaker Model Registry)
- API de recomendacao conteinerizada em ECS Fargate (ou Lambda + API Gateway)

## Como rodar

```bash
# 1) Clonar repositorio e entrar na pasta
git clone <url-do-seu-repo>
cd datathon-7mlet

# 2) Criar e ativar ambiente virtual
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate

# 3) Instalar dependencias
pip install -r requirements.txt

# 4) Garantir base em data/bank-additional-full.csv

# 5) Rodar notebook principal
# notebooks/01_eda.ipynb

# 6) Subir API
uvicorn app:app --reload
# Swagger: http://127.0.0.1:8000/docs

# 7) Abrir MLflow UI
mlflow ui --backend-store-uri sqlite:///notebooks/mlflow.db
# UI: http://127.0.0.1:5000
```

## Estrutura do repositorio

```text
datathon-7mlet/
├── data/                    # dataset (nao versionado - baixar do Kaggle)
├── notebooks/
│   └── 01_eda.ipynb         # EDA, tratamento, baseline e bandit
├── app.py                   # API FastAPI de recomendacao
├── requirements.txt
└── README.md
```

## Limitacoes e proximos passos

- A simulacao usa o proprio dataset historico e segmentacao simplificada por `poutcome`.
- O ganho alto observado deve ser interpretado no contexto dessa formulacao (nao equivale automaticamente a uplift causal em producao).
- Proximos passos recomendados:
  - ampliar feature set para contextual bandit
  - validar politicas com avaliacao off-policy
  - incluir monitoramento de drift e fairness
