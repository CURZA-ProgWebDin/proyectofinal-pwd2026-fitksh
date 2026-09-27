<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from 'vue'
import { RouterLink } from 'vue-router'

import {
  clearCart,
  getCart,
  removeCartItem,
  updateCartItem,
} from '../services/cartService'

import { createOrder } from '../services/orderService'

import { formatPrice } from '../utils/formatters'

import { getApiErrorMessage } from '../utils/apiErrors'

import ProductImage from '../components/ProductImage.vue'

const cart = ref(null)
const quantities = reactive({})

const loading = ref(false)
const changingId = ref(null)
const clearing = ref(false)

const errorMessage = ref('')
const successMessage = ref('')
const loadError = ref('')

const notes = ref('')
const creatingOrder = ref(false)
const createdOrder = ref(null)

const isBusy = computed(() => {
  return (
    loading.value
    || changingId.value !== null
    || clearing.value
    || creatingOrder.value
  )
})

const hasItems = computed(() => {
  return cart.value?.items?.length > 0
})

function clearMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

function setCart(updatedCart) {
  cart.value = updatedCart

  for (const itemId of Object.keys(quantities)) {
    delete quantities[itemId]
  }

  for (const item of updatedCart?.items ?? []) {
    quantities[item.id] = item.quantity
  }
}

async function loadCart() {
  loadError.value = ''
  loading.value = true
  clearMessages()

  try {
    setCart(await getCart())
  } catch (error) {
    loadError.value = getApiErrorMessage(
      error,
      'No se pudo cargar la información. Intentá nuevamente.',
    )
  } finally {
    loading.value = false
  }
}

async function changeQuantity(item) {
  if (isBusy.value) {
    return
  }

  clearMessages()

  const quantity = Number(quantities[item.id])

  if (!Number.isInteger(quantity) || quantity <= 0) {
    errorMessage.value = (
      'La cantidad debe ser un entero mayor que cero.'
    )
    return
  }

  if (!item.product.active) {
    errorMessage.value = (
      'El producto ya no se encuentra disponible.'
    )
    return
  }

  if (quantity > item.product.stock) {
    errorMessage.value = (
      `Solo hay ${item.product.stock} unidades disponibles.`
    )
    return
  }

  changingId.value = item.id

  try {
    const updatedCart = await updateCartItem(
      item.id,
      quantity,
    )

    setCart(updatedCart)

    successMessage.value = (
      'Cantidad actualizada correctamente.'
    )
  } catch (error) {
    quantities[item.id] = item.quantity
    errorMessage.value = getApiErrorMessage(error)
  } finally {
    changingId.value = null
  }
}

async function removeItem(item) {
  if (isBusy.value) {
    return
  }

  clearMessages()

  if (
    !window.confirm(
      `¿Deseás quitar "${item.product.name}" del carrito?`,
    )
  ) {
    return
  }

  changingId.value = item.id

  try {
    setCart(await removeCartItem(item.id))

    successMessage.value = (
      'Producto quitado del carrito.'
    )
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error)
  } finally {
    changingId.value = null
  }
}

async function emptyCart() {
  if (isBusy.value) {
    return
  }

  clearMessages()

  if (
    !window.confirm(
      '¿Deseás quitar todos los productos del carrito?',
    )
  ) {
    return
  }

  clearing.value = true

  try {
    setCart(await clearCart())

    successMessage.value = (
      'Carrito vaciado correctamente.'
    )
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error)
  } finally {
    clearing.value = false
  }
}

async function confirmOrder() {
  if (isBusy.value) {
    return
  }

  clearMessages()

  if (!hasItems.value) {
    errorMessage.value = 'El carrito está vacío.'
    return
  }

  if (
    !window.confirm(
      (
        `¿Deseás crear el pedido por `
        + `${formatPrice(cart.value.total)}?`
      ),
    )
  ) {
    return
  }

  creatingOrder.value = true

  try {
    const order = await createOrder(notes.value)

    createdOrder.value = order
    notes.value = ''

    setCart({
      ...cart.value,
      items: [],
      item_count: 0,
      total_quantity: 0,
      total: 0,
    })

    successMessage.value = (
      `Pedido #${order.id} creado correctamente.`
    )
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error)
  } finally {
    creatingOrder.value = false
  }
}

onMounted(loadCart)
</script>

<template>
  <main class="cart-page">
    <header class="page-header">
      <div>
        <h1>Mi carrito</h1>

        <p>
          Revisá los productos y cantidades antes de generar
          el pedido.
        </p>
      </div>

      <nav class="header-links">
        <RouterLink
          to="/catalog"
          class="button-link secondary-button"
        >
          Seguir comprando
        </RouterLink>
      </nav>
    </header>

    <p
      v-if="errorMessage"
      class="message error-message"
      role="alert"
    >
      {{ errorMessage }}
    </p>

    <p
      v-if="successMessage && !createdOrder"
      class="message success-message"
      role="status"
    >
      {{ successMessage }}
    </p>

    <p v-if="loading" class="panel cart-state" role="status">
      Cargando carrito...
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
        @click="loadCart"
      >
        Reintentar
      </button>
    </div>

  <section
  v-else-if="!hasItems"
  class="panel cart-state"
  >
    <template v-if="createdOrder">
      <h2>Pedido #{{ createdOrder.id }} creado</h2>

      <p>
        Estado:
        <strong>{{ createdOrder.status.name }}</strong>
      </p>

      <p>
        Total:
        <strong>{{ formatPrice(createdOrder.total) }}</strong>
      </p>

      <div class="state-actions">
        <RouterLink to="/my-orders" class="button-link">
          Ver mis pedidos
        </RouterLink>

        <RouterLink
          to="/catalog"
          class="button-link secondary-button"
        >
          Seguir comprando
        </RouterLink>
      </div>
    </template>

    <template v-else>
      <h2>Tu carrito está vacío</h2>

      <p class="state-description">
        Agregá productos desde el catálogo para comenzar.
      </p>

      <RouterLink to="/catalog" class="button-link">
        Ir al catálogo
      </RouterLink>
    </template>
  </section>

    <template v-else>
      <section class="panel cart-card">
        <p class="cart-help">
          Después de modificar una cantidad, presioná Actualizar.
        </p>
        <div
          class="table-container"
          role="region"
          aria-label="Productos del carrito"
          tabindex="0"
        >
          <table class="data-table cart-table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>Precio unitario</th>
                <th>Cantidad</th>
                <th>Subtotal</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="item in cart.items"
                :key="item.id"
              >
                <td>
                  <div class="product-info">
                    <ProductImage
                      :src="item.product.image_url"
                      :alt="item.product.name"
                      small
                    />

                    <div>
                      <strong>{{ item.product.name }}</strong>

                      <small
                        v-if="!item.product.active"
                        class="unavailable"
                      >
                        Producto no disponible
                      </small>

                      <small
                        v-else
                        class="stock-information"
                      >
                        Stock disponible:
                        {{ item.product.stock }}
                      </small>
                    </div>
                  </div>
                </td>

                <td>
                  {{ formatPrice(item.unit_price) }}
                </td>

                <td>
                  <div class="quantity-control">
                    <input
                      v-model.number="quantities[item.id]"
                      type="number"
                      min="1"
                      :max="item.product.stock"
                      step="1"
                      :disabled="isBusy || !item.product.active"
                      :aria-label="`Cantidad de ${item.product.name}`"
                    >

                    <button
                      type="button"
                      class="secondary-button"
                      :disabled="isBusy || !item.product.active"
                      @click="changeQuantity(item)"
                    >
                      Actualizar
                    </button>
                  </div>
                </td>

                <td>
                  {{ formatPrice(item.subtotal) }}
                </td>

                <td>
                  <button
                    type="button"
                    class="danger-button"
                    :disabled="isBusy"
                    @click="removeItem(item)"
                  >
                    Quitar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="panel cart-summary">
        <div>
          <span>Productos diferentes</span>
          <strong>{{ cart.item_count }}</strong>
        </div>

        <div>
          <span>Unidades totales</span>
          <strong>{{ cart.total_quantity }}</strong>
        </div>

        <div>
          <span>Total</span>
          <strong class="total">
            {{ formatPrice(cart.total) }}
          </strong>
        </div>

        <button
          type="button"
          class="danger-button"
          :disabled="isBusy"
          @click="emptyCart"
        >
          {{ clearing ? 'Vaciando...' : 'Vaciar carrito' }}
        </button>
      </section>

      <section class="panel checkout-card">
        <div>
          <label for="order-notes">
            Observaciones del pedido
          </label>

          <textarea
            id="order-notes"
            v-model="notes"
            rows="3"
            placeholder="Información adicional para el pedido"
            :disabled="isBusy"
          />
        </div>

        <button
          type="button"
          :disabled="isBusy"
          @click="confirmOrder"
        >
          {{
            creatingOrder
              ? 'Creando pedido...'
              : 'Confirmar pedido'
          }}
        </button>
      </section>

    </template>
  </main>
</template>

<style scoped>
.cart-page {
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

.cart-state {
  text-align: center;
}

.cart-state h2 {
  margin: 0 0 12px;
}

.state-description {
  margin: 0 0 20px;
  color: var(--color-muted);
}

.state-actions {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.cart-help {
  margin: 0 0 16px;
  color: var(--color-muted);
}

.cart-table {
  min-width: 900px;
}

.product-info {
  display: flex;
  min-width: 220px;
  max-width: 340px;
  align-items: center;
  gap: 12px;
}

.product-info > div:last-child {
  min-width: 0;
  overflow-wrap: anywhere;
}

.product-info small {
  display: block;
  margin-top: 4px;
}

.stock-information {
  color: var(--color-muted);
}

.unavailable {
  color: var(--color-danger);
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity-control input {
  width: 84px;
  min-height: 44px;
  flex-shrink: 0;
}

.cart-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 24px;
  margin-top: 24px;
}

.cart-summary div {
  display: grid;
  gap: 4px;
}

.cart-summary span {
  color: var(--color-muted);
}

.total {
  font-size: 1.5rem;
  color: var(--color-primary);
}

.checkout-card {
  display: grid;
  gap: 16px;
  margin-top: 24px;
}

.checkout-card div {
  display: grid;
  gap: 8px;
}

.checkout-card textarea {
  width: 100%;
}

.checkout-card button {
  justify-self: end;
}

@media (max-width: 700px) {
  .page-header,
  .cart-summary,
  .state-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .checkout-card button {
    width: 100%;
  }
}
</style>