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

const products = ref([])
const categories = ref([])

const loading = ref(false)
const saving = ref(false)
const changingId = ref(null)
const editingId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')

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

const priceFormatter = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
})

function formatPrice(price) {
  return priceFormatter.format(price)
}

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

  return true
}

async function loadData() {
  loading.value = true

  try {
    categories.value = await getCategories()
    products.value = await getProducts()
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
    errorMessage.value = getErrorMessage(error)
  } finally {
    saving.value = false
  }
}

function startEditing(product) {
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
  clearMessages()
  resetForm()
}

async function changeProductStatus(product) {
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
    errorMessage.value = getErrorMessage(error)
  } finally {
    changingId.value = null
  }
}

onMounted(loadData)
</script>

<template>
  <main class="products-page">
    <header class="page-header">
      <div>
        <h1>Gestión de productos</h1>

        <p>
          Creá, modificá, desactivá o reactivá los productos
          disponibles.
        </p>
      </div>

      <nav class="header-links">
        <RouterLink to="/categories">
          Gestionar categorías
        </RouterLink>

        <RouterLink to="/">
          Volver al inicio
        </RouterLink>
      </nav>
    </header>

    <section class="form-card">
      <h2>
        {{ isEditing ? 'Editar producto' : 'Nuevo producto' }}
      </h2>

      <p
        v-if="activeCategories.length === 0"
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
              step="0.01"
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
              step="0.01"
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
              step="1"
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
              step="1"
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
          >
        </div>

        <div class="form-actions">
          <button
            type="submit"
            :disabled="
              saving || activeCategories.length === 0
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
      <h2>Productos registrados</h2>

      <p v-if="loading">Cargando productos...</p>

      <p v-else-if="products.length === 0">
        Todavía no hay productos registrados.
      </p>

      <div v-else class="table-container">
        <table>
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
                  :disabled="changingId === product.id"
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

<style scoped>
.products-page {
  width: min(100% - 32px, 1300px);
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

.header-links a {
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

input,
select,
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

.category-warning,
.message {
  padding: 12px;
  border-radius: 4px;
}

.category-warning {
  color: #854d0e;
  background-color: #fef3c7;
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
  vertical-align: top;
  border-bottom: 1px solid #dddddd;
}

.product-description {
  display: block;
  margin-top: 4px;
  color: #666666;
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