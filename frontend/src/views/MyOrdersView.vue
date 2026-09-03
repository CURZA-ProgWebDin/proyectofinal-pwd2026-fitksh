<script setup>
import {
  onMounted,
  ref,
} from 'vue'
import { RouterLink } from 'vue-router'

import {
  cancelOrder,
  getOrders,
} from '../services/orderService'

const orders = ref([])
const loading = ref(false)
const cancellingId = ref(null)
const expandedOrderId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')

const priceFormatter = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
})

const dateFormatter = new Intl.DateTimeFormat('es-AR', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

function formatPrice(price) {
  return priceFormatter.format(price)
}

function formatDate(date) {
  return dateFormatter.format(new Date(date))
}

function formatStatus(statusName) {
  return statusName.replaceAll('_', ' ')
}

function getStatusClass(statusName) {
  return {
    'status-pending': statusName === 'PENDIENTE',
    'status-progress': [
      'CONFIRMADO',
      'EN_PREPARACION',
      'LISTO',
    ].includes(statusName),
    'status-delivered': statusName === 'ENTREGADO',
    'status-cancelled': statusName === 'CANCELADO',
  }
}

function getErrorMessage(error) {
  return (
    error.response?.data?.error
    || error.response?.data?.msg
    || 'Ocurrió un error al procesar la solicitud.'
  )
}

function clearMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

function toggleDetails(orderId) {
  expandedOrderId.value = (
    expandedOrderId.value === orderId
      ? null
      : orderId
  )
}

async function loadOrders() {
  loading.value = true
  errorMessage.value = ''

  try {
    orders.value = await getOrders()
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    loading.value = false
  }
}

async function cancelPendingOrder(order) {
  clearMessages()

  if (
    !window.confirm(
      `¿Deseás cancelar el pedido #${order.id}?`,
    )
  ) {
    return
  }

  cancellingId.value = order.id

  try {
    const updatedOrder = await cancelOrder(order.id)

    const orderIndex = orders.value.findIndex(
      (currentOrder) => currentOrder.id === order.id,
    )

    if (orderIndex !== -1) {
      orders.value[orderIndex] = updatedOrder
    }

    successMessage.value = (
      `Pedido #${order.id} cancelado correctamente.`
    )
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    cancellingId.value = null
  }
}

onMounted(loadOrders)
</script>

<template>
  <main class="orders-page">
    <header class="page-header">
      <div>
        <h1>Mis pedidos</h1>

        <p>
          Consultá el estado y los productos de tus pedidos.
        </p>
      </div>

      <nav class="header-links">
        <RouterLink to="/catalog">
          Ver catálogo
        </RouterLink>

        <RouterLink to="/cart">
          Ver carrito
        </RouterLink>

        <RouterLink to="/">
          Volver al inicio
        </RouterLink>
      </nav>
    </header>

    <p
      v-if="errorMessage"
      class="message error-message"
    >
      {{ errorMessage }}
    </p>

    <p
      v-if="successMessage"
      class="message success-message"
    >
      {{ successMessage }}
    </p>

    <p v-if="loading">
      Cargando pedidos...
    </p>

    <section
      v-else-if="orders.length === 0"
      class="empty-state"
    >
      <h2>Todavía no tenés pedidos</h2>

      <p>
        Agregá productos al carrito para crear tu primer
        pedido.
      </p>

      <RouterLink to="/catalog">
        Ir al catálogo
      </RouterLink>
    </section>

    <section v-else class="orders-list">
      <article
        v-for="order in orders"
        :key="order.id"
        class="order-card"
      >
        <header class="order-card-header">
          <div>
            <h2>Pedido #{{ order.id }}</h2>

            <p class="order-date">
              {{ formatDate(order.ordered_at) }}
            </p>
          </div>

          <span
            class="status-badge"
            :class="getStatusClass(order.status.name)"
          >
            {{ formatStatus(order.status.name) }}
          </span>
        </header>

        <div class="order-summary">
          <div>
            <span>Productos diferentes</span>
            <strong>{{ order.details.length }}</strong>
          </div>

          <div>
            <span>Unidades</span>
            <strong>{{ order.total_quantity }}</strong>
          </div>

          <div>
            <span>Total</span>
            <strong class="total">
              {{ formatPrice(order.total) }}
            </strong>
          </div>
        </div>

        <p v-if="order.notes" class="order-notes">
          <strong>Observaciones:</strong>
          {{ order.notes }}
        </p>

        <div class="order-actions">
          <button
            type="button"
            class="secondary-button"
            @click="toggleDetails(order.id)"
          >
            {{
              expandedOrderId === order.id
                ? 'Ocultar detalle'
                : 'Ver detalle'
            }}
          </button>

          <button
            v-if="order.status.name === 'PENDIENTE'"
            type="button"
            class="danger-button"
            :disabled="cancellingId === order.id"
            @click="cancelPendingOrder(order)"
          >
            {{
              cancellingId === order.id
                ? 'Cancelando...'
                : 'Cancelar pedido'
            }}
          </button>
        </div>

        <section
          v-if="expandedOrderId === order.id"
          class="order-details"
        >
          <h3>Detalle del pedido</h3>

          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Producto</th>
                  <th>Precio unitario</th>
                  <th>Cantidad</th>
                  <th>Subtotal</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="detail in order.details"
                  :key="detail.id"
                >
                  <td>
                    {{ detail.product.name }}
                  </td>

                  <td>
                    {{ formatPrice(detail.unit_price) }}
                  </td>

                  <td>
                    {{ detail.quantity }}
                  </td>

                  <td>
                    {{ formatPrice(detail.subtotal) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </article>
    </section>
  </main>
</template>

<style scoped>
.orders-page {
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

.empty-state {
  padding: 32px;
  text-align: center;
  background-color: white;
  border: 1px solid #dddddd;
  border-radius: 8px;
}

.empty-state h2 {
  margin-top: 0;
}

.orders-list {
  display: grid;
  gap: 20px;
}

.order-card {
  padding: 24px;
  background-color: white;
  border: 1px solid #dddddd;
  border-radius: 8px;
}

.order-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.order-card-header h2 {
  margin: 0;
}

.order-date {
  margin: 6px 0 0;
  color: #666666;
}

.status-badge {
  padding: 6px 10px;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: 16px;
}

.status-pending {
  color: #805400;
  background-color: #fff0c2;
}

.status-progress {
  color: #174ea6;
  background-color: #dbeafe;
}

.status-delivered {
  color: #18794e;
  background-color: #dcfae6;
}

.status-cancelled {
  color: #b42318;
  background-color: #fee4e2;
}

.order-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 20px;
}

.order-summary div {
  display: grid;
  gap: 4px;
  padding: 12px;
  background-color: #f5f5f5;
  border-radius: 6px;
}

.order-summary span {
  color: #666666;
}

.total {
  color: #18794e;
}

.order-notes {
  padding: 12px;
  background-color: #f5f5f5;
  border-radius: 6px;
}

.order-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
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

.order-details {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #dddddd;
}

.order-details h3 {
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
  border-bottom: 1px solid #dddddd;
}

@media (max-width: 700px) {
  .page-header,
  .order-card-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .order-summary {
    grid-template-columns: 1fr;
  }
}
</style>