<script setup lang="ts">
import { useMediaUpload } from '~/composables/useMediaUpload'
import { useToast } from '~/composables/useToast'

const props = defineProps<{
  modelValue: string[]
  postId?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const { uploadImage } = useMediaUpload()
const toast = useToast()
const fileInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)

function triggerUpload() {
  fileInput.value?.click()
}

async function handleUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files?.length) return

  isUploading.value = true
  const newImages = [...props.modelValue]

  try {
    for (const file of Array.from(files)) {
      const url = await uploadImage(file, file.name, 'blog')
      newImages.push(url)
    }
    emit('update:modelValue', newImages)
    toast.success('Успех', 'Изображения добавлены в карусель')
  } catch (error) {
    console.error('Upload failed:', error)
  } finally {
    isUploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

function removeImage(index: number) {
  const newImages = [...props.modelValue]
  newImages.splice(index, 1)
  emit('update:modelValue', newImages)
}

function moveImage(index: number, direction: 'up' | 'down') {
  const newImages = [...props.modelValue]
  const targetIndex = direction === 'up' ? index - 1 : index + 1
  if (targetIndex < 0 || targetIndex >= newImages.length) return

  const temp = newImages[index]
  newImages[index] = newImages[targetIndex]
  newImages[targetIndex] = temp
  emit('update:modelValue', newImages)
}
</script>

<template>
  <div class="carousel-manager">
    <div class="carousel-grid">
      <div
        v-for="(url, index) in modelValue"
        :key="url + index"
        class="carousel-item"
      >
        <div class="carousel-preview">
          <img :src="url" :alt="`Слайд ${index + 1}`" />
          <div v-if="index === 0" class="first-badge">Первый</div>
        </div>

        <div class="carousel-actions">
          <button
            type="button"
            class="action-btn"
            title="Переместить влево"
            :disabled="index === 0"
            @click="moveImage(index, 'up')"
          >
            <Icon name="ph:arrow-left-bold" size="14" />
          </button>
          <button
            type="button"
            class="action-btn"
            title="Переместить вправо"
            :disabled="index === modelValue.length - 1"
            @click="moveImage(index, 'down')"
          >
            <Icon name="ph:arrow-right-bold" size="14" />
          </button>
          <button
            type="button"
            class="action-btn delete-btn"
            title="Удалить"
            @click="removeImage(index)"
          >
            <Icon name="ph:trash-bold" size="14" />
          </button>
        </div>
      </div>

      <!-- Upload placeholder -->
      <button
        type="button"
        class="upload-placeholder"
        :disabled="isUploading"
        @click="triggerUpload"
      >
        <div v-if="isUploading" class="upload-loading">
          <Icon name="ph:spinner" class="animate-spin" size="24" />
          <span>Загрузка...</span>
        </div>
        <div v-else class="upload-content">
          <Icon name="ph:plus-bold" size="24" />
          <span>Добавить фото</span>
        </div>
      </button>
    </div>

    <input
      ref="fileInput"
      type="file"
      multiple
      accept="image/*"
      class="hidden-input"
      @change="handleUpload"
    />
  </div>
</template>

<style scoped>
.carousel-manager {
  width: 100%;
}

.carousel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.carousel-item {
  position: relative;
  aspect-ratio: 16 / 9;
  background: var(--color-surface-2);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.carousel-item:first-child {
  border-color: var(--color-accent);
}

.carousel-preview {
  width: 100%;
  height: 100%;
  position: relative;
}

.carousel-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.first-badge {
  position: absolute;
  top: 4px;
  left: 4px;
  background: var(--color-accent);
  color: var(--color-on-accent);
  font-size: 9px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 3px;
  text-transform: uppercase;
}

.carousel-actions {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.carousel-item:hover .carousel-actions {
  opacity: 1;
}

.action-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background var(--transition-fast);
  padding: 0;
}

.action-btn:hover:not(:disabled) {
  background: var(--color-accent);
}

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.delete-btn:hover:not(:disabled) {
  background: var(--color-error);
}

.upload-placeholder {
  aspect-ratio: 16 / 9;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-2);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.upload-placeholder:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.upload-content,
.upload-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.upload-content span,
.upload-loading span {
  font-size: var(--text-xs);
  font-weight: 500;
}

.hidden-input {
  display: none;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
