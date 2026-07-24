## Arquitetura-alvo em Nuvem (AWS)

Os dados brutos e processados seriam armazenados no S3, com o pipeline de treino
rodando em uma função Lambda ou job agendado (EventBridge). O modelo treinado e as
métricas seriam versionados no MLflow, hospedado em uma instância EC2 pequena ou
substituído pelo SageMaker Model Registry. O serviço de recomendação (nosso `app.py`)
seria empacotado em container e servido via ECS Fargate ou Lambda + API Gateway,
permitindo escalar conforme a demanda de chamadas dos canais digitais.
