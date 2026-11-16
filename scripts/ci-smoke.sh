#!/usr/bin/env bash
set -euo pipefail
mkdir -p teste
echo '--- Estado do Android virtual ---'
adb devices -l
adb shell getprop ro.build.version.sdk
adb shell pm list packages | grep -Ei 'tts|speech|googlequicksearch' || true
adb install -r apk-anterior/app-debug.apk
old_pkg=$(adb shell pm list packages -3 | tr -d '\r' | sed -n 's/^package://p' | head -1)
test -n "$old_pkg" || { echo 'ERRO: pacote antigo nao encontrado'; exit 1; }
echo "Pacote anterior: $old_pkg"
adb install -r apk/app-debug.apk
new_pkg="br.com.helper.curiosidadesreels.nova"
test "$old_pkg" != "$new_pkg" || { echo 'ERRO: pacotes iguais'; exit 1; }
adb shell pm list packages | tr -d '\r' | grep -Fx "package:$old_pkg"
adb shell pm list packages | tr -d '\r' | grep -Fx "package:$new_pkg"
echo "VERSOES CONVIVENDO: $old_pkg e $new_pkg"
echo '--- Consultando fonte externa no Android virtual: Buraco negro ---'
adb logcat -c || true
adb shell am start -W -n br.com.helper.curiosidadesreels.nova/br.com.helper.reels.MainActivity -a br.com.helper.reels.TEST_DYNAMIC_LOOKUP
lookup=0
for i in $(seq 1 18); do
  sleep 3
  if adb logcat -d -s HelperDynamicTest:I 2>/dev/null | grep -q 'PASS:'; then lookup=1; break; fi
  if adb logcat -d -s HelperDynamicTest:E 2>/dev/null | grep -q 'FAIL:'; then break; fi
done
adb logcat -d -s HelperDynamicTest:I HelperDynamicTest:E | tail -12 || true
if (( lookup == 0 )); then
  echo 'FALHA: consulta externa dinâmica não validada no Android'
  exit 1
fi
echo '--- Gerando MP4 de teste de codec, sem alegar narração TTS ---'
# Emuladores podem iniciar o serviço TTS antes do pacote de vozes estar pronto.
adb shell am broadcast -a android.intent.action.LOCALE_CHANGED >/dev/null 2>&1 || true
sleep 12
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
echo '--- Decodificação integral de áudio e vídeo ---'
# ffprobe only checks headers; decoding catches corrupted frames and AAC packets.
ffmpeg -hide_banner -loglevel error -xerror -i teste/reel-gerado-no-android.mp4 -map 0:v:0 -f null - </dev/null
ffmpeg -hide_banner -loglevel error -xerror -i teste/reel-gerado-no-android.mp4 -map 0:a:0 -f null - </dev/null
python3 - <<'PY'
import json, subprocess
p='teste/reel-gerado-no-android.mp4'
data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',p]))
streams=data['streams']
video=next(s for s in streams if s['codec_type']=='video')
audio=next(s for s in streams if s['codec_type']=='audio')
duration=float(data['format']['duration'])
assert 1 <= duration <= 120, f'Invalid video duration: {duration}'
assert video['width'] > 0 and video['height'] > 0, 'Missing video dimensions'
assert video['height'] > video['width'], 'Reels video must be portrait'
assert video['codec_name']=='h264' and audio['codec_name']=='aac'
for stream in (video,audio):
    if 'duration' in stream:
        assert float(stream['duration']) >= duration - 1.0, 'Stream truncated before end'
print(f'FULL DECODE PASS: {duration:.2f}s, {video["width"]}x{video["height"]}, H264/AAC')
PY
echo 'TESTE DE CODEC OK: MP4 H.264 + AAC com áudio sintético; narração TTS e conteúdo editorial não validados.'

echo '--- Teste obrigatório de narração TTS REAL pt-BR ---'
# Remove vídeos anteriores para impedir falso positivo por arquivo de codec antigo.
adb shell 'rm -f /sdcard/Movies/HelperReels/*.mp4' || true
# A opção extra usa NarrationEngine.synthesize, sem áudio sintético.
adb shell am force-stop br.com.helper.curiosidadesreels.nova
adb logcat -c || true
# Force-stop guarantees onCreate receives the new intent extra, rather than
# reusing an existing Activity whose getIntent() still selects synthetic audio.
adb shell am start -W -n br.com.helper.curiosidadesreels.nova/br.com.helper.reels.MainActivity -a br.com.helper.reels.TEST_GENERATION --ez helper_real_tts true
tts_ready=0
for i in $(seq 1 60); do
  sleep 5
  if adb logcat -d -s HelperReels:E AndroidRuntime:E 2>/dev/null | grep -Eq 'Generation failure|FATAL EXCEPTION'; then
    adb logcat -d -s HelperReels:E AndroidRuntime:E | tail -100
    echo 'FALHA: narração TTS real falhou'
    exit 1
  fi
  if adb logcat -d -s HelperReels:I 2>/dev/null | grep -q 'MP4GERADO com sucesso'; then
    tts_ready=1
    break
  fi
done
if (( tts_ready == 0 )); then
  echo 'FALHA: MP4 com TTS real não foi publicado no prazo'
  adb logcat -d -s HelperReels:I HelperReels:E AndroidRuntime:E | tail -100 || true
  exit 1
fi
tts_video=$(adb shell find /sdcard/Movies/HelperReels -type f -name '*.mp4' 2>/dev/null | tr -d '\r' | head -1)
test -n "$tts_video" || { echo 'FALHA: arquivo TTS ausente'; exit 1; }
test "$(adb shell find /sdcard/Movies/HelperReels -type f -name '*.mp4' 2>/dev/null | wc -l)" -eq 1 || { echo 'FALHA: múltiplos MP4 no teste TTS'; exit 1; }
adb pull "$tts_video" teste/reel-tts-real-ptbr.mp4
ffmpeg -hide_banner -loglevel error -xerror -i teste/reel-tts-real-ptbr.mp4 -map 0:a:0 -f null - </dev/null
python3 - <<'PYTTS'
import json,subprocess,math
p='teste/reel-tts-real-ptbr.mp4'
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',p]))
assert any(x['codec_type']=='video' and x['codec_name']=='h264' for x in d['streams'])
assert any(x['codec_type']=='audio' and x['codec_name']=='aac' for x in d['streams'])
raw=subprocess.check_output(['ffmpeg','-v','error','-i',p,'-vn','-ac','1','-ar','16000','-f','s16le','-'])
import array
pcm=array.array('h');pcm.frombytes(raw)
assert len(pcm)>=16000,'TTS audio too short'
rms=math.sqrt(sum(x*x for x in pcm)/len(pcm))
assert rms>100, f'TTS track effectively silent: RMS={rms:.1f}'
# A short beep or one noisy packet must not pass as sustained narration.
window=16000//2
levels=[math.sqrt(sum(x*x for x in pcm[i:i+window])/len(pcm[i:i+window]))
        for i in range(0,len(pcm)-window+1,window)]
active=sum(level>100 for level in levels)
assert active>=3, f'TTS lacks sustained audible segments: {active} active half-second windows'
duration=float(d['format']['duration'])
assert duration>=3, f'TTS video too short: {duration:.2f}s'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-xerror','-i',p,
                '-map','0:v:0','-f','null','-'],check=True,stdin=subprocess.DEVNULL)
print(f'TTS AUDIO/VIDEO CHECK PASS: {len(pcm)/16000:.2f}s, RMS={rms:.1f}, active_windows={active}')
PYTTS
echo 'TTS REAL pt-BR: arquivo MP4 com áudio não silencioso aprovado (inteligibilidade ainda requer escuta humana).'
