<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  src: {
    type: String,
    default: '',
  },
  alt: {
    type: String,
    required: true,
  },
  small: {
    type: Boolean,
    default: false,
  },
})

const imageFailed = ref(false)

watch(
  () => props.src,
  () => {
    imageFailed.value = false
  },
)
</script>

<template>
  <div class="product-picture" :class="{ 'is-small': props.small }">
    <img
      v-if="props.src && !imageFailed"
      :src="props.src"
      :alt="props.alt"
      loading="lazy"
      @error="imageFailed = true"
    >

    <span v-else>
      {{ props.small ? 'Sin imagen' : 'Imagen no disponible' }}
    </span>
  </div>
</template>

<style scoped>
.product-picture {
  display: flex;
  width: 100%;
  height: 200px;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  color: var(--color-muted);
  text-align: center;
  background-color: var(--color-surface);
}

.product-picture img {
  display: block;
  width: 100%;
  height: 100%;
  padding: 16px;
  object-fit: contain;
}

.product-picture.is-small {
  width: 64px;
  height: 64px;
  font-size: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.product-picture.is-small img {
  padding: 4px;
}
</style>