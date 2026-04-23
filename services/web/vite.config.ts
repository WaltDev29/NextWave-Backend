import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',   // Docker 컨테이너에서 외부 접근 허용
    port: 5173,
    watch: { usePolling: true },  // Docker 볼륨 마운트 환경에서 핫리로드
  },
})
