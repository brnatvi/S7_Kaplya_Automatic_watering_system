FROM php:8.1-fpm

# Update system core
RUN sudo apt-get update -y && sudo apt-get upgrade -y
RUN docker-php-ext-install mysqli && docker-php-ext-enable mysqli

# Start PHP-FPM
CMD ["php-fpm"]
