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

import { getApiErrorMessage } from '../utils/apiErrors'

const categories = ref([])
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
const categoryNameInput = ref(null)

const form = reactive({
  name: '',
  description: '',
})

const isEditing = computed(() => editingId.value !== null)

function clearMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

function resetForm() {
  form.name = ''
  form.description = ''
  editingId.value = null
}

async function loadCategories() {
  loadError.value = ''

  loading.value = true

  try {
    categories.value = await getCategories()
  } catch (error) {
    loadError.value = getApiErrorMessage(
      error,
      'No se pudo cargar las categorías. Intentá nuevamente.',
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
    errorMessage.value = getApiErrorMessage(error)
  } finally {
    saving.value = false
  }
}

function startEditing(category) {
  if (isBusy.value) {
    return
  }

  clearMessages()

  editingId.value = category.id
  form.name = category.name
  form.description = category.description ?? ''

  categoryNameInput.value?.focus()
}

function cancelEditing() {
  if (isBusy.value) {
    return
  }
  clearMessages()
  resetForm()
}

async function changeCategoryStatus(category) {
  if (isBusy.value) {
    return
  }
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
    errorMessage.value = getApiErrorMessage(error)
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
        <p>Organizá las categorías de los productos.</p>
      </div>

      <RouterLink
        to="/"
        class="button-link secondary-button"
      >
        Volver al inicio
      </RouterLink>
    </header>

    <p
      v-if="errorMessage"
      class="message error-message"
      role="alert"
    >
      {{ errorMessage }}
    </p>

    <p
      v-if="successMessage"
      class="message success-message"
      role="status"
    >
      {{ successMessage }}
    </p>

    <section class="panel form-card">
      <h2>
        {{ isEditing ? 'Editar categoría' : 'Nueva categoría' }}
      </h2>

      <form
        class="category-form"
        @submit.prevent="submitForm"
      >
        <div class="form-field">
          <label for="category-name">Nombre</label>

          <input
            id="category-name"
            ref="categoryNameInput"
            v-model.trim="form.name"
            type="text"
            maxlength="100"
            required
            aria-describedby="category-name-help"
            :disabled="isBusy"
          >

          <small id="category-name-help">
            Obligatorio. Hasta 100 caracteres.
          </small>
        </div>

        <div class="form-field">
          <label for="category-description">
            Descripción (opcional)
          </label>

          <textarea
            id="category-description"
            v-model.trim="form.description"
            maxlength="255"
            rows="3"
            aria-describedby="category-description-help"
            :disabled="isBusy"
          />

          <small id="category-description-help">
            Hasta 255 caracteres.
          </small>
        </div>

        <div class="form-actions">
          <button type="submit" :disabled="isBusy">
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
            :disabled="isBusy"
            @click="cancelEditing"
          >
            Cancelar edición
          </button>
        </div>
      </form>
    </section>

    <section class="panel list-card">
      <h2>Categorías registradas</h2>

      <p v-if="loading" class="list-state" role="status">
        Cargando categorías...
      </p>

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
          @click="loadCategories"
        >
          Reintentar
        </button>
      </div>

      <div
        v-else-if="categories.length === 0"
        class="empty-state"
      >
        <h3>Todavía no hay categorías</h3>
        <p>Completá el formulario para crear la primera.</p>
      </div>

      <div
        v-else
        class="table-container"
        role="region"
        aria-label="Categorías registradas"
        tabindex="0"
      >
        <table class="data-table categories-table">
          <thead>
            <tr>
              <th scope="col">Nombre</th>
              <th scope="col">Descripción</th>
              <th scope="col">Estado</th>
              <th scope="col">Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="category in categories"
              :key="category.id"
              :class="{ 'editing-row': editingId === category.id }"
            >
              <td class="category-name">
                <strong>{{ category.name }}</strong>
              </td>

              <td class="category-description">
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

              <td>
                <div class="row-actions">
                  <button
                    type="button"
                    class="secondary-button"
                    :disabled="isBusy"
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
                    :disabled="isBusy"
                    @click="changeCategoryStatus(category)"
                  >
                    {{
                      changingId === category.id
                        ? 'Actualizando...'
                        : category.active
                          ? 'Desactivar'
                          : 'Reactivar'
                    }}
                  </button>
                </div>
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
  width: min(100% - 32px, 1200px);
  margin: 0 auto;
  padding: 32px 0 48px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
}

.page-header p {
  margin: 8px 0 0;
  color: var(--color-muted);
}

.page-header .button-link {
  flex-shrink: 0;
}

.form-card {
  margin-bottom: 24px;
}

.form-card h2,
.list-card h2 {
  margin: 0 0 20px;
}

.category-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.form-field {
  display: grid;
  min-width: 0;
  align-content: start;
  gap: 8px;
}

.form-field input,
.form-field textarea {
  width: 100%;
  min-width: 0;
}

.form-field small {
  color: var(--color-muted);
}

.form-actions,
.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.form-actions {
  grid-column: 1 / -1;
}

.row-actions {
  min-width: 220px;
}

.list-state {
  color: var(--color-muted);
}

.load-error p {
  margin: 0 0 12px;
}

.empty-state {
  padding: 24px 0;
  text-align: center;
}

.empty-state h3 {
  margin: 0 0 8px;
}

.empty-state p {
  margin: 0;
  color: var(--color-muted);
}

.categories-table {
  min-width: 720px;
}

.category-name {
  min-width: 150px;
  max-width: 240px;
  overflow-wrap: anywhere;
}

.category-description {
  min-width: 180px;
  max-width: 420px;
  overflow-wrap: anywhere;
}

.editing-row {
  background-color: var(--color-background);
}

.status {
  display: inline-block;
  padding: 4px 10px;
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
  border-radius: 16px;
}

.active {
  color: var(--color-success);
  background-color: var(--color-success-background);
}

.inactive {
  color: var(--color-muted);
  background-color: var(--color-background);
}

@media (max-width: 700px) {
  .page-header {
    align-items: stretch;
    flex-direction: column;
  }

  .category-form {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>