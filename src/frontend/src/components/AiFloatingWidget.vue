<script setup lang="ts">
/**
 * AiFloatingWidget — Global AI assistant floating action button (FAB)
 * and expandable chat panel.
 *
 * Mobile (<768px): FAB at bottom-right, click opens 85vh bottom-sheet overlay.
 * PC (≥768px): FAB at bottom-right, click opens 400px right-side slide-in panel.
 *
 * This is a placeholder for Step 0.5. Full chat functionality is implemented
 * in Step 3.12 (Mock) and Step 11.3 (real LLM API).
 */
import { ref } from 'vue'
import { useResponsive } from '@/composables/useResponsive'

const { isPC } = useResponsive()
const isPanelOpen = ref(false)

function togglePanel() {
  isPanelOpen.value = !isPanelOpen.value
}

function closePanel() {
  isPanelOpen.value = false
}
</script>

<template>
  <!-- FAB Button -->
  <button
    class="ai-fab"
    :class="{ 'ai-fab--open': isPanelOpen }"
    @click="togglePanel"
    aria-label="AI 助手"
  >
    <span class="ai-fab-icon">{{ isPanelOpen ? '✕' : '🤖' }}</span>
  </button>

  <!-- Overlay backdrop (mobile only) -->
  <Transition name="fade">
    <div v-if="isPanelOpen && !isPC" class="ai-overlay" @click="closePanel" />
  </Transition>

  <!-- Chat Panel -->
  <Transition :name="isPC ? 'slide-right' : 'slide-up'">
    <div v-if="isPanelOpen" class="ai-panel" :class="isPC ? 'ai-panel--pc' : 'ai-panel--mobile'">
      <div class="ai-panel-header">
        <span class="ai-panel-title">🤖 AI 财务助手</span>
        <button class="ai-panel-close" @click="closePanel">✕</button>
      </div>
      <div class="ai-panel-body">
        <p class="ai-placeholder">AI 助手功能开发中…</p>
        <p class="ai-placeholder-sub">将在 Phase 3 提供 Mock 对话，Phase 11 对接真实 LLM</p>
      </div>
      <div class="ai-panel-footer">
        <div class="ai-input-bar">
          <input type="text" placeholder="输入消息…" disabled class="ai-input" />
          <button class="ai-send-btn" disabled>发送</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* ── FAB ─────────────────────────────────────────────────── */
.ai-fab {
  position: fixed;
  z-index: 1000;
  bottom: 80px;
  right: 20px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(34, 197, 94, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.ai-fab:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.5);
}

.ai-fab--open {
  background: linear-gradient(135deg, #64748b, #475569);
  box-shadow: 0 4px 12px rgba(100, 116, 139, 0.3);
}

.ai-fab-icon {
  line-height: 1;
}

/* ── Overlay (mobile) ────────────────────────────────────── */
.ai-overlay {
  position: fixed;
  inset: 0;
  z-index: 1001;
  background: rgba(0, 0, 0, 0.4);
}

/* ── Panel ───────────────────────────────────────────────── */
.ai-panel {
  position: fixed;
  z-index: 1002;
  background: var(--color-surface, #fff);
  display: flex;
  flex-direction: column;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.12);
}

/* Mobile: bottom sheet, 85vh */
.ai-panel--mobile {
  bottom: 0;
  left: 0;
  right: 0;
  height: 85vh;
  border-radius: 16px 16px 0 0;
}

/* PC: right side panel, 400px wide */
.ai-panel--pc {
  top: 0;
  right: 0;
  bottom: 0;
  width: 400px;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.1);
}

.ai-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border, #e5e5e5);
  flex-shrink: 0;
}

.ai-panel-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary, #1a1a1a);
}

.ai-panel-close {
  background: none;
  border: none;
  font-size: 18px;
  color: var(--color-text-secondary, #666);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.ai-panel-close:hover {
  background: rgba(0, 0, 0, 0.06);
}

.ai-panel-body {
  flex: 1;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
}

.ai-placeholder {
  font-size: 16px;
  color: var(--color-text-secondary, #666);
  margin-bottom: 8px;
}

.ai-placeholder-sub {
  font-size: 13px;
  color: var(--color-text-secondary, #999);
  opacity: 0.7;
}

.ai-panel-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--color-border, #e5e5e5);
  flex-shrink: 0;
}

.ai-input-bar {
  display: flex;
  gap: 8px;
}

.ai-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--color-border, #e5e5e5);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: var(--color-bg, #f5f5f5);
  color: var(--color-text-secondary, #999);
}

.ai-send-btn {
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  background: var(--color-income, #22c55e);
  color: #fff;
  font-size: 14px;
  cursor: not-allowed;
  opacity: 0.5;
}

/* ── Transitions ─────────────────────────────────────────── */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s ease;
}
.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
}
</style>
