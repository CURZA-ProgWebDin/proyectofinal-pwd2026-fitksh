import axios from 'axios'

import {
  getAccessToken,
  removeAccessToken,
} from './authStorage'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 5000,
})

api.interceptors.request.use((config) => {
  const accessToken = getAccessToken()

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }

  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const accessToken = getAccessToken()

    if (
      error.response?.status === 401
      && accessToken
    ) {
      removeAccessToken()

      const publicPaths = [
        '/login',
        '/register',
      ]

      if (!publicPaths.includes(window.location.pathname)) {
        window.location.assign('/login')
      }
    }

    return Promise.reject(error)
  },
)

export default api