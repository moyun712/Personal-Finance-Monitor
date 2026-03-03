<script setup lang="ts">
/**
 * LayoutSwitch — dynamically renders MobileLayout or PCLayout
 * based on viewport width. Breakpoint: 768px.
 * Used as a parent route component; child routes render inside <router-view />.
 * Also mounts AiFloatingWidget globally (visible on all main pages, not login/register).
 */
import { useResponsive } from '@/composables/useResponsive'
import MobileLayout from './MobileLayout.vue'
import PCLayout from './PCLayout.vue'
import AiFloatingWidget from '@/components/AiFloatingWidget.vue'

const { isPC } = useResponsive()
</script>

<template>
  <PCLayout v-if="isPC">
    <router-view />
  </PCLayout>
  <MobileLayout v-else>
    <router-view />
  </MobileLayout>
  <AiFloatingWidget />
</template>
