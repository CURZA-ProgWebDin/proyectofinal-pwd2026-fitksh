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

const auth = useAuth()

const users = ref([])
const roles = ref([])

const loading = ref(false)
const saving = ref(false)
const changingId = ref(null)
const editingId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')

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

function getErrorMessage(error) {
  return (
    error.response?.data?.error
    || error.response?.data?.msg
    || 'Ocurrió un error al procesar la solicitud.'
  )
}

function resetForm() {
  form.first_name = ''
  form.last_name = ''
  form.email = ''
  form.password = ''
  form.role_id = ''

  editingId.value = null
}

function validatePassword(password) {
  if (password.length < 8) {
    errorMessage.value = (
      'La contraseña debe tener al menos 8 caracteres.'
    )
    return false
  }

  if (![...password].some((character) => /[a-zA-Z]/.test(character))) {
    errorMessage.value = (
      'La contraseña debe contener al menos una letra.'
    )
    return false
  }

  if (![...password].some((character) => /\d/.test(character))) {
    errorMessage.value = (
      'La contraseña debe contener al menos un número.'
    )
    return false
  }

  return true
}

function validateForm() {
  if (!form.first_name.trim()) {
    errorMessage.value = 'El nombre es obligatorio.'
    return false
  }

  if (!form.last_name.trim()) {
    errorMessage.value = 'El apellido es obligatorio.'
    return false
  }

  if (!form.email.trim()) {
    errorMessage.value = 'El email es obligatorio.'
    return false
  }

  const roleId = Number(form.role_id)

  if (!Number.isInteger(roleId) || roleId <= 0) {
    errorMessage.value = 'Debe seleccionar un rol.'
    return false
  }

  if (!isEditing.value && !form.password) {
    errorMessage.value = (
      'La contraseña es obligatoria para crear un usuario.'
    )
    return false
  }

  if (
    form.password
    && !validatePassword(form.password)
  ) {
    return false
  }

  return true
}

async function loadData() {
  loading.value = true

  try {
    roles.value = await getRoles()
    users.value = await getUsers()
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    loading.value = false
  }
}

async function submitForm() {
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
    errorMessage.value = getErrorMessage(error)
  } finally {
    saving.value = false
  }
}

function startEditing(user) {
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
  clearMessages()
  resetForm()
}

async function changeUserStatus(user) {
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
    errorMessage.value = getErrorMessage(error)
  } finally {
    changingId.value = null
  }
}

onMounted(loadData)
</script>

<template>
  <main class="users-page">
    <header class="page-header">
      <div>
        <h1>Gestión de usuarios</h1>

        <p>
          Administrá clientes, administradores, roles y estados.
        </p>
      </div>

      <nav class="header-links">
        <RouterLink to="/categories">
          Categorías
        </RouterLink>

        <RouterLink to="/products">
          Productos
        </RouterLink>

        <RouterLink to="/">
          Volver al inicio
        </RouterLink>
      </nav>
    </header>

    <section class="form-card">
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
              required
            >
          </div>

          <div class="form-group">
            <label for="user-role">Rol</label>

            <select
              id="user-role"
              v-model.number="form.role_id"
              :disabled="isEditingCurrentUser"
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
            :disabled="saving || roles.length === 0"
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
            :disabled="saving"
            @click="cancelEditing"
          >
            Cancelar
          </button>
        </div>
      </form>
    </section>

    <p v-if="errorMessage" class="message error-message">
      {{ errorMessage }}
    </p>

    <p v-if="successMessage" class="message success-message">
      {{ successMessage }}
    </p>

    <section class="list-card">
      <h2>Usuarios registrados</h2>

      <p v-if="loading">Cargando usuarios...</p>

      <p v-else-if="users.length === 0">
        No hay usuarios registrados.
      </p>

      <div v-else class="table-container">
        <table>
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
                    changingId === user.id
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

<style scoped>
.users-page {
  width: min(100% - 32px, 1100px);
  margin: 0 auto;
  padding: 32px 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

.page-header h1,
.form-card h2,
.list-card h2 {
  margin-top: 0;
}

.page-header p {
  margin-bottom: 0;
  color: #666666;
}

.header-links {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.form-card,
.list-card {
  margin-bottom: 24px;
  padding: 24px;
  background-color: white;
  border: 1px solid #dddddd;
  border-radius: 8px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0 16px;
}

.form-group {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
}

.form-group small {
  color: #666666;
}

input,
select {
  width: 100%;
  padding: 10px;
  border: 1px solid #bbbbbb;
  border-radius: 4px;
}

.form-actions,
.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

button {
  padding: 9px 14px;
  color: white;
  cursor: pointer;
  background-color: #2457a7;
  border: 0;
  border-radius: 4px;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.secondary-button {
  color: #222222;
  background-color: #e5e5e5;
}

.danger-button {
  background-color: #b42318;
}

.success-button {
  background-color: #18794e;
}

.message {
  padding: 12px;
  border-radius: 4px;
}

.error-message {
  color: #b42318;
  background-color: #fee4e2;
}

.success-message {
  color: #18794e;
  background-color: #dcfae6;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #dddddd;
}

.status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
}

.active {
  color: #18794e;
  background-color: #dcfae6;
}

.inactive {
  color: #b42318;
  background-color: #fee4e2;
}

.current-user-label {
  color: #2457a7;
}

@media (max-width: 700px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>