package io.github.skitknasctrl.kalejdo

import android.annotation.SuppressLint
import android.content.ContentValues
import android.content.Intent
import android.net.Uri
import android.graphics.Color
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.util.Base64
import android.view.View
import android.view.WindowManager
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.core.view.WindowInsetsCompat
import androidx.webkit.WebViewAssetLoader
import android.app.WallpaperManager
import android.content.ComponentName
import com.android.billingclient.api.AcknowledgePurchaseParams
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.BillingClientStateListener
import com.android.billingclient.api.BillingFlowParams
import com.android.billingclient.api.BillingResult
import com.android.billingclient.api.PendingPurchasesParams
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.Purchase
import com.android.billingclient.api.QueryProductDetailsParams
import com.android.billingclient.api.QueryPurchasesParams
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.codescanner.GmsBarcodeScannerOptions
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning
import org.json.JSONObject

/**
 * Tunt skal runt kalejdoskopet: en WebView som visar index.html och props/ från appens assets.
 * Sidan serveras via WebViewAssetLoader (https://appassets.androidplatform.net/…)
 * så att fetch() av SVG-filerna och localStorage fungerar som på en vanlig webbplats.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var web: WebView

    // Pro (2026-11-12): en månadsprenumeration i Google Play med produkt-id "pro" (första månaden gratis för nya
    // prenumeranter, som ett erbjudande på basplanen i Play Console). Skalet sköter bara köpflödet och skickar
    // köpkvittot (purchaseToken) till sidan, som låter servern kontrollera det mot Google Play och låsa upp Pro.
    private val proProduct = "pro"
    private var billing: BillingClient? = null
    private var proDetails: ProductDetails? = null
    private var proOfferToken: String? = null
    private var pageReady = false

    /** Anropar window.<fn>(arg) i sidan. */
    private fun js(fn: String, arg: String) {
        runOnUiThread { web.evaluateJavascript("window.$fn && window.$fn(${JSONObject.quote(arg)})", null) }
    }

    private fun startBilling() {
        val client = BillingClient.newBuilder(this)
            .setListener { result, purchases ->
                when (result.responseCode) {
                    BillingClient.BillingResponseCode.OK -> handlePurchases(purchases ?: emptyList(), true)
                    BillingClient.BillingResponseCode.USER_CANCELED -> {}
                    BillingClient.BillingResponseCode.ITEM_ALREADY_OWNED -> checkOwned(true)
                    else -> js("kalejdoBilling", "The purchase did not go through")
                }
            }
            .enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
            .enableAutoServiceReconnection()
            .build()
        billing = client
        client.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(result: BillingResult) {
                if (result.responseCode == BillingClient.BillingResponseCode.OK && pageReady) { queryPro(); checkOwned(false) }
            }
            override fun onBillingServiceDisconnected() {}
        })
    }

    /** Hämtar produkten (pris m.m.) och skickar priset till sidan. */
    private fun queryPro() {
        val params = QueryProductDetailsParams.newBuilder().setProductList(listOf(
            QueryProductDetailsParams.Product.newBuilder().setProductId(proProduct).setProductType(BillingClient.ProductType.SUBS).build()
        )).build()
        billing?.queryProductDetailsAsync(params) { result, details ->
            if (result.responseCode != BillingClient.BillingResponseCode.OK) return@queryProductDetailsAsync
            val d = details.productDetailsList.firstOrNull { it.productId == proProduct } ?: return@queryProductDetailsAsync
            val offers = d.subscriptionOfferDetails ?: return@queryProductDetailsAsync
            // Google Play listar bara de erbjudanden kontot har rätt till. Finns ett med en gratis första period
            // (provmånaden) väljs det, annars basplanen.
            val trial = offers.firstOrNull { o -> o.pricingPhases.pricingPhaseList.any { it.priceAmountMicros == 0L } }
            val offer = trial ?: offers.firstOrNull() ?: return@queryProductDetailsAsync
            proDetails = d
            proOfferToken = offer.offerToken
            val price = offer.pricingPhases.pricingPhaseList.lastOrNull()?.formattedPrice ?: ""
            js("kalejdoPrice", JSONObject().put("price", price).put("trial", trial != null).toString())
        }
    }

    /** Finns en aktiv Pro-prenumeration på det här Google-kontot (ny telefon, ominstallation)? Då skickas kvittot till sidan. */
    private fun checkOwned(tell: Boolean) {
        val params = QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.SUBS).build()
        billing?.queryPurchasesAsync(params) { result, purchases ->
            if (result.responseCode != BillingClient.BillingResponseCode.OK) {
                if (tell) js("kalejdoBilling", "Google Play can't be reached right now")
                return@queryPurchasesAsync
            }
            val found = handlePurchases(purchases, false)
            if (tell && !found) js("kalejdoBilling", "No active Kalejdo + subscription was found on this Google account")
        }
    }

    private fun handlePurchases(purchases: List<Purchase>, tell: Boolean): Boolean {
        var found = false
        for (p in purchases) {
            if (!p.products.contains(proProduct)) continue
            if (p.purchaseState == Purchase.PurchaseState.PURCHASED) {
                found = true
                if (!p.isAcknowledged) {
                    billing?.acknowledgePurchase(AcknowledgePurchaseParams.newBuilder().setPurchaseToken(p.purchaseToken).build()) { }
                }
                js("kalejdoPurchase", p.purchaseToken)
            } else if (p.purchaseState == Purchase.PurchaseState.PENDING) {
                found = true
                if (tell) js("kalejdoBilling", "The payment is pending. Kalejdo + unlocks when it has gone through.")
            }
        }
        return found
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        web = WebView(this)
        web.setBackgroundColor(Color.parseColor("#15131C"))
        setContentView(web)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        hideSystemBars()
        startBilling()

        // Android 15 ritar appar kant till kant: håll innehållet innanför statusfältet,
        // utskärningen och navigeringsfältet. Systemfälten är dolda i hela appen (hideSystemBars), så de ger
        // 0 här; kvar blir kamerautskärningen, som fortfarande ger marginal så att inget hamnar under den.
        ViewCompat.setOnApplyWindowInsetsListener(web) { v, insets ->
            val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout())
            v.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            insets
        }

        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = false
            allowContentAccess = false
            setSupportZoom(false)
            builtInZoomControls = false
            displayZoomControls = false
            textZoom = 100
        }
        web.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? =
                loader.shouldInterceptRequest(request.url)

            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean = true // inga externa länkar
        }
        web.overScrollMode = View.OVER_SCROLL_NEVER
        web.isVerticalScrollBarEnabled = false
        web.isHorizontalScrollBarEnabled = false

        web.addJavascriptInterface(AppBridge(), "KalejdoApp")
        web.loadUrl("https://appassets.androidplatform.net/assets/index.html")
    }

    /** Det sidan får anropa från JavaScript: spara en bild i Bilder/Kalejdo, öppna en länk i webbläsaren,
     *  dölja/visa operativets fält (statusfält och navigeringsknappar) i helskärmsläget, köpa/återställa Pro
     *  och skanna webbsidans QR-kod. */
    inner class AppBridge {
        /** Sidan är laddad: hämta priset och kolla om Pro redan är köpt. Svar via window.kalejdoPrice/kalejdoPurchase. */
        @JavascriptInterface
        fun proInit() {
            pageReady = true
            runOnUiThread { queryPro(); checkOwned(false) }
        }

        @JavascriptInterface
        fun proBuy() {
            runOnUiThread {
                val d = proDetails
                val client = billing
                val offer = proOfferToken
                if (d == null || client == null || offer == null) {
                    queryPro()
                    js("kalejdoBilling", "Google Play can't be reached right now. Try again in a moment.")
                    return@runOnUiThread
                }
                val pd = BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(d).setOfferToken(offer)
                client.launchBillingFlow(this@MainActivity, BillingFlowParams.newBuilder().setProductDetailsParamsList(listOf(pd.build())).build())
            }
        }

        @JavascriptInterface
        fun proRestore() {
            runOnUiThread { checkOwned(true) }
        }

        /** Öppnar Googles kodläsare (ingen kamerabehörighet behövs) och skickar texten i QR-koden till window.kalejdoQr. */
        @JavascriptInterface
        fun scanQr() {
            runOnUiThread {
                try {
                    val opts = GmsBarcodeScannerOptions.Builder().setBarcodeFormats(Barcode.FORMAT_QR_CODE).build()
                    GmsBarcodeScanning.getClient(this@MainActivity, opts).startScan()
                        .addOnSuccessListener { code -> js("kalejdoQr", code.rawValue ?: "") }
                        .addOnFailureListener { js("kalejdoBilling", "The scanner could not be opened. Try again in a moment.") }
                } catch (_: Exception) {
                    js("kalejdoBilling", "The scanner could not be opened")
                }
            }
        }

        /** Sidans helskärmsläge. Sedan 2026-11-13 är systemfälten dolda i hela appen, så de visas inte igen när
         *  helskärmsläget lämnas; anropet ser bara till att de är dolda. */
        @JavascriptInterface
        fun setFullscreen(on: Boolean) {
            runOnUiThread { hideSystemBars() }
        }

        /** Androids delningsruta med en länk till ett delat kalejdoskop. */
        @JavascriptInterface
        fun share(text: String, title: String) {
            runOnUiThread {
                try {
                    val send = Intent(Intent.ACTION_SEND).setType("text/plain")
                        .putExtra(Intent.EXTRA_TEXT, text).putExtra(Intent.EXTRA_SUBJECT, title)
                    startActivity(Intent.createChooser(send, null))
                } catch (_: Exception) {
                }
            }
        }

        /** Öppnar Androids förhandsvisning av Kalejdo som levande bakgrund (KalejdoWallpaper). */
        @JavascriptInterface
        fun setWallpaper() {
            runOnUiThread {
                try {
                    startActivity(Intent(WallpaperManager.ACTION_CHANGE_LIVE_WALLPAPER)
                        .putExtra(WallpaperManager.EXTRA_LIVE_WALLPAPER_COMPONENT, ComponentName(this@MainActivity, KalejdoWallpaper::class.java)))
                } catch (_: Exception) {
                    js("kalejdoBilling", "Live wallpapers are not available on this phone")
                }
            }
        }

        @JavascriptInterface
        fun openUrl(url: String): Boolean {
            val uri = Uri.parse(url)
            if (uri.scheme != "https" && uri.scheme != "http") return false
            runOnUiThread {
                try {
                    startActivity(Intent(Intent.ACTION_VIEW, uri).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
                } catch (_: Exception) {
                }
            }
            return true
        }

        @JavascriptInterface
        fun saveImage(base64Png: String, fileName: String): Boolean = try {
            val bytes = Base64.decode(base64Png, Base64.DEFAULT)
            val values = ContentValues().apply {
                put(MediaStore.Images.Media.DISPLAY_NAME, fileName)
                put(MediaStore.Images.Media.MIME_TYPE, "image/png")
                put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/Kalejdo")
                put(MediaStore.Images.Media.IS_PENDING, 1)
            }
            val uri = contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
                ?: error("insert failed")
            contentResolver.openOutputStream(uri).use { out -> out!!.write(bytes) }
            values.clear()
            values.put(MediaStore.Images.Media.IS_PENDING, 0)
            contentResolver.update(uri, values, null, null)
            true
        } catch (e: Exception) {
            false
        }
    }

    /** Statusfält och navigeringsfält är dolda i hela appen (2026-11-13); ett svep från kanten visar dem tillfälligt. */
    private fun hideSystemBars() {
        val c = WindowCompat.getInsetsController(window, window.decorView)
        c.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        c.hide(WindowInsetsCompat.Type.systemBars())
    }

    // fälten kan komma tillbaka när appen tappat fokus (dialoger, köpflödet, andra appar): dölj dem igen
    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) hideSystemBars()
    }

    override fun onPause() { super.onPause(); web.onPause() }
    override fun onResume() { super.onResume(); web.onResume() }
    override fun onDestroy() { billing?.endConnection(); web.destroy(); super.onDestroy() }
}
