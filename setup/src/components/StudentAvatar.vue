<template>
  <div class="student-avatar">
    <img
      v-if="imageUrl"
      :src="imageUrl"
      :alt="altText"
      class="avatar-image"
      @error="handleImageError"
    />
    <div v-else class="avatar-placeholder">
      {{ initials }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  imageUrl: {
    type: String,
    default: ''
  },
  studentName: {
    type: String,
    default: ''
  },
  altText: {
    type: String,
    default: 'Student'
  }
})

const emit = defineEmits(['error'])

const getProfileImageUrl = (imgUrl) => {
  if (!imgUrl) return null
  if (imgUrl.startsWith('http') || imgUrl.startsWith('//')) {
    return imgUrl
  }
  if (imgUrl.startsWith('/')) {
    return window.location.origin + imgUrl
  }
  const baseUrl = window.location.origin
  return `${baseUrl}/${imgUrl.replace(/^\//, '')}`
}

const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map(part => part.charAt(0))
    .join('')
    .toUpperCase()
    .substring(0, 2)
}

const imageUrl = computed(() => {
  return props.imageUrl ? getProfileImageUrl(props.imageUrl) : null
})

const initials = computed(() => {
  return getInitials(props.studentName)
})

const handleImageError = (event) => {
  event.target.style.display = 'none'
  emit('error', event)
}
</script>

<style scoped>
.student-avatar {
  flex-shrink: 0;
}

.avatar-image {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
}
</style>