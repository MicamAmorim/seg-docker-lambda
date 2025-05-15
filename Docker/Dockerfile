FROM public.ecr.aws/lambda/python:3.11

# Copia o código para /var/task (diretório padrão do runtime)
COPY . /var/task

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Dependências de sistema para OpenCV
RUN yum install -y \
      mesa-libGL mesa-libGLU libX11 libXext libpng \
      libjpeg-turbo libtiff libwebp \
    && yum clean all

# Define o handler (arquivo.nome_funcao)
# Define o entrypoint para a função Lambda
CMD ["api.lambda_handler"]
