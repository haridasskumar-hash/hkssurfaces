# SEO Changelog

## 1. Pages Modified
- Updated the shared static-page generator and regenerated Thai and English homepage, About, contact, product, project, service, certificate, blog-list and blog-article pages.
- Updated the hand-authored Thai and English privacy-policy pages with social metadata and language alternates.
- Added editable Thai and English homepage introduction fields to the existing admin homepage editor; existing save/export and image-upload workflows remain intact.
- Updated project content for the pickleball project to use four existing court photos with bilingual alt text.
- Updated site configuration, robots.txt and sitemap.xml.

## 2. Titles Changed
- Set the Thai homepage title to “พื้นสนามกีฬา พื้น EPDM และพื้นสนามเด็กเล่น | HKS Surfaces”.
- Added concise commercial SEO titles for the priority product pages in both languages, including EPDM, playground safety, pickleball, running track, basketball, tennis, padel, multi-sport, gym, artificial turf, EPDM/SBR granules, rubber tiles, epoxy, badminton and water-park EPDM.
- Kept visible page headings and visual layout unchanged except for adding missing H1 headings to four material-oriented product pages and older blog articles.

## 3. Meta Descriptions Added or Updated
- Added a natural Thai homepage description covering sports flooring, EPDM, playground and impact-absorbing rubber flooring, design/supply/installation, Bangkok and nationwide service. It is 151 characters.
- Kept product descriptions distinct and language-specific; generated public pages now consistently expose their descriptions in metadata.
- Added Open Graph title and description values from each page’s SEO metadata.

## 4. Structured Data Added
- Homepage: LocalBusiness with verified business name, phone, email, address and Thailand service area.
- Product details: Service and BreadcrumbList.
- Blog articles: BlogPosting and BreadcrumbList, with publication dates and article images only when supplied.
- EPDM Flooring and Pickleball Court Flooring: FAQPage data matching the visible FAQ text.
- Other generated section/list pages: BreadcrumbList where the page hierarchy is clear.

## 5. Internal Links Added
- Added contextual links between related EPDM, playground, water-play, granule and rubber-tile pages; between pickleball, padel and multi-sport pages; and between track/gym pages and relevant materials.
- Added relevant product links to blog articles.
- Replaced the nonexistent pickleball project thumbnail reference with existing project photos.

## 6. FAQ Sections Added
- EPDM Flooring: six visible bilingual questions covering definition, applications, outdoor use, thickness selection, maintenance and service coverage.
- Pickleball Court Flooring: four visible bilingual questions covering system choice, Acrylic vs. PU, outdoor courts and color options.
- FAQ structured data mirrors the visible answers.

## 7. Sitemap Changes
- Removed the duplicate homepage `/index.html` entry while retaining the root homepage URL.
- Kept the site’s existing `/index.html` route convention, privacy-policy trailing-slash routes, XML stylesheet, last-modified values and priorities.
- The final sitemap contains 64 unique HTTPS URLs. All resolve to public index pages; no admin or development routes are included.

## 8. robots.txt Changes
- Continued to allow crawling of public pages and assets.
- Added `Disallow: /admin/` for the editor area.
- Kept `Sitemap: https://www.hkssurfaces.com/sitemap.xml`.

## 9. Technical Problems Discovered
- The pickleball project referenced a missing SVG. Replaced it with four existing project photos and descriptive Thai/English alt text.
- Historical underwater blog source files referenced by blog data are absent. The generator now preserves the existing published article body when a legacy source is unavailable, instead of failing or replacing its images and content.
- The legacy-source fallback was appending its related-product links on every rebuild. It now removes the prior generated section before adding one; two consecutive builds leave exactly one section in each underwater article.
- Removed external citations [1], [2], [3], [4] and [5], plus NJ Feeling caption credits, from both underwater article languages while retaining the surrounding copy and images.
- Rich blog pages contained multi-megabyte base64 image data in their HTML. The builder now writes the exact image bytes to reusable files under `images/blog/`; generated underwater article HTML fell from about 6.5 MiB to 19–32 KiB, and padel article HTML from about 2.4 MiB to 14–22 KiB. The lead article image remains eager/high-priority; later images load lazily.
- Three internal padel source HTML files are marked noindex and canonicalize to their published localized article pages. They are not sitemap entries.

## 10. Manual Follow-Up
- Restore or migrate the missing underwater source HTML files if those articles need to be edited from source and regenerated; current published content is preserved as a fallback.
- After deployment, submit the sitemap in Google Search Console and check live indexing, rich-result eligibility and host redirects. Local checks cannot verify production HTTP responses or Google’s indexing decisions.
- The extracted article images total about 6.6 MiB and are now separately cached/lazy-loaded where appropriate; further image compression should be reviewed visually before changing image quality.
