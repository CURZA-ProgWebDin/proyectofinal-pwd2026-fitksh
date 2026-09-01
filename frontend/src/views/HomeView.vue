<script setup>
import {
  onMounted,
  ref,
} from 'vue'
import {
  RouterLink,
  useRouter,
} from 'vue-router'

import api from '../services/api'
import { useAuth } from '../stores/auth'

const router = useRouter()
const auth = useAuth()

const message = ref('Comprobando conexión con el backend...')
const connected = ref(false)

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(async () => {
  try {
    const response = await api.get('/health')

    if (
      response.data.status === 'ok'
      && response.data.database === 'connected'
    ) {
      connected.value = true
      message.value = 'Vue, Flask y PostgreSQL están conectados.'
    }
  } catch (error) {
    message.value = 'No se pudo establecer conexión con el backend.'
    console.error(error)
  }
})
</script>

<template>
  <main class="home">
    <section class="status-card">
      <h1>Punto Mayorista</h1>

      <p>Trabajo Final de Programación Web Dinámica</p>

      <p :class="connected ? 'success' : 'error'">
        {{ message }}
      </p>

      <div
        v-if="auth.isAuthenticated()"
        class="session-info"
      >
        <p>
          Sesión iniciada como
          <strong>
            {{ auth.state.user.first_name }}
            {{ auth.state.user.last_name }}
          </strong>
        </p>

        <p>
          Rol: {{ auth.state.user.role.name }}
        </p>

        <button type="button" @click="logout">
          Cerrar sesión
        </button>
      </div>

      <div v-else class="management-links">
        <RouterLink to="/login">
          Iniciar sesión
        </RouterLink>

        <RouterLink to="/register">
          Crear cuenta
        </RouterLink>
      </div>

      <div
        v-if="
          auth.isAuthenticated()
          && auth.hasAnyRole(['ADMINISTRADOR'])
        "
        class="management-links"
      >
        <RouterLink to="/categories">
          Gestionar categorías
        </RouterLink>

        <RouterLink to="/products">
          Gestionar productos
        </RouterLink>

        <RouterLink to="/users">
          Gestionar usuarios
        </RouterLink>
      </div>
            <div
        v-if="
          auth.isAuthenticated()
          && auth.hasAnyRole(['CLIENTE'])
        "
        class="management-links"
      >
        <RouterLink to="/catalog">
          Ver catálogo
        </RouterLink>
        <RouterLink to="/cart">
          Ver carrito
        </RouterLink>
      </div>
    </section>
  </main>
</template>
<style scoped>
.home {
  display: flex;
  min-height: 100vh;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.status-card {
  width: 100%;
  max-width: 600px;
  padding: 32px;
  text-align: center;
  background-color: white;
  border: 1px solid #dddddd;
  border-radius: 8px;
}

.success {
  color: #18794e;
}

.error {
  color: #b42318;
}

.management-links {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
}

.session-info {
  margin-top: 24px;
  padding: 16px;
  background-color: #f5f5f5;
  border-radius: 6px;
}

.session-info button {
  padding: 9px 14px;
  color: white;
  cursor: pointer;
  background-color: #b42318;
  border: 0;
  border-radius: 4px;
}
</style>