<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from 'vue'
import { RouterLink } from 'vue-router'

import { useAuth } from '../stores/auth'
import {
  createUser,
  deactivateUser,
  getRoles,
  getUsers,
  updateUser,
} from '../services/userService'

import { getApiErrorMessage } from '../utils/apiErrors'

import { getUserFormError } from '../utils/userValidation'

const auth = useAuth()

const users = ref([])
const roles = ref([])

const isBusy = computed(() => {
  return (
    loading.value
    || saving.value
    || changingId.value !== null
  )
})
const loading = ref(false)
const saving = ref(false)
const changingId = ref(null)
const editingId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')
const loadError = ref('')

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  role_id: '',
})

const isEditing = computed(() => editingId.value !== null)

const isEditingCurrentUser = computed(() => {
  return editingId.value === auth.state.user?.id
})

function clearMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

function resetForm() {
  form.first_name = ''
  form.last_name = ''
  form.email = ''
  form.password = ''
  form.role_id = ''

  editingId.value = null
}


function validateForm() {
  errorMessage.value = getUserFormError(
    form,
    !isEditing.value,
  )

  if (errorMessage.value) {
    return false
  }

  const roleId = Number(form.role_id)

  if (!Number.isInteger(roleId) || roleId <= 0) {
    errorMessage.value = 'Debe seleccionar un rol.'
    return false
  }

  return true
}

async function loadData() {
  loadError.value = ''
  loading.value = true

  try {
    roles.value = await getRoles()
    users.value = await getUsers()
  } catch (error) {
    loadError.value = getApiErrorMessage(
      error,
      'No se pudo cargar la información. Intentá nuevamente.',
    )
  } finally {
    loading.value = false
  }
}

async function submitForm() {
  if (isBusy.value) {
    return
  }
  clearMessages()

  if (!validateForm()) {
    return
  }

  saving.value = true

  const userData = {
    first_name: form.first_name,
    last_name: form.last_name,
    email: form.email,
    role_id: Number(form.role_id),
  }

  if (form.password) {
    userData.password = form.password
  }

  try {
    if (isEditing.value) {
      const updatedUserId = editingId.value

      await updateUser(updatedUserId, userData)

      if (updatedUserId === auth.state.user?.id) {
        await auth.refreshCurrentUser()
      }

      successMessage.value = 'Usuario actualizado correctamente.'
    } else {
      await createUser(userData)
      successMessage.value = 'Usuario creado correctamente.'
    }

    resetForm()
    await loadData()
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error)
  } finally {
    saving.value = false
  }
}

function startEditing(user) {
  if (isBusy.value) {
    return
  }

  clearMessages()

  editingId.value = user.id
  form.first_name = user.first_name
  form.last_name = user.last_name
  form.email = user.email
  form.password = ''
  form.role_id = user.role_id

  window.scrollTo({
    top: 0,
    behavior: 'smooth',
  })
}

function cancelEditing() {
  if (isBusy.value) {
    return
  }

  clearMessages()
  resetForm()
}

async function changeUserStatus(user) {
  if (isBusy.value) {
    return
  }

  clearMessages()

  if (
    user.id === auth.state.user?.id
    && user.active
  ) {
    errorMessage.value = (
      'No podés desactivar tu propio usuario.'
    )
    return
  }

  if (
    user.active
    && !window.confirm(
      `¿Deseás desactivar al usuario "${user.email}"?`,
    )
  ) {
    return
  }

  changingId.value = user.id

  try {
    if (user.active) {
      await deactivateUser(user.id)
      successMessage.value = 'Usuario desactivado correctamente.'
    } else {
      await updateUser(user.id, {
        active: true,
      })

      successMessage.value = 'Usuario reactivado correctamente.'
    }

    if (editingId.value === user.id) {
      resetForm()
    }

    await loadData()
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error)
  } finally {
    changingId.value = null
  }
}

onMounted(loadData)
</script>

<template>
  <main class="admin-page users-page">
    <header class="page-header">
      <div>
        <h1>Gestión de usuarios</h1>

        <p>
          Administrá clientes, administradores, roles y estados.
        </p>
      </div>
      <nav class="header-links">
        <RouterLink
          to="/"
          class="button-link secondary-button"
        >
          Volver al inicio
        </RouterLink>
      </nav>
    </header>

    <section class="panel form-card">
      <h2>
        {{ isEditing ? 'Editar usuario' : 'Nuevo usuario' }}
      </h2>

      <form @submit.prevent="submitForm">
        <div class="form-grid">
          <div class="form-group">
            <label for="user-first-name">Nombre</label>

            <input
              id="user-first-name"
              v-model.trim="form.first_name"
              type="text"
              maxlength="80"
              :disabled="isBusy"
              required
            >
          </div>

          <div class="form-group">
            <label for="user-last-name">Apellido</label>

            <input
              id="user-last-name"
              v-model.trim="form.last_name"
              type="text"
              maxlength="80"
              :disabled="isBusy"
              required
            >
          </div>

          <div class="form-group">
            <label for="user-email">Email</label>

            <input
              id="user-email"
              v-model.trim="form.email"
              type="email"
              maxlength="150"
              :disabled="isBusy"
              required
            >
          </div>

          <div class="form-group">
            <label for="user-role">Rol</label>

            <select
              id="user-role"
              v-model.number="form.role_id"
              :disabled="isBusy || isEditingCurrentUser"
              required
            >
              <option disabled value="">
                Seleccioná un rol
              </option>

              <option
                v-for="role in roles"
                :key="role.id"
                :value="role.id"
              >
                {{ role.name }}
              </option>
            </select>

            <small v-if="isEditingCurrentUser">
              No podés cambiar tu propio rol.
            </small>
          </div>
        </div>

        <div class="form-group">
          <label for="user-password">
            Contraseña
          </label>

          <input
            id="user-password"
            v-model="form.password"
            type="password"
            minlength="8"
            maxlength="128"
            :required="!isEditing"
            autocomplete="new-password"
            :disabled="isBusy"
          >

          <small>
            {{
              isEditing
                ? 'Dejala vacía para conservar la contraseña actual.'
                : 'Mínimo 8 caracteres, una letra y un número.'
            }}
          </small>
        </div>

        <div class="form-actions">
          <button
            type="submit"
            :disabled="isBusy || roles.length === 0"
          >
            {{
              saving
                ? 'Guardando...'
                : isEditing
                  ? 'Guardar cambios'
                  : 'Crear usuario'
            }}
          </button>

          <button
            v-if="isEditing"
            type="button"
            class="secondary-button"
            :disabled="isBusy"
            @click="cancelEditing"
          >
            Cancelar
          </button>
        </div>
      </form>
    </section>

    <p v-if="errorMessage" class="message error-message" role="alert">
      {{ errorMessage }}
    </p>

    <p v-if="successMessage" class="message success-message" role="status">
      {{ successMessage }}
    </p>

    <section class="panel list-card">
      <h2>Usuarios registrados</h2>

      <p v-if="loading" class="list-state" role="status">Cargando usuarios...</p>

      <div
        v-else-if="loadError"
        class="message error-message load-error"
        role="alert"
      >
        <p>{{ loadError }}</p>

        <button
          type="button"
          class="secondary-button"
          :disabled="isBusy"
          @click="loadData"
        >
          Reintentar
        </button>
      </div>

      <p
        v-else-if="users.length === 0"
        class="empty-state"
      >
        No hay usuarios registrados.
      </p>

      <div
        v-else
        class="table-container"
        role="region"
        aria-label="Usuarios registrados"
        tabindex="0"
      >
        <table class="data-table">
          <thead>
            <tr>
              <th>Usuario</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="user in users"
              :key="user.id"
            >
              <td>
                {{ user.first_name }} {{ user.last_name }}

                <strong
                  v-if="user.id === auth.state.user?.id"
                  class="current-user-label"
                >
                  (vos)
                </strong>
              </td>

              <td>{{ user.email }}</td>

              <td>{{ user.role?.name }}</td>

              <td>
                <span
                  class="status"
                  :class="user.active ? 'active' : 'inactive'"
                >
                  {{ user.active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>

              <td class="row-actions">
                <button
                  type="button"
                  class="secondary-button"
                  :disabled="isBusy"
                  @click="startEditing(user)"
                >
                  Editar
                </button>

                <button
                  type="button"
                  :class="
                    user.active
                      ? 'danger-button'
                      : 'success-button'
                  "
                  :disabled="
                    isBusy
                    || (
                      user.id === auth.state.user?.id
                      && user.active
                    )
                  "
                  @click="changeUserStatus(user)"
                >
                  {{
                    user.active
                      ? 'Desactivar'
                      : 'Reactivar'
                  }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>