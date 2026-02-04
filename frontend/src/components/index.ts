import { type App } from "vue"
import Chat from "@/components/chat/index.vue"









export default {
  install(app: App) {
    app.component('Chat', Chat)
    }
}