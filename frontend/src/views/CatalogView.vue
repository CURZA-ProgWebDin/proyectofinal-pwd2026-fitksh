<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from 'vue'
import { RouterLink } from 'vue-router'

import {
  addCartItem,
  getCart,
} from '../services/cartService'
import { getProducts } from '../services/productService'

const products = ref([])
const cart = ref(null)

const quantities = reactive({})

const loading = ref(false)
const addingId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')

const activeProducts = computed(() => {
  return products.value.filter(
    (product) => product.active,
  )
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
    || error.response?.data?.msg
    || 'Ocurrió un error al procesar la solicitud.'
  )
}

async function loadData() {
  loading.value = true
  clearMessages()

  try {
    const [
      loadedProducts,
      loadedCart,
    ] = await Promise.all([
      getProducts(),
      getCart(),
    ])

    products.value = loadedProducts
    cart.value = loadedCart

    for (const product of loadedProducts) {
      quantities[product.id] = 1
    }
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    loading.value = false
  }
}

async function addProduct(product) {
  clearMessages()

  const quantity = Number(quantities[product.id])

  if (!Number.isInteger(quantity) || quantity <= 0) {
    errorMessage.value = (
      'La cantidad debe ser un entero mayor que cero.'
    )
    return
  }

  if (quantity > product.stock) {
    errorMessage.value = (
      `Solo hay ${product.stock} unidades disponibles.`
    )
    return
  }

  addingId.value = product.id

  try {
    cart.value = await addCartItem(
      product.id,
      quantity,
    )

    quantities[product.id] = 1

    successMessage.value = (
      `"${product.name}" fue agregado al carrito.`
    )
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    addingId.value = null
  }
}

onMounted(loadData)
</script>

<template>
  <main class="catalog-page">
    <header class="page-header">
      <div>
        <h1>Catálogo de productos</h1>

        <p>
          Seleccioná los productos y cantidades que quieras comprar.
        </p>
      </div>

      <nav class="header-links">
        <RouterLink to="/">
          Volver al inicio
        </RouterLink>
        <RouterLink to="/cart">
          Ver carrito ({{ cart?.total_quantity ?? 0 }})
        </RouterLink>
      </nav>
    </header>

    <section
      v-if="cart"
      class="cart-summary"
    >
      <strong>Tu carrito:</strong>

      <span>
        {{ cart.total_quantity }} unidades
      </span>

      <span>
        Total: {{ formatPrice(cart.total) }}
      </span>
    </section>

    <p v-if="errorMessage" class="message error-message">
      {{ errorMessage }}
    </p>

    <p v-if="successMessage" class="message success-message">
      {{ successMessage }}
    </p>

    <p v-if="loading">
      Cargando productos...
    </p>

    <p v-else-if="activeProducts.length === 0">
      No hay productos disponibles.
    </p>

    <section v-else class="products-grid">
      <article
        v-for="product in activeProducts"
        :key="product.id"
        class="product-card"
      >
        <img
          v-if="product.image_url"
          :src="product.image_url"
          :alt="product.name"
          class="product-image"
        >

        <div v-else class="image-placeholder">
          Sin imagen
        </div>

        <div class="product-content">
          <small>
            {{ product.category?.name || 'Sin categoría' }}
          </small>

          <h2>{{ product.name }}</h2>

          <p class="description">
            {{ product.description || 'Sin descripción' }}
          </p>

          <p class="price">
            {{ formatPrice(product.retail_price) }}
          </p>

          <p
            class="stock"
            :class="{ unavailable: product.stock === 0 }"
          >
            {{
              product.stock > 0
                ? `Stock disponible: ${product.stock}`
                : 'Sin stock'
            }}
          </p>

          <div class="product-actions">
            <label :for="`quantity-${product.id}`">
              Cantidad
            </label>

            <input
              :id="`quantity-${product.id}`"
              v-model.number="quantities[product.id]"
              type="number"
              min="1"
              :max="product.stock"
              step="1"
              :disabled="product.stock === 0"
            >

            <button
              type="button"
              :disabled="
                product.stock === 0
                || addingId === product.id
              "
              @click="addProduct(product)"
            >
              {{
                addingId === product.id
                  ? 'Agregando...'
                  : 'Agregar al carrito'
              }}
            </button>
          </div>
        </div>
      </article>
    </section>
  </main>
</template>

<style scoped>
.catalog-page {
  width: min(100% - 32px, 1200px);
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

.page-header h1 {
  margin: 0;
}

.page-header p {
  margin-bottom: 0;
  color: #666666;
}

.header-links {
  display: flex;
  gap: 16px;
}

.cart-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background-color: white;
  border: 1px solid #dddddd;
  border-radius: 8px;
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

.products-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.product-card {
  overflow: hidden;
  background-color: white;
  border: 1px solid #dddddd;
  border-radius: 8px;
}

.product-image,
.image-placeholder {
  width: 100%;
  height: 200px;
}

.product-image {
  display: block;
  object-fit: cover;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666666;
  background-color: #eeeeee;
}

.product-content {
  padding: 20px;
}

.product-content h2 {
  margin: 8px 0;
}

.product-content small,
.description {
  color: #666666;
}

.price {
  font-size: 1.3rem;
  font-weight: bold;
  color: #18794e;
}

.stock {
  color: #18794e;
}

.unavailable {
  color: #b42318;
}

.product-actions {
  display: grid;
  gap: 8px;
  margin-top: 16px;
}

.product-actions input {
  width: 100%;
  padding: 9px;
  border: 1px solid #bbbbbb;
  border-radius: 4px;
}

.product-actions button {
  padding: 10px;
  color: white;
  cursor: pointer;
  background-color: #2457a7;
  border: 0;
  border-radius: 4px;
}

.product-actions button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 900px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .products-grid {
    grid-template-columns: 1fr;
  }
}
</style>