package io.github.skitknasctrl.kalejdo

import android.annotation.SuppressLint
import android.app.Presentation
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.service.wallpaper.WallpaperService
import android.view.SurfaceHolder
import android.view.View
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.webkit.WebViewAssetLoader

/**
 * Levande bakgrund (2026-11-12): kalejdoskopet som bakgrundsbild på hemskärmen.
 *
 * En bakgrundstjänst har bara en yta (Surface) att rita på och inget fönster, medan sidan behöver en riktig WebView
 * med grafikacceleration. Därför skapas en virtuell skärm som ritar direkt på bakgrundens yta, och på den visas en
 * Presentation (ett fönster utan aktivitet) med en WebView. WebView:n laddar samma index.html som appen med
 * ?wallpaper=1: då visas bara mönstret i helskärm och kalejdoskopet hämtas ur localStorage (nyckeln
 * kalejdo.wallpaper.v1, som appen skriver när användaren väljer "Use as live wallpaper"). Tjänsten körs i appens
 * process, så localStorage är gemensamt med appen.
 *
 * När bakgrunden inte syns (annan app i förgrunden, skärmen släckt) pausas WebView:n så att den inte drar batteri.
 */
class KalejdoWallpaper : WallpaperService() {

    override fun onCreateEngine(): Engine = KalejdoEngine()

    inner class KalejdoEngine : Engine() {
        private var display: VirtualDisplay? = null
        private var presentation: Presentation? = null
        private var web: WebView? = null

        override fun onCreate(surfaceHolder: SurfaceHolder) {
            super.onCreate(surfaceHolder)
            setTouchEventsEnabled(false)
        }

        @SuppressLint("SetJavaScriptEnabled")
        override fun onSurfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
            super.onSurfaceChanged(holder, format, width, height)
            release()
            try {
                val dm = getSystemService(DISPLAY_SERVICE) as DisplayManager
                val vd = dm.createVirtualDisplay(
                    "kalejdo-wallpaper", width, height, resources.displayMetrics.densityDpi,
                    holder.surface, DisplayManager.VIRTUAL_DISPLAY_FLAG_OWN_CONTENT_ONLY
                ) ?: return
                display = vd
                val p = Presentation(this@KalejdoWallpaper, vd.display)
                p.window?.setBackgroundDrawable(ColorDrawable(Color.BLACK))
                val loader = WebViewAssetLoader.Builder()
                    .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this@KalejdoWallpaper))
                    .build()
                val w = WebView(p.context)
                w.settings.apply {
                    javaScriptEnabled = true
                    domStorageEnabled = true
                    allowFileAccess = false
                    allowContentAccess = false
                    textZoom = 100
                }
                w.webViewClient = object : WebViewClient() {
                    override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? =
                        loader.shouldInterceptRequest(request.url)

                    override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean = true
                }
                w.setBackgroundColor(Color.BLACK)
                w.overScrollMode = View.OVER_SCROLL_NEVER
                w.isVerticalScrollBarEnabled = false
                w.isHorizontalScrollBarEnabled = false
                p.setContentView(w)
                p.show()
                presentation = p
                web = w
                w.loadUrl("https://appassets.androidplatform.net/assets/index.html?wallpaper=1")
                if (!isVisible) w.onPause()
            } catch (_: Exception) {
                release()
            }
        }

        override fun onVisibilityChanged(visible: Boolean) {
            val w = web ?: return
            if (visible) {
                w.onResume()
                // har användaren valt ett nytt kalejdoskop som bakgrund sedan sist? Då byter sidan till det
                w.evaluateJavascript("window.kalejdoWallpaperCheck && window.kalejdoWallpaperCheck()", null)
            } else {
                w.onPause()
            }
        }

        override fun onSurfaceDestroyed(holder: SurfaceHolder) {
            release()
            super.onSurfaceDestroyed(holder)
        }

        override fun onDestroy() {
            release()
            super.onDestroy()
        }

        private fun release() {
            try { presentation?.dismiss() } catch (_: Exception) {}
            presentation = null
            try { web?.destroy() } catch (_: Exception) {}
            web = null
            try { display?.release() } catch (_: Exception) {}
            display = null
        }
    }
}
