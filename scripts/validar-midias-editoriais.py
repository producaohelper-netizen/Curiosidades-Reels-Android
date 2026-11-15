#!/usr/bin/env python3
"""Preflight for original 9:16 story production. No downloads or invented licenses."""
from urllib.parse import urlparse
ALLOWED={"public_domain","cc0","cc_by","licensed","original"}
def validate_assets(story,assets):
 errors=[]
 if not story.get("review_approved"):errors.append("editorial_approval_required")
 if not story.get("sources") or len(story["sources"])<2:errors.append("two_sources_required")
 if not assets:errors.append("scene_assets_missing")
 for i,asset in enumerate(assets):
  license=asset.get("license","")
  if license not in ALLOWED:errors.append(f"scene_{i}:license_missing_or_invalid")
  if not asset.get("scene_text") or not asset.get("description"):errors.append(f"scene_{i}:subject_match_not_described")
  if license!="original" and not asset.get("source_url"):errors.append(f"scene_{i}:source_url_required")
  if license=="cc_by" and not asset.get("attribution"):errors.append(f"scene_{i}:attribution_required")
  if asset.get("source_url") and urlparse(asset["source_url"]).scheme!="https":errors.append(f"scene_{i}:https_required")
  if asset.get("is_reused_social_video"):errors.append(f"scene_{i}:reused_social_video_disallowed")
 return errors
if __name__=="__main__":
 story={"review_approved":True,"sources":["https://example.org/a","https://example.net/b"]}
 assets=[{"license":"original","scene_text":"A cidade foi evacuada","description":"Ilustração própria da cidade, não fotografia documental"}]
 assert validate_assets(story,assets)==[]
 assert "editorial_approval_required" in validate_assets(dict(story,review_approved=False),assets)
 assert any("attribution" in e for e in validate_assets(story,[dict(assets[0],license="cc_by",source_url="https://example.org/image")]))
 assert "scene_assets_missing" in validate_assets(story,[])
 print("Scene asset preflight PASS")
