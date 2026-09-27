const priceFormatter = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
})

const dateFormatter = new Intl.DateTimeFormat('es-AR', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

export function formatPrice(price) {
  return priceFormatter.format(price)
}

export function formatDate(date) {
  return dateFormatter.format(new Date(date))
}

export function formatStatus(statusName) {
  return statusName.replaceAll('_', ' ')
}