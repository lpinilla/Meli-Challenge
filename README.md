# Meli-Challenge

Desafío Meli

## Contexto

El equipo de Seguridad Informática de Mercado Libre, se encarga de hacer las reválidas anuales del proceso
de clasificación de la información. Sabemos por el feedback del año pasado, que generar reuniones
presenciales para validar esto, es un poco molesto para el usuario, más aún cuando las bases no son muy
críticas. Por eso y dado que estamos cerca de la fecha de reválida de bases de datos, este año queremos
hacerlo de manera automática. Pensamos pedirle a los managers de las bases más críticas que nos den el
OK por mail.

## Objetivo

Generar un programa que, a partir de los archivos dados, guarde su contenido en una base de datos y por
cada registro guardado, en donde la clasificación sea alta (high), envíe un email al manager del owner
pidiendo su OK respecto de la clasificación.

# Diseño de la solución

## Supuestos tomados

Los siguientes supuestos fueron tenidos en cuenta para el diseño de la solución:

- El archivo de entrada CSV incluye el campo `user_mail` que indica el mail de dicho empleado
- El archivo de entrada CSV no incluye campos vacíos o malformados
- El archivo de entrada JSON puede contener campos vacíos

Se considera que una entrada del información de bases de datos, proveniente del archivo JSON es válida sii:

1. Tiene los tres campos requeridos (`db_name`, `owner_id` y `classification`)
2. Los campos no son el valor nulo `None`
3. El valor `owner_id` no es negativo ni está vacío (`''`)
4. El valor del campo `classification` está en el rango `[0;3]`

En caso de que no se cumplan los requisitos, la entrada no será añadida a la base de datos y se devolverá por la respuesta del request

## Arquitectura candidata

![](diagrama_solucion.png)

## Esquema de DB

El siguiente diagrama representa el esquema de la base de datos

![](db_schema.png)

# Cómo correr la herramienta

## Requisitos

Es necesario tener instalado git, [docker](https://www.docker.com/) y [docker compose](https://docs.docker.com/compose/)

## Descargando el repositorio

Simplemente utilizando `git clone https://github.com/lpinilla/Meli-Challenge.git`

## Levantando servicios

Antes de levantar los servicios, es importante crear el archivo `.env` con las variables de entorno antes de correr la aplicación. Puede usar el template `.env.example` corriendo `cp .env.example .env` aunque se desalienta el uso de estas variables en producción.

Accediendo a la carpeta raíz del repositorio, puede ejecutar `docker compose up` para levantar los servicios. Este comando descargará las imágenes de
`postgres` y `mailhog` mientras que creará y levantará la imágen principal de la API.

## Usando la aplicación

Para utilizar la aplicación, es importante primero cargar el archivo `csv` de empleados y luego el archivo de `json` con la información de las bases de datos. En caso de realizarlo al revéz, el sistema rechazará el request.

Para probar el sistema, puede probar los archivos `employee_data.csv` y `db_info.json`.

Sitúese en la carpeta raíz del proyecto y corra el siguiente comando para cargar los empleados:

`curl -X POST localhost:8080/employees/upload -F "file=@./employee_data.csv"`

Luego, puede correr el siguiente comando para levantar la información de las bases de datos:

`curl -X POST localhost:8080/db_info/upload -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@./dbs_data.json"`

Ambos endpoint indicarán el resultado obtenido del request.

Si quiere ver todas las bases de datos que no tienen clasificación, puede ejecutar:

`curl localhost:8080/db_info/unclassified`.

Por último, para ejecutar las notificaciones, puede correr `curl -X POST localhost:8080/notify`.

El archivo `curl_test_commands.sh` incluye todos los comandos anteriores para realizar el testeo de forma más automatizada.

Puede ver los mails "enviados" accediendo al portal web de mailhog: `http://localhost:8025`

La documentación de los endpoints se puede ver en `http://localhost:8080/docs`.
