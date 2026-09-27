import api from './api'

export async function getUsers() {
  const response = await api.get('/users')
  return response.data.data
}

export async function getRoles() {
  const response = await api.get('/roles')
  return response.data.data
}

export async function createUser(userData) {
  const response = await api.post('/users', userData)
  return response.data.data
}

export async function updateUser(userId, userData) {
  const response = await api.put(
    `/users/${userId}`,
    userData,
  )

  return response.data.data
}

export async function deactivateUser(userId) {
  const response = await api.delete(`/users/${userId}`)
  return response.data.data
}