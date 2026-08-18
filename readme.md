# Trabajo Final Integrador – Programación Web Dinámica  
Tecnicatura Universitaria en Desarrollo Web  

## Objetivo general  
Desarrollar una aplicación web de elección libre aplicando los conceptos vistos durante la cursada, integrando frontend, backend y base de datos bajo una arquitectura MVC, con comunicación mediante API REST.

---

## Tecnologías obligatorias  
- Frontend: Vue.js  
- Backend: Flask (uso de Blueprints obligatorio)  
- Base de datos: PostgreSQL  
- ORM: SQLAlchemy  
- Arquitectura: MVC (Modelo – Vista – Controlador)  
- Comunicación: API REST (Axios por parte del frontend)

---

## Requisitos funcionales obligatorios  

### 1. Autenticación y autorización  
La aplicación deberá implementar un sistema de autenticación basado en tokens (JWT), con las siguientes características:

- Login de usuarios  
- Generación y validación de JWT  
- Sistema de roles (al menos dos niveles: usuario y administrador o equivalente)  
- Protección de rutas en backend mediante verificación de token  
- Protección de rutas en frontend mediante Vue Router Navigation Guards  
- Mecanismo de renovación de token (refresh token o equivalente), pudiendo ser anticipado antes de su expiración  

---

### 2. Módulos del sistema  
La aplicación deberá contar con:

- Al menos 4 módulos funcionales  
- Al menos 2 módulos con relación directa entre sí  

Cada módulo debe implementar operaciones CRUD completas:
- Creación  
- Lectura  
- Actualización  
- Eliminación  

---

### 3. Backend (Flask)  
El backend deberá:

- Estar organizado mediante Blueprints  
- Separar claramente modelos, controladores y rutas  
- Implementar lógica de negocio de forma desacoplada del acceso a datos  
- Exponer una API REST consumida por el frontend  
- Gestionar autenticación y autorización basada en JWT  

---

### 4. Frontend (Vue.js)  
El frontend deberá:

- Consumir completamente la API REST del backend  
- Implementar Vue Router para navegación entre vistas  
- Utilizar Navigation Guards para protección de rutas  
- Incluir formularios con validaciones básicas  
- Mantener una interfaz consistente y funcional  

---

### 5. Base de datos  
La base de datos deberá:

- Estar modelada de forma coherente con el dominio de la aplicación  
- Incluir relaciones entre entidades cuando corresponda  
- Ser accedida exclusivamente a través del backend  

---
git 
## Consideraciones generales  
- La aplicación debe ser completamente funcional.  
- No se aceptarán proyectos que no cumplan los requisitos mínimos.  
- Se valorará la coherencia del diseño del sistema y la correcta separación de responsabilidades.  
- Se espera que el estudiante seleccione un dominio de aplicación propio, evitando replicar ejemplos vistos en clase de forma literal.  