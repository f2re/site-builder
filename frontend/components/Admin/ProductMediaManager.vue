<script setup lang="ts">
import { ref } from 'vue'
import { useMediaUpload } from '~/composables/useMediaUpload'
import { useToast } from '~/composables/useToast'

interface ProductImage {
  id?: string
  url: string
  alt: string
  is_cover: boolean
  sort_order: number
}

const props = defineProps<{
  modelValue: ProductImage[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: ProductImage[]]
}>()

const { uploadImage } = useMediaUpload()
const toast = useToast()
const fileInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files?.length) return

  isUploading.value = true
  const newImages = [...props.modelValue]

  try {
    for (const file of Array.from(files)) {
      const url = await uploadImage(file, file.name, 'product')
      newImages.push({
        url,
        alt: file.name,
        is_cover: newImages.length === 0,
        sort_order: newImages.length
      })
    }
    emit('update:modelValue', newImages)
    toast.success('Успех', 'Изображения загружены')
  } catch (error) {
    console.error('Upload failed:', error)
  } finally {
    isUploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

const removeImage = (index: number) => {
  const newImages = [...props.modelValue]
  const removed = newImages.splice(index, 1)[0]
  
  // If we removed the cover, set the first remaining as cover
  if (removed.is_cover && newImages.length > 0) {
    newImages[0].is_cover = true
  }
  
  emit('update:modelValue', newImages)
}

const setCover = (index: number) => {
  const newImages = props.modelValue.map((img, i) => ({
    ...img,
    is_cover: i === index
  }))
  emit('update:modelValue', newImages)
}

const moveImage = (index: number, direction: 'up' | 'down') => {
  const newImages = [...props.modelValue]
  const targetIndex = direction === 'up' ? index - 1 : index + 1
  
  if (targetIndex < 0 || targetIndex >= newImages.length) return
  
  const temp = newImages[index]
  newImages[index] = newImages[targetIndex]
  newImages[targetIndex] = temp
  
  // Update sort order
  newImages.forEach((img, i) => {
    img.sort_order = i
  })
  
  emit('update:modelValue', newImages)
}
</script>

<template>
  <div class="media-manager">
    <div class="media-grid">
      <div 
        v-for="(image, index) in modelValue" 
        :key="image.url" 
        class="media-item"
        :class="{ 'is-cover': image.is_cover }"
      >
        <div class="media-preview">
          <img :src="image.url" :alt="image.alt" />
          <div v-if="image.is_cover" class="cover-badge">Обложка</div>
        </div>
        
        <div class="media-actions">
          <button 
            type="button" 
            class="action-btn" 
            title="Сделать обложкой"
            @click="setCover(index)"
            :disabled="image.is_cover"
          >
            <Icon name="ph:star-bold" :class="{ 'text-yellow-400': image.is_cover }" />
          </button>
          <button 
            type="button" 
            class="action-btn" 
            title="Переместить влево"
            @click="moveImage(index, 'up')"
            :disabled="index === 0"
          >
            <Icon name="ph:arrow-left-bold" />
          </button>
          <button 
            type="button" 
            class="action-btn" 
            title="Переместить вправо"
            @click="moveImage(index, 'down')"
            :disabled="index === modelValue.length - 1"
          >
            <Icon name="ph:arrow-right-bold" />
          </button>
          <button 
            type="button" 
            class="action-btn delete-btn" 
            title="Удалить"
            @click="removeImage(index)"
          >
            <Icon name="ph:trash-bold" />
          </button>
        </div>
      </div>

      <button 
        type="button" 
        class="upload-placeholder" 
        @click="triggerUpload"
        :disabled="isUploading"
      >
        <div v-if="isUploading" class="upload-loading">
          <Icon name="ph:spinner" class="animate-spin" size="32" />
          <span>Загрузка...</span>
        </div>
        <div v-else class="upload-content">
          <Icon name="ph:plus-bold" size="32" />
          <span>Добавить фото</span>
        </div>
      </button>
    </div>

    <input 
      ref="fileInput"
      type="file" 
      multiple 
      accept="image/*" 
      class="hidden" 
      @change="handleUpload"
    />
  </div>
</template>

<style scoped>
.media-manager {
  width: 100%;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}

.media-item {
  position: relative;
  aspect-ratio: 1;
  background: var(--color-surface-2);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: all var(--transition-fast);
}

.media-item.is-cover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.media-preview {
  width: 100%;
  height: 100%;
  position: relative;
}

.media-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: var(--color-accent);
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.media-actions {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.media-item:hover .media-actions {
  opacity: 1;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover:not(:disabled) {
  background: var(--color-accent);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.delete-btn:hover:not(:disabled) {
  background: var(--color-error);
}

.upload-placeholder {
  aspect-ratio: 1;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-2);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.upload-placeholder:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: var(--color-bg-subtle);
}

.upload-content, .upload-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-content span {
  font-size: var(--text-sm);
  font-weight: 500;
}

.hidden {
  display: none;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.text-yellow-400 {
  color: #fbbf24;
}
</style>
