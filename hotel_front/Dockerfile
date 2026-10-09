# Etapa 1: Compilación de Flutter Web con imagen oficial pública en Docker Hub
FROM mobiledevops/flutter-sdk:3.27.0 AS build

WORKDIR /app

# Copiar dependencias e instalarlas
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get

# Copiar el código fuente
COPY . .

# Compilar la aplicación para Web apuntando a la API en producción
RUN flutter build web --release --dart-define=API_BASE_URL=https://www.api.ttr.lat

# Etapa 2: Servidor web de producción con Nginx
FROM nginx:alpine

# Copiar la compilación de Flutter al directorio de Nginx
COPY --from=build /app/build/web /usr/share/nginx/html

# Copiar configuración personalizada de Nginx para SPAs
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]