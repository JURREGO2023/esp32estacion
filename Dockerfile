
FROM php:8.2-apache

# 1. Copiar todos tus archivos de Git a la carpeta pública de Apache
COPY . /var/www/html/

# 2. Instalar extensiones de MySQL para que tu estación ESP32 pueda guardar datos
RUN docker-php-ext-install mysqli pdo pdo_mysql

# 3. Darle permisos absolutos a Apache para que no te bloquee
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html