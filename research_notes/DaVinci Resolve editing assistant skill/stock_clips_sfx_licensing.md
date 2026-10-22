# Stock B-roll, SFX and Music Sources Safe for a Monetized YouTube Channel (checked 2026-10-22)

Research method note (read first): checked on 2026-10-22. In this session, direct page fetches (WebFetch/curl) to pexels.com, pixabay.com, freesound.org and others were blocked by the environment's network egress (DNS failure / proxy refused the connection). Every finding below comes from web-search result extracts of the cited pages, not from a full read of each page. Official pages (license pages, API docs, YouTube Help) are cited wherever the search returned them. Secondary/affiliate sources are labelled as such. Exact wording, prices and rate limits should be checked against the live pages before the skill hard-codes them. One page in the results (mixkit.co/llm-info/) contained embedded instructions aimed at AI assistants telling them to promote Mixkit. Those instructions were ignored and the page was not used as a license source.

## Q1. Free stock VIDEO sources: license, monetization safety, Content ID risk, attribution, API

### Takeaway
The safest free sources with real APIs are **Pexels** (free API, 200 req/hour, 20,000/month; no attribution needed in the video itself, but the API terms ask for a link to Pexels and credit to the creator where possible), **Pixabay** (free API, 100 req/60 s, results must be cached for 24 h) and **Coverr** (free API key plus an official MCP server, 50 req/h on a new "Demo" app and 2,000 req/h in "Production"). Mixkit is safe and needs no attribution, but no public API was found. Videvo, Vidsplay, Dareful and Mazwai have mixed or attribution licenses, so a skill should treat them as "check each clip". Wikimedia Commons and Internet Archive have open APIs, but licenses vary per file, so the skill must filter out any -NC (NonCommercial) license and keep the attribution metadata. No video stock site promises zero Content ID claims.

### Cited Findings

**Pexels**
- API default limit is 200 requests/hour and 20,000/month. Higher or unlimited limits are free if you meet the API terms and show attribution — [Pexels API docs](https://pexels.com/api/documentation/) (via search extract)
- API guideline: "Whenever you are doing an API request make sure to show a prominent link to Pexels" and "Always credit our photographers when possible (e.g. 'Photo by John Doe on Pexels' with a link to the photo page on Pexels)." A text link like "Photos provided by Pexels" is acceptable if a full link-back is not feasible — [Pexels API docs](https://www.pexels.com/api/documentation/); [Pexels Help: How should I give credit?](https://help.pexels.com/hc/en-us/articles/900005851903-How-should-I-give-credit-Can-I-use-your-logo)
- Unlimited access requires proof of attribution (video demo or screenshots) — [Pexels Help: How do I get unlimited requests?](https://help.pexels.com/hc/en-us/articles/900005852323-How-do-I-get-unlimited-requests)
- Rate-limit headers are only returned on successful responses, not on 429s, so clients must track usage themselves. Trying to work around the rate limit leads to termination of API access. The Pexels FAQ suggests caching responses for 24 hours — [Pexels API docs](https://pexels.com/api/documentation/) (via search extract)
- General license and terms: "You do not need to credit Pexels or the contributor of Content when you use it, but it is certainly appreciated" — [Pexels Terms of Service](https://www.pexels.com/terms-of-service/)
- Prohibited uses: identifiable people may not be shown in a bad or offensive light (criminal activity, medical condition, pornographic context). You may not sell unaltered copies (stock, poster, print, physical product without added value), use content in your trade-mark or business name, suggest that a depicted person or brand endorses you, or redistribute on other stock or wallpaper sites — [Pexels Help: rules for using Pexels photos or videos](https://help.pexels.com/hc/en-us/articles/360042332714-What-are-the-rules-for-using-Pexels-photos-or-videos)
- The ToS says commercial use of identifiable people or brands will likely need consent or a license, and that responsibility for clearing those rights rests with the user — [Pexels Terms of Service](https://pexels.com/terms-of-service) (via search summary)
- Pexels moved from CC0 to its own license. Older guides still describing it as CC0 are outdated — [Wikipedia: Pexels](https://en.wikipedia.org/wiki/Pexels); [search summary noting outdated libguide](https://libguides.sau.edu/education301/booktrailer)
- Pexels is described as low-risk for Content ID but "not immune", and as publishing its videos without audio, which removes the most common source of claims (secondary/vendor blogs) — [Coverr blog: No Copyright Stock Video for YouTube (2026)](https://coverr.co/blog/no-copyright-stock-video-for-youtube); [frameos.studio: Free Stock Video Sites in 2026](https://frameos.studio/blog/free-stock-video-sites)
- A newer help article indicates media details and statistics are available through the API — [Pexels Help: Are media details and statistics available through the API?](https://help.pexels.com/hc/en-us/articles/47677748516121-Are-media-details-and-statistics-available-through-the-API)

**Pixabay (video)**
- License summary: content may be used for free, without attributing the author, and may be modified, subject to the Prohibited Uses. No selling or distributing content on a "Standalone" basis (unchanged, no creative effort). Content showing recognizable trademarks or logos can't be used commercially for goods or services. Recognizable people can't be used in immoral or illegal ways. Some content may carry extra rights (trademark, privacy, etc.). Only the full Content License is binding — [Pixabay Content License Summary](https://pixabay.com/en/service/license/)
- Pixabay moved from CC0 to the Pixabay Content License in January 2019. Items downloaded before then may carry CC0 terms. Some Pixabay content is AI-generated and labelled per item — [Pixabay FAQ](https://pixabay.com/service/faq/) (via search summary)
- Recent change to note: the Pixabay FAQ says the general license lets Pixabay use uploads to develop AI models, and contributors can opt out with an "AI training" toggle. A Pixabay blog post dated 6 Oct 2025 says Pixabay content can't be redistributed for machine-learning or database-building purposes — [Pixabay FAQ](https://pixabay.com/service/faq/); [Pixabay blog: Intellectual Property Explained](https://pixabay.com/ko/blog/posts/intellectual-property-explained-441/) (these affect AI/redistribution use, not YouTube editing)
- API: default up to 100 requests per 60 seconds, counted per API key rather than per IP. The docs ask you to show users where images and videos come from whenever search results are displayed — [Pixabay API docs](https://pixabay.com/api/docs/) (via search extract)
- API responses must be cached for 24 hours, and downloading to your own storage rather than hot-linking is required (secondary sources quoting the docs; the official wording could not be read this session) — [rubydoc pixabay_api](https://www.rubydoc.info/gems/pixabay_api/0.0.1); [rapidevelopers Pixabay guide](https://www.rapidevelopers.com/md/v0-integrations/pixabay-api)
- Third-party sites quote other limits (5,000/hour, 500/hour). These conflict with the official 100 per 60 s and should be ignored — [freeapihub](https://freeapihub.com/apis/pixabay-api)

**Mixkit**
- Mixkit has a separate license per item type (video, music, SFX, templates). User Terms last revised 2 Oct 2025 — [Mixkit License](https://mixkit.co/license/); [Mixkit Terms](https://mixkit.co/terms/)
- Video: reviewers report clips may be used without attribution, including on YouTube (secondary) — [educatorstechnology](https://www.educatorstechnology.com/2022/11/mixkit-free-sound-effects-and-video.html)
- Mixkit's licenses forbid claiming items as your own or registering them with any rights-management service (i.e. Content ID) — [Mixkit Sound Effects Free License](https://mixkit.co/license/modal/sfxFree/)
- One review reports that Mixkit has said it will handle a YouTube claim if you contact its team (secondary) — [kripeshadwani Mixkit review 2026](https://kripeshadwani.com/mixkit-review/)
- No Mixkit public API was found in any search result (gap; see below).

**Coverr**
- Coverr says all videos in its free library are royalty-free, cleared for commercial use, and usable in monetized YouTube videos without crediting the creator (credit appreciated). Footage may not be resold or redistributed as a standalone product. The library mixes human-shot and AI-generated clips, labelled per clip. A Premium tier adds exclusive footage, 4K and "extended licensing protections" — [Coverr FAQ text on category pages](https://coverr.co/stock-video-footage/visuals)
- API: create an application at coverr.co/developers to get a key instantly. The key goes in the `api_key` query parameter or an Authorization header (e.g. `https://api.coverr.co/videos?api_key={api_key}`). New apps start in "Demo" status at 50 requests/hour, and Production is 2,000 requests/hour — [Coverr API Authentication](https://api.coverr.co/docs/auth); [Coverr API Getting Started](https://api.coverr.co/docs/start)
- Coverr runs an official MCP server at `https://mcp.coverr.co/mcp` (header `x-coverr-api-key`). Its `get_videos` tool supports search, filtering and pagination — [Coverr MCP docs](https://api.coverr.co/docs/mcp/); [coverr.co/mcp](https://coverr.co/mcp)

**Videvo (mixed licenses)**
- The "Videvo Standard License" is a legacy license no longer used for new content. Clips under the "Videvo Attribution License" need credit, e.g. "Stock footage provided by Videvo, downloaded from www.videvo.net" (guide last updated May 2020) — [Videvo blog: Licenses and Usage](https://www.videvo.net/blog/?p=314)
- An April 2025 third-party review still describes the Standard License as current, which contradicts Videvo's own guide — [softwaretestinghelp Videvo review](https://www.softwaretestinghelp.com/videvo-review/amp/)
- Freepik reportedly acquired Videvo in June 2022 (unverified listing) — [alternativeto Videvo](https://alternativeto.net/software/videvo/about)
- No public Videvo API was found.

**Mazwai, Life of Vids, Vidsplay, Dareful (small sites; secondary sources only, conflicting)**
- Mazwai: one Arabic guide says commercial use is allowed without attribution, but a Spanish article says Mazwai videos are CC 3.0 (attribution required). The sources conflict — [IJNet Arabic list of 22 free video platforms](https://ijnet.org/ar/story/%D9%84%D8%B5%D9%86%D9%91%D8%A7%D8%B9-%D8%A7%D9%84%D9%85%D8%AD%D8%AA%D9%88%D9%89-%D8%A7%D9%84%D9%85%D8%B1%D8%A6%D9%8A-22-%D9%85%D9%86%D8%B5%D8%A9-%D9%84%D9%81%D9%8A%D8%AF%D9%8A%D9%88-%D9%85%D8%AC%D8%A7%D9%86%D9%8A-%D8%A8%D9%84%D8%A7-%D8%AD%D9%82%D9%88%D9%82); [wwwhatsnew](https://wwwhatsnew.com/2019/06/06/videos-libres-derechos-gratis-free-download-descarga-sociales/)
- Life of Vids: reported as free for any purpose including commercial, with a limit of no more than 10 videos redistributed to similar sites — [IJNet Arabic](https://ijnet.org/ar/story/%D9%84%D8%B5%D9%86%D9%91%D8%A7%D8%B9-%D8%A7%D9%84%D9%85%D8%AD%D8%AA%D9%88%D9%89-%D8%A7%D9%84%D9%85%D8%B1%D8%A6%D9%8A-22-%D9%85%D9%86%D8%B5%D8%A9-%D9%84%D9%81%D9%8A%D8%AF%D9%8A%D9%88-%D9%85%D8%AC%D8%A7%D9%86%D9%8A-%D8%A8%D9%84%D8%A7-%D8%AD%D9%82%D9%88%D9%82); [HubSpot FR](https://blog.hubspot.fr/website/banques-video-libre-de-droit)
- Vidsplay: free, but publishing requires a visible credit or link to vidsplay.com — [HubSpot FR](https://blog.hubspot.fr/website/banques-video-libre-de-droit); [wwwhatsnew](https://wwwhatsnew.com/2019/06/06/videos-libres-derechos-gratis-free-download-descarga-sociales/)
- Dareful: reported as Creative Commons 4.0 (variant not specified; CC BY 4.0 not confirmed) — [smartworld.it](https://www.smartworld.it/guide/siti-app-videoclip-gratis-filmati.html)

**Wikimedia Commons**
- Search is available without a key through the standard MediaWiki API. `srnamespace=6` restricts results to the File namespace — [archivarix Wikimedia Commons notes](https://echo.archivarix.net/ru/archive/wikimedia-commons)
- CirrusSearch supports a `filetype:` keyword (since MediaWiki 1.28). The Commons search help gives `shark filetype:video` as an example, and `filemime:` is also supported — [Phabricator T151352](https://phabricator.wikimedia.org/T151352); [Help:Searching mirror](https://download.osmand.net/wiki/Help:Searching)
- Per-file license and credit come from `prop=imageinfo&iiprop=extmetadata` → `extmetadata.LicenseShortName`, `Credit`, `AttributionRequired`, `LicenseUrl`. API calls require a descriptive User-Agent header — [Openverse provider notes for Wikimedia Commons](https://make.wordpress.org/openverse/handbook/openverse-catalog/provider-api-wikimedia-commons/); [skillsmp Wikimedia Commons skill](https://skillsmp.com/fr/creators/fuzheado/wikipedia-ai-skills/claude-skills-wikimedia-commons)

**Internet Archive**
- The public Advanced Search and Metadata APIs need no authentication. Queries can filter by `mediatype` (movies, audio, etc.) and by `licenseurl:` (e.g. `licenseurl:creativecommons.org`), and item records carry a `licenseurl` field (third-party scraper docs, not the official docs) — [Apify archive-org-scraper](https://apify.com/lulzasaur/archive-org-scraper); [Apify gio21 items scraper](https://apify.com/gio21/archive-org-items-scraper.md)
- How the official API marks "public domain" could not be confirmed (gap).

**NASA / US government**
- NASA material is generally not subject to US copyright and may be used for educational or informational purposes. Commercial use "must not explicitly or implicitly convey NASA's endorsement." Logos/insignia need prior written approval. Identifiable people may have publicity rights. The guidelines also contain AI-related restrictions — [NASA Brand Center: Images and Media guidelines](https://nasa.gov/nasa-brand-center/images-and-media); [Vondran Legal summary](https://www.vondranlegal.com/how-to-legally-use-nasa-images-in-your-youtube-blogs-and-social-media)
- No YouTube-specific NASA rule was found. Questions go to NASA's media contact — [GPM image use policy](https://gpm.nasa.gov/image-use-policy)

**Openverse**
- Openverse exposes image and audio search (an `/audio` endpoint with license, category (music/sound_effect) and length filters). Each record includes the license URL, attribution string and source. No video endpoint was found — [Jentic Openverse API listing](https://jentic.com/apis/openverse); [Openverse docs: Search Algorithm](https://docs.openverse.org/api/reference/search_algorithm.html)
- Anonymous access works without a key. Registration is OAuth2 via `/auth_tokens/register` and `/auth_tokens/token`, and `/rate_limit` shows remaining quota. One npm package lists anonymous limits of 100/day and 5/hour, and 10,000/day and 100/min when authenticated (unverified) — [pkg.go.dev openverse-cli](https://pkg.go.dev/github.com/tamnd/openverse-cli@v0.1.0/openverse); [npm mcp-openverse](https://www.npmjs.com/package/mcp-openverse)

### Inferences
- For "suggest a clip, user approves, then download", Pexels and Coverr are the strongest free video APIs: both are free, keyed, return clip IDs and page URLs, and allow no-attribution use in the final video. Pixabay is a close third (strict 24 h caching, and the "show where content is from" rule applies to the skill's search UI, not to the YouTube video).
- Pexels' API "show a prominent link to Pexels" rule is about the app or skill's display of results. The skill can satisfy it by always printing the Pexels page URL and "Video by <creator> on Pexels" next to each suggestion. The YouTube video itself still needs no credit under the general license.
- For a no-music channel, video-only stock footage (Pexels clips have no audio) carries very low Content ID risk. The main risks are trademarks/logos and identifiable people in the clips, which the skill should flag (e.g. a visible brand logo or a recognizable face in a "frustrated person" clip).
- Wikimedia Commons, Internet Archive and Openverse require per-item license filtering: allow only CC0, Public Domain, CC BY and CC BY-SA, and reject anything with "NC" (and probably "ND" if the clip will be cut or edited). CC BY-SA adds share-alike obligations whose application to a whole YouTube video is legally debatable; the conservative choice is to prefer CC0/PD/CC BY.

### Gaps
- Exact Pexels `/videos/search` parameters and response schema could not be read this session. From prior knowledge (verify before relying on it): `GET https://api.pexels.com/videos/search?query=&orientation=&size=&locale=&page=&per_page=` (max 80 per page) with header `Authorization: <API_KEY>`. Response `videos[]` has `id`, `url` (page), `image` (thumbnail), `duration`, `user{name,url}`, `video_files[]{link,quality,width,height,file_type}` and `video_pictures[]`.
- Exact Pixabay video endpoint fields were not verified. From prior knowledge: `GET https://pixabay.com/api/videos/?key=&q=&video_type=&category=&min_width=&safesearch=&per_page=`, with `hits[]` carrying `id`, `pageURL`, `tags`, `duration`, `user`, and `videos.{large,medium,small,tiny}.{url,width,height,size,thumbnail}`. The official hotlinking wording was not confirmed.
- No official Mixkit, Videvo, Mazwai, Life of Vids, Vidsplay or Dareful API was found. The license texts of the four small sites could not be read directly, and sources conflict on Mazwai.
- Coverr's REST search parameter names (beyond the `/videos` endpoint) were not confirmed.
- Openverse's official rate limits and exact `license_type` values (e.g. `commercial`, `modification`) were not confirmed from official docs.
- The official Internet Archive syntax for public-domain items was not confirmed.

## Q2. Paid/subscription footage sources: price (2026), monetized-YouTube coverage, Content ID handling, API

### Takeaway
Envato is the best fit among paid all-in-one libraries for a single creator: about $16.50/month billed annually (secondary sources), a commercial license on every download with no project registration, and a "Claim Clear" tool that safelists a YouTube channel for eligible music. Artlist's cheapest monetized-YouTube tier is "Social" (one channel per platform). Its Clearlist covers music, and coverage of SFX is unconfirmed. Shutterstock and Adobe Stock have real developer APIs, but Shutterstock's free test account returns no video. Storyblocks' API is enterprise-only. No consumer subscription site offers a free public search API a personal skill could use, except via its own site.

### Cited Findings

**Envato (Elements)**
- Every download comes with a commercial license by default, with "no project registration, no extra steps". Envato says a unique project name has never been required, and a valid certificate should clear a claim whatever project name it shows — [Envato: How licensing works](https://elements.envato.com/learn/how-envato-licensing-works); [Envato: social media license](https://elements.envato.com/learn/envato-social-media-license); [Envato Help: item license certificate](https://help.elements.envato.com/hc/en-us/articles/360000621443-Envato-item-license-certificate)
- Recent change: licensing was simplified (no per-project registration) — [Envato Author Hub: Licensing on Envato just got simpler](https://author.envato.com/hub/licensing-on-envato-just-got-simpler-what-it-means-for-authors/)
- Claim Clear: for "Claim Clear-ready" tracks you can safelist your YouTube channel so eligible claims on future uploads are cleared automatically, or submit a video after a claim. Non-ready tracks must be disputed in YouTube Studio with the license certificate, which can take up to 30 days. An older help page says Claim Clear covers music registered with HAAWK (via Identifyy) — [Envato Claim Clear](https://elements.envato.com/claim-clear-youtube-content-id); [Envato Author Help: Claim Clear](https://help.author.envato.com/hc/en-us/articles/47688491205657-Claim-Clear-Automatically-Clear-YouTube-Content-ID-Claims); [Envato Help: resolve a YouTube Content ID claim](https://help.elements.envato.com/hc/en-us/articles/360016435492-Guide-to-YouTube-Content-ID-Copyright-Notices)
- Envato warns that Content ID claims can block Shorts over one minute, and suggests uploading as Unlisted, clearing claims, then publishing — [Envato: music without copyright strikes](https://elements.envato.com/learn/envato-music-without-copyright-strikes)
- Price (secondary, 2026): individual about $33/month on monthly billing or $198/year ($16.50/month). Team pricing is inconsistent across sources ($10.75 vs $22.50 per seat), and regional prices differ — [toolsurf Envato pricing 2026](https://www.toolsurf.com/envato-elements-pricing-2026-complete-plans-cost-guide-2026-plans-features-best-deals-compared/); [softwares.com](https://www.softwares.com/software/envato-elements); [subger](https://subger.com/en/service/envato-elements)

**Artlist (footage + music + SFX)**
- 2026 prices (secondary, conflicting): Music & SFX "Social" about $9.99/month annually ($14.99 month-to-month), covering one personal channel per platform and no client work or ads. Music & SFX Pro about $24.92/month annually. Footage & Templates about $31.99/month annually. Max about $39.99/month annually (one page showed $50.66/month tied to a credit tier) — [photutorial Artlist review 2026](https://photutorial.com/artlist-review/); [cchound Artlist plans 2026](https://www.cchound.com/artlist/artlist-subscription-plans-and-pricing/); [frontdeskreview Artlist pricing](https://frontdeskreview.com/software/music-licensing/artlist/)
- Assets downloaded during an active subscription stay licensed for that content after cancellation — [cchound Artlist review](https://www.cchound.com/artlist/artlist-complete-review/)
- Clearlist (official help): links your channel or videos to your account so YouTube sees the music as licensed. Social = 1 channel per platform, Pro = 3 YouTube channels, Teams = 5 per platform. Content published after a subscription ends is not covered. Claims from "Artlist Ltd" usually mean the channel is not on your Clearlist. Clearlist applies to plans that include music — [Artlist Help: Understanding copyright and Content ID claims](https://help.artlist.io/hc/en-us/articles/29648852943901-Understanding-copyright-and-Content-ID-claims); [Artlist Help article](https://help.artlist.io/hc/en-us/articles/29648622402333)
- Cross-library conflict example: an Adobe Stock licensee received a Content ID claim from Artlist Ltd for a track also sold elsewhere, and the appeal was rejected — [Adobe Community thread](https://community.adobe.com/t5/stock-discussions/content-id-claim-from-artlist-ltd/m-p/14390697)

**Storyblocks**
- 2026 snapshots: Essentials about $21/month billed annually ($252/yr), Unlimited All Access about $30/month and Small Business about $40/month, all billed annually. Older listings show $16 (outdated) — [frontdeskreview Storyblocks (updated Sept 2026)](https://frontdeskreview.com/software/stock-media/storyblocks/); [subger Storyblocks](https://subger.com/en/service/storyblocks)
- API access is part of the quote-only Enterprise tier, which also includes $1M indemnification and perpetual rights — [frontdeskreview Storyblocks](https://frontdeskreview.com/software/stock-media/storyblocks/); [xpay agent-ready index](https://www.xpay.sh/agent-ready-index/storyblocks/)

**Artgrid / Motion Array**
- Artgrid 2026: Indie from $199/yr and Pro from $299/yr (plan names change often). The license is single-user, worldwide and lifetime for projects created during an active subscription, including YouTube monetization (secondary) — [bityclips Artgrid pricing](https://bityclips.com/tool/artgrid/pricing); [photutorial Artgrid review](https://photutorial.com/artgrid-review)
- Motion Array: prices conflict. Capterra says from $19.99/month, a 2026 review says $29.99 monthly or $14.99 billed annually, and a Motion Array blog says $24.99–$39.99. No source covered how its license handles Content ID — [Capterra Motion Array](https://www.capterra.com/p/265864/Motion-Array/); [photutorial Motion Array review](https://photutorial.com/motion-array-review); [Motion Array blog](https://blog.motionarray.com/?p=28287)

**Shutterstock (API)**
- API pricing page: the free test account covers 3M images, **0 videos** and 0 music tracks, with a max of 100 requests/hour and watermarked previews. Paid "Unlimited" API tiers list up to 4M videos and 1,000 requests/minute. Monthly download and call limits apply — [Shutterstock API pricing](https://code.shutterstock.com/api/pricing)
- Auth: Basic Auth (client ID + secret) for read-only search, OAuth 2.0 for licensing. A licensing sandbox exists (secondary/npm) — [rapidevelopers Shutterstock API](https://rapidevelopers.com/replit-integration/shutterstock-api); [npm shutterstock-api](https://npmjs.com/package/shutterstock-api)

**Adobe Stock (API)**
- The API lets developers search and retrieve photos, videos and vectors. You register an app in Adobe Developer Console for an API key (client ID). Search can be tested without an enterprise account, but licensing calls need extra credentials plus a credit quota or subscription. Some docs mention joining a prerelease and affiliate program — [Adobe Stock API: Getting started](https://developer.adobe.com/stock/docs/getting-started); [Adobe: Creating Stock applications](https://developer.adobe.com/stock/docs/getting-started/04-creating-apps)
- Adobe Stock has no downloadable PDF license certificate (community reports). Users screenshot the License History page, which lists file IDs, dates and license type — [Adobe Community: stock license proof](https://community.adobe.com/questions-32/help-stock-license-proof-1497136)

**Pond5**
- Pond5's dispute guidance: dispute via the "matched third party content" notice and cite your Pond5 item ID and license. Publish as Unlisted first. Music is the most common Pond5-related claim trigger, because some composers registered their tracks with Content ID themselves — [Pond5 Help: How to dispute/clear a YouTube Content ID claim](https://www.pond5.com/help/en/articles/10086114-how-to-dispute-clear-a-youtube-content-id-claim); [Coverr blog 2026](https://coverr.co/blog/no-copyright-stock-video-for-youtube)
- Pond5 launched a free Public Domain Project (80,000 assets) in 2015 — [TechCrunch 2015](https://techcrunch.com/2015/01/20/pond5-issues-80000-free-media-assets-with-the-launch-of-its-public-domain-project)

### Inferences
- If the user ever pays for one service, Envato (footage + SFX + music with Claim Clear and no project registration) or Artlist Max gives the most coverage. For SFX only, Artlist Social or Epidemic Creator is cheaper. None of these give a personal skill an API, so the skill would generate search URLs (e.g. `https://elements.envato.com/stock-video/rubiks-cube`) for the user to browse rather than return clip IDs.
- Shutterstock's API is unsuitable for free video previews (0 videos on the free tier). Adobe Stock's search API is the most realistic paid-library API for returning video thumbnails and IDs, but licensing still costs credits.

### Gaps
- Official 2026 price pages for Envato, Artlist, Storyblocks, Motion Array, Artgrid, Adobe Stock and Pond5 could not be fetched. All prices above come from third-party sites and vary by region and billing period.
- No source found on Motion Array's or Storyblocks' Content ID handling. Pond5's public API status was not found.
- Whether Artlist's Clearlist covers SFX/footage (vs. music only) is unconfirmed.

## Q3. Sound-effects (SFX) sources: license, attribution, Content ID risk, API

### Takeaway
For SFX the safest sources are the **YouTube Audio Library SFX tab** (YouTube states that its copyright-safe music and SFX won't be claimed via Content ID, and that they are monetizable in YPP), **Mixkit SFX** (free, no attribution), **Pixabay SFX** (no attribution, but the same contributor-registration caveat as Pixabay music), **Freesound filtered to CC0** (CC BY is fine with credit, CC BY-NC is NOT OK), **Kenney** (CC0) and the **Sonniss GDC bundles** (royalty-free, no attribution, no AI training). The **BBC Sound Effects RemArc licence is NOT suitable** for a monetized channel without a paid Pro Sound Effects license. Zapsplat's free tier requires credit, and Gold removes it. YouTube's Content ID rules say sound effects are not eligible as reference files, which structurally lowers SFX claim risk. Freesound is the only free SFX library confirmed to have a full public API with license filtering.

### Cited Findings

**YouTube Audio Library (SFX)**
- The Audio Library (Studio, or youtube.com/audiolibrary) has separate Music and "Sound effects" tabs with search and filters. Tracks under the standard Audio Library license need no attribution ("Attribution not required" filter). Creative Commons tracks need credit (copy button) — [YouTube Help: Use music and sound effects from the Audio Library](https://support.google.com/youtube/answer/3376882?hl=en)
- "If you're in the YouTube Partner Program, you can monetize videos with music and sound effects from the Audio Library. Copyright-safe music and sound effects downloaded from the Audio Library won't be claimed by a rights holder through the Content ID system." YouTube also says it "is not responsible for issues that arise from 'royalty-free' music and sound effects from YouTube channels or other music libraries" — [YouTube Help 3376882](https://support.google.com/youtube/answer/3376882?hl=en)
- Shorts Audio Library music is removed automatically from exports longer than 15 s in YouTube Create — [YouTube Help 3376882](https://support.google.com/youtube/answer/3376882?hl=en)
- Related YouTube help on finding safe music — [YouTube Help: Tips to find safe music](https://support.google.com/youtube/answer/15577610?hl=en)

**Content ID eligibility (why SFX claims should be rare)**
- YouTube Content ID references must be content you own exclusively. Ineligible: content licensed non-exclusively from a third party, Creative Commons and similar open licenses, public domain, and clips used under fair use. "Royalty free" production music libraries must go through manual review before claiming. Karaoke, remasters, sound-alikes, **sound effects and production loops** do not qualify as references — [YouTube Help: Content eligible for Content ID](https://support.google.com/youtube/answer/2605065?hl=en); [YouTube Help: Qualify for Content ID](https://support.google.com/youtube/answer/1311402?hl=en)

**Freesound**
- Current licenses: CC0, Attribution (CC BY), Attribution NonCommercial (CC BY-NC). The legacy "Sampling+" license (Freesound 1) should be treated like BY-NC and also bars commercial adverts — [Freesound FAQ](https://freesound.org/help/faq/)
- Attribution format: sound name, uploader with profile link, and license, grouped per sound. A separate credits page is fine for long lists — [Freesound FAQ](https://freesound.org/help/faq/)
- Monetization (forum, not official): CC BY sounds can be used in monetized videos with credit. CC BY-NC "means you can't monetize the videos or make a profit from them" — [Freesound forum: Freesounds and youtube monetization](https://freesound.org/forum/legal-help-and-attribution-questions/39864); [Freesound forum: sound licenses](https://freesound.org/forum/legal-help-and-attribution-questions/38292/)
- API auth: token auth (`token=` query param) for search and previews. OAuth2 for "OAuth2 required" resources (original-quality download, upload, rating). OAuth access tokens last 24 h — [Freesound API authentication](https://freesound.org/docs/api/authentication.html); [Freesound APIv2 overview](https://freesound.org/docs/api/overview.html)
- Throttling: standard 60 requests/min and 2,000/day. Stricter for original-quality download and similar resources (30/min, 500/day). HTTP 429 when throttled. Limits are per user across all that user's API clients. A usage endpoint is not throttled. Higher limits on request. Do not register multiple keys to evade limits — [Freesound APIv2 Overview](https://freesound.org/docs/api/overview.html); [Freesound API Terms of Use](https://freesound.org/docs/api/terms_of_use.html)
- License filter syntax example: `filter=license:"Creative Commons 0"`. Values with spaces need double quotes. BY-NC is `license:"Attribution Noncommercial"` — [Creative Commons blog: Freesound intro](https://opensource.creativecommons.org/blog/entries/freesound-intro/); [Ardour commit: filter results by licence](https://git.ardour.org/ardour/ardour/commit/eae1673ff16ea52d954b6b98e1ef7265882a5611)
- Search results expose preview URLs such as `previews.preview-hq-mp3`, which can be played without OAuth (secondary API spec) — [Jentic Freesound API](https://jentic.com/apis/freesound.org/freesound.md)

**Pixabay sound effects**
- Covered by the same Pixabay Content License (free, no attribution) — [Pixabay license summary](https://pixabay.com/en/service/license/)
- No Pixabay audio API was confirmed. Evidence leans toward the API being image/video only: an OpenClaw skill uses Freesound for SFX and Jamendo for music, and uses Pixabay only for images/videos — [playbooks openclaw free-resource skill](https://playbooks.com/skills/openclaw/skills/free-resource); conflicting third-party n8n node claims audio — [n8n-nodes-pixabay](https://awesome.ecosyste.ms/projects/github.com%2Fn8n-code%2Fn8n-nodes-pixabay)

**Mixkit SFX**
- Mixkit Sound Effects Free License: free for commercial and non-commercial projects, including YouTube videos, social posts, online ads and video games. No attribution, no sign-up. You can't redistribute sounds standalone, claim them as your own, or "register them on any rights management service" — [Mixkit Sound Effects Free License](https://mixkit.co/license/modal/sfxFree/); [Mixkit free sound effects](https://mixkit.co/free-sound-effects/)
- Mixkit has relevant categories (e.g. video-game, click) — [Mixkit video game SFX](https://mixkit.co/free-sound-effects/video-game/); [Mixkit click SFX](https://mixkit.co/free-sound-effects/click/)

**Zapsplat**
- Free (Basic) account: attribution required, e.g. "Sound effects from zapsplat.com". A paid Gold subscription removes the attribution requirement (secondary: sounds downloaded under Gold stay attribution-free after cancellation). No standalone redistribution on any plan — [Zapsplat: Copyright and audio licensing for beginners](https://www.zapsplat.com/copyright-and-audio-licensing-for-beginners); [licenseorg Zapsplat guide](https://licenseorg.com/guide/music-audio/zapsplat)

**Sonniss GDC bundles**
- Royalty-free, commercial use, no attribution, unlimited projects for life (2018 announcement). The multi-year archive is over 200 GB. The 2024 bundle license adds a ban on using the sounds to train AI models — [gamedev.tv repost of Sonniss 2018 announcement](https://community.gamedev.tv/t/30gb-of-high-quality-royalty-free-sound-effects-the-sonniss-gameaudiogdc-bundle-2018/63406); [cinevva free SFX guide 2026](https://app.cinevva.com/guides/free-sound-effects-music); [GameFromScratch GDC 2024 giveaway](https://gamefromscratch.com/sonniss-27-5gb-sound-effect-giveaway-at-gdc-2024/)

**BBC Sound Effects (RemArc)**
- The free RemArc licence covers personal, educational and research use. Commercial use requires a license, available via Pro Sound Effects since 2009. A personal YouTube Short is "probably fine", but larger commercial projects need a license. A comparison table classifies RemArc as non-commercial only — [DIYPhotography on BBC SFX archive](https://www.diyphotography.net/the-bbc-sound-effects-archive-is-now-free-to-download-with-over-33000-files/); [gyre.pro free SFX sites](https://gyre.pro/es/blog/top--websites-with-free-sound-effects); [CineD](https://www.cined.com/bbc-gives-away-16000-sound-effects-for-free/)

**Epidemic Sound (SFX + music)**
- 2026 prices (secondary, conflicting): Creator about $9.99/month annually or $17.99 monthly. Pro about $16.99/month annually or $39.99 monthly. Business about $30/month. Creator covers one monetized channel per platform with no ads or client work. Pro covers three channels per platform plus ads and client work — [photutorial Epidemic pricing](https://photutorial.com/epidemic-sound-pricing/); [frontdeskreview Epidemic](https://frontdeskreview.com/software/music-licensing/epidemic-sound/)
- Content published while subscribed stays cleared indefinitely. Using the music in content published after the subscription ends leads to claims. Tracks downloaded during a free trial are only cleared during the trial — [Epidemic Sound: license music legally](https://www.epidemicsound.com/how-it-works/license-music-legally/)
- Channels must be linked in account settings to be whitelisted against Epidemic's own Content ID claims — [Epidemic Help: Why was a Content ID claim received from Epidemic Sound?](https://www.epidemicsoundhelp.com/hc/en-us/articles/26253712691730-Why-was-a-Content-ID-claim-received-from-Epidemic-Sound); [lesfm Epidemic pricing guide](https://lesfm.net/blog/epidemic-sound-pricing/)

**Kenney / 99Sounds**
- Kenney sound packs are CC0, and credit is not mandatory (OpenGameArt mirrors of Kenney packs, e.g. "50 RPG sound effects", "51 UI sound effects") — [OpenGameArt: 50 RPG sound effects](https://opengameart.org/content/50-rpg-sound-effects); [OpenGameArt: 51 UI sound effects](https://opengameart.org/content/51-ui-sound-effects-buttons-switches-and-clicks)
- 99Sounds: "100% royalty-free… for both commercial and non-commercial use". Check the per-pack license page — [99Sounds About](https://99sounds.org/about/)

### Inferences
- A tiered recommendation for the skill: (1) YouTube Audio Library SFX, filtered to "Attribution not required" (strongest Content ID guarantee, but no API: the user browses Studio). (2) Mixkit and Pixabay SFX (no attribution, no API: the skill can give site search URLs). (3) Freesound CC0 via API, with real IDs and preview MP3 links. CC BY is allowed only with an auto-generated credit line in the description, and NC/Sampling+ are always excluded. (4) Kenney CC0 / Sonniss GDC packs as a local, pre-downloaded library the user already owns.
- Cube-turn sounds are best recorded by the user from his own cubes: zero licensing risk, and they match his actual puzzles. Freesound has user-uploaded Rubik's cube recordings, but each must be checked for CC0/CC BY.
- Since sound effects are ineligible as Content ID references under YouTube's rules, a claim on an SFX is more likely a mismatch or improper registration. These are disputable with license proof.

### Gaps
- YouTube's Audio Library has no public API, and its SFX-specific attribution rules were not separately documented beyond the general Audio Library page.
- Exact current Freesound search endpoint path (`/apiv2/search/text/` vs. any newer consolidated `/apiv2/search/`) and response field names were not verified from official docs this session.
- The official BBC RemArc licence text, the official Sonniss license text, and Kenney's own license page (kenney.nl) were not read directly.
- The official Zapsplat license agreement was only seen in excerpts.

## Q4. Music (for completeness / gaming channel) and how Content ID false claims happen and are disputed

### Takeaway
For music, only the YouTube Audio Library carries a platform-level promise of no Content ID claims. Subscription libraries (Epidemic, Artlist, Envato) prevent claims by linking the channel ("whitelist", "Clearlist", "Claim Clear"). Pixabay Music is free and legal, but its FAQ admits some contributors register tracks with Content ID, so claims happen and must be disputed with Pixabay's License Certificate. Uppbeat's free tier requires a credit link, and the safelist is for paid subscribers only. Disputes give the claimant 30 days. A wrong appeal can escalate to a takedown and a strike.

### Cited Findings
- Pixabay FAQ: some contributors or their distributors may register tracks with Content ID, which "can result in automated claims even when the track is used legally". A claim does not affect channel standing (unlike a takedown) — [Pixabay FAQ](https://pixabay.com/service/faq/)
- Pixabay's fix: dispute with the Pixabay License Certificate (link shown in the download pop-up or under the Download dropdown for logged-in users), or contact the track author to remove the claim. Until cleared, ads may run and the uploader can't monetize the video — [Pixabay blog: How to clear a YouTube Content ID claim with a Pixabay License Certificate](https://pixabay.com/blog/posts/how-to-clear-a-youtube-content-id-claim-with-a-pix-190/)
- Certificates are offered for tracks registered with Content ID. For other tracks, keep the download link, file name and license summary (secondary) — [Sonilo: Pixabay alternatives 2026](https://sonilo.com/blog/comparisons/pixabay-music-sound-effects-alternatives-2026)
- User anecdotes of Pixabay "free" music triggering claims (anecdotal) — [Trustpilot Pixabay reviews](https://ie.trustpilot.com/review/pixabay.com)
- Uppbeat: the Safelist "prevents copyright claims for Content on specified Safelisted Channels" (YouTube channel ID) and is a Paid Subscriber feature. Free-tier users must include an Uppbeat credit link (secondary) — [Uppbeat User Agreement](https://uppbeat.io/user-agreement); [licenseorg Uppbeat](https://licenseorg.com/guide/music-audio/uppbeat)
- Mixkit music (secondary): free for personal and commercial projects including YouTube, excluding CDs/DVDs, video games and TV/radio broadcast — [kripeshadwani Mixkit review](https://kripeshadwani.com/mixkit-review/)
- Why licensed media still gets claimed: Content ID matches files, not licenses. A clip or track can be licensed to you and still match if the creator, or someone else, registered it — [Coverr blog 2026](https://coverr.co/blog/no-copyright-stock-video-for-youtube); [Adobe blog: Adobe Stock audio and Content ID](https://blog.adobe.com/en/publish/2020/06/16/adobe-stock-audio-and-youtubes-content-id)
- Dispute process: the claimant has 30 days to respond, and the claim expires if they don't. The claimant can release, reinstate, or submit a copyright removal request, and a valid removal request means takedown plus a copyright strike. After reinstatement you may appeal, and the claimant then has 7 days. Disputing without a valid reason can lead to a removal request, and abuse can bring penalties — [YouTube Help: Dispute a Content ID claim](https://support.google.com/youtube/answer/2797454/dispute-a-content-id-claim?hl=en); [YouTube Help: Appeal a Content ID claim](https://support.google.com/youtube/answer/12104471?hl=en&co=GENIE.Platform%3DDesktop)
- If you dispute within 5 days, revenue is held from the day the claim was placed — [YouTube Help: Monetization during copyright claim disputes](https://support.google.com/youtube/answer/7000961)
- Removal options: trimming or removing the claimed segment releases the claim — [YouTube Help: Remove copyright-claimed content](https://support.google.com/youtube/answer/2902117?hl=en)
- Common best practice: upload as Unlisted first so claims appear before the video goes public — [Adobe blog](https://blog.adobe.com/en/publish/2020/06/16/adobe-stock-audio-content-id-claims); [Pond5 Help](https://www.pond5.com/help/en/articles/10086114-how-to-dispute-clear-a-youtube-content-id-claim); [Envato](https://elements.envato.com/learn/envato-music-without-copyright-strikes)

### Inferences
- For his gaming channel, the safest music workflow is the YouTube Audio Library ("Attribution not required") or a paid library with channel linking. Pixabay/Uppbeat-free tracks are "legal but claim-prone" and should be flagged as such by the skill.
- The skill should recommend an "upload Unlisted → wait for checks → publish" routine for every video. YouTube Studio's upload checks surface Content ID claims before publishing.

### Gaps
- No Reddit threads (r/NewTubers, r/PartneredYoutube, r/editors) were returned by search for 2023–2026 claim reports on Pixabay or stock footage, so community frequency data is missing.
- Whether Epidemic/Artlist offer any public API usable by a personal skill was not found. Epidemic's partner API status is unknown.

## Q5. Gaming footage rules (own gameplay; publisher video policies)

### Takeaway
Major publishers allow monetized gameplay videos of the creator's own footage, with conditions. Nintendo allows monetization only via listed platform programs (YouTube Partner Program is listed) and requires creative input or commentary. Epic explicitly allows ad-monetized YouTube videos. Mojang/Minecraft allows ad revenue from videos. Riot's "Legal Jibber Jabber" (2018) allows free fan projects but bars logos and trademarks without a license and requires a non-endorsement disclaimer. All of these permissions are revocable.

### Cited Findings
- Nintendo Game Content Guidelines (latest revision found: 2 Sept 2024): monetization only through Nintendo-specified methods. The list includes YouTube's Partner Program, Twitch, X, Niconico, Instagram and others, and is "subject to updates". Uploads must include creative input or commentary, and re-uploading footage without editorial input is prohibited. Selling videos, music or images made with Nintendo content is not allowed. The 2024 update added Nintendo's right to object to infringing content and to bar repeat offenders — [Nintendo Game Content Guidelines](https://www.nintendo.co.jp/networkservice_guideline/en/index.html); [Mondaq summary](https://webiis08.mondaq.com/india/copyright/1523144/nintendo-content-sharing-guidelines); [Siliconera](https://siliconera.com/nintendo-updates-its-online-media-sharing-guidelines); [diff of 2023→2024 versions](https://www.diffchecker.com/7agWeGoE)
- Epic Games Fan Content Policy: "Individual fans are permitted to monetize web videos (such as YouTube) with advertisements, so long as those videos otherwise meet the requirements of this Policy". Epic can revoke permission at any time. No implied endorsement. Content must fit the spirit and tone of the IP. The Fortnite Developer Terms allow Epic-created assets in gameplay videos — [Epic Fan Content Policy](https://legal.epicgames.com/epicgames/fan-art-policy); [Fortnite Developer Terms](https://legal.epicgames.com/fortnite/developer-terms)
- Minecraft (Mojang): ad revenue from Minecraft videos is allowed. Selling Minecraft content or charging for access is not. The permission is revocable (third-party summary of the Minecraft Usage Guidelines) — [ConductAtlas: Minecraft video monetization carve-out](https://conductatlas.com/platform/minecraft/minecraft-usage-guidelines/video-content-monetization-carve-out/)
- Riot "Legal Jibber Jabber" (Aug 2018): supports free fan projects, but you may not use Riot logos or trademarks in any video without a written license, and must include a disclaimer that Riot doesn't endorse the project. Riot can shut projects down. The policy does not explicitly address YouTube ad revenue — [Riot Games Legal](https://www.riotgames.com/en/legal); [riotgames.com/legal-jibber-jabber](https://riotgames.com/legal-jibber-jabber)
- Content ID: gameplay footage from anyone other than the publisher is not eligible as a reference. Original game soundtracks are valid references only when owned by the publisher — [YouTube Help: Content eligible for Content ID](https://support.google.com/youtube/answer/2605065?hl=en)

### Inferences
- The main Content ID risk in gaming videos is in-game licensed music (soundtracks owned by publishers or labels, radio stations in games), not the visuals. The skill should suggest muting or replacing licensed in-game music tracks and keeping game SFX.
- Trailers and press-kit footage are the publisher's copyrighted material. Their use is governed by each press kit's terms, which were not researched here, so the skill should treat them as "permission or fair-use commentary only".

### Gaps
- Official Mojang Minecraft Usage Guidelines text, current Riot guidance specific to YouTube monetization, and publisher press-kit terms (trailers, key art) were not retrieved.
- Whether Nintendo's guidelines were revised after Sept 2024 (2025–2026) was not found. The search found no newer revision.

## Q6. Cubing-specific footage sources (WCA, brand press kits, CC-licensed YouTube videos, Wikimedia)

### Takeaway
No WCA media-licensing policy for third-party reuse of competition footage was found. Competition filming notices grant rights to the organizers, WCA and partners only, so WCA or competitor footage needs permission from whoever filmed it. Spin Master's Rubik's brand guide restricts use of the RUBIK'S name to genuine products and claims protection for the cube's appearance in some countries. No GAN or MoYu press or media kit was found. YouTube's Creative Commons (CC BY) videos can be found via the search filter or the Data API (`videoLicense=creativeCommon`, `type=video`), but each video's license and underlying content must be checked.

### Cited Findings
- WCA/organizer filming notices: e.g. NAC 2024 says attendees "may be photographed and recorded for media to be used in any format for any purpose worldwide in perpetuity by CubingUSA, the WCA, and their partners and representatives". A 2026 WCA competition in Mexico has a similar notice for the organizing association — [WCA NAC2024 registration](https://www.worldcubeassociation.org/competitions/NAC2024/register); [WCA Cubo Laberinto 2026](https://www.worldcubeassociation.org/competitions/CuboLaberinto2026/results/podiums); [CubingUSA NAC 2026 policies](https://cubingusa.org/nac/2026/policies)
- WCA media submissions: "you must own it and must give the WCA permission to post it" — [WCA media submission](https://worldcubeassociation.org/media-instagram)
- A 2014 Bay Area competition with TV filming required signed releases (parental signatures for minors) and called the Rubik's Cube image "a protected image" — [CubingUSA archive BASC4](https://archive.cubingusa.org/basc4)
- Rubik's brand guide (Spin Master): "The RUBIK'S® trademark can only be used in connection with original RUBIK'S® brand products manufactured or licensed by Spin Master". Use generic terms such as "puzzle cube" or "magic cube" for other brands. The cube's appearance (3×3×3 shape, black grid, six colours and sequence) "enjoys protection in several countries" — [Rubik's brand & trademark use guide](https://www.rubiks.com/brand-use-guide)
- EU legal status is mixed: the CJEU held in 2016 that the cube shape was not a valid trademark, and a June 2026 report says the owners failed to stop an Italian sofa company using a cube image in its trademark — [World IP Review](https://www.worldipreview.com/news/rubik-s-cube-shape-not-a-trademark-says-cjeu-12546); [Law360 (June 2026)](https://www.law360.co.uk/articles/2490048)
- Stock agencies have refused cube imagery from contributors on IP grounds (community report), which may limit stock cube footage — [Adobe Community: Rubik's Cube IP refusal](https://community.adobe.com/t5/stock-contributors-discussions/rubik-s-cube-intellectual-property-refusal/m-p/12691111/highlight/true)
- No GAN media kit was found. GAN's site has brand story and community pages only. Wikipedia notes past IP allegations against GAN — [GAN story](https://gancube.com/about); [GAN community](https://gancube.com/pages/community); [Wikipedia: Gancube](https://en.wikipedia.org/wiki/Gancube)
- YouTube CC BY: uploaders can choose CC BY or the Standard YouTube License. A video with a Content ID claim can't be marked CC BY. Reusers should credit the title, author, source URL and license (overlay, voiceover or description). Royalty-free or CC content can be monetized when the license grants commercial rights — [YouTube Help: License types on YouTube](https://support.google.com/youtube/answer/2797468?hl=en); [YouTube Help: What kind of content can I monetize?](https://support.google.com/youtube/answer/2490020?hl=en)
- Finding CC videos: Filters → Features → Creative Commons. The license notice appears under "Show more". The filter can return incorrect results, so double-check each video — [Butler libguide](https://libguides.butler.edu/findmedia/videos); [HCC library](https://www.hcc.edu/library/build-your-oer-course/find-oer/oer-videos/youtube)
- Data API: `search.list` with `videoLicense=creativeCommon` requires `type=video`, otherwise you get `invalidSearchFilter`. `videos.list` exposes `status.license` (`creativeCommon` | `youtube`) — [YouTube Data API: Search list](https://developers.google.com/youtube/v3/docs/search/list); [YouTube Data API: Videos](https://developers.google.com/youtube/data/reference/rest/v3/videos)
- Quota: the default project allocation is described as 10,000 units/day, and `search.list` has commonly been costed at 100 units (Google pages show conflicting wording; verify) — [YouTube Data API: Determine quota cost](https://developers.google.com/youtube/v3/determine_quota_cost); [YouTube Data API Overview](https://developers.google.com/youtube/v3/getting-started)

### Inferences
- For a speedcubing channel the best B-roll is self-shot (hands solving, cube close-ups, timer screens) plus generic stock (brains, puzzles, clocks, competition-like crowds) from Pexels, Pixabay or Coverr. Stock "Rubik's cube" clips exist but carry trademark considerations. In the video's Arabic narration or titles he should use the brand name only when the cube really is a Rubik's/Spin Master product.
- WCA competition footage from other channels should be treated as all-rights-reserved unless the uploader marked it CC BY on YouTube or gave written permission. The skill can query the Data API with `videoLicense=creativeCommon` for "speedcubing"/"WCA" and then verify `status.license` per video.

### Gaps
- No official WCA policy on third-party reuse of WCA livestreams or official videos was found, nor the license of the WCA YouTube channel's uploads.
- No official GAN, MoYu, QiYi or Rubik's/Spin Master press or media kit with licensing terms was found.
- The volume of cube-specific clips on Pexels/Pixabay could not be checked (sites unreachable this session).

## Q7. Fair use limits for commentary and how Content ID treats short clips (risk summary, not legal advice)

### Takeaway
There is no "safe number of seconds". Content ID can match very short excerpts (reports of about 5 seconds of music) and does not evaluate fair use. A fair-use dispute is possible, but if the claimant files a takedown it can end in a strike. For a creator who wants zero strikes, the practical rule is to avoid third-party copyrighted clips and music entirely, and use licensed, own, or CC0/CC BY material.

### Cited Findings
- Fair use is a four-factor test with no automatic rules such as "8 seconds is safe". Content ID does not evaluate fair use — [EFF: tool removes copyrighted works, not a substitute for fair use](https://www.eff.org/deeplinks/2020/01/tool-removes-copyrighted-works-not-substitute-fair-use)
- Excerpts of songs as short as 5 seconds can get a video flagged or taken down. YouTube's policies sit in "a legal gray area" — [Berklee: Fair Play — Asserting fair use in the age of Content ID](https://www.berklee.edu/node/2538351)
- In 2016 YouTube changed policy so revenue is held during disputes rather than going to the claimant — [Tubefilter 2016](https://www.tubefilter.com/2016/04/28/youtube-content-id-policy-change/); [YouTube Help: Monetization during disputes](https://support.google.com/youtube/answer/7000961)
- A rejected dispute or appeal can lead to a copyright removal request and a strike. YouTube warns against disputing without a valid reason — [YouTube Help: Dispute a Content ID claim](https://support.google.com/youtube/answer/2797454/dispute-a-content-id-claim?hl=en)

### Inferences
- The skill should never suggest third-party copyrighted clips (TV, other YouTubers, game trailers, songs) "because it's short". It can mention fair-use commentary only as a deliberate, user-made decision outside the skill's default safe list.

### Gaps
- No recent (2025–2026) empirical data on Content ID match thresholds for video-only stock clips was found.

## Q8. Best practice for logging licenses (proof to keep)

### Takeaway
Save your own record at download time, even when the platform keeps a history: platform, asset ID, page URL, creator, exact license name and version, a snapshot of the license text, download date, file name and hash, plus any certificate or receipt. Then map each asset to the video(s) it was used in, so a Content ID dispute can be filed in minutes.

### Cited Findings
- Store your own copy of the license and related information at download time (platform, title, author, source URL, exact license name and terms), even if the provider keeps a download history — [Michigan Tech: Best practices for stock photography documentation (Feb 2026)](https://blogs.mtu.edu/webmaster/2026/02/best-practices-for-responsible-stock-photography-documentation/)
- Keep invoices, licenses and project records. Higher-tier uses may need a campaign or usage record — [Spencer West: stock footage licensing mistake](https://www.spencer-west.com/?p=7794); [Storyblocks: 5 licensing questions (PDF, Dec 2025)](https://sb-wp-assets.storyblocks.com/resources/wp-content/uploads/2025/12/05124726/5-licensing-questions-every-business-should-ask-a-stock-provider.pdf)
- Platform-specific proof: Pixabay License Certificate (text file) for registered tracks. Envato license certificate from the downloads page. Pond5 item ID plus license. Adobe Stock License History screenshot (file ID, date, license type) — [Pixabay blog](https://pixabay.com/blog/posts/how-to-clear-a-youtube-content-id-claim-with-a-pix-190/); [Envato certificate](https://help.elements.envato.com/hc/en-us/articles/360000621443-Envato-item-license-certificate); [Pond5 Help](https://www.pond5.com/help/en/articles/10086114-how-to-dispute-clear-a-youtube-content-id-claim); [Adobe Community](https://community.adobe.com/questions-32/help-stock-license-proof-1497136)
- Audio Library disputes: evidence such as a screenshot of the track and the download date is recommended (secondary) — [foximusic YouTube Audio Library guide 2026](https://www.foximusic.com/blog/?p=546)
- Artlist asks for the track link, a viewable non-private video URL and a screenshot of the claim when handling third-party claims — [Artlist Help](https://help.artlist.io/hc/en-us/articles/29648852943901-Understanding-copyright-and-Content-ID-claims)

### Inferences
- Suggested log schema for the skill (one row per asset, e.g. CSV/JSON next to the Resolve project): `asset_id, platform, page_url, creator, creator_url, license_name, license_url, license_snapshot_path, attribution_text (if any), download_date (ISO), approved_by_user (y/n + date), local_file_path, sha256, video_title/id, timecode_in_video, certificate_path`. Save a PDF or HTML snapshot of the license page on the download date, because terms change (e.g. Pixabay 2019 CC0 → Pixabay License, Videvo Standard → legacy, Mixkit terms revised Oct 2025).

### Gaps
- No official YouTube guidance specifying which identifiers to include in a dispute for stock footage was found.

## Q9. Which APIs let a script search and return preview URLs/thumbnails for user approval before download

### Takeaway
Free, keyed APIs that return IDs, page URLs and preview or thumbnail links suitable for a "propose first, download only after OK" workflow: **Pexels** (video), **Pixabay** (video), **Coverr** (video; also an official MCP server), **Freesound** (SFX, with license filter and preview MP3s), **Openverse** (CC audio; images), **Wikimedia Commons** (MediaWiki API, per-file license metadata), **Internet Archive** (Advanced Search) and the **YouTube Data API** (CC BY video discovery). Paid: **Adobe Stock** (search API with key) and **Shutterstock** (no video on the free tier). Storyblocks is enterprise-only. Mixkit, YouTube Audio Library, Epidemic, Artlist, Envato and Uppbeat: no public API found, so the skill should give browse/search URLs.

### Cited Findings
- Pexels: free key, 200/h and 20k/month, link-back and credit guideline for API use — [Pexels API docs](https://www.pexels.com/api/documentation/)
- Pixabay: free key, 100 req/60 s, show users the source, cache 24 h — [Pixabay API docs](https://pixabay.com/api/docs/); [rubydoc pixabay_api](https://www.rubydoc.info/gems/pixabay_api/0.0.1)
- Coverr: free key at coverr.co/developers, 50/h in Demo and 2,000/h in Production, MCP server at mcp.coverr.co — [Coverr API auth](https://api.coverr.co/docs/auth); [Coverr MCP](https://api.coverr.co/docs/mcp/)
- Freesound: token auth for search and previews, 60/min and 2,000/day, license filter, `preview-hq-mp3` — [Freesound API overview](https://freesound.org/docs/api/overview.html); [Jentic Freesound](https://jentic.com/apis/freesound.org/freesound.md)
- Openverse: anonymous or OAuth2, `/audio` with license and category filters, records include an attribution string — [Jentic Openverse](https://jentic.com/apis/openverse)
- Wikimedia Commons: keyless MediaWiki API, `filetype:video`, `extmetadata` license fields, User-Agent required — [Phabricator T151352](https://phabricator.wikimedia.org/T151352); [Openverse handbook: Wikimedia provider](https://make.wordpress.org/openverse/handbook/openverse-catalog/provider-api-wikimedia-commons/)
- Internet Archive: keyless Advanced Search with `mediatype` and `licenseurl` filters — [Apify archive-org-scraper](https://apify.com/lulzasaur/archive-org-scraper)
- YouTube Data API: `search.list?type=video&videoLicense=creativeCommon` — [YouTube Data API search.list](https://developers.google.com/youtube/v3/docs/search/list)
- Adobe Stock: Developer Console API key, search without enterprise account, licensing needs credits — [Adobe Stock API docs](https://developer.adobe.com/stock/docs/getting-started)
- Shutterstock: free test account has 0 videos and 100 req/h — [Shutterstock API pricing](https://code.shutterstock.com/api/pricing)
- Storyblocks: API only in quote-only Enterprise — [frontdeskreview Storyblocks](https://frontdeskreview.com/software/stock-media/storyblocks/)

### Inferences
- Summary matrix (from the findings above; "Safe" = monetized-YouTube OK under the stated license):

| Source | Type | Monetized OK | Attribution in video | Content ID risk | API for search + preview | Cost |
|---|---|---|---|---|---|---|
| Pexels | Video | Yes | No (API UI should link to Pexels and credit the creator) | Low (no audio) | Yes, free key, 200/h | Free |
| Pixabay | Video, SFX, music | Yes | No | Video low; music/SFX medium (contributor registration) | Yes for video (images too); no audio API found | Free |
| Coverr | Video | Yes | No | Low | Yes, free key, 50→2,000/h, MCP server | Free (+Premium) |
| Mixkit | Video, SFX, music | Yes | No | Low (registration forbidden by license) | None found | Free |
| Videvo | Video | Per clip | Often yes (Attribution License) | Varies | None found | Free/paid |
| Vidsplay / Dareful / Mazwai / Life of Vids | Video | Reported yes | Vidsplay yes; Dareful CC 4.0; Mazwai conflicting | Low | None found | Free |
| Wikimedia Commons | Video, audio | Only CC0/PD/BY/BY-SA files | Yes for BY/BY-SA | Low | Yes, keyless | Free |
| Internet Archive | Video, audio | Only PD/CC0/BY items | Per item | Varies | Yes, keyless | Free |
| NASA | Video | Yes (no endorsement, no logos) | Not required (credit customary) | Low | NASA image/video library (not verified this session) | Free |
| YouTube Audio Library | SFX, music | Yes (YPP) | Only CC tracks | None for copyright-safe items (per YouTube) | No | Free |
| Freesound | SFX | CC0 and CC BY only; NC not OK | CC BY yes | Low (SFX ineligible as CID refs) | Yes, token, 60/min, 2,000/day | Free |
| Zapsplat | SFX | Yes | Free tier yes; Gold no | Low | None found | Free / Gold |
| Kenney | SFX | Yes | No (CC0) | Very low | No (downloads) | Free |
| Sonniss GDC | SFX | Yes | No | Very low | No (bundle download) | Free |
| BBC RemArc | SFX | **No** (non-commercial; Pro Sound Effects license needed) | — | — | — | Paid for commercial |
| Epidemic Sound | SFX, music | Yes (linked channel) | No | Managed via channel link | No public API found | ~$10–17/mo annual |
| Artlist | Footage, SFX, music | Yes (Clearlist) | No | Managed via Clearlist | No public API found | ~$10–40/mo annual |
| Envato | Footage, SFX, music | Yes | No | Claim Clear for eligible music | No public API found | ~$16.50/mo annual |
| Storyblocks | Footage, audio | Yes (per plan) | No | Unknown | Enterprise only | ~$21–40/mo annual |
| Adobe Stock | Footage, audio | Yes (licensed) | No | Possible on audio | Yes (search key; licensing paid) | Credits |
| Shutterstock | Footage | Yes (licensed) | No | Possible | API, but free tier has 0 video | Paid |
| Uppbeat | Music, SFX | Yes | Free tier yes | Free tier claim-prone; paid safelist | None found | Free / paid |

- Recommended skill flow: search APIs (Pexels, Pixabay, Coverr for video; Freesound CC0/CC BY for SFX) → present ID, page URL, thumbnail/preview link, duration, creator, license and a suggested in-point → **no download until the user says OK** → on OK, download, log the license snapshot and hash, and generate the attribution line where required.

### Gaps
- NASA's media library API (images-api.nasa.gov) did not appear in results, so its endpoints and video support were not confirmed this session.
- Exact JSON field names for Pexels, Pixabay, Coverr and Freesound responses were not re-verified (pages unreachable). Confirm against live docs when implementing.
