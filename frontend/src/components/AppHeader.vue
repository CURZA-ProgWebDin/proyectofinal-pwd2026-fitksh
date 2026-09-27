<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { useAuth } from '../stores/auth'

const auth = useAuth()
const router = useRouter()
const loggingOut = ref(false)

async function logout() {
  if (loggingOut.value) {
    return
  }

  loggingOut.value = true

  try {
    await auth.logout()
    await router.push('/login')
  } finally {
    loggingOut.value = false
  }
}
</script>

<template>
  <header class="site-header">
    <div class="header-content">
      <RouterLink to="/" class="brand">
        <span>Punto</span> Mayorista
      </RouterLink>

      <nav
        v-if="auth.state.initialized"
        class="main-nav"
        aria-label="Navegación principal"
      >
        <RouterLink to="/">
          Inicio
        </RouterLink>

        <template v-if="auth.state.user">
          <template v-if="auth.hasAnyRole(['CLIENTE'])">
            <RouterLink to="/catalog">
              Catálogo
            </RouterLink>

            <RouterLink to="/cart">
              Carrito
            </RouterLink>

            <RouterLink to="/my-orders">
              Mis pedidos
            </RouterLink>
          </template>

          <template v-else-if="auth.hasAnyRole(['ADMINISTRADOR'])">
            <RouterLink to="/categories">
              Categorías
            </RouterLink>

            <RouterLink to="/products">
              Productos
            </RouterLink>

            <RouterLink to="/users">
              Usuarios
            </RouterLink>

            <RouterLink to="/admin/orders">
              Pedidos
            </RouterLink>
          </template>

          <button
            type="button"
            class="secondary-button"
            :disabled="loggingOut"
            @click="logout"
          >
            {{ loggingOut ? 'Cerrando sesión...' : 'Cerrar sesión' }}
          </button>
        </template>

        <template v-else>
          <RouterLink to="/login">
            Iniciar sesión
          </RouterLink>

          <RouterLink to="/register">
            Crear cuenta
          </RouterLink>
        </template>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.site-header {
  background-color: var(--color-surface);
  border-top: 4px solid var(--color-brand);
  border-bottom: 1px solid var(--color-border);
}

.header-content {
  display: flex;
  width: min(100% - 32px, 1200px);
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  margin: 0 auto;
  padding: 16px 0;
}

.brand {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--color-text);
  text-decoration: none;
  white-space: nowrap;
}

.brand span {
  color: var(--color-primary);
}

.main-nav {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.main-nav a {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  padding: 8px 12px;
  font-weight: 600;
  color: var(--color-muted);
  text-decoration: none;
  border-radius: 8px;
}

.main-nav a:hover {
  color: var(--color-text);
  background-color: var(--color-background);
}

.main-nav a.router-link-exact-active {
  font-weight: 700;
  color: var(--color-text);
  background-color: var(--color-highlight);
}

@media (max-width: 700px) {
  .header-content {
    align-items: flex-start;
    flex-direction: column;
  }

  .main-nav {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>