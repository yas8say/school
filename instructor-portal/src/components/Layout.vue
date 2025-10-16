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
        <div class="flex items-center space-x-4 border-b pb-4">
          <div class="w-16 h-16 rounded-full bg-gray-200 overflow-hidden flex items-center justify-center">
            <img
              v-if="admin.image"
              :src="`data:image/jpeg;base64,${admin.image}`"
              alt="Admin"
              class="object-cover w-full h-full"
            />
            <span v-else class="text-sm text-gray-500">No Image</span>
          </div>
          <div>
            <h2 class="text-xl font-semibold text-gray-800">{{ admin.name || 'No Name' }}</h2>
            <p class="text-sm text-gray-500">{{ admin.role || 'Admin' }}</p>
          </div>
        </div>
  
        <!-- Navigation Buttons -->
        <nav class="space-y-3">
          <router-link to="/attendance" class="block">
            <button class="w-full text-left px-4 py-2 rounded hover:bg-blue-100 bg-blue-50 text-blue-800 font-medium">
              Attendance Portal
            </button>
          </router-link>
        </nav>
  
        <!-- Logout Button -->
        <div class="pt-4 border-t">
          <button
            class="w-full px-4 py-2 rounded bg-red-100 text-red-600 font-medium hover:bg-red-200"
            @click="logout"
          >
            Logout
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
  import { ref } from 'vue'
  import { session } from '../data/session'
  
  const admin = ref({
    name: 'Admin User',
    role: 'Admin',
    image: null
  })
  
  const logout = session.logout.submit
  const showSidebar = ref(false)
  </script>
  