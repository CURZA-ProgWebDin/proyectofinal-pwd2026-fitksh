import { createRouter, createWebHistory } from 'vue-router'

import CategoriesView from '../views/CategoriesView.vue'
import HomeView from '../views/HomeView.vue'
import ProductsView from '../views/ProductsView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/categories',
    name: 'categories',
    component: CategoriesView,
  },
  {
    path: '/products',
    name: 'products',
    component: ProductsView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router