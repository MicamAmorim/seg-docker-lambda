# 🖼️ Lambda Segmentation API

Uma **API de segmentação de imagens** construída em **Python** para execução em **AWS Lambda** com contêineres Docker. Esta API processa imagens via URL ou base64, retorna os contornos das áreas detectadas e foi otimizada para uso no **Amazon ECR**.

---

## 📁 Estrutura do Projeto

```
/SEG-DOCKER-LAMBDA
│
├── Docker/               # Configurações e modelos adicionais
│   └── models/           # Modelos para segmentação
├── src/                  # Código fonte principal
│   ├── api.py            # Ponto de entrada principal (handler)
│   ├── Dockerfile        # Configuração do contêiner para AWS Lambda
│   └── requirements.txt  # Dependências do Python
├── .gitignore            # Exclusões do Git
└── README.md             # Documentação do projeto

---

## 🚀 Funcionalidades

* Segmentação de imagens a partir de URLs ou base64
* Baixo tempo de inicialização (cold-start) com imagem otimizada
* Compatível com API Gateway, Lambda URLs e invocação direta
* Dockerfile simplificado para rápida implantação no AWS Lambda

---

## 📝 Pré-requisitos

* Conta AWS com permissões para Lambda, ECR e IAM
* Docker instalado e configurado
* Python 3.11 (para desenvolvimento local)

---

## 🔧 Como Construir e Enviar a Imagem para o ECR

1. **Clone o Repositório**

```bash
git clone https://github.com/<seu-usuario>/lambda-segmentation-api.git
cd lambda-segmentation-api
```

2. **Crie o Repositório no ECR**

```bash
aws ecr create-repository --repository-name lambda-segmentation-api --region us-east-2
```

3. **Construa a Imagem Docker**

```bash
docker build -t lambda-segmentation-api .
```

4. **Tag para o ECR**

```bash
docker tag lambda-segmentation-api:latest <account-id>.dkr.ecr.us-east-2.amazonaws.com/lambda-segmentation-api:latest
```

5. **Faça o Login no ECR**

```bash
aws ecr get-login-password --region us-east-2 | \
docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-2.amazonaws.com
```

6. **Envie a Imagem para o ECR**

```bash
docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/lambda-segmentation-api:latest
```

---

## 🚀 Criação da Função Lambda

```bash
aws lambda create-function \
  --function-name LambdaSegmentationAPI \
  --package-type Image \
  --code ImageUri=<account-id>.dkr.ecr.us-east-2.amazonaws.com/lambda-segmentation-api:latest \
  --role arn:aws:iam::<account-id>:role/LambdaSegmentationRole \
  --memory-size 3008 \
  --timeout 300 \
  --region us-east-2
```

---

## 🔗 Teste Rápido com Curl

```bash
curl -X POST https://<api-id>.execute-api.us-east-2.amazonaws.com/prod/segment \
-H "Content-Type: application/json" \
-d '{"body": "{\"image\":\"https://example.com/image.jpg\"}"}'
```

---

## 🧪 Teste Local

```bash
docker run -p 9000:8080 lambda-segmentation-api

curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
-H "Content-Type: application/json" \
-d '{"image": "https://example.com/image.jpg"}'
```

---

## 📄 Licença

Este projeto é licenciado sob a **MIT License**.

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir *Issues* ou enviar *Pull Requests*.

---

## 📧 Contato

**Autor:** Miqueias Amorim
**Email:** [contato@exemplo.com](mailto:kekoamorimsilva@gmail.com)
**LinkedIn:** [miqueiasamorimsantossilva](https://www.linkedin.com/in/miqueiasamorimsantossilva/)
