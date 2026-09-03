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

const cart = ref(null)
const quantities = reactive({})

const loading = ref(false)
const changingId = ref(null)
const clearing = ref(false)

const errorMessage = ref('')
const successMessage = ref('')

const notes = ref('')
const creatingOrder = ref(false)
const createdOrder = ref(null)

const hasItems = computed(() => {
  return cart.value?.items?.length > 0
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
  loading.value = true
  clearMessages()

  try {
    setCart(await getCart())
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    loading.value = false
  }
}

async function changeQuantity(item) {
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
    errorMessage.value = getErrorMessage(error)
  } finally {
    changingId.value = null
  }
}

async function removeItem(item) {
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
    errorMessage.value = getErrorMessage(error)
  } finally {
    changingId.value = null
  }
}

async function emptyCart() {
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
    errorMessage.value = getErrorMessage(error)
  } finally {
    clearing.value = false
  }
}

async function confirmOrder() {
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
    errorMessage.value = getErrorMessage(error)
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
        <RouterLink to="/catalog">
          Seguir comprando
        </RouterLink>

        <RouterLink to="/">
          Volver al inicio
        </RouterLink>
      </nav>
    </header>

    <p v-if="errorMessage" class="message error-message">
      {{ errorMessage }}
    </p>

    <p v-if="successMessage" class="message success-message">
      {{ successMessage }}
    </p>

    <p v-if="loading">
      Cargando carrito...
    </p>

    <section
      v-else-if="!hasItems"
      class="empty-cart"
    >
      <h2>Tu carrito está vacío</h2>
      <div
        v-if="createdOrder"
        class="created-order"
        >
        <p>
            Se creó el pedido
            <strong>#{{ createdOrder.id }}</strong>.
        </p>

        <p>
            Estado: {{ createdOrder.status.name }}
        </p>

        <p>
            Total: {{ formatPrice(createdOrder.total) }}
        </p>
        <RouterLink to="/my-orders">
        Ver mis pedidos
        </RouterLink>
    </div>
      <p>
        Agregá productos desde el catálogo para comenzar
        una compra.
      </p>
      <RouterLink to="/catalog">
        Ir al catálogo
      </RouterLink>
    </section>

    <template v-else>
      <section class="cart-card">
        <div class="table-container">
          <table>
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
                    <img
                      v-if="item.product.image_url"
                      :src="item.product.image_url"
                      :alt="item.product.name"
                    >

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
                      :disabled="
                        !item.product.active
                        || changingId === item.id
                      "
                    >

                    <button
                      type="button"
                      class="secondary-button"
                      :disabled="
                        !item.product.active
                        || changingId === item.id
                      "
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
                    :disabled="changingId === item.id"
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

      <section class="cart-summary">
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
          :disabled="clearing"
          @click="emptyCart"
        >
          {{ clearing ? 'Vaciando...' : 'Vaciar carrito' }}
        </button>
      </section>
      <section class="checkout-card">
        <div>
            <label for="order-notes">
            Observaciones del pedido
            </label>

            <textarea
            id="order-notes"
            v-model="notes"
            rows="3"
            placeholder="Información adicional para el pedido"
            :disabled="creatingOrder"
            />
        </div>

        <button
            type="button"
            :disabled="creatingOrder"
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
  flex-wrap: wrap;
  gap: 16px;
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

.empty-cart,
.cart-card,
.cart-summary {
  padding: 24px;
  background-color: white;
  border: 1px solid #dddddd;
  border-radius: 8px;
}

.empty-cart {
  text-align: center;
}

.empty-cart h2 {
  margin-top: 0;
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
  vertical-align: middle;
  border-bottom: 1px solid #dddddd;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-info img {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: 4px;
}

.product-info small {
  display: block;
  margin-top: 4px;
}

.stock-information {
  color: #666666;
}

.unavailable {
  color: #b42318;
}

.quantity-control {
  display: flex;
  gap: 8px;
}

.quantity-control input {
  width: 80px;
  padding: 8px;
  border: 1px solid #bbbbbb;
  border-radius: 4px;
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

.cart-summary {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 32px;
  margin-top: 24px;
}

.cart-summary div {
  display: grid;
  gap: 4px;
}

.cart-summary span {
  color: #666666;
}

.total {
  font-size: 1.3rem;
  color: #18794e;
}
.checkout-card {
  display: grid;
  gap: 16px;
  margin-top: 24px;
  padding: 24px;
  background-color: white;
  border: 1px solid #dddddd;
  border-radius: 8px;
}

.checkout-card div {
  display: grid;
  gap: 8px;
}

.checkout-card label {
  font-weight: 600;
}

.checkout-card textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 10px;
  font: inherit;
  resize: vertical;
  border: 1px solid #bbbbbb;
  border-radius: 4px;
}

.checkout-card button {
  justify-self: end;
}

.created-order {
  margin-bottom: 16px;
  padding: 16px;
  color: #18794e;
  background-color: #dcfae6;
  border-radius: 6px;
}

.created-order p {
  margin: 4px 0;
}

@media (max-width: 700px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .cart-summary {
    align-items: stretch;
    flex-direction: column;
  }
  .checkout-card button {
  width: 100%;
    }
}
</style>