#!/usr/bin/env bash
set -euo pipefail
mkdir -p teste
echo '--- Estado do Android virtual ---'
adb devices -l
adb shell getprop ro.build.version.sdk
adb shell pm list packages | grep -Ei 'tts|speech|googlequicksearch' || true
adb install -r apk/app-debug.apk
adb shell pm list packages | grep -q 'package:br.com.helper.curiosidadesreels.nova'
echo 'Instalacao independente: pacote NOVO confirmado'
echo '--- Iniciando geração local de Reel ---'
adb logcat -c || true
adb shell am start -W -n br.com.helper.curiosidadesreels.nova/br.com.helper.reels.MainActivity -a br.com.helper.reels.TEST_GENERATION
ready=0
for i in $(seq 1 180); do
  sleep 5
  if adb logcat -d -s HelperReels:E 2>/dev/null | grep -q 'Generation failure'; then
    echo 'FALHA DO APLICATIVO:'
    adb logcat -d -s HelperReels:E AndroidRuntime:E | tail -150
    exit 1
  fi
  if adb shell content query --uri content://media/external/video/media --projection _id:_display_name:is_pending 2>/dev/null | grep -Eq 'is_pending=0|IS_PENDING=0'; then
    ready=1
    break
  fi
  if (( i % 12 == 0 )); then
    echo "Aguardando MP4... etapa $i"
    adb shell ls -l /sdcard/Movies/HelperReels/ || true
    adb logcat -d -s HelperReels:E AndroidRuntime:E | tail -40 || true
  fi
done
if (( ready == 0 )); then
  echo 'ERRO: não houve publicação de MP4 no MediaStore.'
  adb shell content query --uri content://media/external/video/media || true
  adb logcat -d -s HelperReels:E AndroidRuntime:E | tail -120 || true
  exit 1
fi
video=$(adb shell find /sdcard/Movies/HelperReels/ -type f -name '*.mp4' 2>/dev/null | tr -d '\r' | head -1)
if [ -z "$video" ]; then echo 'ERRO: MP4 não encontrado no armazenamento local'; exit 1; fi
adb pull "$video" teste/reel-gerado-no-android.mp4
echo '--- Metadados do MP4 ---'
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 teste/reel-gerado-no-android.mp4
ffprobe -v error -show_entries stream=codec_name,codec_type,width,height -of default=noprint_wrappers=1 teste/reel-gerado-no-android.mp4
ffprobe -v error -select_streams v -show_entries stream=codec_name -of csv=p=0 teste/reel-gerado-no-android.mp4 | grep -q h264
ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 teste/reel-gerado-no-android.mp4 | grep -q aac
test "$(stat -c%s teste/reel-gerado-no-android.mp4)" -gt 100000
echo 'TESTE REAL OK: novo MP4 H.264 + AAC gerado e exportado pelo app Android.'
