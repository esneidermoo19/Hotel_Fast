# Etapa 1: Compilación de Flutter Web sobre una imagen limpia de Debian
FROM debian:bookworm-slim AS build

# Instalar dependencias básicas para Flutter y Git
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    && rm -rf /var/lib/apt/get/lists/*

# Descargar e instalar Flutter SDK (3.27.x / 3.29.x compatible)
RUN git clone https://github.com/flutter/flutter.git -b stable /sdks/flutter
ENV PATH="/sdks/flutter/bin:${PATH}"

# Habilitar soporte Web y configurar entorno
RUN flutter config --enable-web \
    && flutter doctor

WORKDIR /app

# Copiar dependencias e instalarlas
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get

# Copiar el código fuente
COPY . .

# Compilar la aplicación para Web
RUN flutter build web --release --dart-define=API_BASE_URL=https://www.api.ttr.lat

# Etapa 2: Servidor web de producción ligero con Nginx
FROM nginx:alpine

# Copiar los estáticos compilados
COPY --from=build /app/build/web /usr/share/nginx/html

# Copiar configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]