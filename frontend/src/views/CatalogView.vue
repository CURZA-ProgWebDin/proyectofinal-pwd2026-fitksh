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

import { formatPrice } from '../utils/formatters'

import { getApiErrorMessage } from '../utils/apiErrors'
import ProductImage from '../components/ProductImage.vue'

const products = ref([])
const cart = ref(null)

const quantities = reactive({})

const loading = ref(false)
const addingId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')
const loadError = ref('')

const activeProducts = computed(() => {
  return products.value.filter(
    (product) => product.active,
  )
})

function clearMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

async function loadData() {
  loadError.value = ''
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
    loadError.value = getApiErrorMessage(
      error,
      'No se pudo cargar la información. Intentá nuevamente.',
    )
  } finally {
    loading.value = false
  }
}

function getAvailableQuantity(product) {
  const item = cart.value?.items?.find(
    (item) => item.product_id === product.id,
  )

  const quantityInCart = item?.quantity ?? 0

  return Math.max(
    product.stock - quantityInCart,
    0,
  )
}

async function addProduct(product) {
  if (addingId.value !== null) {
    return
  }

  clearMessages()

  const quantity = Number(quantities[product.id])

  if (!Number.isInteger(quantity) || quantity <= 0) {
    errorMessage.value = (
      'La cantidad debe ser un entero mayor que cero.'
    )
    return
  }

  const availableQuantity = getAvailableQuantity(product)

  if (quantity > availableQuantity) {
    errorMessage.value = (
      `Podés agregar hasta ${availableQuantity} unidades más de este producto.`
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
    errorMessage.value = getApiErrorMessage(error)
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
          Elegí los productos y las cantidades para tu pedido.
        </p>
      </div>

      <RouterLink
        to="/cart"
        class="button-link secondary-button"
      >
        Ver carrito
      </RouterLink>
    </header>

    <section
      v-if="cart && !loading && !loadError"
      class="cart-summary"
      aria-label="Resumen del carrito"
    >
      <strong>Tu carrito</strong>

      <span>{{ cart.total_quantity }} unidades</span>

      <span>
        Total: <strong>{{ formatPrice(cart.total) }}</strong>
      </span>
    </section>

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

    <p v-if="loading" class="catalog-state" role="status">
      Cargando productos...
    </p>

    <div
      v-else-if="loadError"
      class="message error-message"
      role="alert"
    >
      <p>{{ loadError }}</p>

      <button
        type="button"
        :disabled="loading"
        @click="loadData"
      >
        Reintentar
      </button>
    </div>

    <section
      v-else-if="activeProducts.length === 0"
      class="catalog-state"
    >
      <h2>No hay productos disponibles</h2>
      <p>Volvé a consultar más tarde.</p>
    </section>

    <section v-else class="products-grid">
      <article
        v-for="product in activeProducts"
        :key="product.id"
        class="product-card"
      >
        <ProductImage
          :src="product.image_url"
          :alt="product.name"
        />

        <div class="product-content">
          <small>
            {{ product.category?.name || 'Sin categoría' }}
          </small>

          <h2>{{ product.name }}</h2>

          <p v-if="product.description" class="description">
            {{ product.description }}
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
              :max="getAvailableQuantity(product)"
              step="1"
              :disabled="
                getAvailableQuantity(product) === 0
                || addingId !== null
              "
            >

            <small>
              Podés agregar {{ getAvailableQuantity(product) }}
              unidades más.
            </small>

            <button
              type="button"
              :disabled="
                getAvailableQuantity(product) === 0
                || addingId !== null
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

.cart-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 24px;
  margin-bottom: 24px;
  padding: 16px 24px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.catalog-state {
  padding: 32px;
  color: var(--color-muted);
  text-align: center;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.catalog-state h2 {
  margin-top: 0;
  color: var(--color-text);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
}

.product-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.product-content {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 20px;
  overflow-wrap: anywhere;
}

.product-content h2 {
  margin: 8px 0 12px;
  font-size: 1.25rem;
}

.product-content small {
  font-size: 0.875rem;
  color: var(--color-muted);
}

.description {
  margin: 0 0 16px;
  color: var(--color-muted);
}

.price {
  margin: 0 0 12px;
  font-size: 1.5rem;
  font-weight: 700;
}

.stock {
  margin: 0 0 16px;
  color: var(--color-success);
}

.stock.unavailable {
  color: var(--color-danger);
}

.product-actions {
  display: grid;
  gap: 8px;
  margin-top: auto;
  padding-top: 16px;
}

.product-actions input {
  width: 100%;
  min-height: 44px;
}

@media (max-width: 900px) {
  .products-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .page-header {
    align-items: stretch;
    flex-direction: column;
  }

  .products-grid {
    grid-template-columns: 1fr;
  }
}
</style>