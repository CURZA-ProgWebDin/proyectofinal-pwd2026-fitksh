import {
  reactive,
  readonly,
} from 'vue'

import {
  getCurrentUser,
  loginUser,
  registerUser,
} from '../services/authService'
import {
  getAccessToken,
  removeAccessToken,
  saveAccessToken,
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

  if (!accessToken) {
    state.initialized = true
    return
  }

  try {
    state.user = await getCurrentUser()
  } catch (error) {
    removeAccessToken()
    state.user = null
  } finally {
    state.initialized = true
  }
}

async function login(credentials) {
  const response = await loginUser(credentials)

  saveAccessToken(response.access_token)

  state.user = response.user
  state.initialized = true

  return response
}

async function register(userData) {
  return registerUser(userData)
}

function logout() {
  removeAccessToken()
  state.user = null
  state.initialized = true
}

function isAuthenticated() {
  return Boolean(
    getAccessToken()
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
    login,
    register,
    logout,
    isAuthenticated,
    hasAnyRole,
  }
}