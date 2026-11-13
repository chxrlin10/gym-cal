import {readFile,writeFile,mkdir,readdir,rm} from 'node:fs/promises';
const manifest='android/app/src/main/AndroidManifest.xml';let m=await readFile(manifest,'utf8');
if(!m.includes('android.permission.CAMERA'))m=m.replace('<application','<uses-permission android:name="android.permission.CAMERA" />\n    <uses-feature android:name="android.hardware.camera" android:required="false" />\n    <application');
m=m.replace(/android:allowBackup="[^"]*"/,'android:allowBackup="false"');
if(!m.includes('android:allowBackup='))m=m.replace('<application','<application android:allowBackup="false"');
m=m.replace(/ android:dataExtractionRules="[^"]*"/g,'').replace(/ android:fullBackupContent="[^"]*"/g,'');
m=m.replace(/android:launchMode="singleTask"/,'android:launchMode="singleTop"');
m=m.replace('<application','<application android:dataExtractionRules="@xml/data_extraction_rules" android:fullBackupContent="false"');
await writeFile(manifest,m);
await writeFile('android/app/src/main/res/xml/data_extraction_rules.xml','<data-extraction-rules><cloud-backup><exclude domain="root" path="."/></cloud-backup><device-transfer><exclude domain="root" path="."/></device-transfer></data-extraction-rules>');
let v=await readFile('android/variables.gradle','utf8');v=v.replace(/targetSdkVersion\s*=\s*\d+/,'targetSdkVersion = 36').replace(/compileSdkVersion\s*=\s*\d+/,'compileSdkVersion = 36');await writeFile('android/variables.gradle',v);
const code=process.env.ANDROID_VERSION_CODE||'2';if(!/^\d+$/.test(code))throw Error('Invalid version code');
let g=await readFile('android/app/build.gradle','utf8');g=g.replace(/versionCode \d+/,`versionCode ${code}`).replace(/versionName "[^"]+"/,'versionName "1.0.4"');
g=g.replace(/\n\/\/ GYMCAL_SIGNING_START[\s\S]*?\/\/ GYMCAL_SIGNING_END\n/g,'');
if(process.env.ANDROID_KEYSTORE_PATH){g+=`\n// GYMCAL_SIGNING_START\nandroid {\n signingConfigs { release {\n storeFile file(System.getenv('ANDROID_KEYSTORE_PATH'))\n storePassword System.getenv('ANDROID_KEYSTORE_PASSWORD')\n keyAlias System.getenv('ANDROID_KEY_ALIAS')\n keyPassword System.getenv('ANDROID_KEY_PASSWORD')\n } }\n buildTypes { release { signingConfig signingConfigs.release } }\n}\n// GYMCAL_SIGNING_END\n`;}
await writeFile('android/app/build.gradle',g);

// Native vectors reproduce the existing ring favicon without an external image toolchain.
const res='android/app/src/main/res';
for(const dir of await readdir(res)){if(dir.startsWith('mipmap')||dir.startsWith('drawable'))for(const f of await readdir(res+'/'+dir))if(f.startsWith('ic_launcher')||f==='splash.png')await rm(res+'/'+dir+'/'+f);}
for(const dir of ['mipmap-anydpi','mipmap-anydpi-v26','drawable','values-night'])await mkdir(res+'/'+dir,{recursive:true});
const ring='<path android:fillColor="#00000000" android:strokeColor="#4DFFFFFF" android:strokeWidth="3.5" android:pathData="M16,6 A10,10 0,1 1,16,26 A10,10 0,1 1,16,6"/><path android:fillColor="#00000000" android:strokeColor="#D9F88B" android:strokeWidth="3.5" android:strokeLineCap="round" android:pathData="M16,6 A10,10 0,0 1,26,16"/>';
const vector=(background=false)=>'<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="32" android:viewportHeight="32">'+(background?'<path android:fillColor="#245844" android:pathData="M0,0 H32 V32 H0 Z"/>':'')+ring+'</vector>';
await writeFile(res+'/drawable/gymcal_icon_foreground.xml',vector());
await writeFile(res+'/values/gymcal_colors.xml','<resources><color name="gymcal_icon_background">#245844</color></resources>');
for(const name of ['ic_launcher','ic_launcher_round']){
 await writeFile(res+'/mipmap-anydpi/'+name+'.xml',vector(true));
 await writeFile(res+'/mipmap-anydpi-v26/'+name+'.xml','<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android"><background android:drawable="@color/gymcal_icon_background"/><foreground android:drawable="@drawable/gymcal_icon_foreground"/></adaptive-icon>');
}
await writeFile(res+'/drawable/splash.xml','<layer-list xmlns:android="http://schemas.android.com/apk/res/android"><item android:drawable="@color/gymcal_icon_background"/></layer-list>');
let styles=await readFile(res+'/values/styles.xml','utf8');styles=styles.replace('<item name="android:background">@drawable/splash</item>','<item name="windowSplashScreenBackground">@color/gymcal_icon_background</item><item name="windowSplashScreenAnimatedIcon">@drawable/gymcal_icon_foreground</item><item name="postSplashScreenTheme">@style/AppTheme.NoActionBar</item>');await writeFile(res+'/values/styles.xml',styles);
