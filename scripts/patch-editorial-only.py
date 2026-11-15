#!/usr/bin/env python3
"""Replace legacy trend/free-topic UI with the approved four-pillar editorial flow.
Run after patch-dynamic-topics.py and before compiling Android.
"""
from pathlib import Path
p=Path("app/src/main/java/br/com/helper/reels/MainActivity.java")
s=p.read_text(encoding="utf-8")
# No RSS trend feed or arbitrary prompt is permitted to select a video in this edition.
# Existing offline FactCatalog contains mixed subjects and is not an approved editorial queue.
# Fail closed until a sourced, reviewed story is integrated into the Android renderer.
s=s.replace('        if("br.com.helper.reels.TEST_DYNAMIC_VIDEO".equals(getIntent().getAction())){','        if("br.com.helper.reels.TEST_DYNAMIC_VIDEO_LEGACY".equals(getIntent().getAction())){')
s=s.replace('        if("br.com.helper.reels.TEST_DYNAMIC_LOOKUP".equals(getIntent().getAction())){','        if("br.com.helper.reels.TEST_DYNAMIC_LOOKUP_LEGACY".equals(getIntent().getAction())){')
# Disable old generation button rather than silently rendering generic/off-plan stories.
anchor='        if(testMode){trends.setChecked(false);optionalTopic.setText("ciclone");generate();}'
if anchor not in s:raise RuntimeError("MainActivity layout changed: update editorial gate")
s=s.replace(anchor,'''        trends.setChecked(false);
        trends.setEnabled(false);
        trends.setText("Pesquisa de pautas verificadas (em implantação)");
        optionalTopic.setText("");
        optionalTopic.setEnabled(false);
        optionalTopic.setHint("Temas livres desativados nesta edição");
        generateButton.setEnabled(false);
        generateButton.setText("Aguardando integração editorial");
''') if 'generateButton' in s else s
# Guard generation centrally so no alternate UI path can bypass editorial approval.
needle='    private void generate(){'
if needle not in s:raise RuntimeError("Cannot locate generation entry point")
s=s.replace(needle,'''    private void generate(){
        android.widget.Toast.makeText(this,
            "Geração indisponível: primeiro é necessária uma pauta verificada e aprovada.",
            android.widget.Toast.LENGTH_LONG).show();
        return;
    }
    private void legacyGenerate(){''',1)
p.write_text(s,encoding="utf-8")
print("Editorial-only edition: legacy generation disabled until reviewed brief is wired to renderer")
