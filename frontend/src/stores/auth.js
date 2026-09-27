import {
  reactive,
  readonly,
} from 'vue'

import {
  getCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
} from '../services/authService'

import {
  clearAuthTokens,
  getAccessToken,
  getRefreshToken,
  saveAccessToken,
  saveRefreshToken,
} from '../services/authStorage'

const state = reactive({
  user: null,
  initialized: false,
})

const readonlyState = readonly(state)

async function initializeAuth() {
  if (state.initialized) {
    return
  }

  const accessToken = getAccessToken()
  const refreshToken = getRefreshToken()

  if (
    !accessToken
    && !refreshToken
  ) {
    state.initialized = true
    return
  }

  try {
    state.user = await getCurrentUser()
  } catch (error) {
    clearAuthTokens()
    state.user = null
  } finally {
    state.initialized = true
  }
}

async function refreshCurrentUser() {
  if (
    !getAccessToken()
    && !getRefreshToken()
  ) {
    state.user = null
    return null
  }

  state.user = await getCurrentUser()

  return state.user
}

async function login(credentials) {
  const response = await loginUser(credentials)

  saveAccessToken(response.access_token)
  saveRefreshToken(response.refresh_token)

  state.user = response.user
  state.initialized = true

  return response
}

async function register(userData) {
  return registerUser(userData)
}

async function logout() {
  const refreshToken = getRefreshToken()

  try {
    if (refreshToken) {
      await logoutUser(refreshToken)
    }
  } catch (error) {
    console.error(
      'No fue posible revocar el refresh token.',
      error,
    )
  } finally {
    clearAuthTokens()
    state.user = null
    state.initialized = true
  }
}

function isAuthenticated() {
  const hasToken = Boolean(
    getAccessToken()
    || getRefreshToken()
  )

  return Boolean(
    hasToken
    && state.user
  )
}

function hasAnyRole(roles) {
  const currentRole = state.user?.role?.name

  if (!currentRole) {
    return false
  }

  const normalizedRoles = roles.map(
    (role) => role.toUpperCase(),
  )

  return normalizedRoles.includes(
    currentRole.toUpperCase(),
  )
}

export function useAuth() {
  return {
    state: readonlyState,
    initializeAuth,
    refreshCurrentUser,
    login,
    register,
    logout,
    isAuthenticated,
    hasAnyRole,
  }
}