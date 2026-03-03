/**
 * Reactive composable that tracks whether the viewport matches PC breakpoint.
 * Uses `matchMedia('(min-width: 768px)')` with event-based updates.
 */
import { ref, onMounted, onUnmounted } from 'vue'

const PC_BREAKPOINT = '(min-width: 768px)'

export function useResponsive() {
  const isPC = ref(false)
  let mql: MediaQueryList | null = null

  const update = (e: MediaQueryListEvent | MediaQueryList) => {
    isPC.value = e.matches
  }

  onMounted(() => {
    mql = window.matchMedia(PC_BREAKPOINT)
    isPC.value = mql.matches
    mql.addEventListener('change', update as (e: MediaQueryListEvent) => void)
  })

  onUnmounted(() => {
    mql?.removeEventListener('change', update as (e: MediaQueryListEvent) => void)
  })

  return { isPC }
}
