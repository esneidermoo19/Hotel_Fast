# Etapa 1: Compilación de Flutter Web
FROM fservant/flutter:3.29.0 AS build

WORKDIR /app

ENV CI=true

# Copiar dependencias e instalar
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get

# Copiar código fuente
COPY . .

# Compilar Flutter Web
RUN flutter build web --release --dart-define=API_BASE_URL=https://www.api.ttr.lat

# Etapa 2: Servidor web ligero con Nginx
FROM nginx:alpine

# Copiar estáticos compilados
COPY --from=build /app/build/web /usr/share/nginx/html

# Copiar configuración de Nginx para SPAs
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]