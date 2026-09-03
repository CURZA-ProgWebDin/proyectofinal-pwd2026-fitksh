<script setup>
import {
  reactive,
  ref,
} from 'vue'
import {
  RouterLink,
  useRouter,
} from 'vue-router'

import { useAuth } from '../stores/auth'

const router = useRouter()
const auth = useAuth()

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  password_confirmation: '',
})

const submitting = ref(false)
const errorMessage = ref('')

function getErrorMessage(error) {
  return (
    error.response?.data?.error
    || 'No fue posible completar el registro.'
  )
}

async function submitRegistration() {
  errorMessage.value = ''

  if (form.password !== form.password_confirmation) {
    errorMessage.value = 'Las contraseñas no coinciden.'
    return
  }

  submitting.value = true

  try {
    await auth.register({
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      password: form.password,
    })

    await router.push({
      name: 'login',
      query: {
        registered: 'true',
      },
    })
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card">
      <h1>Crear cuenta</h1>

      <p v-if="errorMessage" class="auth-error">
        {{ errorMessage }}
      </p>

      <form
        class="auth-form"
        @submit.prevent="submitRegistration"
      >
        <div class="auth-field">
          <label for="register-first-name">Nombre</label>

          <input
            id="register-first-name"
            v-model.trim="form.first_name"
            type="text"
            maxlength="80"
            autocomplete="given-name"
            required
          >
        </div>

        <div class="auth-field">
          <label for="register-last-name">Apellido</label>

          <input
            id="register-last-name"
            v-model.trim="form.last_name"
            type="text"
            maxlength="80"
            autocomplete="family-name"
            required
          >
        </div>

        <div class="auth-field">
          <label for="register-email">Email</label>

          <input
            id="register-email"
            v-model.trim="form.email"
            type="email"
            maxlength="150"
            autocomplete="email"
            required
          >
        </div>

        <div class="auth-field">
          <label for="register-password">Contraseña</label>

          <input
            id="register-password"
            v-model="form.password"
            type="password"
            minlength="8"
            maxlength="128"
            autocomplete="new-password"
            required
          >

          <small>
            Mínimo 8 caracteres, una letra y un número.
          </small>
        </div>

        <div class="auth-field">
          <label for="register-confirmation">
            Repetir contraseña
          </label>

          <input
            id="register-confirmation"
            v-model="form.password_confirmation"
            type="password"
            minlength="8"
            maxlength="128"
            autocomplete="new-password"
            required
          >
        </div>

        <button type="submit" :disabled="submitting">
          {{
            submitting
              ? 'Registrando...'
              : 'Crear cuenta'
          }}
        </button>
      </form>

      <p>
        ¿Ya tenés una cuenta?
        <RouterLink to="/login">
          Iniciá sesión
        </RouterLink>
      </p>

      <RouterLink to="/">
        Volver al inicio
      </RouterLink>
    </section>
  </main>
</template>