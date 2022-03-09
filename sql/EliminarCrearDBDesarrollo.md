# Eliminar y crear base de datos para desarrollo

Lo mas practico es crear un archivo SQL en `~/.sql/eliminar-y-crear-pjecz-plataforma-web.sql`

    DROP SCHEMA IF EXISTS public CASCADE;
    CREATE SCHEMA public;
    GRANT ALL ON SCHEMA public TO public;
    GRANT ALL ON SCHEMA public TO adminpjeczplataformaweb;

Y agregar estos aliases a `~/.bashrc.d/61-postgresql.sql`

    alias eliminar-y-crear-pjecz-plataforma-web="psql -f ~/.sql/eliminar-y-crear-pjecz-plataforma-web.sql pjecz_plataforma_web"
    echo "-- PostgreSQL eliminar tablas"
    echo "   eliminar-y-crear-pjecz-plataforma-web"
    echo

Asi puede ejecutar con su usuario con cuenta en postgresql de altos privilegios

    eliminar-y-crear-pjecz-plataforma-web
