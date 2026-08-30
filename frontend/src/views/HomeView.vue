<script setup>
import { onMounted, ref } from 'vue'

import api from '../services/api'

const message = ref('Comprobando conexión con el backend...')
const connected = ref(false)

onMounted(async () => {
  try {
    const response = await api.get('/health')

    if (
      response.data.status === 'ok' &&
      response.data.database === 'connected'
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
      <RouterLink to="/categories" class="categories-link">
        Gestionar categorías
      </RouterLink>
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

.categories-link {
  display: inline-block;
  margin-top: 16px;
  color: #2457a7;
}
</style>