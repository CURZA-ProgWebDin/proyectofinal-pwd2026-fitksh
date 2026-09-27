import axios from 'axios'

import {
  clearAuthTokens,
  getAccessToken,
  getRefreshToken,
  saveAccessToken,
} from './authStorage'

const apiConfiguration = {
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 5000,
}

const api = axios.create(apiConfiguration)

// Cliente separado para evitar que la petición de renovación
// pase nuevamente por los interceptores principales.
const refreshApi = axios.create(apiConfiguration)

function redirectToLogin() {
  const publicPaths = [
    '/login',
    '/register',
  ]

  if (!publicPaths.includes(window.location.pathname)) {
    window.location.assign('/login')
  }
}

api.interceptors.request.use((config) => {
  const accessToken = getAccessToken()

  if (
    accessToken
    && !config.headers.Authorization
  ) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }

  return config
})

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config

    const excludedUrls = [
      '/auth/login',
      '/auth/register',
      '/auth/refresh',
      '/auth/logout',
    ]

    if (
      error.response?.status !== 401
      || !originalRequest
      || excludedUrls.includes(originalRequest.url)
    ) {
      return Promise.reject(error)
    }

    const refreshToken = getRefreshToken()

    if (
      !refreshToken
      || originalRequest._retry
    ) {
      clearAuthTokens()
      redirectToLogin()

      return Promise.reject(error)
    }

    originalRequest._retry = true

    try {
      const refreshResponse = await refreshApi.post(
        '/auth/refresh',
        null,
        {
          headers: {
            Authorization: `Bearer ${refreshToken}`,
          },
        },
      )

      const newAccessToken =
        refreshResponse.data.access_token

      saveAccessToken(newAccessToken)

      originalRequest.headers.Authorization =
        `Bearer ${newAccessToken}`

      return api(originalRequest)
    } catch (refreshError) {
      clearAuthTokens()
      redirectToLogin()

      return Promise.reject(refreshError)
    }
  },
)

export default api