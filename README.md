# WardTV

**Television for everyone.** Powered by TVN.

WardTV 1.0.0 is a free, browser-based television: curated channels of entertainment on a schedule, with a Guide and a remote. There is no account, no sign-up, no adverts, no analytics and no tracking. It is published as a static site at [wardtv.uk](https://wardtv.uk) on GitHub Pages.

WardTV is an independent edition of TVN, taken from TVN commit `4242c2b`. It is not updated from TVN automatically, and it shares no code at runtime and no browser storage with TVN.

## What WardTV has

| Channels | What they are |
| --- | --- |
| 000 | The WardTV channel surfer: plays something airing elsewhere, then chooses another |
| 001–999 | The curated central catalogue from TVN `4242c2b`, with hospital-safe channel changes (below) |
| 991–1000 | Local Media: files chosen from the viewer's own device, played in the browser and never uploaded |
| 1001 and up | Not available |

Changed from TVN for hospital television, using only programmes already in the shipped catalogue:

- **729 Cosy Kitchen**: calm, quiet cooking (Li Ziqi, Dianxi Xiaoge, Pasta Grannies, Made With Lau), in place of a podcast.
- **776 Slow TV**: unhurried rail journeys and nature films (Rail Relaxation, Nature Relaxation Films, Balu, Relaxation Film, National Rail Scenic Railway Journeys), in place of a podcast.
- **777 Armchair Travel**: Rick Steves' Europe, Lonely Planet and Wolters World, in place of a podcast.
- **120 Trailer TV** / **121 Classic Trailers**: the only trailer channels kept; soft / classic trailers only (no horror or thriller genres).
- **122–139** and **891**: former trailer / promo slots, now calm nature, rail, classical, jazz, ambient, yoga, walking, wildlife, kids and film-score channels.
- Broader hospital pass: horror, cult, combat-sport and medical-risk channel names renamed and re-routed; unsuitable publishers cleared from air. See [docs/WARDTV_HOSPITAL_AUDIT.md](docs/WARDTV_HOSPITAL_AUDIT.md).

The viewer gets the Guide (All and Favourites), channel navigation, numbers, random surfing (Space or SURF), the Programme Director, Multi View (including picture-in-picture), Favourites, bookmarks, programme information, the Info centre (news, sports, weather and more), Credits, Options (picture, sound, playback, sleep, surf timing, Space bar, shortcuts, usage) and About · Sources · Legal. Keyboard, remote and on-screen key hints match TVN. User Network tools (Add, Edit, Export, schedule rearrange) still do nothing here because WardTV has no User Network; the hospital channel catalogue is the other intentional difference.

Every page load tunes a random on-air channel from 001–999 (never 000 or Local Media). The first visit shows the welcome:

> WELCOME TO WARDTV · Television for everyone. · Choose a channel, explore the guide or simply start watching.

WATCH TV carries on with the channel behind it; CHANNEL GUIDE opens the Guide; INFORMATION opens About · Sources · Legal. Sound starts only as the browser allows. WardTV never works around a browser's autoplay rules.

## What WardTV does not have

WardTV is a fixed edition: there is no User Network. Code-level gates (`src/edition.ts`, `EDITION.userNetwork = false`) mean:

- no User Network is created, seeded, loaded or read, and no starter network is fetched;
- no Add Channel, import, export, restore, Network Editor, users or user tabs;
- no editing, rescanning, reloading or rearranging of channels 001–999 (only Local Media and the 000 surfer settings can be changed);
- channels above 1000 cannot be tuned;
- nothing calls TVN's `/api/channel` or `/api/feed` servers, which GitHub Pages does not have.

## Disability Assist

Options → Disability Assist changes how the picture answers a single tap or click:

- **Tap or click on the picture**: Show information (standard), Next channel (in number order), or Random channel. When a tap changes channel, double-click full screen is off; full screen stays on the remote and F.
- **Long press opens the Guide**: on as standard. Hold anywhere on the picture for just over half a second; moving the finger makes it a swipe instead.

Both are kept in this browser.

## Storage

Everything WardTV keeps is in the viewer's browser: `localStorage` keys and IndexedDB databases are all named `wardtv:…`. On wardtv.uk that is a separate origin from TVN anyway. Even where both are served from one origin (for example `localhost`), WardTV never reads or changes TVN's settings, favourites or channels, and a browser that has used TVN still starts WardTV clean. Clearing the site data for wardtv.uk resets WardTV.

## Accessibility

- Keyboard, mouse, touch and TV-remote style navigation (arrows, Enter, Escape, numbers).
- Large touch targets on the welcome and remote, with visible focus rings.
- No action is only reachable by a long press: holds and right-clicks are shortcuts for things that also have a button.
- Honours the system "reduce motion" setting.

## Keys

| Key | Action |
| --- | --- |
| ↑ ↓ | Channel up / down (in the Guide: move) |
| ← → | Volume (in the Guide: move) |
| 0–9 | Tune a channel by number |
| G | Guide |
| I | Programme information |
| Space | Surf to another channel |
| P | Pause |
| S | Favourite |
| M | Mute |
| R | Guide: All / Favourites |
| U | Local Media |
| F | Full screen |
| H | Help |

## Privacy

WardTV asks for no personal information and sets no cookies of its own. Programmes are played from their providers, so the viewer's browser connects to them: YouTube programmes play in YouTube's embedded player (under the [YouTube Terms of Service](https://www.youtube.com/t/terms) and [Google Privacy Policy](https://policies.google.com/privacy)), which loads YouTube and Google services of its own. Typefaces come from Google Fonts. GitHub Pages serves the site and may keep standard request logs. This is all stated in About · Sources · Legal.

## Content

The catalogue is the central TVN catalogue, unchanged in this release: entertainment-focused, with TVN's editorial exclusions kept (no factual space, religious, or aircraft/aerospace programming). Programmes remain hosted by, and attributable to, their creators and providers. Rights holders can reach us through About · Sources · Legal → Rights & attribution.

## Developing

Requires Node 20.19+ or 22.12+.

```sh
npm ci          # install
npm run dev     # development server
npm test        # WardTV's focused tests
npm run lint
npm run build   # production build into dist/ (also writes dist/404.html)
npm run preview # serve dist/ locally
```

## Publishing on GitHub Pages

The workflow in `.github/workflows/deploy.yml` installs, lints, tests, builds and deploys `dist/` to GitHub Pages on every push to `main` (or by hand from the Actions tab). `public/CNAME` names the custom domain, and `dist/404.html` is a copy of the app so any address on wardtv.uk opens WardTV.

One-time setup on GitHub:

1. Push this repository to GitHub.
2. Settings → Pages → Build and deployment → Source: **GitHub Actions**.
3. Settings → Pages → Custom domain: `wardtv.uk`, then Save.
4. When the certificate has been issued, tick **Enforce HTTPS**.

DNS at the registrar for wardtv.uk:

| Type | Name | Value |
| --- | --- | --- |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| AAAA | @ | 2606:50c0:8000::153 |
| AAAA | @ | 2606:50c0:8001::153 |
| AAAA | @ | 2606:50c0:8002::153 |
| AAAA | @ | 2606:50c0:8003::153 |
| CNAME | www | `<github-user>.github.io` |

Remove any other A, AAAA or CNAME records for `@` and `www`. Verifying the domain under the GitHub account's Pages settings is recommended, to stop anyone else claiming it.

## Licences

The bundled libraries are React and React DOM (MIT), and mpegts.js (Apache-2.0). Barlow and Barlow Condensed are loaded from Google Fonts (SIL Open Font License). The WardTV logo and icons are WardTV's own. The programmes themselves are not part of WardTV, and are not licensed by it.

## Version

WardTV 1.0.0, from TVN `4242c2b`. About · Sources · Legal → Version shows both; each build also records its own commit and build time, shown in the diagnostics (D).
