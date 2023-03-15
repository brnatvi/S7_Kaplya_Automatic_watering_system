FROM php:8.1-fpm

# Update system core
RUN apt update -y && apt upgrade -y
RUN docker-php-ext-install mysqli && docker-php-ext-enable mysqli

# Start PHP-FPM
CMD ["php-fpm"]
