<script setup>
import {
  onMounted,
  reactive,
  computed,
  ref,
} from 'vue'
import { RouterLink } from 'vue-router'

import {
  getOrders,
  getOrderStatuses,
  updateOrderStatus,
} from '../services/orderService'

import {
  formatDate,
  formatPrice,
  formatStatus,
} from '../utils/formatters'

import { getApiErrorMessage } from '../utils/apiErrors'

const orders = ref([])
const statuses = ref([])
const selectedStatuses = reactive({})

const loading = ref(false)
const updatingId = ref(null)
const isBusy = computed(() => {
  return loading.value || updatingId.value !== null
})

const expandedOrderId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')
const loadError = ref('')

const allowedTransitions = {
  PENDIENTE: [
    'CONFIRMADO',
    'CANCELADO',
  ],
  CONFIRMADO: [
    'EN_PREPARACION',
    'CANCELADO',
  ],
  EN_PREPARACION: [
    'LISTO',
    'CANCELADO',
  ],
  LISTO: [
    'ENTREGADO',
  ],
  ENTREGADO: [],
  CANCELADO: [],
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

function clearMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

function getAvailableStatuses(order) {
  const allowedNames = (
    allowedTransitions[order.status.name] ?? []
  )

  return statuses.value.filter(
    (status) => allowedNames.includes(status.name),
  )
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
    statuses.value = await getOrderStatuses()

    for (const order of orders.value) {
      selectedStatuses[order.id] = ''
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

async function changeOrderStatus(order) {
  if (isBusy.value) {
    return
  }
  clearMessages()

  const statusId = Number(
    selectedStatuses[order.id],
  )

  if (!Number.isInteger(statusId) || statusId <= 0) {
    errorMessage.value = (
      'Debe seleccionar un estado.'
    )
    return
  }

  const selectedStatus = statuses.value.find(
    (status) => status.id === statusId,
  )

  if (!selectedStatus) {
    errorMessage.value = (
      'El estado seleccionado no es válido.'
    )
    return
  }

  if (
    !window.confirm(
      (
        `¿Deseás cambiar el pedido #${order.id} `
        + `a ${formatStatus(selectedStatus.name)}?`
      ),
    )
  ) {
    return
  }

  updatingId.value = order.id

  try {
    const updatedOrder = await updateOrderStatus(
      order.id,
      statusId,
    )

    const orderIndex = orders.value.findIndex(
      (currentOrder) => currentOrder.id === order.id,
    )

    if (orderIndex !== -1) {
      orders.value[orderIndex] = updatedOrder
    }

    selectedStatuses[order.id] = ''

    successMessage.value = (
      `Pedido #${order.id} actualizado correctamente.`
    )
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error)
  } finally {
    updatingId.value = null
  }
}

onMounted(loadOrders)
</script>

<template>
  <main class="admin-page admin-orders-page">
    <header class="page-header">
      <div>
        <h1>Gestión de pedidos</h1>
        <p>Consultá los pedidos de los clientes y actualizá su estado.</p>
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
      <p class="message error-message" role="alert">
        {{ loadError }}
      </p>

      <button
        type="button"
        :disabled="isBusy"
        @click="loadOrders"
      >
        Reintentar
      </button>
    </section>

    <section
      v-else-if="orders.length === 0"
      class="panel orders-state"
    >
      <h2>No hay pedidos registrados</h2>

      <p class="state-description">
        Los pedidos creados por los clientes aparecerán acá.
      </p>
    </section>

    <section
      v-else
      class="orders-list"
      aria-label="Pedidos registrados"
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

        <div class="customer-information">
          <span>Cliente</span>

          <strong>
            {{ order.user.first_name }}
            {{ order.user.last_name }}
          </strong>

          <span>{{ order.user.email }}</span>
        </div>

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

        <section class="status-management">
          <template v-if="getAvailableStatuses(order).length > 0">
            <label :for="`status-${order.id}`">
              Cambiar estado
            </label>

            <div class="status-controls">
              <select
                :id="`status-${order.id}`"
                v-model="selectedStatuses[order.id]"
                :disabled="isBusy"
              >
                <option value="">
                  Seleccioná un estado
                </option>

                <option
                  v-for="status in getAvailableStatuses(order)"
                  :key="status.id"
                  :value="status.id"
                >
                  {{ formatStatus(status.name) }}
                </option>
              </select>

              <button
                type="button"
                :disabled="isBusy || !selectedStatuses[order.id]"
                @click="changeOrderStatus(order)"
              >
                {{
                  updatingId === order.id
                    ? 'Actualizando...'
                    : 'Actualizar estado'
                }}
              </button>
            </div>
          </template>

          <p v-else class="final-status">
            Este pedido ya no admite cambios de estado.
          </p>
        </section>

        <button
          type="button"
          class="secondary-button details-toggle"
          :aria-expanded="expandedOrderId === order.id"
          :aria-controls="`admin-order-details-${order.id}`"
          @click="toggleDetails(order.id)"
        >
          {{
            expandedOrderId === order.id
              ? 'Ocultar detalle'
              : 'Ver detalle'
          }}
        </button>

        <section
          v-show="expandedOrderId === order.id"
          :id="`admin-order-details-${order.id}`"
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
                  <td>{{ detail.product.name }}</td>

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
.orders-state {
  text-align: center;
}

.orders-state h2 {
  margin: 0 0 12px;
}

.state-description {
  margin: 0;
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

.customer-information {
  display: grid;
  gap: 4px;
  margin-top: 20px;
  padding: 16px;
  overflow-wrap: anywhere;
  background-color: var(--color-background);
  border-radius: 8px;
}

.customer-information span {
  color: var(--color-muted);
}

.order-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin: 16px 0 0;
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

.status-management {
  margin: 20px 0;
}

.status-management label {
  display: block;
  margin-bottom: 8px;
}

.status-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.status-controls select {
  width: min(100%, 280px);
  min-width: 0;
  min-height: 44px;
}

.final-status {
  margin: 0;
  color: var(--color-muted);
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
  min-width: 620px;
}

.details-table .money {
  text-align: right;
  white-space: nowrap;
}

.details-table .quantity {
  text-align: center;
}

@media (max-width: 700px) {
  .order-card-header {
    flex-direction: column;
  }

  .order-summary {
    grid-template-columns: 1fr;
  }

  .status-controls {
    align-items: stretch;
    flex-direction: column;
  }

  .status-controls select,
  .details-toggle {
    width: 100%;
  }
}
</style>