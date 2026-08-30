<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from 'vue'
import { RouterLink } from 'vue-router'

import {
  createCategory,
  deactivateCategory,
  getCategories,
  updateCategory,
} from '../services/categoryService'

const categories = ref([])
const loading = ref(false)
const saving = ref(false)
const changingId = ref(null)
const editingId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')

const form = reactive({
  name: '',
  description: '',
})

const isEditing = computed(() => editingId.value !== null)

function clearMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

function getErrorMessage(error) {
  return (
    error.response?.data?.error
    || 'Ocurrió un error al procesar la solicitud.'
  )
}

function resetForm() {
  form.name = ''
  form.description = ''
  editingId.value = null
}

async function loadCategories() {
  loading.value = true

  try {
    categories.value = await getCategories()
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    loading.value = false
  }
}

async function submitForm() {
  clearMessages()

  if (!form.name.trim()) {
    errorMessage.value = 'El nombre de la categoría es obligatorio.'
    return
  }

  saving.value = true

  const categoryData = {
    name: form.name,
    description: form.description,
  }

  try {
    if (isEditing.value) {
      await updateCategory(editingId.value, categoryData)
      successMessage.value = 'Categoría actualizada correctamente.'
    } else {
      await createCategory(categoryData)
      successMessage.value = 'Categoría creada correctamente.'
    }

    resetForm()
    await loadCategories()
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    saving.value = false
  }
}

function startEditing(category) {
  clearMessages()

  editingId.value = category.id
  form.name = category.name
  form.description = category.description ?? ''
}

function cancelEditing() {
  clearMessages()
  resetForm()
}

async function changeCategoryStatus(category) {
  clearMessages()

  if (
    category.active
    && !window.confirm(
      `¿Deseás desactivar la categoría "${category.name}"?`,
    )
  ) {
    return
  }

  changingId.value = category.id

  try {
    if (category.active) {
      await deactivateCategory(category.id)
      successMessage.value = 'Categoría desactivada correctamente.'
    } else {
      await updateCategory(category.id, {
        active: true,
      })

      successMessage.value = 'Categoría reactivada correctamente.'
    }

    if (editingId.value === category.id) {
      resetForm()
    }

    await loadCategories()
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    changingId.value = null
  }
}

onMounted(loadCategories)
</script>

<template>
  <main class="categories-page">
    <header class="page-header">
      <div>
        <h1>Gestión de categorías</h1>
        <p>
          Creá, modificá, desactivá o reactivá las categorías
          disponibles.
        </p>
      </div>

      <RouterLink to="/" class="back-link">
        Volver al inicio
      </RouterLink>
    </header>

    <section class="form-card">
      <h2>
        {{ isEditing ? 'Editar categoría' : 'Nueva categoría' }}
      </h2>

      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label for="category-name">Nombre</label>

          <input
            id="category-name"
            v-model.trim="form.name"
            type="text"
            maxlength="100"
            required
          >
        </div>

        <div class="form-group">
          <label for="category-description">
            Descripción
          </label>

          <textarea
            id="category-description"
            v-model.trim="form.description"
            maxlength="255"
            rows="3"
          />
        </div>

        <div class="form-actions">
          <button type="submit" :disabled="saving">
            {{
              saving
                ? 'Guardando...'
                : isEditing
                  ? 'Guardar cambios'
                  : 'Crear categoría'
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
      <h2>Categorías registradas</h2>

      <p v-if="loading">Cargando categorías...</p>

      <p v-else-if="categories.length === 0">
        Todavía no hay categorías registradas.
      </p>

      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="category in categories"
              :key="category.id"
            >
              <td>{{ category.name }}</td>

              <td>
                {{ category.description || 'Sin descripción' }}
              </td>

              <td>
                <span
                  class="status"
                  :class="category.active ? 'active' : 'inactive'"
                >
                  {{ category.active ? 'Activa' : 'Inactiva' }}
                </span>
              </td>

              <td class="row-actions">
                <button
                  type="button"
                  class="secondary-button"
                  @click="startEditing(category)"
                >
                  Editar
                </button>

                <button
                  type="button"
                  :class="
                    category.active
                      ? 'danger-button'
                      : 'success-button'
                  "
                  :disabled="changingId === category.id"
                  @click="changeCategoryStatus(category)"
                >
                  {{
                    category.active
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
.categories-page {
  width: min(100% - 32px, 1000px);
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

.back-link {
  color: #2457a7;
}

.form-card,
.list-card {
  margin-bottom: 24px;
  padding: 24px;
  background-color: white;
  border: 1px solid #dddddd;
  border-radius: 8px;
}

.form-group {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
}

input,
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #bbbbbb;
  border-radius: 4px;
}

textarea {
  resize: vertical;
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

@media (max-width: 600px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>