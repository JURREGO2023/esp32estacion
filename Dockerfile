FROM php:8.2-apache

# Instalar extensiones de MySQL esenciales para PHP
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Asegurar que Apache tenga los permisos correctos sobre tus archivos
RUN chown -R www-data:www-data /var/www/html