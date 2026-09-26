# Punto Mayorista — Frontend

Interfaz de Punto Mayorista desarrollada con Vue 3.

Utiliza Vue Router para la navegación y Axios para comunicarse con la API REST de Flask.

Permite registrarse, iniciar sesión, consultar el catálogo, gestionar el carrito y consultar pedidos. Los administradores también pueden gestionar categorías, productos, usuarios y pedidos.

## Desarrollo local

Se requieren las dependencias instaladas y un archivo `.env` configurado a partir de `.env.example`.

Desde la carpeta `frontend`:

```powershell
npm run dev
```

Para utilizar las funciones de la aplicación, Flask y PostgreSQL deben estar en ejecución.

## Compilación

Desde la carpeta `frontend`:

```powershell
npm run build
```

Los archivos compilados se generan en `dist/`.

## Documentación relacionada

- [Consigna del trabajo y diagrama de base de datos](../readme.md).