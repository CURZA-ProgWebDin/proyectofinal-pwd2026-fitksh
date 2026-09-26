<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import { RouterLink } from 'vue-router'

import {
  cancelOrder,
  getOrders,
} from '../services/orderService'

import {
  formatDate,
  formatPrice,
  formatStatus,
} from '../utils/formatters'

import { getApiErrorMessage } from '../utils/apiErrors'

const orders = ref([])
const loading = ref(false)
const cancellingId = ref(null)
const isBusy = computed(() => {
  return loading.value || cancellingId.value !== null
})
const expandedOrderId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')
const loadError = ref('')

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
  loadError.value = ''

  try {
    orders.value = await getOrders()
  } catch (error) {
    loadError.value = getApiErrorMessage(
      error,
      'No se pudo cargar la información. Intentá nuevamente.',
    )
  } finally {
    loading.value = false
  }
}

async function cancelPendingOrder(order) {
  if (isBusy.value) {
    return
  }
  
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
    errorMessage.value = getApiErrorMessage(error)
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
        <p>Consultá el estado y los productos de tus pedidos.</p>
      </div>

      <RouterLink
        to="/catalog"
        class="button-link secondary-button"
      >
        Ver catálogo
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

    <p
      v-if="loading"
      class="panel orders-state"
      role="status"
    >
      Cargando pedidos...
    </p>

    <section
      v-else-if="loadError"
      class="panel orders-state"
    >
      <h2>No pudimos cargar tus pedidos</h2>

      <p class="message error-message" role="alert">
        {{ loadError }}
      </p>

      <button
        type="button"
        :disabled="loading"
        @click="loadOrders"
      >
        Reintentar
      </button>
    </section>

    <section
      v-else-if="orders.length === 0"
      class="panel orders-state"
    >
      <h2>Todavía no tenés pedidos</h2>

      <p class="state-description">
        Elegí productos del catálogo y agregalos al carrito
        para crear tu primer pedido.
      </p>

      <RouterLink to="/catalog" class="button-link">
        Ir al catálogo
      </RouterLink>
    </section>

    <section
      v-else
      class="orders-list"
      aria-label="Listado de pedidos"
    >
      <article
        v-for="order in orders"
        :key="order.id"
        class="panel order-card"
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

        <dl class="order-summary">
          <div>
            <dt>Productos diferentes</dt>
            <dd>{{ order.details.length }}</dd>
          </div>

          <div>
            <dt>Unidades</dt>
            <dd>{{ order.total_quantity }}</dd>
          </div>

          <div>
            <dt>Total</dt>
            <dd class="total">
              {{ formatPrice(order.total) }}
            </dd>
          </div>
        </dl>

        <p v-if="order.notes" class="order-notes">
          <strong>Observaciones:</strong>
          {{ order.notes }}
        </p>

        <div class="order-actions">
          <button
            type="button"
            class="secondary-button"
            :aria-expanded="expandedOrderId === order.id"
            :aria-controls="`order-details-${order.id}`"
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
            :disabled="isBusy"
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
          v-show="expandedOrderId === order.id"
          :id="`order-details-${order.id}`"
          class="order-details"
        >
          <h3>Detalle del pedido</h3>

          <div
            class="table-container"
            role="region"
            :aria-label="`Productos del pedido ${order.id}`"
            tabindex="0"
          >
            <table class="data-table details-table">
              <thead>
                <tr>
                  <th scope="col">Producto</th>
                  <th scope="col" class="money">
                    Precio unitario
                  </th>
                  <th scope="col" class="quantity">
                    Cantidad
                  </th>
                  <th scope="col" class="money">
                    Subtotal
                  </th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="detail in order.details"
                  :key="detail.id"
                >
                  <td class="product-name">
                    {{ detail.product.name }}
                  </td>

                  <td class="money">
                    {{ formatPrice(detail.unit_price) }}
                  </td>

                  <td class="quantity">
                    {{ detail.quantity }}
                  </td>

                  <td class="money">
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

.orders-state {
  text-align: center;
}

.orders-state h2 {
  margin: 0 0 12px;
}

.state-description {
  margin: 0 0 20px;
  color: var(--color-muted);
}

.orders-list {
  display: grid;
  gap: 24px;
}

.order-card {
  min-width: 0;
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
  margin: 8px 0 0;
  color: var(--color-muted);
}

.status-badge {
  display: inline-flex;
  align-self: flex-start;
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: 700;
  border-radius: 20px;
}

.status-pending {
  color: var(--color-text);
  background-color: var(--color-highlight);
}

.status-progress {
  color: #174ea6;
  background-color: #dbeafe;
}

.status-delivered {
  color: var(--color-success);
  background-color: var(--color-success-background);
}

.status-cancelled {
  color: var(--color-danger);
  background-color: var(--color-danger-background);
}

.order-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin: 20px 0 0;
}

.order-summary div {
  display: grid;
  gap: 6px;
  padding: 16px;
  background-color: var(--color-background);
  border-radius: 8px;
}

.order-summary dt {
  font-size: 0.875rem;
  color: var(--color-muted);
}

.order-summary dd {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  overflow-wrap: anywhere;
}

.total {
  color: var(--color-primary);
}

.order-notes {
  margin: 16px 0 0;
  padding: 12px 16px;
  overflow-wrap: anywhere;
  background-color: var(--color-background);
  border-radius: 8px;
}

.order-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.order-details {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.order-details h3 {
  margin: 0 0 16px;
}

.details-table {
  min-width: 600px;
}

.product-name {
  min-width: 180px;
  max-width: 320px;
  overflow-wrap: anywhere;
}

.money {
  text-align: right;
  white-space: nowrap;
}

.quantity {
  text-align: center;
}

@media (max-width: 700px) {
  .page-header {
    align-items: stretch;
    flex-direction: column;
  }

  .order-card-header {
    flex-direction: column;
  }

  .order-summary {
    grid-template-columns: 1fr;
  }

  .order-actions {
    flex-direction: column;
  }
}
</style>