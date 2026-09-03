<script setup>
import {
  onMounted,
  reactive,
  ref,
} from 'vue'
import { RouterLink } from 'vue-router'

import {
  getOrders,
  getOrderStatuses,
  updateOrderStatus,
} from '../services/orderService'

const orders = ref([])
const statuses = ref([])
const selectedStatuses = reactive({})

const loading = ref(false)
const updatingId = ref(null)
const expandedOrderId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')

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

  try {
    orders.value = await getOrders()
    statuses.value = await getOrderStatuses()

    for (const order of orders.value) {
      selectedStatuses[order.id] = ''
    }
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    loading.value = false
  }
}

async function changeOrderStatus(order) {
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
    errorMessage.value = getErrorMessage(error)
  } finally {
    updatingId.value = null
  }
}

onMounted(loadOrders)
</script>

<template>
  <main class="orders-page">
    <header class="page-header">
      <div>
        <h1>Gestión de pedidos</h1>

        <p>
          Consultá pedidos y actualizá su estado.
        </p>
      </div>

      <RouterLink to="/">
        Volver al inicio
      </RouterLink>
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
      <h2>No hay pedidos registrados</h2>
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

        <section class="customer-information">
          <strong>
            {{ order.user.first_name }}
            {{ order.user.last_name }}
          </strong>

          <span>{{ order.user.email }}</span>
        </section>

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

        <section class="status-management">
          <template
            v-if="getAvailableStatuses(order).length > 0"
          >
            <label :for="`status-${order.id}`">
              Cambiar estado
            </label>

            <div class="status-controls">
              <select
                :id="`status-${order.id}`"
                v-model="selectedStatuses[order.id]"
                :disabled="updatingId === order.id"
              >
                <option value="">
                  Seleccionar estado
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
                :disabled="updatingId === order.id"
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
            Este pedido se encuentra en un estado final.
          </p>
        </section>

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
                  <td>{{ detail.product.name }}</td>

                  <td>
                    {{ formatPrice(detail.unit_price) }}
                  </td>

                  <td>{{ detail.quantity }}</td>

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

.empty-state,
.order-card {
  padding: 24px;
  background-color: white;
  border: 1px solid #dddddd;
  border-radius: 8px;
}

.empty-state {
  text-align: center;
}

.orders-list {
  display: grid;
  gap: 20px;
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

.customer-information {
  display: grid;
  gap: 4px;
  margin-top: 20px;
  padding: 12px;
  background-color: #f5f5f5;
  border-radius: 6px;
}

.customer-information span {
  color: #666666;
}

.order-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 16px;
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

.status-management {
  margin: 20px 0;
}

.status-management label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
}

.status-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-controls select {
  min-width: 220px;
  padding: 9px;
  background-color: white;
  border: 1px solid #bbbbbb;
  border-radius: 4px;
}

.final-status {
  color: #666666;
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
  .order-card-header,
  .status-controls {
    align-items: stretch;
    flex-direction: column;
  }

  .order-summary {
    grid-template-columns: 1fr;
  }

  .status-controls select {
    width: 100%;
  }
}
</style>