# Etapa 1: Compilacion de Flutter Web
FROM plugaggregator/flutter:latest AS build

WORKDIR /app

# Copiar archivos de dependencias e instalarlas
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get

# Copiar el resto del codigo fuente
COPY . .

# Compilar la aplicacion para Web apuntando a la API en produccion
RUN flutter build web --release --dart-define=API_BASE_URL=https://www.api.ttr.lat

# Etapa 2: Servidor web de produccion con Nginx
FROM nginx:alpine

# Copiar la compilacion de Flutter al directorio de Nginx
COPY --from=build /app/build/web /usr/share/nginx/html

# Copiar configuracion personalizada de Nginx para SPAs
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]