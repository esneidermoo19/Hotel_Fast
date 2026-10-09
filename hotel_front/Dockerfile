# Etapa 1: Compilación de Flutter Web
FROM instrumentisto/flutter:3.27.1 AS build

WORKDIR /app

# Desactivar avisos de superusuario en CI
ENV CI=true

# Copiar el pubspec
COPY pubspec.yaml ./

# Si existe pubspec.lock, opcionalmente podrías ignorarlo o copiarlo; 
# copiar pubspec.yaml primero asegura que resuelva dependencias con el SDK actual
COPY pubspec.lock ./

RUN flutter pub get

# Copiar el resto del código fuente
COPY . .

# Compilar la aplicación para Web
RUN flutter build web --release --dart-define=API_BASE_URL=https://www.api.ttr.lat

# Etapa 2: Servidor web de producción con Nginx
FROM nginx:alpine

# Copiar los estáticos de Flutter
COPY --from=build /app/build/web /usr/share/nginx/html

# Copiar configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]