#!/usr/bin/env python3
"""Install this experimental app alongside the existing production app."""
from pathlib import Path
import re
gradle=Path("app/build.gradle")
if not gradle.exists(): gradle=Path("app/build.gradle.kts")
assert gradle.exists(),"Android app Gradle file missing"
s=gradle.read_text(encoding="utf-8")
# Change only the application ID; Java package and activity class stay unchanged.
if gradle.suffix==".kts":
 pattern=r'(applicationId\s*=\s*")[^"]+(")'
else:
 pattern=r'(applicationId\s+")[^"]+(")'
s,n=re.subn(pattern,r'\g<1>br.com.helper.curiosidadesreels.nova\2',s)
if n==0:
 # Some archived Android sources derive applicationId from namespace; add it explicitly.
 if gradle.suffix==".kts":
  s,n=re.subn(r"(defaultConfig\s*\{)",'\\1\n        applicationId = "br.com.helper.curiosidadesreels.nova"',s,count=1)
 else:
  s,n=re.subn(r"(defaultConfig\s*\{)",'\\1\n        applicationId "br.com.helper.curiosidadesreels.nova"',s,count=1)
assert n==1,f"Expected one applicationId or defaultConfig block, found {n}"
# Override late in the script: legacy Gradle source can reset applicationId in build types.
if gradle.suffix==".kts":
 s+='\nandroid { defaultConfig { applicationId = "br.com.helper.curiosidadesreels.nova" } }\n'
else:
 s+='\nandroid { defaultConfig { applicationId "br.com.helper.curiosidadesreels.nova" } }\n'
gradle.write_text(s,encoding="utf-8")
manifest=Path("app/src/main/AndroidManifest.xml")
m=manifest.read_text(encoding="utf-8")
# Explicit separate user-visible name, independent of source resources.
m,n=re.subn(r'android:label="[^"]*"', 'android:label="Curiosidades Reels NOVO"',m,count=1)
assert n==1,"Expected application label in manifest"
manifest.write_text(m,encoding="utf-8")
print("Separate package: br.com.helper.curiosidadesreels.nova; label: Curiosidades Reels NOVO")
