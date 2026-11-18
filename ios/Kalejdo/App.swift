import UIKit
import WebKit
import Photos

// Kalejdo för iPhone: ett tunt skal runt samma index.html + props/ som Android-appen och webben.
// Sidan ligger i appens mapp "web" och serveras via ett eget URL-schema (com.gr8eam.kalejdo://app/index.html),
// så att fetch(), localStorage och WebCrypto fungerar som på en vanlig webbplats. Schemat innehåller paketnamnet
// med flit: servern (kalejdo.app/api/bas.php) känner igen appen på det i Origin-huvudet och svarar aldrig admin.

@main
final class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        application.isIdleTimerDisabled = true      // skärmen hålls tänd, som i Android-appen
        return true
    }

    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession,
                     options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        let c = UISceneConfiguration(name: "Default", sessionRole: connectingSceneSession.role)
        c.delegateClass = SceneDelegate.self
        return c
    }
}

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let ws = scene as? UIWindowScene else { return }
        let w = UIWindow(windowScene: ws)
        w.backgroundColor = WebViewController.background
        w.rootViewController = WebViewController()
        w.makeKeyAndVisible()
        window = w
    }
}

/// Serverar filerna i appens mapp "web" på com.gr8eam.kalejdo://app/…
final class WebAssets: NSObject, WKURLSchemeHandler {
    static let scheme = "com.gr8eam.kalejdo"
    static let start = URL(string: "com.gr8eam.kalejdo://app/index.html")!

    private let root = Bundle.main.bundleURL.appendingPathComponent("web", isDirectory: true).standardizedFileURL

    private static let mime: [String: String] = [
        "html": "text/html; charset=utf-8", "json": "application/json", "svg": "image/svg+xml",
        "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp",
        "js": "text/javascript; charset=utf-8", "css": "text/css; charset=utf-8", "txt": "text/plain; charset=utf-8",
    ]

    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        guard let url = task.request.url else {
            task.didFailWithError(URLError(.badURL)); return
        }
        var path = url.path
        if path.isEmpty || path == "/" { path = "/index.html" }
        let file = root.appendingPathComponent(String(path.dropFirst())).standardizedFileURL
        // aldrig utanför web-mappen
        guard file.path.hasPrefix(root.path + "/"), let data = try? Data(contentsOf: file) else {
            respond(task, url: url, status: 404, type: "text/plain; charset=utf-8", data: Data("Not found".utf8)); return
        }
        let type = WebAssets.mime[file.pathExtension.lowercased()] ?? "application/octet-stream"
        respond(task, url: url, status: 200, type: type, data: data)
    }

    func webView(_ webView: WKWebView, stop task: WKURLSchemeTask) {}

    private func respond(_ task: WKURLSchemeTask, url: URL, status: Int, type: String, data: Data) {
        let head = ["Content-Type": type, "Content-Length": String(data.count), "Cache-Control": "no-cache"]
        guard let r = HTTPURLResponse(url: url, statusCode: status, httpVersion: "HTTP/1.1", headerFields: head) else {
            task.didFailWithError(URLError(.unknown)); return
        }
        task.didReceive(r)
        task.didReceive(data)
        task.didFinish()
    }
}

final class WebViewController: UIViewController, WKNavigationDelegate, WKScriptMessageHandler, WKUIDelegate {
    static let background = UIColor(red: 0x15 / 255, green: 0x13 / 255, blue: 0x1C / 255, alpha: 1)

    private var web: WKWebView!
    private var fullscreen = false

    override var prefersStatusBarHidden: Bool { fullscreen }
    override var prefersHomeIndicatorAutoHidden: Bool { fullscreen }
    override var preferredStatusBarStyle: UIStatusBarStyle { .lightContent }
    override var supportedInterfaceOrientations: UIInterfaceOrientationMask { .portrait }

    private var version: String {
        let i = Bundle.main.infoDictionary
        let v = i?["CFBundleShortVersionString"] as? String ?? ""
        let b = i?["CFBundleVersion"] as? String ?? ""
        return "ios-\(v).\(b)"
    }

    /// window.KalejdoApp i sidan: samma namn som Android-skalets brygga, men bara det som finns på iPhone.
    /// Det som saknas (proBuy, proRestore, scanQr, setWallpaper) känner sidan av med native(namn).
    private var bridgeScript: String {
        """
        (function () {
          function post(name, args) {
            try { window.webkit.messageHandlers.kalejdo.postMessage({name: name, args: args || []}); } catch (e) {}
          }
          window.__kalejdoErrors = [];
          window.addEventListener("error", function (e) { window.__kalejdoErrors.push(String(e.message || e)); });
          window.addEventListener("unhandledrejection", function (e) { window.__kalejdoErrors.push("rejection: " + String(e.reason)); });
          window.KalejdoApp = {
            platform: "ios",
            appVersion: function () { return "\(version)"; },
            openUrl: function (u) { u = String(u); if (!/^https?:\\/\\//i.test(u)) return false; post("openUrl", [u]); return true; },
            share: function (text, title) { post("share", [String(text), String(title || "")]); },
            setFullscreen: function (on) { post("setFullscreen", [!!on]); },
            saveImage: function (b64, name) { post("saveImage", [String(b64), String(name || "kalejdo.png")]); return true; }
          };
        })();
        """
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = WebViewController.background

        let conf = WKWebViewConfiguration()
        conf.setURLSchemeHandler(WebAssets(), forURLScheme: WebAssets.scheme)
        conf.allowsInlineMediaPlayback = true
        conf.userContentController.addUserScript(
            WKUserScript(source: bridgeScript, injectionTime: .atDocumentStart, forMainFrameOnly: true))
        conf.userContentController.add(self, name: "kalejdo")

        web = WKWebView(frame: view.bounds, configuration: conf)
        web.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        web.isOpaque = false
        web.backgroundColor = WebViewController.background
        web.scrollView.backgroundColor = WebViewController.background
        web.scrollView.bounces = false
        web.scrollView.isScrollEnabled = false
        web.scrollView.showsVerticalScrollIndicator = false
        web.scrollView.showsHorizontalScrollIndicator = false
        // sidan sköter själv marginalerna mot klocka, kamerautskärning och hemstreck (env(safe-area-inset-*))
        web.scrollView.contentInsetAdjustmentBehavior = .never
        web.allowsLinkPreview = false
        web.allowsBackForwardNavigationGestures = false
        web.navigationDelegate = self
        web.uiDelegate = self
        #if DEBUG
        if #available(iOS 16.4, *) { web.isInspectable = true }
        #endif
        view.addSubview(web)
        web.load(URLRequest(url: WebAssets.start))
    }

    // MARK: navigering – bara appens egen sida får laddas i fönstret

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if navigationAction.targetFrame?.isMainFrame == false { decisionHandler(.allow); return }
        decisionHandler(navigationAction.request.url?.scheme == WebAssets.scheme ? .allow : .cancel)
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        webView.scrollView.pinchGestureRecognizer?.isEnabled = false
        diagnose()
    }

    // window.open / target=_blank öppnar inget nytt fönster i appen
    func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration,
                 for navigationAction: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? { nil }

    // alert() i sidan (confirm() används inte – sidan har egna rutor)
    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        let a = UIAlertController(title: nil, message: message, preferredStyle: .alert)
        a.addAction(UIAlertAction(title: "OK", style: .default) { _ in completionHandler() })
        present(a, animated: true)
    }

    // MARK: bryggan

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any], let name = body["name"] as? String else { return }
        let args = body["args"] as? [Any] ?? []
        switch name {
        case "openUrl":
            if let s = args.first as? String, let url = URL(string: s), url.scheme == "https" || url.scheme == "http" {
                UIApplication.shared.open(url)
            }
        case "share":
            guard let text = args.first as? String else { return }
            let item: Any = URL(string: text).flatMap { $0.scheme?.hasPrefix("http") == true ? $0 : nil } ?? text
            let sheet = UIActivityViewController(activityItems: [item], applicationActivities: nil)
            sheet.popoverPresentationController?.sourceView = view
            present(sheet, animated: true)
        case "setFullscreen":
            fullscreen = (args.first as? Bool) ?? false
            setNeedsStatusBarAppearanceUpdate()
            setNeedsUpdateOfHomeIndicatorAutoHidden()
        case "saveImage":
            guard let b64 = args.first as? String, let data = Data(base64Encoded: b64, options: .ignoreUnknownCharacters) else {
                tell("Could not save the picture"); return
            }
            savePhoto(data)
        default:
            break
        }
    }

    /// Lägger bilden (PNG, oförändrad) i telefonens bildbibliotek. Frågar bara om lov att lägga till, inte läsa.
    private func savePhoto(_ data: Data) {
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { [weak self] status in
            guard status == .authorized || status == .limited else {
                self?.tell("Allow Kalejdo to add photos in Settings to save pictures"); return
            }
            PHPhotoLibrary.shared().performChanges({
                PHAssetCreationRequest.forAsset().addResource(with: .photo, data: data, options: nil)
            }, completionHandler: { ok, _ in
                if !ok { self?.tell("Could not save the picture") }
            })
        }
    }

    /// Visar ett meddelande i sidans toast (window.kalejdoBilling är sidans allmänna meddelandekanal från skalet).
    private func tell(_ msg: String) {
        guard let d = try? JSONSerialization.data(withJSONObject: [msg]), let arr = String(data: d, encoding: .utf8) else { return }
        DispatchQueue.main.async {
            self.web.evaluateJavaScript("window.kalejdoBilling && window.kalejdoBilling(\(arr)[0])", completionHandler: nil)
        }
    }

    // MARK: självtest i simulatorn (GitHub Actions)

    /// Startas appen med miljövariabeln KALEJDO_DIAG skrivs en liten rapport om sidan till Documents/diag.json
    /// efter några sekunder. Bygget på GitHub läser filen och underkänner bygget om sidan inte kom igång.
    private func diagnose() {
        guard ProcessInfo.processInfo.environment["KALEJDO_DIAG"] != nil else { return }
        let js = """
        JSON.stringify({
          url: location.href, origin: location.origin, secure: window.isSecureContext,
          subtle: !!(window.crypto && crypto.subtle), caches: !!window.caches,
          storage: (function () { try { localStorage.setItem("kalejdo.diag", "1"); return localStorage.getItem("kalejdo.diag") === "1"; } catch (e) { return false; } })(),
          konto: (function () { try { return !!localStorage.getItem("kalejdo.konto.v1"); } catch (e) { return false; } })(),
          lib: (function () { try { return (localStorage.getItem("kalejdo.lib.v1") || "").length; } catch (e) { return -1; } })(),
          chips: document.querySelectorAll("#chips > *").length,
          canvas: (function () { var c = document.querySelector("#view"); return c ? c.width + "x" + c.height : ""; })(),
          version: KalejdoApp.appVersion(), errors: window.__kalejdoErrors
        })
        """
        DispatchQueue.main.asyncAfter(deadline: .now() + 15) {
            self.web.evaluateJavaScript(js) { result, error in
                let text = (result as? String) ?? "{\"evalError\": \"\(String(describing: error))\"}"
                if let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first {
                    try? text.write(to: dir.appendingPathComponent("diag.json"), atomically: true, encoding: .utf8)
                }
            }
        }
    }
}
