# Etapa 1: Compilación de Flutter Web
FROM instrumentisto/flutter:3.24.3 AS build

WORKDIR /app

# Copiar archivos de dependencias e instalarlas
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get

# Copiar el código fuente
COPY . .

# Compilar la aplicación para Web
RUN flutter build web --release --dart-define=API_BASE_URL=https://www.api.ttr.lat

# Etapa 2: Servidor web de producción con Nginx
FROM nginx:alpine

# Copiar los estáticos de Flutter al directorio de Nginx
COPY --from=build /app/build/web /usr/share/nginx/html

# Copiar la configuración personalizada de Nginx para SPAs
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]