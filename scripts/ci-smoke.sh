#!/usr/bin/env bash
set -euo pipefail
adb install apk/app-debug.apk
adb shell pm list packages | grep -i 'tts\|speech' || true
adb shell am start -n br.com.helper.curiosidadesreels/br.com.helper.reels.MainActivity -a br.com.helper.reels.TEST_GENERATION
mkdir -p teste
ready=0
for i in $(seq 1 120); do
  sleep 6
  if adb shell content query --uri content://media/external/video/media --projection _id:_display_name:is_pending 2>/dev/null | grep -q 'is_pending=0'; then
    ready=1
    break
  fi
  if adb logcat -d -s HelperReels:E 2>/dev/null | grep -q 'Generation failure'; then
    echo 'ERRO do aplicativo detectado durante a geração:'
    adb logcat -d -s HelperReels:E | tail -110
    exit 1
  fi
  if [ "$((i%10))" = "0" ]; then
    echo "Teste ainda ativo, passo $i."
    adb logcat -d -s HelperReels:E AndroidRuntime:E | tail -15 || true
  fi
done
if [ "$ready" = "0" ]; then
  echo 'ERRO: aplicativo nao terminou um MP4 dentro do prazo.'
  adb logcat -d -s HelperReels:E AndroidRuntime:E | tail -130
  exit 1
fi
video=$(adb shell find /sdcard/Movies/HelperReels -type f -name '*.mp4' | tr -d '\r' | head -1)
if [ -z "$video" ]; then echo 'MP4 nao encontrado'; exit 1; fi
adb pull "$video" teste/reel-gerado-no-android.mp4
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 teste/reel-gerado-no-android.mp4
ffprobe -v error -show_entries stream=codec_name,codec_type,width,height -of default=noprint_wrappers=1 teste/reel-gerado-no-android.mp4
ffprobe -v error -select_streams v -show_entries stream=codec_name -of csv=p=0 teste/reel-gerado-no-android.mp4 | grep -q h264
ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 teste/reel-gerado-no-android.mp4 | grep -q aac
test "$(stat -c%s teste/reel-gerado-no-android.mp4)" -gt 100000
echo 'TESTE REAL OK - MP4 H264 + AAC foi criado pelo aplicativo Android.'
