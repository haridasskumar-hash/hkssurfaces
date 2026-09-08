HKS Surfaces SEO Website Final

Thai is the default language and is written directly into the HTML.
English pages are under /en/.

Easy edit files:
- products-data.json
- projects-data.json
- blog-data.json
- site-config.json

SEO included:
- Static crawlable HTML
- Separate Thai/English URLs
- hreflang
- canonical tags
- sitemap.xml
- robots.txt
- Organization/Breadcrumb/Article JSON-LD
- Dedicated product URLs
- Internal links
- Mobile responsive layout

IMPORTANT DOMAIN:
This version currently uses https://www.hkssurfaces.com. If this is not your final domain, replace it before launch so canonical/hreflang/sitemap URLs are correct.

IMPORTANT CONTACT:
Replace placeholders in site-config.json before publishing.

The enquiry form is visual only until connected to a form/email service.


BUSINESS ADDRESS
78/23 City Sense Village, Soi Watchrapol 2, Tharang, Bangkhen, Bangkok 10230, Thailand

BRAND LOGO
Supplied HKS Surfaces logo:
  /images/hks-surfaces-logo.png

FINAL DOMAIN
https://www.hkssurfaces.com

CONTACT DETAILS
Phone: 087 707 0280
International: +66 87 707 0280
Email: info@hkssurfaces.com


SEO
Thai pages are at the root. English pages are under /en/.
Canonical tags, hreflang, robots.txt and sitemap.xml use www.hkssurfaces.com.


REDESIGN
Homepage rebuilt to closely follow the approved reference image: dark blue contact bar, oversized circular logo, white navigation, photographic-style hero, right-side quotation form, six category cards, and navy statistics band.


LOCAL PREVIEW FIX
This version uses relative CSS, JavaScript, image and internal navigation paths.
You can now extract the ZIP and double-click index.html to preview the styled site locally.

HOSTING
The same relative paths also work when uploaded to the root of www.hkssurfaces.com.
Upload the CONTENTS of the extracted folder, not the parent folder itself.


ADMIN EDITOR
============
Open:
  admin/index.html

The editor has five sections:
- Main Page
- Products
- Projects
- Blog
- Site Settings

You can:
- Edit Thai and English text
- Add/edit/delete products
- Add/edit/delete projects
- Add/edit/delete blog posts
- Reorder products/projects/blog posts
- Change image paths
- Edit contact/site settings
- Preview homepage text
- Save working changes in the browser
- Export each updated JSON file
- Export one complete backup

IMPORTANT
This is a static website, so the editor cannot securely overwrite files on your web server by itself.
After exporting a JSON file, replace the matching file in the website folder.

For true one-click online Save/Publish from the admin interface, your web hosting needs a server-side CMS/API
(for example PHP, Node.js, or a hosted CMS). If your hosting supports PHP, HKS Surfaces can be upgraded to
a password-protected online editor that publishes directly.

SEO
The public website remains static/crawlable. Do not replace the public SEO pages with JavaScript-only rendering.


LOGO UPDATE
The website now uses the HKS Surfaces logo with a white background at /images/hks-surfaces-logo.png.


MULTIPLE PRODUCT IMAGE UPLOAD
=============================
In admin/index.html:
1. Open Products.
2. Click Edit on a product.
3. Use Upload Images and select one or many JPG/PNG/WebP/AVIF files.
4. Preview the images.
5. Reorder them with arrow controls.
6. Set one image as Primary.
7. Add Thai and English alt text.
8. Remove unwanted images.
9. Click Save Item.
10. Click Download Uploaded Images to download the newly selected image files.
11. Copy those files into /images/products/ in the website.
12. Export products-data.json and replace the old products-data.json.

The editor stores image filenames/paths in products-data.json, not large image binaries.
This keeps the website fast and avoids browser localStorage size limits.

SEO NOTE
Each product image now supports separate Thai and English alt text in the product data.
The public product pages remain static HTML for crawlability. After changing product galleries,
regenerate the static product pages so the new gallery images and alt text appear in crawlable HTML.


MAIN PAGE IMAGE EDITOR
======================
Open admin/index.html > Main Page.

You can now:
- Upload a new hero image
- Preview the hero image
- Set Thai and English hero alt text
- Upload multiple homepage gallery images
- Preview gallery images
- Reorder gallery images
- Remove images
- Mark one gallery image as Featured
- Add Thai and English alt text
- Download uploaded hero/gallery image files for publishing
- Export homepage-data.json

Publishing:
1. Download the uploaded images.
2. Put them in /images/home/ on the website.
3. Export homepage-data.json.
4. Replace the old homepage-data.json.
5. Regenerate/update the static homepage HTML so Google can crawl the new image URLs and alt text.


PRIVACY POLICY
Thai and English privacy-policy pages have been added and linked at the bottom/footer of public pages. Both URLs are included in sitemap.xml.

HOMEPAGE HERO IMAGE UPDATE
The uploaded playground + pickleball image is now the default homepage hero image:
images/home/hks-surfaces-playground-pickleball-hero.png

It is also set as the default Hero Image inside the Main Page Editor.
