<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from 'vue'
import { RouterLink } from 'vue-router'

import { getCategories } from '../services/categoryService'
import {
  createProduct,
  deactivateProduct,
  getProducts,
  updateProduct,
} from '../services/productService'

import { formatPrice } from '../utils/formatters'

import { getApiErrorMessage } from '../utils/apiErrors'

const products = ref([])
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

const MAX_PRICE = 9999999999.99
const MAX_INTEGER = 2147483647

const form = reactive({
  category_id: '',
  name: '',
  description: '',
  retail_price: '',
  wholesale_price: '',
  minimum_wholesale_quantity: 1,
  stock: 0,
  image_url: '',
})

const isEditing = computed(() => editingId.value !== null)

const activeCategories = computed(() => {
  return categories.value.filter((category) => category.active)
})

const availableCategories = computed(() => {
  return categories.value.filter((category) => {
    return (
      category.active
      || category.id === Number(form.category_id)
    )
  })
})

function clearMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

function resetForm() {
  form.category_id = ''
  form.name = ''
  form.description = ''
  form.retail_price = ''
  form.wholesale_price = ''
  form.minimum_wholesale_quantity = 1
  form.stock = 0
  form.image_url = ''

  editingId.value = null
}

function validateForm() {
  const categoryId = Number(form.category_id)
  const retailPrice = Number(form.retail_price)
  const wholesalePrice = Number(form.wholesale_price)
  const minimumQuantity = Number(
    form.minimum_wholesale_quantity,
  )
  const stock = Number(form.stock)

  if (!Number.isInteger(categoryId) || categoryId <= 0) {
    errorMessage.value = 'Debe seleccionar una categoría.'
    return false
  }

  if (!form.name.trim()) {
    errorMessage.value = 'El nombre del producto es obligatorio.'
    return false
  }

  if (
    form.retail_price === ''
    || !Number.isFinite(retailPrice)
    || retailPrice < 0
  ) {
    errorMessage.value = 'El precio minorista no es válido.'
    return false
  }

  if (
    form.wholesale_price === ''
    || !Number.isFinite(wholesalePrice)
    || wholesalePrice < 0
  ) {
    errorMessage.value = 'El precio mayorista no es válido.'
    return false
  }

  if (
    !Number.isInteger(minimumQuantity)
    || minimumQuantity <= 0
  ) {
    errorMessage.value = (
      'La cantidad mínima mayorista debe ser mayor que cero.'
    )
    return false
  }

  if (!Number.isInteger(stock) || stock < 0) {
    errorMessage.value = (
      'El stock debe ser un entero mayor o igual que cero.'
    )
    return false
  }

  if (form.stock === '') {
    errorMessage.value = 'El stock es obligatorio.'
    return false
  }

  if (
    retailPrice > MAX_PRICE
    || wholesalePrice > MAX_PRICE
  ) {
    errorMessage.value = (
      'Los precios no pueden superar 9999999999.99.'
    )
    return false
  }

  if (
    minimumQuantity > MAX_INTEGER
    || stock > MAX_INTEGER
  ) {
    errorMessage.value = (
      'El stock y la cantidad mínima no pueden superar 2147483647.'
    )
    return false
  }

  return true
}

async function loadData() {
  loadError.value = ''
  loading.value = true

  try {
    categories.value = await getCategories()
    products.value = await getProducts()
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

  const productData = {
    category_id: Number(form.category_id),
    name: form.name,
    description: form.description,
    retail_price: Number(form.retail_price),
    wholesale_price: Number(form.wholesale_price),
    minimum_wholesale_quantity: Number(
      form.minimum_wholesale_quantity,
    ),
    stock: Number(form.stock),
    image_url: form.image_url,
  }

  try {
    if (isEditing.value) {
      await updateProduct(editingId.value, productData)
      successMessage.value = 'Producto actualizado correctamente.'
    } else {
      await createProduct(productData)
      successMessage.value = 'Producto creado correctamente.'
    }

    resetForm()
    await loadData()
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error)
  } finally {
    saving.value = false
  }
}

function startEditing(product) {
  if (isBusy.value) {
    return
  }
  clearMessages()

  editingId.value = product.id
  form.category_id = product.category_id
  form.name = product.name
  form.description = product.description ?? ''
  form.retail_price = product.retail_price
  form.wholesale_price = product.wholesale_price
  form.minimum_wholesale_quantity = (
    product.minimum_wholesale_quantity
  )
  form.stock = product.stock
  form.image_url = product.image_url ?? ''

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

async function changeProductStatus(product) {
  if (isBusy.value) {
    return
  }

  clearMessages()

  if (
    product.active
    && !window.confirm(
      `¿Deseás desactivar el producto "${product.name}"?`,
    )
  ) {
    return
  }

  changingId.value = product.id

  try {
    if (product.active) {
      await deactivateProduct(product.id)
      successMessage.value = 'Producto desactivado correctamente.'
    } else {
      await updateProduct(product.id, {
        active: true,
      })

      successMessage.value = 'Producto reactivado correctamente.'
    }

    if (editingId.value === product.id) {
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
  <main class="admin-page products-page">
    <header class="page-header">
      <div>
        <h1>Gestión de productos</h1>

        <p>
          Creá, modificá, desactivá o reactivá los productos
          disponibles.
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
        {{ isEditing ? 'Editar producto' : 'Nuevo producto' }}
      </h2>

      <p
        v-if="!loading && !loadError && activeCategories.length === 0"
        class="category-warning"
      >
        Debe existir al menos una categoría activa para guardar
        productos.
      </p>

      <form @submit.prevent="submitForm">
        <div class="form-grid">
          <div class="form-group">
            <label for="product-category">Categoría</label>

            <select
              id="product-category"
              v-model.number="form.category_id"
              :disabled="isBusy"
              required
            >
              <option disabled value="">
                Seleccioná una categoría
              </option>

              <option
                v-for="category in availableCategories"
                :key="category.id"
                :value="category.id"
                :disabled="!category.active"
              >
                {{ category.name }}
                {{ category.active ? '' : '(inactiva)' }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="product-name">Nombre</label>

            <input
              id="product-name"
              v-model.trim="form.name"
              type="text"
              maxlength="150"
              :disabled="isBusy"
              required
            >
          </div>

          <div class="form-group">
            <label for="retail-price">
              Precio minorista
            </label>

            <input
              id="retail-price"
              v-model.number="form.retail_price"
              type="number"
              min="0"
            :max="MAX_PRICE"
              step="0.01"
              :disabled="isBusy"
              required
            >
          </div>

          <div class="form-group">
            <label for="wholesale-price">
              Precio mayorista
            </label>

            <input
              id="wholesale-price"
              v-model.number="form.wholesale_price"
              type="number"
              min="0"
              :max="MAX_PRICE"
              step="0.01"
              :disabled="isBusy"
              required
            >
          </div>

          <div class="form-group">
            <label for="minimum-quantity">
              Cantidad mínima mayorista
            </label>

            <input
              id="minimum-quantity"
              v-model.number="
                form.minimum_wholesale_quantity
              "
              type="number"
              min="1"
              :max="MAX_INTEGER"
              step="1"
              :disabled="isBusy"
              required
            >
          </div>

          <div class="form-group">
            <label for="product-stock">Stock</label>

            <input
              id="product-stock"
              v-model.number="form.stock"
              type="number"
              min="0"
              :max="MAX_INTEGER"
              step="1"
              :disabled="isBusy"
              required
            >
          </div>
        </div>

        <div class="form-group">
          <label for="product-description">Descripción</label>

          <textarea
            id="product-description"
            v-model.trim="form.description"
            rows="3"
            :disabled="isBusy"
          />
        </div>

        <div class="form-group">
          <label for="product-image">
            URL de la imagen
          </label>

          <input
            id="product-image"
            v-model.trim="form.image_url"
            type="url"
            maxlength="500"
            placeholder="https://ejemplo.com/imagen.jpg"
            :disabled="isBusy"
          >
        </div>

        <div class="form-actions">
          <button
            type="submit"
            :disabled="
              isBusy || activeCategories.length === 0
            "
          >
            {{
              saving
                ? 'Guardando...'
                : isEditing
                  ? 'Guardar cambios'
                  : 'Crear producto'
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
      <h2>Productos registrados</h2>

      <p v-if="loading" class="list-state" role="status">Cargando productos...</p>

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
        v-else-if="products.length === 0"
        class="empty-state"
      >
        Todavía no hay productos registrados.
      </p>

      <div
        v-else
        class="table-container"
        role="region"
        aria-label="Productos registrados"
        tabindex="0"
      >
        <table class="data-table">
          <thead>
            <tr>
              <th>Producto</th>
              <th>Categoría</th>
              <th>Precio minorista</th>
              <th>Precio mayorista</th>
              <th>Stock</th>
              <th>Imagen</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="product in products"
              :key="product.id"
            >
              <td>
                <strong>{{ product.name }}</strong>

                <small class="product-description">
                  {{ product.description || 'Sin descripción' }}
                </small>
              </td>

              <td>
                {{ product.category?.name || 'Sin categoría' }}
              </td>

              <td>
                {{ formatPrice(product.retail_price) }}
              </td>

              <td>
                {{ formatPrice(product.wholesale_price) }}

                <small class="product-description">
                  Desde
                  {{ product.minimum_wholesale_quantity }}
                  unidades
                </small>
              </td>

              <td>{{ product.stock }}</td>

              <td>
                <a
                  v-if="product.image_url"
                  :href="product.image_url"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Ver imagen
                </a>

                <span v-else>Sin imagen</span>
              </td>

              <td>
                <span
                  class="status"
                  :class="product.active ? 'active' : 'inactive'"
                >
                  {{ product.active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>

              <td class="row-actions">
                <button
                  type="button"
                  class="secondary-button"
                  :disabled="isBusy"
                  @click="startEditing(product)"
                >
                  Editar
                </button>

                <button
                  type="button"
                  :class="
                    product.active
                      ? 'danger-button'
                      : 'success-button'
                  "
                  :disabled="isBusy"
                  @click="changeProductStatus(product)"
                >
                  {{
                    product.active
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
