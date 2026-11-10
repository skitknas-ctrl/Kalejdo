import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// Kalejdoskopet ligger i index.html, props/ och store/ i repots rot (så att GitHub Pages kan köra det direkt).
// Här kopieras de in som app-assets vid varje bygge.
val webAssets = layout.buildDirectory.dir("webassets")
val copyWeb by tasks.registering(Copy::class) {
    from(rootProject.file("index.html"))
    from(rootProject.file("props")) { into("props") }
    from(rootProject.file("store")) { into("store") }
    into(webAssets)
}

android {
    namespace = "io.github.skitknasctrl.kalejdo"
    compileSdk = 35

    defaultConfig {
        applicationId = "io.github.skitknasctrl.kalejdo"
        minSdk = 29 // Android 10: bilder kan sparas i Bilder/ utan behörighetsfråga
        targetSdk = 35
        // CI skickar -PbuildNumber=<körningsnummer>; testbyggen får då versionen 0.1.0-test.<n>
        val baseVersion = "0.1.0"
        val buildNumber = (project.findProperty("buildNumber") as String?)?.toIntOrNull()
        versionCode = buildNumber ?: 1
        versionName = if (buildNumber != null) "$baseVersion-test.$buildNumber" else "$baseVersion-dev"
    }

    signingConfigs {
        // Testnyckel så att varje CI-bygge kan uppdatera det föregående på plats.
        // Riktiga utgåvor signeras med nyckel från GitHub secrets (se build.yml).
        getByName("debug") {
            storeFile = file("debug.keystore")
            storePassword = "android"
            keyAlias = "androiddebugkey"
            keyPassword = "android"
        }
        create("release") {
            val ksPath = System.getenv("RELEASE_KEYSTORE")
            if (ksPath != null && file(ksPath).exists()) {
                storeFile = file(ksPath)
                storePassword = System.getenv("RELEASE_KEYSTORE_PASSWORD")
                keyAlias = System.getenv("RELEASE_KEY_ALIAS")
                keyPassword = System.getenv("RELEASE_KEY_PASSWORD")
            }
        }
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".debug" // testappen kan ligga bredvid den riktiga utgåvan
            signingConfig = signingConfigs.getByName("debug")
        }
        release {
            isMinifyEnabled = false
            val rel = signingConfigs.getByName("release")
            signingConfig = if (rel.storeFile != null) rel else null
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    sourceSets {
        getByName("main").kotlin.srcDirs("src/main/kotlin")
        getByName("main").assets.srcDirs(webAssets)
    }
    lint {
        abortOnError = false
    }
    dependenciesInfo {
        // F-Droid: inget Google-signerat beroendeblock i APK:n
        includeInApk = false
        includeInBundle = false
    }
}

tasks.named("preBuild") { dependsOn(copyWeb) }

kotlin {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_17)
    }
}

dependencies {
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.webkit:webkit:1.11.0")
}
