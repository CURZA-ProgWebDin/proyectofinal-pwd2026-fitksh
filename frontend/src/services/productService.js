import api from './api'

export async function getProducts() {
  const response = await api.get('/products')
  return response.data.data
}

export async function createProduct(product) {
  const response = await api.post('/products', product)
  return response.data.data
}

export async function updateProduct(productId, product) {
  const response = await api.put(
    `/products/${productId}`,
    product,
  )

  return response.data.data
}

export async function deactivateProduct(productId) {
  const response = await api.delete(
    `/products/${productId}`,
  )

  return response.data.data
}