<script setup>
import {
  computed,
  reactive,
  ref,
} from 'vue'
import {
  RouterLink,
  useRoute,
  useRouter,
} from 'vue-router'

import { useAuth } from '../stores/auth'

import { getApiErrorMessage } from '../utils/apiErrors'

const route = useRoute()
const router = useRouter()
const auth = useAuth()

const form = reactive({
  email: '',
  password: '',
})

const submitting = ref(false)
const errorMessage = ref('')

const registrationMessage = computed(() => {
  if (route.query.registered === 'true') {
    return 'Registro realizado. Ya podés iniciar sesión.'
  }

  return ''
})

async function submitLogin() {

  if (submitting.value) {
    return
  }

  errorMessage.value = ''

  submitting.value = true

  try {
    await auth.login({
      email: form.email,
      password: form.password,
    })

    const requestedRedirect = route.query.redirect

    const redirect = (
      typeof requestedRedirect === 'string'
      && requestedRedirect.startsWith('/')
      && !requestedRedirect.startsWith('//')
    )
      ? requestedRedirect
      : '/'

    await router.push(redirect)
  } catch (error) {
    errorMessage.value = getApiErrorMessage(
      error,
      'No fue posible iniciar sesión.',
    )
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card">
      <h1>Iniciar sesión</h1>

      <p v-if="registrationMessage" class="auth-success">
        {{ registrationMessage }}
      </p>

      <p v-if="errorMessage" class="auth-error">
        {{ errorMessage }}
      </p>

      <form class="auth-form" @submit.prevent="submitLogin">
        <div class="auth-field">
          <label for="login-email">Email</label>

          <input
            id="login-email"
            v-model.trim="form.email"
            type="email"
            maxlength="150"
            autocomplete="email"
            required
          >
        </div>

        <div class="auth-field">
          <label for="login-password">Contraseña</label>

          <input
            id="login-password"
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            required
          >
        </div>

        <button type="submit" :disabled="submitting">
          {{ submitting ? 'Ingresando...' : 'Ingresar' }}
        </button>
      </form>

      <p>
        ¿No tenés una cuenta?
        <RouterLink to="/register">
          Registrate
        </RouterLink>
      </p>

      <RouterLink to="/">
        Volver al inicio
      </RouterLink>
    </section>
  </main>
</template>