<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import { useAuth } from '../stores/auth'

const auth = useAuth()

const isAdmin = computed(() => {
  return auth.hasAnyRole(['ADMINISTRADOR'])
})

const shortcuts = computed(() => {
  if (isAdmin.value) {
    return [
      {
        title: 'Categorías',
        description: 'Organizá las categorías del catálogo.',
        to: '/categories',
      },
      {
        title: 'Productos',
        description: 'Actualizá productos, precios y stock.',
        to: '/products',
      },
      {
        title: 'Usuarios',
        description: 'Gestioná cuentas, roles y estado de los usuarios.',
        to: '/users',
      },
      {
        title: 'Pedidos',
        description: 'Consultá los pedidos y actualizá sus estados.',
        to: '/admin/orders',
      },
    ]
  }

  if (auth.hasAnyRole(['CLIENTE'])) {
    return [
      {
        title: 'Catálogo',
        description: 'Consultá los productos disponibles y sus precios.',
        to: '/catalog',
      },
      {
        title: 'Mi carrito',
        description: 'Revisá las cantidades y confirmá tu pedido.',
        to: '/cart',
      },
      {
        title: 'Mis pedidos',
        description: 'Consultá el detalle y el estado de tus pedidos.',
        to: '/my-orders',
      },
    ]
  }

  return []
})
</script>

<template>
  <main class="home-page">
    <section class="hero" aria-labelledby="home-title">
      <p class="hero-label">
        Punto Mayorista · Viedma
      </p>

      <p v-if="auth.state.user" class="welcome">
        Hola, {{ auth.state.user.first_name }}.
      </p>

      <h1 id="home-title">
        {{
          isAdmin
            ? 'Administración del negocio'
            : 'Elegí tus golosinas y armá tu pedido.'
        }}
      </h1>

      <p v-if="isAdmin" class="hero-description">
        Gestioná categorías, productos, usuarios y pedidos
        desde un mismo lugar.
      </p>

      <p v-else class="hero-description">
        Encontrá tus productos favoritos, agregalos al carrito
        y confirmá tu pedido. Después podés consultar su estado
        desde tu cuenta.
      </p>

      <div class="hero-actions">
        <template v-if="!auth.state.user">
          <RouterLink to="/login" class="button-link">
            Iniciar sesión
          </RouterLink>

          <RouterLink
            to="/register"
            class="button-link secondary-button"
          >
            Crear cuenta
          </RouterLink>
        </template>

        <RouterLink
          v-else-if="isAdmin"
          to="/admin/orders"
          class="button-link"
        >
          Gestionar pedidos
        </RouterLink>

        <RouterLink
          v-else-if="auth.hasAnyRole(['CLIENTE'])"
          to="/catalog"
          class="button-link"
        >
          Ver catálogo
        </RouterLink>
      </div>
    </section>

    <section
      v-if="shortcuts.length > 0"
      class="home-section"
      aria-labelledby="shortcuts-title"
    >
      <h2 id="shortcuts-title">
        Accesos rápidos
      </h2>

      <div class="shortcuts-grid">
        <RouterLink
          v-for="shortcut in shortcuts"
          :key="shortcut.to"
          :to="shortcut.to"
          class="shortcut-card"
        >
          <h3>{{ shortcut.title }}</h3>
          <p>{{ shortcut.description }}</p>
          <span>Abrir sección →</span>
        </RouterLink>
      </div>
    </section>

    <section
      v-if="!auth.state.user"
      class="home-section"
      aria-labelledby="steps-title"
    >
      <h2 id="steps-title">
        ¿Cómo hacer tu pedido?
      </h2>

      <ol class="steps">
        <li>Creá una cuenta o iniciá sesión.</li>
        <li>Elegí productos y cantidades desde el catálogo.</li>
        <li>Revisá el carrito y confirmá tu pedido.</li>
        <li>Consultá su estado desde Mis pedidos.</li>
      </ol>
    </section>
  </main>
</template>

<style scoped>
.home-page {
  width: min(100% - 32px, 1200px);
  margin: 0 auto;
  padding: 32px 0 48px;
}

.hero {
  padding: 40px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-top: 4px solid var(--color-brand);
  border-radius: 12px;
}

.hero-label {
  margin: 0 0 16px;
  font-weight: 700;
  color: var(--color-primary);
}

.welcome {
  margin: 0 0 12px;
  font-weight: 600;
}

.hero h1 {
  max-width: 800px;
  margin: 0;
  font-size: 2.5rem;
}

.hero-description {
  max-width: 700px;
  margin: 20px 0;
  color: var(--color-muted);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.home-section {
  margin-top: 32px;
}

.home-section h2 {
  margin: 0 0 20px;
}

.shortcuts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.shortcut-card {
  display: flex;
  flex-direction: column;
  padding: 24px;
  color: var(--color-text);
  text-decoration: none;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.shortcut-card:hover {
  border-color: var(--color-primary);
}

.shortcut-card:hover h3 {
  text-decoration: underline;
}

.shortcut-card h3 {
  margin: 0 0 12px;
  font-size: 1.15rem;
}

.shortcut-card p {
  margin: 0 0 20px;
  color: var(--color-muted);
}

.shortcut-card span {
  margin-top: auto;
  font-weight: 600;
  color: var(--color-primary);
}

.steps {
  margin: 0;
  padding-left: 24px;
  color: var(--color-muted);
}

.steps li + li {
  margin-top: 12px;
}

@media (max-width: 600px) {
  .hero {
    padding: 24px;
  }

  .hero h1 {
    font-size: 1.9rem;
  }

  .hero-actions {
    flex-direction: column;
  }
}
</style>