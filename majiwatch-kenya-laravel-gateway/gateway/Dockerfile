FROM node:24-alpine AS assets
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY resources resources
COPY vite.config.js postcss.config.js tailwind.config.js ./
RUN npm run build

FROM php:8.3-fpm-alpine
RUN apk add --no-cache icu-dev libzip-dev oniguruma-dev postgresql-dev bash \
  && docker-php-ext-install intl zip pdo pdo_pgsql

WORKDIR /var/www/html

COPY composer.json composer.lock ./
COPY artisan artisan
COPY app app
COPY bootstrap bootstrap
COPY config config
COPY database database
COPY public public
COPY resources resources
COPY routes routes
COPY storage storage

COPY --from=assets /app/public/build /var/www/html/public/build

COPY docker/entrypoint.sh /entrypoint.sh

ENV GATEWAY_STATE_DIR=/state

RUN mkdir -p /state \
  && chown -R www-data:www-data /var/www/html /state

RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" \
  && php composer-setup.php --install-dir=/usr/local/bin --filename=composer \
  && rm composer-setup.php \
  && composer install --no-dev --no-interaction --prefer-dist --no-progress \
  && php artisan optimize:clear || true

CMD ["/entrypoint.sh"]

