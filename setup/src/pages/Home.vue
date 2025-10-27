<template>
  <div class="flex min-h-screen bg-gray-50 flex-col md:flex-row">
    <!-- Mobile Toggle -->
    <div class="md:hidden p-4 bg-white shadow">
      <button
        @click="showSidebar = !showSidebar"
        class="px-4 py-2 bg-blue-600 text-white rounded"
      >
        {{ showSidebar ? 'Close Menu' : 'Open Menu' }}
      </button>
    </div>

    <!-- Sidebar -->
    <aside
      :class="[
        'bg-white shadow-md p-6 space-y-8 md:block',
        showSidebar ? 'block' : 'hidden',
        'md:w-72'
      ]"
    >
      <!-- Admin Info Card -->
      <div class="flex items-start space-x-4 border-b pb-4">
        <div class="flex-shrink-0 w-16 h-16 rounded-full bg-gray-200 overflow-hidden">
          <img
            :src="adminImage"
            alt="Admin"
            class="object-cover w-full h-full"
          />
        </div>
        <div class="min-w-0 flex-1">
          <h2 class="text-xl font-semibold text-gray-800 break-words">{{ admin.name || 'No Name Available' }}</h2>
          <p class="text-sm text-gray-500 mt-1">Admin</p>
        </div>
      </div>

      <!-- Navigation Buttons -->
      <div class="space-y-3">
        <h3 class="text-sm font-medium text-gray-700">Navigation</h3>
        <nav class="space-y-2">
          <router-link to="/home/quick-setup" class="block">
            <button
              :class="[
                'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors',
                $route.path === '/home/quick-setup' 
                  ? 'bg-blue-100 border border-blue-200 text-blue-800' 
                  : 'bg-blue-50 text-blue-800 hover:bg-blue-100'
              ]"
            >
              <span>Quick Setup</span>
            </button>
          </router-link>

          <router-link to="/home/upload-students" class="block">
            <button
              :class="[
                'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors',
                $route.path === '/home/upload-students' 
                  ? 'bg-blue-100 border border-blue-200 text-blue-800' 
                  : 'bg-blue-50 text-blue-800 hover:bg-blue-100'
              ]"
            >
              <span>Upload Students</span>
            </button>
          </router-link>

          <router-link to="/home/add-student" class="block">
            <button
              :class="[
                'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors',
                $route.path === '/home/add-student' 
                  ? 'bg-green-100 border border-green-200 text-green-800' 
                  : 'bg-green-50 text-green-800 hover:bg-green-100'
              ]"
            >
              <span>Add Student</span>
            </button>
          </router-link>

          <router-link to="/home/upload-instructors" class="block">
            <button
              :class="[
                'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors',
                $route.path === '/home/upload-instructors' 
                  ? 'bg-yellow-100 border border-yellow-200 text-yellow-800' 
                  : 'bg-yellow-50 text-yellow-800 hover:bg-yellow-100'
              ]"
            >
              <span>Upload Instructors</span>
            </button>
          </router-link>

          <router-link to="/home/add-instructor" class="block">
            <button
              :class="[
                'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors',
                $route.path === '/home/add-instructor' 
                  ? 'bg-purple-100 border border-purple-200 text-purple-800' 
                  : 'bg-purple-50 text-purple-800 hover:bg-purple-100'
              ]"
            >
              <span>Add Instructor</span>
            </button>
          </router-link>

          <!-- Admin Settings Button -->
          <router-link to="/home/admin-settings" class="block">
            <button
              :class="[
                'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors',
                $route.path === '/home/admin-settings' 
                  ? 'bg-gray-100 border border-gray-200 text-gray-800' 
                  : 'bg-gray-50 text-gray-800 hover:bg-gray-100'
              ]"
            >
              <span>Admin Settings</span>
            </button>
          </router-link>
        </nav>
      </div>

      <!-- Logout Button -->
      <div class="pt-4 border-t">
        <button
          class="w-full px-4 py-3 rounded bg-red-100 text-red-600 font-medium hover:bg-red-200 flex items-center justify-center space-x-2 transition-colors"
          @click="logout"
        >
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 p-4 md:p-10 bg-white shadow-inner">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { session } from '../data/session'

const route = useRoute()
const router = useRouter()

const admin = ref({
  name: 'Admin User',
  role: 'Admin',
  image: null
})

// Computed property to handle the image source
const adminImage = computed(() => {
  // If admin.image exists and is a base64 string, use it
  if (admin.value.image) {
    return `data:image/jpeg;base64,${admin.value.image}`
  }
  // Otherwise, default to the assets/admin.png
  return new URL('../assets/admin.png', import.meta.url).href
})

const logout = async () => {
  try {
    await session.logout.submit()
    router.push('/account/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

const showSidebar = ref(false)
</script>