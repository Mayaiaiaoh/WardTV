#!/usr/bin/env python3
"""WardTV hospital pass: cut trailers, replace risky channels, rewrite playable routes."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / 'src/data/canonical-network.json'
MANIFEST = ROOT / 'src/data/independent/manifest.json'
PLAYABLE = ROOT / 'public/independent/playable.json'
DIST_PLAYABLE = ROOT / 'dist/independent/playable.json'
AUDIT = ROOT / 'docs/WARDTV_HOSPITAL_AUDIT.md'

RISK_TITLE = re.compile(
  r'horror|gore|blood|slasher|zombie|kill(?:er|ing)?|murder|terror|haunt|scream|evil\b|'
  r'\bdead\b|chucky|exorcist|friday the 13|halloween|chainsaw|torture|nude|erotic|'
  r'cannibal|psycho|nightmare|demon|devil|possess|vampire|werewolf|grindhouse|giallo|'
  r'splatter|saw\b|hostels?|human centipede|texas chainsaw|nightmare on elm',
  re.I,
)
UNSAFE_GENRES = {'Horror', 'Thriller'}
SOFT_GENRES = {'Comedy', 'Animation', 'Family', 'Documentary', 'Music', 'Musical', 'Romance', 'Biography', 'History'}

# Trailer slots kept + calm replacements for former trailer / promo numbers.
RENAMES: dict[int, tuple[str, str, str]] = {
  # number: (name, category, group)
  120: ('Trailer TV', 'film', 'film'),
  121: ('Classic Trailers', 'film', 'film'),
  122: ('Nature Ambient', 'lifestyle', 'lifestyle'),
  123: ('Scenic Rail', 'lifestyle', 'lifestyle'),
  124: ('Classical Calm', 'music', 'music'),
  125: ('Jazz Lounge', 'music', 'music'),
  126: ('Ambient Dreams', 'music', 'music'),
  127: ('Yoga Hour', 'lifestyle', 'lifestyle'),
  128: ('Walking Tours', 'lifestyle', 'lifestyle'),
  129: ('Quiet Cities', 'lifestyle', 'lifestyle'),
  130: ('Open Country', 'lifestyle', 'lifestyle'),
  131: ('Model Railways', 'lifestyle', 'lifestyle'),
  132: ('Wild Earth', 'knowledge', 'knowledge'),
  133: ('Wildlife Hour', 'knowledge', 'knowledge'),
  134: ('Ocean Quiet', 'knowledge', 'knowledge'),
  135: ('Bluey', 'entertainment', 'entertainment'),
  136: ('Mr Bean', 'entertainment', 'entertainment'),
  137: ('Film Scores', 'music', 'music'),
  138: ('Travel Archive', 'knowledge', 'knowledge'),
  139: ('Thunderbirds', 'entertainment', 'entertainment'),
  891: ('Night Calm', 'lifestyle', 'lifestyle'),
  # Broader hospital-risk film / sports slots
  38: ('Soft Cinema', 'film', 'film'),
  82: ('Quiet Night', 'music', 'music'),
  104: ('Archive Shorts', 'film', 'film'),
  119: ('Family Animation', 'entertainment', 'entertainment'),
  140: ('Gentle Features', 'film', 'film'),
  141: ('Classic Features', 'film', 'film'),
  142: ('Concert Calm', 'music', 'music'),
  150: ('Daytime Drama', 'entertainment', 'entertainment'),
  184: ('Public Domain Cinema', 'film', 'film'),
  185: ('Scenic Drive', 'lifestyle', 'lifestyle'),
  186: ('Easy Listening', 'music', 'music'),
  191: ('Nature Archive', 'knowledge', 'knowledge'),
  215: ('Daytime Stories', 'entertainment', 'entertainment'),
  218: ('Story Time', 'entertainment', 'entertainment'),
  223: ('Kids Animation', 'entertainment', 'entertainment'),
  256: ('Movie Talk', 'entertainment', 'entertainment'),
  328: ('Table Tennis', 'sport', 'sport'),
  329: ('Volleyball Archive', 'sport', 'sport'),
  # Audit round: cult, combat sports, medical-risk names
  39: ('Mystery Science', 'entertainment', 'entertainment'),
  183: ('Soft Classics', 'film', 'film'),
  192: ('Comedy Double Bill', 'film', 'film'),
  219: ('Classic Adventure', 'entertainment', 'entertainment'),
  330: ('Football Archive', 'sport', 'sport'),
  331: ('Rugby Archive', 'sport', 'sport'),
  389: ('Court Sports', 'sport', 'sport'),
  391: ('Match Analysis', 'sport', 'sport'),
  461: ('Lab Notes', 'knowledge', 'knowledge'),
  475: ('Science Hour', 'knowledge', 'knowledge'),
  746: ('Heritage Digs', 'knowledge', 'knowledge'),
}

# Dedicated source pools for replacement channels (and kept trailers handled separately).
DEDICATED: dict[int, list[str]] = {
  122: ['src_nature_relaxation_films', 'src_balu_nature', 'src_relaxation_film'],
  123: ['src_rail_relaxation'],
  124: ['src_hr_symphony'],
  125: ['src_jalc'],
  126: ['src_hammock'],
  127: ['src_yoga_adriene'],
  128: ['src_prowalk'],
  129: ['src_rambalac'],
  130: ['src_j_utah'],
  131: ['src_sams_trains'],
  132: ['src_free_documentary_nature'],
  133: ['src_real_wild'],
  134: ['src_schmidt_ocean'],
  135: ['src_bluey'],
  136: ['src_mr_bean'],
  137: ['src_soundworks'],
  138: ['src_travel_film_archive'],
  139: ['src_gerry_anderson'],
  891: ['src_nature_relaxation_films', 'src_hammock', 'src_rail_relaxation'],
  38: ['src_film_detective'],
  82: ['src_hammock'],
  104: ['src_nfb'],
  119: ['src_bluey', 'src_sesame_street', 'src_glitch'],
  140: ['src_film_detective'],
  141: ['src_film_detective'],
  142: ['src_hr_symphony'],
  150: ['src_hollyoaks'],
  184: ['src_nfb'],
  185: ['src_prowalk'],
  186: ['src_jalc'],
  191: ['src_nfb'],
  215: ['src_this_morning'],
  218: ['src_sesame_street'],
  223: ['src_bluey', 'src_sesame_street', 'src_glitch'],
  256: ['src_screen_junkies'],
  328: ['src_wtt'],
  329: ['src_fivb_archive'],
  39: ['src_mst3k'],
  183: ['src_film_detective'],
  192: ['src_mst3k'],
  219: ['src_gerry_anderson'],
  330: ['src_fifa'],
  331: ['src_world_rugby'],
  389: ['src_fivb_archive', 'src_wtt'],
  391: ['src_royal_institution'],
  461: ['src_royal_institution'],
  475: ['src_royal_institution', 'src_harvard_chan'],
  746: ['src_time_team', 'src_harvard_chan'],
}

TOUCHED = sorted(set(RENAMES) | set(DEDICATED) | {120, 121})


def genres_for(playable: dict, video_id: str) -> set[str]:
  entry = (playable.get('trailerGenres') or {}).get(video_id)
  if entry:
    return set(entry[1])
  return set((playable.get('filmGenres') or {}).get(video_id) or [])


def title_ok(title: str) -> bool:
  return not RISK_TITLE.search(title or '')


def soft_trailer(playable: dict, video_id: str, title: str) -> bool:
  if not title_ok(title):
    return False
  genres = genres_for(playable, video_id)
  if genres & UNSAFE_GENRES:
    return False
  if genres & SOFT_GENRES:
    return True
  # Untagged modern RT trailers: keep only if the title clearly looks soft.
  return bool(re.search(r'comedy|animation|animated|cartoon|documentary|disney|pixar|ghibli|family|musical|romance', title, re.I))


def classic_trailer_ok(playable: dict, video_id: str, title: str) -> bool:
  if not title_ok(title):
    return False
  genres = genres_for(playable, video_id)
  if genres & UNSAFE_GENRES:
    return False
  return True


def film_detective_ok(title: str) -> bool:
  return title_ok(title) and not re.search(r'horror|thriller|double feature.*horror', title, re.I)


def rename_channels(canon: dict) -> None:
  by_number = {c['number']: c for c in canon['channels']}
  for number, (name, category, group) in RENAMES.items():
    channel = by_number[number]
    channel['name'] = name
    channel['category'] = category
    channel['group'] = group


def update_manifest(manifest: dict) -> None:
  routes = {r['number']: r for r in manifest.get('routes', [])}
  for number, sources in DEDICATED.items():
    route = routes.get(number)
    if route is None:
      route = {'number': number, 'sourceIds': sources}
      manifest['routes'].append(route)
      routes[number] = route
    else:
      route['sourceIds'] = sources
  # Kept trailers: classic + soft RT only.
  for number, sources in {
    120: ['src_rt_trailers', 'src_rt_classic_trailers'],
    121: ['src_rt_classic_trailers'],
  }.items():
    route = routes.get(number)
    if route is None:
      manifest['routes'].append({'number': number, 'sourceIds': sources})
    else:
      route['sourceIds'] = sources
  # Source target lists: ensure replacements are named.
  by_id = {s['id']: s for s in manifest.get('sources', [])}
  for number, sources in {**DEDICATED, 120: ['src_rt_trailers', 'src_rt_classic_trailers'], 121: ['src_rt_classic_trailers']}.items():
    for source_id in sources:
      source = by_id.get(source_id)
      if not source:
        continue
      targets = list(source.get('targets') or [])
      if number not in targets:
        targets.append(number)
        source['targets'] = sorted(targets)


def rewrite_playable(playable: dict) -> dict[str, int]:
  stats: dict[str, int] = defaultdict(int)
  # Index items by source for dedication.
  by_source: dict[str, list] = defaultdict(list)
  for item in playable['items']:
    by_source[item[3]].append(item)

  # Strip every touched channel from all items first.
  touched = set(TOUCHED)
  for item in playable['items']:
    before = item[4]
    after = [n for n in before if n not in touched]
    if len(after) != len(before):
      stats['stripped'] += 1
      item[4] = after

  # Ban hospital-unsuitable publishers from airing anywhere.
  banned = {
    'src_trailers_from_hell', 'src_dead_meat', 'src_adult_swim', 'src_alter',
    'src_wwe_vault', 'src_wcw', 'src_wwe', 'src_top_rank', 'src_one', 'src_chubbyemu',
  }
  for item in playable['items']:
    if item[3] in banned:
      if item[4]:
        stats['banned_cleared'] += 1
      item[4] = []

  # Strip risk-titled MST3K / KOFA programmes from every channel.
  for item in playable['items']:
    if item[3] in {'src_mst3k', 'src_kofa'} and item[4] and not title_ok(item[1]):
      stats['risk_title_cleared'] += 1
      item[4] = []

  def add(number: int, item: list) -> None:
    if number not in item[4]:
      item[4].append(number)
      stats[f'ch{number}'] += 1

  # 120 Trailer TV — soft trailers only.
  for item in by_source.get('src_rt_trailers', []) + by_source.get('src_rt_classic_trailers', []):
    if soft_trailer(playable, item[0], item[1]):
      add(120, item)

  # 121 Classic Trailers — classic RT only, hospital-filtered.
  for item in by_source.get('src_rt_classic_trailers', []):
    if classic_trailer_ok(playable, item[0], item[1]):
      add(121, item)

  kids_ok = {135, 136, 139, 218, 223, 219}
  film_det = {38, 140, 141, 183}

  # Dedicated calm / replacement channels.
  for number, sources in DEDICATED.items():
    for source_id in sources:
      for item in by_source.get(source_id, []):
        if number in film_det and source_id == 'src_film_detective' and not film_detective_ok(item[1]):
          continue
        if source_id == 'src_mst3k' and not title_ok(item[1]):
          continue
        if not title_ok(item[1]) and number not in kids_ok:
          continue
        add(number, item)

  # programmeRoutes: rebuild for touched channels from explicit lists.
  routes = dict(playable.get('programmeRoutes') or {})
  for number in TOUCHED:
    routes.pop(str(number), None)
  for number in TOUCHED:
    ids = [item[0] for item in playable['items'] if number in item[4]]
    if ids:
      routes[str(number)] = ids
  playable['programmeRoutes'] = routes
  playable['generatedAt'] = playable.get('generatedAt', 0)
  return stats


def write_audit(stats: dict[str, int]) -> None:
  lines = [
    '# WardTV hospital catalogue audit',
    '',
    'WardTV is television for hospital and care settings. This pass cut the large trailer block,',
    'replaced hospital-risky genres, and filtered unsuitable publishers from the shipped playable catalogue.',
    '',
    '## Trailers',
    '',
    '- Kept **120 Trailer TV** (comedy / animation / documentary / family-leaning trailers only).',
    '- Kept **121 Classic Trailers** (classic trailer publisher, horror/thriller genres and risk titles removed).',
    '- Replaced **122–139** and **891** with calm nature, rail, classical, jazz, ambient, yoga, walking, wildlife, kids and film-score channels.',
    '',
    '## Other channels renamed and re-routed',
    '',
  ]
  for number in sorted(n for n in RENAMES if n not in set(range(120, 140)) | {891}):
    name, _, _ = RENAMES[number]
    lines.append(f'- **{number}** → {name}')
  lines += [
    '',
    '## Publishers cleared from air',
    '',
    '- Trailers from Hell, Dead Meat, Adult Swim, ALTER (horror shorts), WWE / WWE Vault, WCW, Top Rank Boxing, ONE Championship, Chubbyemu.',
    '- MST3K / KOFA titles matching hospital risk keywords were cleared from every channel.',
    '',
    '## Playable rewrite counts',
    '',
  ]
  for key in sorted(stats):
    lines.append(f'- `{key}`: {stats[key]}')
  lines.append('')
  AUDIT.parent.mkdir(parents=True, exist_ok=True)
  AUDIT.write_text('\n'.join(lines), encoding='utf8')


def main() -> None:
  canon = json.loads(CANON.read_text(encoding='utf8'))
  manifest = json.loads(MANIFEST.read_text(encoding='utf8'))
  playable = json.loads(PLAYABLE.read_text(encoding='utf8'))

  rename_channels(canon)
  update_manifest(manifest)
  stats = rewrite_playable(playable)
  write_audit(stats)

  CANON.write_text(json.dumps(canon, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
  MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf8')
  payload = json.dumps(playable, ensure_ascii=False, separators=(',', ':')) + '\n'
  PLAYABLE.write_text(payload, encoding='utf8')
  if DIST_PLAYABLE.parent.is_dir():
    DIST_PLAYABLE.write_text(payload, encoding='utf8')

  print('Renamed', len(RENAMES), 'channels')
  print('Playable stats:', dict(stats))
  for number in (120, 121, 122, 130, 135, 891, 38, 256, 328):
    count = sum(1 for item in playable['items'] if number in item[4])
    name = RENAMES.get(number, (str(number), '', ''))[0]
    print(f'  {number} {name}: {count}')


if __name__ == '__main__':
  main()
