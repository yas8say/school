<template>
  <div class="border border-gray-300 rounded-lg p-6 mb-6 shadow-sm bg-white max-w-xl mx-auto">
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-1">Institution Name</label>
      <input 
        type="text"
        v-model="institutionName"
        @input="updateField('institutionName', $event.target.value)"
        placeholder="Enter institution name"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>

    <button 
      @click="$emit('pick-image')"
      class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition mb-4"
    >
      Upload Logo
    </button>

    <div v-if="selectedImage" class="my-4 text-center">
      <p class="text-sm font-medium text-gray-700 mb-2">Logo Preview:</p>
      <img :src="selectedImage" class="max-w-[200px] max-h-[200px] mx-auto mb-2 rounded-md shadow" />
      <button 
        @click="$emit('remove-image')"
        class="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition"
      >
        Remove Image
      </button>
    </div>

    <button 
      @click="$emit('submit-institution')"
      class="px-5 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
    >
      Submit Institution Details
    </button>
  </div>
</template>


<script>
export default {
  props: {
    values: Object
  },
  computed: {
    institutionName: {
      get() {
        return this.values.institutionName;
      },
      set(value) {
        this.$emit('update-field', { field: 'institutionName', value });
      }
    },
    selectedImage() {
      return this.values.logo;
    }
  },
  methods: {
    updateField(field, value) {
      this.$emit('update-field', { field, value });
    }
  }
};
</script>

<style scoped>
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.field {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.image-preview {
  margin: 15px 0;
  text-align: center;
}

.image {
  max-width: 200px;
  max-height: 200px;
  margin: 10px 0;
}

button {
  padding: 10px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

button:hover {
  background-color: #45a049;
}
</style>