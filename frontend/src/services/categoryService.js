import api from './api'

export async function getCategories() {
  const response = await api.get('/categories')
  return response.data.data
}

export async function createCategory(category) {
  const response = await api.post('/categories', category)
  return response.data.data
}

export async function updateCategory(categoryId, category) {
  const response = await api.put(
    `/categories/${categoryId}`,
    category,
  )

  return response.data.data
}

export async function deactivateCategory(categoryId) {
  const response = await api.delete(
    `/categories/${categoryId}`,
  )

  return response.data.data
}