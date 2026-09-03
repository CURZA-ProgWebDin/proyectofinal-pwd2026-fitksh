import api from './api'

export async function getOrders() {
  const response = await api.get('/orders')
  return response.data.data
}

export async function getOrder(orderId) {
  const response = await api.get(
    `/orders/${orderId}`,
  )

  return response.data.data
}

export async function createOrder(notes = '') {
  const response = await api.post('/orders', {
    notes,
  })

  return response.data.data
}

export async function updateOrderStatus(
  orderId,
  statusId,
) {
  const response = await api.put(
    `/orders/${orderId}`,
    {
      status_id: statusId,
    },
  )

  return response.data.data
}

export async function cancelOrder(orderId) {
  const response = await api.delete(
    `/orders/${orderId}`,
  )

  return response.data.data
}

export async function getOrderStatuses() {
  const response = await api.get(
    '/order-statuses',
  )

  return response.data.data
}