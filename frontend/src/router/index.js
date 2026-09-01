import { createRouter, createWebHistory } from 'vue-router'

import { useAuth } from '../stores/auth'
import CategoriesView from '../views/CategoriesView.vue'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ProductsView from '../views/ProductsView.vue'
import RegisterView from '../views/RegisterView.vue'
import UsersView from '../views/UsersView.vue'
import CatalogView from '../views/CatalogView.vue'
import CartView from '../views/CartView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      guestOnly: true,
    },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: {
      guestOnly: true,
    },
  },
  {
    path: '/catalog',
    name: 'catalog',
    component: CatalogView,
    meta: {
      requiresAuth: true,
      roles: ['CLIENTE'],
    },
  },
    {
    path: '/cart',
    name: 'cart',
    component: CartView,
    meta: {
      requiresAuth: true,
      roles: ['CLIENTE'],
    },
  },
  {
    path: '/categories',
    name: 'categories',
    component: CategoriesView,
    meta: {
      requiresAuth: true,
      roles: ['ADMINISTRADOR'],
    },
  },
  {
    path: '/products',
    name: 'products',
    component: ProductsView,
    meta: {
      requiresAuth: true,
      roles: ['ADMINISTRADOR'],
    },
  },
  {
    path: '/users',
    name: 'users',
    component: UsersView,
    meta: {
      requiresAuth: true,
      roles: ['ADMINISTRADOR'],
    },
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuth()

  await auth.initializeAuth()

  if (
    to.meta.guestOnly
    && auth.isAuthenticated()
  ) {
    return {
      name: 'home',
    }
  }

  if (
    to.meta.requiresAuth
    && !auth.isAuthenticated()
  ) {
    return {
      name: 'login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (
    Array.isArray(to.meta.roles)
    && !auth.hasAnyRole(to.meta.roles)
  ) {
    return {
      name: 'home',
    }
  }

  return true
})

export default router