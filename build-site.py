"""Build the public static pages from the content files exported by admin/."""
from html import escape
import base64
from hashlib import sha256
import json
import random
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).parent

SEO_PRODUCT_TITLES = {
	"playground-safety-flooring": ("พื้นสนามเด็กเล่น EPDM พื้นยางกันกระแทก | HKS Surfaces", "Playground EPDM Safety Flooring | HKS Surfaces"),
	"epdm-flooring": ("พื้น EPDM รับติดตั้งพื้นยางสนามเด็กเล่น | HKS Surfaces", "EPDM Rubber Flooring Installation | HKS Surfaces"),
	"pickleball-court-flooring": ("พื้นสนามพิคเคิลบอล ระบบ Acrylic และ PU | HKS Surfaces", "Pickleball Court Flooring, Acrylic & PU | HKS Surfaces"),
	"running-track-flooring": ("พื้นลู่วิ่งสนามกีฬา ระบบยางสังเคราะห์ | HKS Surfaces", "Synthetic Rubber Running Track Flooring | HKS Surfaces"),
	"basketball-court-flooring": ("พื้นสนามบาสเกตบอล สำหรับในร่มและกลางแจ้ง | HKS Surfaces", "Basketball Court Flooring Systems | HKS Surfaces"),
	"tennis-court-flooring": ("พื้นสนามเทนนิส ระบบพื้นกีฬา | HKS Surfaces", "Tennis Court Flooring Systems | HKS Surfaces"),
	"padel-court-flooring": ("พื้นสนามพาเดล ระบบหญ้าเทียม PU และ Acrylic | HKS Surfaces", "Padel Court Flooring, Turf, PU & Acrylic | HKS Surfaces"),
	"multi-sport-court-flooring": ("พื้นสนามกีฬาอเนกประสงค์ สำหรับหลายประเภทกีฬา | HKS Surfaces", "Multi-Sport Court Flooring Systems | HKS Surfaces"),
	"gym-flooring": ("พื้นฟิตเนสและยิม พื้นยางรองรับแรงกระแทก | HKS Surfaces", "Gym & Fitness Rubber Flooring | HKS Surfaces"),
	"artificial-turf": ("หญ้าเทียมสำหรับสนามกีฬาและพื้นที่ใช้งาน | HKS Surfaces", "Artificial Turf for Sports & Recreation | HKS Surfaces"),
	"epdm-granules": ("เม็ดยาง EPDM สำหรับพื้นสนามและพื้นนิรภัย | HKS Surfaces", "EPDM Rubber Granules for Sports & Safety Floors | HKS Surfaces"),
	"sbr-rubber-granules": ("เม็ดยาง SBR สำหรับพื้นยางรองรับแรงกระแทก | HKS Surfaces", "SBR Rubber Granules for Impact-Absorbing Floors | HKS Surfaces"),
	"rubber-safety-tiles": ("แผ่นยางนิรภัย พื้นสนามเด็กเล่นและพื้นที่กีฬา | HKS Surfaces", "Rubber Safety Tiles for Playgrounds & Sports | HKS Surfaces"),
	"epoxy-flooring": ("พื้นอีพ็อกซี่สำหรับอาคารพาณิชย์และอุตสาหกรรม | HKS Surfaces", "Epoxy Flooring for Commercial & Industrial Spaces | HKS Surfaces"),
	"badminton-court-flooring": ("พื้นสนามแบดมินตัน ระบบ PU และ Acrylic | HKS Surfaces", "Badminton Court Flooring, PU & Acrylic | HKS Surfaces"),
	"epdm-flooring-wet-area": ("พื้น EPDM สวนน้ำและ Splash Pad | HKS Surfaces", "EPDM Flooring for Water Parks & Splash Pads | HKS Surfaces"),
}


def read_json(name):
	with (ROOT / name).open(encoding="utf-8") as source:
		return json.load(source)


def text(value):
	return escape(str(value or ""))


def asset(path, prefix, fallback="images/hks-surfaces-logo.png"):
	value = (path or fallback).lstrip("/")
	if value.startswith(("http://", "https://", "data:")):
		return value
	if not value.startswith(("images/", "Project Images/")):
		value = f"images/{value}"
	return f"{prefix}{value}"


def write(path, content):
	target = ROOT / path
	target.parent.mkdir(parents=True, exist_ok=True)
	target.write_text(content, encoding="utf-8")


def build_admin_seed():
	path = ROOT / "admin/index.html"
	content = path.read_text(encoding="utf-8")
	seed_start = content.find("window.HKS_SEED=")
	seed_end = content.find(";</script>", seed_start)
	if seed_start < 0 or seed_end < 0:
		raise ValueError("Could not find the embedded admin seed in admin/index.html")
	seed = {
		"homepage": read_json("homepage-data.json"),
		"products": read_json("products-data.json"),
		"projects": read_json("projects-data.json"),
		"certificates": read_json("certificates-data.json"),
		"blogs": read_json("blog-data.json"),
		"settings": read_json("site-config.json"),
	}
	serialized = json.dumps(seed, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
	updated = content[:seed_start] + "window.HKS_SEED=" + serialized + content[seed_end:]
	if updated != content:
		write("admin/index.html", updated)


def build_sitemap(settings):
	namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
	old_entries = {}
	old_urls = []
	sitemap_path = ROOT / "sitemap.xml"
	if sitemap_path.exists():
		try:
			old_root = ET.parse(sitemap_path).getroot()
			for entry in old_root.findall(f"{{{namespace}}}url"):
				loc = entry.findtext(f"{{{namespace}}}loc") or ""
				old_urls.append(loc)
				key = loc.replace("/index.html", "/")
				old_entries[key] = [
					(child.tag.rsplit("}", 1)[-1], child.text or "")
					for child in entry if child.tag.rsplit("}", 1)[-1] != "loc"
				]
		except ET.ParseError:
			pass
	urls = []
	expected_urls = []
	for page in sorted(ROOT.rglob("index.html")):
		relative = page.relative_to(ROOT)
		if any(part in {"admin", ".venv", ".git", "__pycache__", "tests", "test"} for part in relative.parts):
			continue
		route = relative.as_posix()
		if route in ("privacy-policy/index.html", "en/privacy-policy/index.html"):
			route = route.removesuffix("index.html")
		url = page_url(route, settings)
		expected_urls.append(url)
		metadata = old_entries.get(url, [])
		children = f"<loc>{escape(url)}</loc>" + "".join(f"<{name}>{escape(value)}</{name}>" for name, value in metadata)
		urls.append(f"<url>{children}</url>")
	if len(old_urls) == len(expected_urls) and set(old_urls) == set(expected_urls):
		return
	content = "\n".join(urls)
	write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="{namespace}" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{content}\n</urlset>\n')


def nav(prefix, language, active, settings, products, show_quote=True):
	english = language == "en"
	labels = {
		"home": "Home" if english else "หน้าแรก",
		"about": "About Us" if english else "เกี่ยวกับเรา",
		"products": "Products" if english else "ผลิตภัณฑ์",
		"services": "Services" if english else "บริการ",
		"projects": "Projects" if english else "โครงการ",
		"certificates": "Certificate" if english else "ใบรับรองมาตรฐาน",
		"blog": "Blog" if english else "บทความ",
		"contact": "Contact Us" if english else "ติดต่อเรา",
	}
	base = "en/" if english else ""
	links = {
		"home": f"{prefix}{base}index.html",
		"about": f"{prefix}{base}about/index.html",
		"products": f"{prefix}{base}products/index.html",
		"services": f"{prefix}{base}services/index.html",
		"projects": f"{prefix}{base}projects/index.html",
		"certificates": f"{prefix}{base}certificates/index.html",
		"blog": f"{prefix}{base}blog/index.html",
		"contact": f"{prefix}{base}contact/index.html",
	}
	category_labels = {
		"safety": "Safety Flooring" if english else "พื้นนิรภัย",
		"sports": "Sports Flooring" if english else "พื้นสนามกีฬา",
		"materials": "Materials" if english else "วัสดุสำหรับระบบพื้น",
	}
	product_groups = "".join(
		f'<section class="product-menu-group"><h3>{category_labels.get(category, category.title())}</h3>'
		+ "".join(
			f'<a href="{prefix}{base}products/{text(product["slug"])}/index.html">{text(product.get("en" if english else "th"))}</a>'
			for product in products if product.get("cat") == category
		) + "</section>"
		for category in category_labels
	)
	product_menu = f'''<div class="nav-dropdown"><button class="nav-dropdown-toggle" type="button" aria-expanded="false">{labels['products']}<span aria-hidden="true">⌄</span></button><div class="product-menu"><a class="product-menu-all" href="{links['products']}">{"All Products" if english else "ดูผลิตภัณฑ์ทั้งหมด"}</a><div class="product-menu-groups">{product_groups}</div></div></div>'''
	service_items = [
		("Free Consultation & Quotation Request" if english else "ปรึกษาและขอใบเสนอราคาฟรี", "free-consultation"),
		("Transportation, Installation & Repair" if english else "ขนส่ง ติดตั้ง และซ่อมแซม", "transportation-installation-repair"),
		("Warranty & After-Sales Service" if english else "รับประกันและบริการหลังการขาย", "warranty-after-sales"),
	]
	service_menu = f'''<div class="nav-dropdown"><button class="nav-dropdown-toggle" type="button" aria-expanded="false">{labels['services']}<span aria-hidden="true">⌄</span></button><div class="product-menu service-menu">{"".join(f'<a href="{links["services"]}#{anchor}">{text(label)}</a>' for label, anchor in service_items)}</div></div>'''
	nav_links = "".join(
		product_menu if key == "products" else service_menu if key == "services" else f'<a class="{"active" if key == active else ""}" href="{url}">{labels[key]}</a>'
		for key, url in links.items()
	)
	phone = text(settings.get("phone_display", "087 707 0280"))
	email = text(settings.get("contact_email", "info@hkssurfaces.com"))
	language_link = f"{prefix}index.html" if english else f"{prefix}en/index.html"
	language_label = "TH" if english else "EN"
	mobile_language_link = f'<a class="mobile-language" href="{language_link}">{language_label}</a>'
	quote_button = f'<a class="quote-btn" href="{links["contact"]}">{"Request a Quote" if english else "ขอใบเสนอราคา"}</a>' if show_quote else ""
	return f'''<div class="topbar"><div class="container"><div class="left"><a href="tel:+66877070280">{phone}</a><a href="mailto:{email}">{email}</a></div><div class="right"><a href="{language_link}">{language_label}</a></div></div></div>
	<header class="mainnav"><div class="container"><a href="{links['home']}" class="logo-wrap"><img src="{asset(settings.get('logo'), prefix, 'images/hks-surfaces-logo.png')}" alt="HKS Surfaces"></a><a class="header-language" href="{language_link}" aria-label="Switch language">{language_label}</a><button class="menu" aria-label="Menu">☰</button><nav>{nav_links}{mobile_language_link}</nav>{quote_button}</div></header>'''


def footer(prefix, language, settings):
	contact = "Contact Us" if language == "en" else "ติดต่อเรา"
	privacy = "Privacy Policy" if language == "en" else "นโยบายความเป็นส่วนตัว"
	social_label = "Follow us" if language == "en" else "ติดตามเรา"
	quick_links = "Quick Links" if language == "en" else "ลิงก์ด่วน"
	products = "Products" if language == "en" else "ผลิตภัณฑ์"
	blog = "Blog" if language == "en" else "บทความ"
	services = "Services" if language == "en" else "บริการ"
	base = "en/" if language == "en" else ""
	return f'''<footer class="site-footer"><div class="container footer-grid"><div><img src="{asset(settings.get('logo'), prefix, 'images/hks-surfaces-logo.png')}" alt="HKS Surfaces" style="width:120px;border-radius:50%"></div><div><h3>{text(settings.get('site_name', 'HKS Surfaces'))}</h3><p><strong>{"Head Office" if language == "en" else "สำนักงานใหญ่"}</strong><br><address>{text(settings.get('business_address'))}</address></p></div><div><h3>{quick_links}</h3><nav class="footer-quick-links"><a href="{prefix}{base}products/index.html">{products}</a><a href="{prefix}{base}blog/index.html">{blog}</a><a href="{prefix}{base}services/index.html">{services}</a><a href="{prefix}{'en/' if language == 'en' else ''}privacy-policy/index.html">{privacy}</a></nav></div><div><h3>{contact}</h3><p><a href="tel:+66877070280">{text(settings.get('phone_display', '087 707 0280'))}</a><br><a href="mailto:{text(settings.get('contact_email'))}">{text(settings.get('contact_email'))}</a></p><div class="social-links" aria-label="{social_label}"><a href="https://www.facebook.com/hkssurfaces" target="_blank" rel="noopener noreferrer" aria-label="Facebook"><i class="bi bi-facebook"></i></a><a href="https://www.youtube.com/@hkssurfaces" target="_blank" rel="noopener noreferrer" aria-label="YouTube"><i class="bi bi-youtube"></i></a><a href="https://www.instagram.com/hkssurfaces" target="_blank" rel="noopener noreferrer" aria-label="Instagram"><i class="bi bi-instagram"></i></a><a href="https://line.me/ti/p/Rn_AsnrLLf" target="_blank" rel="noopener noreferrer" aria-label="LINE"><i class="bi bi-line"></i></a><a href="https://x.com/hkssurfaces" target="_blank" rel="noopener noreferrer" aria-label="X"><i class="bi bi-twitter-x"></i></a><a href="https://www.threads.com/@hkssurfaces" target="_blank" rel="noopener noreferrer" aria-label="Threads"><i class="bi bi-threads"></i></a></div></div></div></footer>'''


def page_url(route_path, settings):
	base_url = settings.get("site_url", "https://www.hkssurfaces.com").rstrip("/")
	path = route_path.lstrip("/")
	if path in ("", "index.html"):
		return f"{base_url}/"
	return f"{base_url}/{path}"


def absolute_asset_url(path, settings):
	base_url = settings.get("site_url", "https://www.hkssurfaces.com").rstrip("/")
	value = (path or settings.get("logo") or "/images/hks-surfaces-logo.png").lstrip("/")
	return value if value.startswith(("http://", "https://", "data:")) else f"{base_url}/{value}"


def breadcrumb_schema(items, settings):
	return {
		"@type": "BreadcrumbList",
		"itemListElement": [
			{"@type": "ListItem", "position": index, "name": name, "item": page_url(route, settings)}
			for index, (name, route) in enumerate(items, start=1)
		],
	}


def homepage_schema(settings):
	return {
		"@context": "https://schema.org",
		"@type": "LocalBusiness",
		"name": "HKS Surfaces",
		"url": page_url("index.html", settings),
		"telephone": "+66877070280",
		"email": settings.get("contact_email", "info@hkssurfaces.com"),
		"address": {
			"@type": "PostalAddress",
			"streetAddress": settings.get("business_address", "78/23 City Sense Village, Soi Watchrapol 2, Tharang, Bangkhen, Bangkok 10230, Thailand"),
			"addressCountry": "TH",
		},
		"areaServed": {"@type": "Country", "name": "Thailand"},
	}


def localized_route(route_path, language):
	path = route_path.strip("/")
	if language == "en":
		path = path.removeprefix("en/")
		return f"en/{path}" if path != "index.html" else "en/index.html"
	return path.removeprefix("en/") or "index.html"


def document(title, description, prefix, language, active, body, settings, products, route_path, show_quote=True, meta_title=None, meta_description=None, og_image=None, schema=None, page_type="website"):
	canonical = page_url(route_path, settings)
	thai_url = page_url(localized_route(route_path, "th"), settings)
	english_url = page_url(localized_route(route_path, "en"), settings)
	title_text = meta_title or f"{title} | HKS Surfaces"
	description_text = meta_description or description
	image_url = absolute_asset_url(og_image, settings)
	metadata = f'''<title>{text(title_text)}</title><meta name="description" content="{text(description_text)}"><meta name="robots" content="index,follow"><link rel="canonical" href="{text(canonical)}"><link rel="alternate" hreflang="th" href="{text(thai_url)}"><link rel="alternate" hreflang="en" href="{text(english_url)}"><link rel="alternate" hreflang="x-default" href="{text(thai_url)}"><meta property="og:type" content="{text(page_type)}"><meta property="og:site_name" content="HKS Surfaces"><meta property="og:title" content="{text(title_text)}"><meta property="og:description" content="{text(description_text)}"><meta property="og:url" content="{text(canonical)}"><meta property="og:image" content="{text(image_url)}">'''
	if schema:
		schema_json = json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c")
		metadata += f'<script type="application/ld+json">{schema_json}</script>'
	elif active != "home":
		home_label = "Home" if language == "en" else "หน้าแรก"
		schema_json = json.dumps({
			"@context": "https://schema.org",
			**breadcrumb_schema([(home_label, localized_route("index.html", language)), (title, route_path)], settings),
		}, ensure_ascii=False).replace("<", "\\u003c")
		metadata += f'<script type="application/ld+json">{schema_json}</script>'
	body_class = ' class="homepage"' if active == "home" else ' class="internal-page"'
	return f'''<!doctype html><html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{metadata}<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"><link rel="stylesheet" href="{prefix}assets/styles.css"><link rel="icon" href="{prefix}images/hks-surfaces-logo.png"></head><body{body_class}>{nav(prefix, language, active, settings, products, show_quote)}{body}{footer(prefix, language, settings)}<script src="{prefix}assets/site.js"></script></body></html>'''


def hero(title, description, eyebrow):
	eyebrow_markup = f'<div class="eyebrow">{text(eyebrow)}</div>' if eyebrow else ""
	return f'<section class="page-hero"><div class="container">{eyebrow_markup}<h1>{text(title)}</h1><p>{text(description)}</p></div></section>'


def product_image(product, prefix, language=None):
	images = product.get(f"images_{language}") if language else None
	images = images or product.get("images") or []
	primary = next((image for image in images if image.get("primary")), images[0] if images else {})
	return asset(primary.get("file") or product.get("image"), prefix)


def product_detail_images(product, prefix, alt, language):
	images = product.get(f"images_{language}") or product.get("images") or [{"file": product.get("image")}]
	primary = next((image for image in images if image.get("primary")), images[0])
	ordered_images = [primary] + [image for image in images if image is not primary]
	result = []
	for image in ordered_images:
		loading = ' loading="eager" fetchpriority="high"' if image is primary else ' loading="lazy"'
		image_alt = image.get(f"alt_{language}") or alt
		result.append(f'<img src="{asset(image.get("file"), prefix)}" alt="{text(image_alt)}"{loading}>')
	return "".join(result)


def product_detail_sections(product, language, start=0, end=None):
	sections = []
	product_sections = product.get(f"detail_sections_{language}", product.get("detail_sections", []))[start:end]
	for section in product_sections:
		paragraphs = "".join(f"<p>{text(paragraph)}</p>" for paragraph in section.get("paragraphs", []))
		items = "".join(f"<li>{text(item)}</li>" for item in section.get("list", []))
		list_title = section.get("list_title")
		list_html = f'<h3>{text(list_title)}</h3>' if list_title else ""
		list_html += f'<ul class="feature-list">{items}</ul>' if items else ""
		subsections = "".join(f'<h3>{text(item.get("title"))}</h3><p>{text(item.get("text"))}</p>' for item in section.get("sections", []))
		rows = "".join(
			f"<tr><th>{text(row[0])}</th>{''.join(f'<td>{text(value)}</td>' for value in row[1:])}</tr>"
			for row in section.get("specifications", []) if row
		)
		table = f'<table><tbody>{rows}</tbody></table>' if rows else ""
		sections.append(f'<section class="article"><h2>{text(section.get("heading"))}</h2>{paragraphs}{list_html}{subsections}{table}</section>')
	return "".join(sections)


def product_faqs(slug, language):
	faqs = {
		"epdm-flooring": {
			"th": [
				("พื้น EPDM คืออะไร?", "พื้นยางแบบเทในที่ที่ใช้เม็ดยาง EPDM เป็นชั้นผิว โดยเลือกระบบฐานและสารยึดประสานให้เหมาะกับโครงการ"),
				("พื้น EPDM เหมาะกับพื้นที่แบบไหน?", "นิยมใช้กับสนามเด็กเล่น พื้นที่นันทนาการ ทางเดิน และพื้นที่กลางแจ้งที่ต้องการพื้นผิวยืดหยุ่นและออกแบบสีได้"),
				("พื้น EPDM ใช้กลางแจ้งได้หรือไม่?", "ใช้ได้เมื่อเลือกวัสดุ เตรียมฐาน และออกแบบการระบายน้ำให้เหมาะกับสภาพหน้างานและคำแนะนำผู้ผลิต"),
				("ความหนาของพื้น EPDM ควรเท่าไร?", "ไม่มีความหนาเดียวที่เหมาะกับทุกงาน ต้องพิจารณาการใช้งาน ฐานรองรับ และข้อกำหนดด้านแรงกระแทกของโครงการ"),
				("พื้น EPDM ดูแลรักษาอย่างไร?", "กวาดเศษฝุ่น ล้างตามคำแนะนำผู้ผลิต และตรวจสอบขอบพื้น จุดระบายน้ำ และบริเวณที่ใช้งานหนักเป็นระยะ"),
				("HKS Surfaces รับติดตั้งต่างจังหวัดหรือไม่?", "HKS Surfaces ให้บริการโครงการในกรุงเทพฯ และจังหวัดต่าง ๆ ทั่วประเทศไทย โดยขอบเขตงานขึ้นอยู่กับรายละเอียดโครงการ"),
			],
			"en": [
				("What is EPDM flooring?", "A poured-in-place rubber surface with EPDM granules as the wearing layer, specified with a suitable base and compatible binder."),
				("Where is EPDM flooring used?", "It is commonly used for playgrounds, recreation areas, walkways and outdoor spaces needing a resilient, colour-customizable finish."),
				("Can EPDM flooring be used outdoors?", "Yes, when the materials, substrate preparation and drainage are selected for the site and manufacturer guidance."),
				("How thick should EPDM flooring be?", "There is no single thickness for every project. Selection depends on use, substrate and any impact-performance requirements."),
				("How should EPDM flooring be maintained?", "Remove debris, clean according to the manufacturer’s guidance, and periodically inspect edges, drains and high-use areas."),
				("Does HKS Surfaces install outside Bangkok?", "HKS Surfaces supports projects in Bangkok and throughout Thailand; scope is confirmed for each project."),
			],
		},
		"pickleball-court-flooring": {
			"th": [
				("พื้นสนามพิคเคิลบอลควรใช้ระบบอะไร?", "ควรเลือกระบบให้เหมาะกับสนามในร่มหรือกลางแจ้ง สภาพพื้นฐาน การระบายน้ำ และระดับการใช้งาน โดยมีระบบ Acrylic และ PU ให้พิจารณาตามโครงการ"),
				("Acrylic กับ PU ต่างกันอย่างไร?", "Acrylic ให้ผิวสนามที่แน่นและตอบสนองรวดเร็ว ส่วน PU เป็นระบบยืดหยุ่นแบบไร้รอยต่อที่เน้นความสบายและการรองรับแรงกระแทก ทั้งนี้ขึ้นกับโครงสร้างระบบที่เลือก"),
				("สนามพิคเคิลบอลกลางแจ้งใช้พื้นอะไร?", "ระบบ Acrylic เป็นตัวเลือกสำหรับสนามกลางแจ้งได้ เมื่อฐาน การระบายน้ำ และวัสดุเหมาะกับสภาพอากาศและหน้างาน"),
				("สามารถปรับสีสนามได้หรือไม่?", "สามารถวางแผนสีและเส้นสนามให้เหมาะกับแนวทางออกแบบและความต้องการของโครงการได้"),
			],
			"en": [
				("Which surface system suits a pickleball court?", "Choose for indoor or outdoor use, the existing base, drainage and expected play. Acrylic and PU options can be assessed for the project."),
				("How do Acrylic and PU differ?", "Acrylic provides a firmer, responsive surface; PU is a resilient seamless system focused on comfort and impact absorption. Performance depends on the selected build-up."),
				("What flooring works for an outdoor pickleball court?", "Acrylic can suit outdoor courts when the base, drainage and materials are appropriate for site conditions."),
				("Can court colours be customized?", "Court colours and line layouts can be planned to suit the project design and requirements."),
			],
		},
	}
	return faqs.get(slug, {}).get(language, [])


def product_faq_markup(faqs, language):
	if not faqs:
		return "", None
	title = "Frequently Asked Questions" if language == "en" else "คำถามที่พบบ่อย"
	markup = f'<section class="article"><h2>{title}</h2>' + "".join(f"<h3>{text(question)}</h3><p>{text(answer)}</p>" for question, answer in faqs) + "</section>"
	schema = {
		"@type": "FAQPage",
		"mainEntity": [
			{"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": answer}}
			for question, answer in faqs
		],
	}
	return markup, schema


def related_products_markup(product, products, language, prefix):
	related = {
		"epdm-flooring": ["epdm-granules", "sbr-rubber-granules", "playground-safety-flooring", "epdm-flooring-wet-area", "rubber-safety-tiles"],
		"playground-safety-flooring": ["epdm-flooring", "epdm-flooring-wet-area", "rubber-safety-tiles"],
		"pickleball-court-flooring": ["indoor-sports-flooring", "multi-sport-court-flooring", "padel-court-flooring"],
		"padel-court-flooring": ["artificial-turf", "indoor-sports-flooring", "multi-sport-court-flooring"],
		"running-track-flooring": ["epdm-granules", "sbr-rubber-granules"],
		"gym-flooring": ["rubber-safety-tiles", "indoor-sports-flooring"],
	}.get(product.get("slug"), [])
	by_slug = {item.get("slug"): item for item in products}
	language_prefix = "en/" if language == "en" else ""
	links = [
		f'<a href="{prefix}{language_prefix}products/{text(slug)}/index.html">{text(by_slug[slug].get("en" if language == "en" else "th"))}</a>'
		for slug in related if slug in by_slug
	]
	if not links:
		return ""
	label = "Related surface systems" if language == "en" else "ระบบพื้นที่เกี่ยวข้อง"
	return f'<section class="article"><h2>{label}</h2><p>{" · ".join(links)}</p></section>'


def externalize_inline_images(content, slug, detail_prefix):
	pattern = re.compile(r'(?P<prefix>\bsrc=["\'])data:(?P<mime>image/[^;,]+);base64,(?P<data>[^"\']+)(?P<quote>["\'])', re.IGNORECASE)

	def replace_image(match):
		mime = match.group("mime").lower()
		extension = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "image/gif": "gif"}.get(mime)
		if not extension:
			return match.group(0)
		payload = match.group("data")
		image_bytes = base64.b64decode(payload)
		filename = f"{slug}-{sha256(image_bytes).hexdigest()[:16]}.{extension}"
		asset_path = ROOT / "images" / "blog" / filename
		if not asset_path.exists():
			asset_path.parent.mkdir(parents=True, exist_ok=True)
			asset_path.write_bytes(image_bytes)
		return f'{match.group("prefix")}{detail_prefix}images/blog/{filename}{match.group("quote")}'

	return pattern.sub(replace_image, content)


def remove_underwater_citations(content):
	for url in (
		"https://nofault.com/products/poured-in-place/water-play/",
		"https://njfeelingtrack.com/water-park-epdm-rubber-floor-surface/",
		"https://www.rubberecycle.com/aquabond",
		"https://fortco.ca/specs-waterparks/",
		"https://www.polycoatusa.com/product/aliphatic-binder-8000/",
	):
		pattern = re.compile(r'\s*<a\b(?=[^>]*\bhref=["\']' + re.escape(url) + r'["\'])[^>]*>\s*\[\d+\]\s*</a>', re.IGNORECASE)
		content = pattern.sub("", content)
	return re.sub(r"\s*(?:Source:|ที่มา:)\s*NJ Feeling\.?", "", content, flags=re.IGNORECASE)


def project_image(project, prefix):
	images = project.get("images") or []
	primary = next((image for image in images if image.get("primary")), images[0] if images else {})
	return asset(primary.get("file") or project.get("image"), prefix, "images/hks-surfaces-logo.png")


def contact_form(settings, english):
	first_number = random.randint(2, 9)
	second_number = random.randint(2, 9)
	math_answer = first_number + second_number
	math_label = f"What is {first_number} + {second_number}?" if english else f"กรุณาแก้โจทย์ {first_number} + {second_number}"
	return f'<form class="quote-card" id="contact" data-math-answer="{math_answer}"><h3>{"Request a Quote" if english else "ขอใบเสนอราคา"}</h3><input placeholder="{"Name" if english else "ชื่อ-นามสกุล"}"><input placeholder="{"Phone" if english else "เบอร์โทรศัพท์"}"><input placeholder="Email"><textarea rows="4" placeholder="{"Project details" if english else "รายละเอียดโครงการ"}"></textarea><label class="math-challenge" for="math-answer">{math_label}</label><input id="math-answer" class="math-answer" type="number" inputmode="numeric" autocomplete="off" required aria-describedby="math-help"><small id="math-help">{"Solve the question to enable Send Enquiry." if english else "แก้โจทย์ให้ถูกต้องเพื่อเปิดใช้งานปุ่มส่งข้อมูล"}</small><button class="btn green" type="button" disabled>{"Send Enquiry" if english else "ส่งข้อมูล"}</button></form>'


def build_homepage(homepage, products, settings, language):
	english = language == "en"
	prefix = "../" if english else ""
	title = homepage.get(f"hero_title_{language}")
	subtitle = homepage.get(f"hero_subtitle_{language}")
	description = homepage.get(f"hero_text_{language}")
	product_by_slug = {product.get("slug"): product for product in products}
	pickleball = product_by_slug.get("pickleball-court-flooring")
	epoxy = product_by_slug.get("epoxy-flooring")
	homepage_products = [
		(epoxy if product.get("slug") == "tennis-court-flooring" and epoxy else
		 pickleball if product.get("slug") == "epdm-flooring" and pickleball else product)
		for product in products[:6]
	]
	product_cards = "".join(
		f'<a class="cat-card" href="{prefix}{"en/" if english else ""}products/{text(product["slug"])}/index.html"><div class="cat-img" style="background-image:url(\'{product_image(product, prefix, language)}\')"></div><div class="cat-body"><h3>{text(product.get("en" if english else "th"))}</h3><small>{text(product.get("cat", "SURFACES")).upper()}</small><b>→</b></div></a>'
		for product in homepage_products
	)
	gallery = "".join(
		f'<a class="home-gallery-link" href="{prefix}{"en/" if english else ""}{text(image["link"])}" aria-label="{text(image.get("alt_en" if english else "alt_th"))}"><img src="{asset(image.get("file"), prefix)}" alt="{text(image.get("alt_en" if english else "alt_th"))}" loading="lazy"><span class="home-gallery-label">{text(image.get("label_en" if english else "label_th") or image.get("alt_en" if english else "alt_th"))}</span></a>'
		if image.get("link") else
		f'<img src="{asset(image.get("file"), prefix)}" alt="{text(image.get("alt_en" if english else "alt_th"))}" loading="lazy">'
		for image in homepage.get("gallery_images", [])
	)
	featured_title = "Our Featured Products" if english else "ผลิตภัณฑ์เด่นของเรา"
	featured_link = f'{prefix}{"en/" if english else ""}products/index.html'
	seo_intro = "".join(f"<p>{text(paragraph)}</p>" for paragraph in homepage.get(f"seo_intro_{language}", "").split("\n\n") if paragraph.strip())
	hero_images = [
		asset(homepage.get("hero_image"), prefix, "images/home/hks-surfaces-playground-pickleball-hero.png"),
		asset("Project Images/EPDM Flooring Project (1).jpg", prefix),
		asset("Project Images/Underwater EPDM (1).jpeg", prefix),
		asset("Project Images/Running Track Project 1.jpg", prefix),
		asset("images/projects/artificial-grass/Artificial Project.jpg", prefix),
		asset("Project Images/pickleball court.jpg", prefix),
	]
	hero_image_data = text(json.dumps(hero_images, ensure_ascii=True))
	body = f'''<main><section class="hero homepage-hero" data-hero-images="{hero_image_data}" style="background-image:url('{hero_images[0]}')"><div class="container"><div class="hero-copy"><h1>{text(title)}</h1><div class="hero-actions"><a class="btn green" href="{prefix}{'en/' if english else ''}products/index.html">{"Explore Products" if english else "ดูผลิตภัณฑ์ของเรา"} →</a><a class="btn outline" href="{prefix}{'en/' if english else ''}contact/index.html">{"Request a Quote" if english else "ขอใบเสนอราคา"} →</a></div></div></div></section><section class="category-strip"><div class="container"><div class="featured-intro"><h2>{text(subtitle)}</h2><p>{text(description)}</p></div><div class="featured-heading"><h2>{featured_title}</h2><a class="featured-link" href="{featured_link}">{"Learn More" if english else "ดูรายละเอียดเพิ่มเติม"} <span aria-hidden="true">→</span></a></div><div class="category-grid">{product_cards}</div></div></section><section class="section"><div class="container"><div class="section-head"><h2>{text(homepage.get(f'gallery_title_{language}'))}</h2></div><div class="home-gallery-grid">{gallery}</div></div></section><section class="section" id="about"><div class="container"><div class="section-head"><h2>{text(homepage.get(f'about_title_{language}'))}</h2><p>{text(homepage.get(f'about_text_{language}'))}</p>{seo_intro}</div></div></section></main>'''
	route_path = ("en/" if english else "") + "index.html"
	meta_title = "Sports Flooring, EPDM & Playground Flooring | HKS Surfaces" if english else "พื้นสนามกีฬา พื้น EPDM และพื้นสนามเด็กเล่น | HKS Surfaces"
	meta_description = description if english else "ออกแบบ จำหน่าย และติดตั้งพื้นสนามกีฬา พื้น EPDM พื้นสนามเด็กเล่น และพื้นยางกันกระแทก สำหรับโรงเรียน สโมสร และโครงการในกรุงเทพฯ พร้อมบริการทั่วประเทศไทย"
	write(route_path, document(title, description, prefix, language, "home", body, settings, products, route_path, meta_title=meta_title, meta_description=meta_description, og_image=homepage.get("hero_image"), schema=homepage_schema(settings)))


def build_contact(settings, products, language):
	english = language == "en"
	prefix = "../../" if english else "../"
	title = "Contact Us" if english else "ติดต่อเรา"
	description = "Tell us about your project and our team will help you choose the right surface system." if english else "บอกความต้องการของโครงการ แล้วทีมงานของเราจะช่วยแนะนำระบบพื้นที่เหมาะสม"
	contact_details = f'<div class="contact-details"><p><strong>{"Head Office" if english else "สำนักงานใหญ่"}</strong><br>{text(settings.get("business_address"))}</p><p class="hotline"><strong>{"Hotline" if english else "สายด่วน"}</strong><br><a href="tel:{text(settings.get("phone_href", "+66877070280"))}">{text(settings.get("phone_display", "087 707 0280"))}</a></p><p>Tel: {text(settings.get("office_phone", "+66 2 3636660-1"))}<br>Fax: {text(settings.get("office_fax", "+66 2 3636662"))}<br><a href="mailto:{text(settings.get("contact_email"))}">{text(settings.get("contact_email"))}</a><br><a href="https://line.me/ti/p/Rn_AsnrLLf" target="_blank" rel="noopener noreferrer"><i class="bi bi-line"></i> LINE</a></p></div>'
	body = hero(title, description, "HKS SURFACES") + f'<main class="section"><div class="container"><div class="contact-page-grid"><div class="contact-page-copy"><h2>{"Let’s discuss your project" if english else "พูดคุยเกี่ยวกับโครงการของคุณ"}</h2><p>{"Contact HKS Surfaces for product guidance, technical information, and a quotation tailored to your project." if english else "ติดต่อ HKS Surfaces เพื่อขอคำแนะนำผลิตภัณฑ์ ข้อมูลทางเทคนิค และใบเสนอราคาที่เหมาะกับโครงการของคุณ"}</p>{contact_details}</div>{contact_form(settings, english)}</div></div></main>'
	route_path = ("en/" if english else "") + "contact/index.html"
	write(route_path, document(title, description, prefix, language, "contact", body, settings, products, route_path))


def build_about(products, settings, language):
	english = language == "en"
	prefix = "../../" if english else "../"
	title = "About HKS Surfaces" if english else "เกี่ยวกับ HKS Surfaces"
	description = "Professional safety, sports and recreational surface solutions for projects throughout Thailand." if english else "ผู้เชี่ยวชาญด้านพื้นเพื่อความปลอดภัย พื้นสนามกีฬา และระบบพื้นสำหรับพื้นที่นันทนาการในประเทศไทย"
	intro_title = "Professional Flooring Solutions for Thailand" if english else "ผู้เชี่ยวชาญด้านพื้นสนามกีฬาและพื้นเพื่อความปลอดภัยในประเทศไทย"
	intro = "HKS Surfaces is a Thailand-based specialist in safety flooring, sports flooring and recreational surface solutions. We provide durable, practical and performance-focused flooring systems for playgrounds, sports facilities, schools, parks, commercial developments, hotels, resorts and public spaces." if english else "HKS Surfaces คือผู้เชี่ยวชาญด้านพื้นเพื่อความปลอดภัย พื้นสนามกีฬา และระบบพื้นสำหรับพื้นที่นันทนาการในประเทศไทย เรามุ่งเน้นการนำเสนอระบบพื้นที่มีคุณภาพ ทนทาน ใช้งานได้จริง และเหมาะสมกับลักษณะการใช้งานของแต่ละโครงการ"
	location = "Based in Bangkok, Thailand, we support projects from product selection and system recommendations through to supply and installation." if english else "เราตั้งอยู่ในกรุงเทพมหานคร ประเทศไทย พร้อมให้บริการตั้งแต่การให้คำปรึกษา การเลือกระบบพื้นและวัสดุที่เหมาะสม ไปจนถึงการจัดหาและติดตั้งสำหรับโครงการหลากหลายประเภท"
	solutions_title = "Our Solutions" if english else "ผลิตภัณฑ์และโซลูชันของเรา"
	solutions = [
		"Playground Safety Flooring" if english else "พื้นสนามเด็กเล่นเพื่อความปลอดภัย",
		"EPDM & SBR Rubber Granules" if english else "เม็ดยาง EPDM และ SBR",
		"Rubber Safety Tiles" if english else "แผ่นยางกันกระแทก",
		"Running Track Systems" if english else "พื้นลู่วิ่ง",
		"Basketball Courts" if english else "พื้นสนามบาสเกตบอล",
		"Pickleball Courts" if english else "พื้นสนามพิคเคิลบอล",
		"Padel Courts" if english else "พื้นสนามพาเดล",
		"Tennis Courts" if english else "พื้นสนามเทนนิส",
		"Badminton Courts" if english else "พื้นสนามแบดมินตัน",
		"Multi-Sport Courts" if english else "พื้นสนามกีฬาอเนกประสงค์",
		"Gym & Fitness Flooring" if english else "พื้นยางสำหรับยิมและฟิตเนส",
		"Artificial Grass" if english else "หญ้าเทียม",
		"Water Park & Splash Pad Flooring" if english else "พื้นสำหรับสวนน้ำและ Splash Pad",
		"Epoxy Flooring Systems" if english else "ระบบพื้นอีพ็อกซี่",
		"Aqua Fitness Solutions" if english else "โซลูชันอุปกรณ์ออกกำลังกายในน้ำ",
	]
	what_title = "What We Do" if english else "เราทำอะไร"
	what_text = "Every project has different requirements. HKS Surfaces works closely with developers, architects, contractors, schools, sports facilities, hotels, resorts and project owners to recommend suitable surface systems based on application, performance, durability, maintenance and budget." if english else "เราเข้าใจว่าแต่ละโครงการมีความต้องการที่แตกต่างกัน HKS Surfaces จึงทำงานร่วมกับเจ้าของโครงการ ผู้พัฒนาโครงการ สถาปนิก ผู้รับเหมา โรงเรียน ศูนย์กีฬา โรงแรม และรีสอร์ท เพื่อเลือกระบบพื้นที่เหมาะสม โดยพิจารณาจากประเภทการใช้งาน ประสิทธิภาพ ความทนทาน การบำรุงรักษา และงบประมาณ"
	what_text_2 = "Our focus is not simply on supplying flooring materials. We aim to provide a complete surface solution suited to the environment and intended use." if english else "เราไม่ได้มุ่งเน้นเพียงการจำหน่ายวัสดุปูพื้น แต่ให้ความสำคัญกับการนำเสนอโซลูชันระบบพื้นที่ครบถ้วน และเหมาะสมกับสภาพแวดล้อมและวัตถุประสงค์การใช้งานของแต่ละพื้นที่"
	why_title = "Why HKS Surfaces?" if english else "ทำไมต้องเลือก HKS Surfaces?"
	why_items = [
		("Specialized Solutions", "A focused range of flooring systems for sports, recreation, safety and commercial applications.", "ความเชี่ยวชาญด้านระบบพื้น", "เรามีโซลูชันสำหรับงานพื้นสนามกีฬา พื้นเพื่อความปลอดภัย พื้นนันทนาการ และพื้นสำหรับงานเชิงพาณิชย์"),
		("Project Support", "Technical guidance from surface selection and specification through to project implementation.", "การสนับสนุนโครงการ", "ให้คำแนะนำตั้งแต่การเลือกระบบพื้น การกำหนดรายละเอียดวัสดุ ไปจนถึงการดำเนินงานและติดตั้ง"),
		("Quality & Performance", "Products and systems selected with emphasis on durability, safety, functionality and long-term performance.", "คุณภาพและประสิทธิภาพ", "เราให้ความสำคัญกับคุณภาพ ความปลอดภัย ความทนทาน ประสิทธิภาพในการใช้งาน และอายุการใช้งานของระบบพื้น"),
		("Custom Solutions", "Colours, surface systems and configurations can be adapted to suit different project requirements and design concepts.", "ออกแบบให้เหมาะกับแต่ละโครงการ", "สามารถเลือกสี รูปแบบ และระบบพื้นให้เหมาะสมกับการใช้งาน แนวคิดการออกแบบ และความต้องการเฉพาะของแต่ละโครงการ"),
	]
	why_cards = "".join(f'<article class="content-card"><h3>{text(item[0] if english else item[2])}</h3><p>{text(item[1] if english else item[3])}</p></article>' for item in why_items)
	commitment_title = "Our Commitment" if english else "ความมุ่งมั่นของเรา"
	commitment = "At HKS Surfaces, our goal is to create surfaces that are safe, durable, functional and built for everyday use." if english else "ที่ HKS Surfaces เรามุ่งมั่นที่จะสร้างพื้นผิวที่ปลอดภัย ทนทาน ใช้งานได้จริง และพร้อมรองรับการใช้งานในระยะยาว"
	commitment_2 = "Whether it is a colourful EPDM playground, a professional sports court, a running track, a gym or a commercial flooring project, we work to provide the right surface solution for every space." if english else "ไม่ว่าจะเป็นสนามเด็กเล่น EPDM ที่มีสีสัน สนามกีฬา ลู่วิ่ง พื้นยิม หรือระบบพื้นสำหรับโครงการเชิงพาณิชย์ เราพร้อมนำเสนอโซลูชันพื้นที่เหมาะสมสำหรับทุกพื้นที่"
	hero_description = "Sports flooring, safety surfacing and material solutions for projects throughout Thailand." if english else "โซลูชันพื้นสนามกีฬา พื้นเพื่อความปลอดภัย และวัสดุสำหรับโครงการทั่วประเทศไทย"
	body = hero(title, hero_description, "HKS SURFACES") + f'''<main class="section about-page"><div class="container"><section class="about-intro"><h2>{text(intro_title)}</h2><p>{text(intro)}</p><p>{text(location)}</p></section><section class="about-block"><h2>{text(solutions_title)}</h2><ul class="feature-list about-solutions">{"".join(f"<li>{text(item)}</li>" for item in solutions)}</ul></section><section class="about-block"><h2>{text(what_title)}</h2><p>{text(what_text)}</p><p>{text(what_text_2)}</p></section><section class="about-block"><h2>{text(why_title)}</h2><div class="content-grid">{why_cards}</div></section><section class="about-commitment"><h2>{text(commitment_title)}</h2><p>{text(commitment)}</p><p>{text(commitment_2)}</p><strong>HKS Surfaces</strong><em>Safety • Sports • Performance Surfaces</em></section></div></main>'''
	route_path = ("en/" if english else "") + "about/index.html"
	write(route_path, document(title, description, prefix, language, "about", body, settings, products, route_path))


def build_products(products, settings, language):
	english = language == "en"
	prefix = "../../" if english else "../"
	title = "Products & Surface Systems" if english else "ผลิตภัณฑ์และระบบพื้น"
	description = "Safety, sports, and specialty surface systems." if english else "ระบบพื้นนิรภัย พื้นสนามกีฬา และวัสดุสำหรับงานพื้น"
	ordered_products = sorted(products, key=lambda product: product.get("slug", ""))
	category_labels = {
		"safety": "Safety Flooring" if english else "พื้นนิรภัย",
		"sports": "Sports Flooring" if english else "พื้นสนามกีฬา",
		"materials": "Materials" if english else "วัสดุสำหรับระบบพื้น",
	}
	category_sections = "".join(
		f'<section class="product-category"><h2>{category_labels[category]}</h2><div class="grid-3">' + "".join(
			f'<a class="card" href="{text(product["slug"])}/index.html"><div class="media" style="background-image:url(\'{product_image(product, prefix, language)}\')"></div><div class="card-body"><h2>{text(product.get("en" if english else "th"))}</h2><p>{text(product.get("den" if english else "dth"))}</p></div></a>'
			for product in ordered_products if product.get("cat") == category
		) + "</div></section>"
		for category in ("safety", "sports", "materials")
	)
	body = hero(title, description, "PRODUCTS & SYSTEMS") + f'<main class="section"><div class="container">{category_sections}</div></main>'
	root = ("en/" if english else "") + "products/index.html"
	write(root, document(title, description, prefix, language, "products", body, settings, products, root))
	for product in products:
		detail_prefix = "../../../" if english else "../../"
		product_title = product.get("en" if english else "th")
		product_description = product.get("den" if english else "dth")
		features = product.get("fen" if english else "fth", [])
		feature_list = "".join(f"<li>{text(feature)}</li>" for feature in features)
		extra_content = product_detail_sections(product, language)
		is_epdm_granules = product.get("slug") == "epdm-granules"
		is_epdm_flooring = product.get("slug") == "epdm-flooring"
		is_sbr_granules = product.get("slug") == "sbr-rubber-granules"
		is_running_track = product.get("slug") == "running-track-flooring"
		is_pu_binder = product.get("slug") == "polyurethane-binder"
		is_basketball = product.get("slug") == "basketball-court-flooring"
		is_padel = product.get("slug") == "padel-court-flooring"
		is_pickleball = product.get("slug") == "pickleball-court-flooring"
		is_badminton = product.get("slug") == "badminton-court-flooring"
		is_rubber_tiles = product.get("slug") == "rubber-safety-tiles"
		is_indoor_sports = product.get("slug") == "indoor-sports-flooring"
		is_interlocking_tiles = product.get("slug") == "interlocking-tiles-sport-flooring"
		is_gym = product.get("slug") == "gym-flooring"
		is_wet_area_epdm = product.get("slug") == "epdm-flooring-wet-area"
		is_multi_sport = product.get("slug") == "multi-sport-court-flooring"
		is_tennis = product.get("slug") == "tennis-court-flooring"
		is_epoxy = product.get("slug") == "epoxy-flooring"
		is_artificial_turf = product.get("slug") == "artificial-turf"
		is_playground_safety = product.get("slug") == "playground-safety-flooring"
		uses_image_first_layout = is_epdm_granules or is_sbr_granules or is_running_track or is_pu_binder
		right_column_content = product_detail_sections(product, language, 0, 2) if is_epdm_granules else ""
		below_content = product_detail_sections(product, language, 2) if is_epdm_granules else extra_content
		layout_class = "product-layout product-layout--image-first" if uses_image_first_layout else "product-layout"
		layout_class += " product-layout--basketball" if is_basketball else ""
		layout_class += " product-layout--padel" if is_padel else ""
		layout_class += " product-layout--pickleball" if is_pickleball else ""
		layout_class += " product-layout--badminton" if is_badminton else ""
		layout_class += " product-layout--rubber-tiles" if is_rubber_tiles else ""
		layout_class += " product-layout--rubber-tiles" if is_indoor_sports else ""
		layout_class += " product-layout--rubber-tiles" if is_interlocking_tiles else ""
		layout_class += " product-layout--gym" if is_gym else ""
		layout_class += " product-layout--wet-area-epdm" if is_wet_area_epdm else ""
		layout_class += " product-layout--multi-sport" if is_multi_sport else ""
		layout_class += " product-layout--tennis" if is_tennis else ""
		layout_class += " product-layout--epoxy" if is_epoxy else ""
		layout_class += " product-layout--artificial-turf" if is_artificial_turf else ""
		layout_class += " product-layout--playground-safety" if is_playground_safety else ""
		layout_class += " product-layout--rubber-tiles" if is_epdm_flooring else ""
		image_stack_class = "product-image-stack product-image-stack--epdm-granules" if is_epdm_granules else "product-image-stack"
		image_stack_class += " product-image-stack--epdm-flooring" if is_epdm_flooring else ""
		image_stack_class += " product-image-stack--running-track" if is_running_track else ""
		contact_prefix = "en/" if english else ""
		cta_label = "Request a Quote" if english else "ขอใบเสนอราคา"
		feature_heading = "Key features" if english else "จุดเด่น"
		category = text(product.get("cat"))
		detail_images = product_detail_images(product, detail_prefix, product_title, language)
		selected_images = product.get(f"images_{language}") or product.get("images") or []
		primary_image = next((image for image in selected_images if image.get("primary")), selected_images[0] if selected_images else {})
		og_image = primary_image.get("file") or product.get("image")
		quote_cta = "" if is_basketball or is_padel or is_pickleball else f'<a class="btn green" href="{detail_prefix}{contact_prefix}contact/index.html">{cta_label}</a>'
		intro_content = right_column_content if is_epdm_granules else f'<span class="pill">{category}</span><h2>{text(product_title)}</h2><p>{text(product_description)}</p><h3>{feature_heading}</h3><ul class="feature-list">{feature_list}</ul>{quote_cta}{right_column_content}'
		hero_content = "" if uses_image_first_layout else hero(product_title, product_description, "HKS SURFACES")
		intro_column = "" if is_epdm_flooring or is_sbr_granules or is_running_track or is_pu_binder or is_basketball or is_padel or is_pickleball or is_badminton or is_rubber_tiles or is_indoor_sports or is_interlocking_tiles or is_gym or is_wet_area_epdm or is_multi_sport or is_tennis or is_epoxy or is_artificial_turf or is_playground_safety else f'<div>{intro_content}</div>'
		details_class = ""
		path = ("en/" if english else "") + f'products/{product["slug"]}/index.html'
		faq_markup, faq_schema = product_faq_markup(product_faqs(product.get("slug"), language), language)
		related_markup = related_products_markup(product, products, language, detail_prefix)
		detail_heading = f'<h1 class="product-detail-title">{text(product_title)}</h1>' if uses_image_first_layout else ""
		detail = hero_content + f'<main class="section"><div class="container">{detail_heading}<div class="{layout_class}"><div class="{image_stack_class}">{detail_images}</div>{intro_column}</div><div class="{details_class}">{below_content}</div>{faq_markup}{related_markup}</div></main>'
		seo_title = SEO_PRODUCT_TITLES.get(product.get("slug"), (f"{product_title} | HKS Surfaces", f"{product_title} | HKS Surfaces"))[1 if english else 0]
		breadcrumb = breadcrumb_schema([
			("Home" if english else "หน้าแรก", "en/index.html" if english else "index.html"),
			("Products" if english else "ผลิตภัณฑ์", "en/products/index.html" if english else "products/index.html"),
			(product_title, path),
		], settings)
		service = {"@type": "Service", "name": product_title, "description": product_description, "provider": {"@type": "Organization", "name": "HKS Surfaces", "url": page_url("index.html", settings)}, "areaServed": {"@type": "Country", "name": "Thailand"}}
		graph = {"@context": "https://schema.org", "@graph": [service, breadcrumb] + ([faq_schema] if faq_schema else [])}
		write(path, document(product_title, product_description, detail_prefix, language, "products", detail, settings, products, path, show_quote=not (is_padel or is_pickleball), meta_title=seo_title, og_image=og_image, schema=graph))


def build_projects(projects, products, settings, language):
	english = language == "en"
	prefix = "../../" if english else "../"
	title = "Our Projects" if english else "โครงการของเรา"
	description = "Examples of HKS Surfaces installations." if english else "ผลงานระบบพื้นนิรภัย พื้น EPDM และพื้นสนามกีฬา"
	cards = []
	for project in projects:
		location = project.get("loc_en" if english else "loc_th") or ""
		category = project.get("category") or project.get("cat") or ""
		meta = text(" | ".join(filter(None, [str(category), str(project.get("year") or ""), str(location)])))
		project_title = text(project.get("title_en" if english else "title_th"))
		project_description = text(project.get("desc_en" if english else "desc_th"))
		image = project_image(project, prefix)
		project_images = project.get("images") or []
		gallery = "".join(
			f'<img class="project-image-trigger" src="{asset(item.get("file"), prefix)}" data-lightbox-group="{text(project_title)}" data-lightbox-src="{asset(item.get("file"), prefix)}" alt="{text(item.get("alt_en" if english else "alt_th") or project_title)}" loading="lazy">'
			for item in project_images[1:]
		)
		gallery_markup = f'<div class="image-gallery project-gallery">{gallery}</div>' if gallery else ""
		project_id = text(project.get("slug"))
		cards.append(f'<article class="card" id="{project_id}"><div class="media project-image-trigger" role="button" tabindex="0" data-lightbox-group="{project_title}" data-lightbox-src="{image}" aria-label="{project_title}" style="background-image:url(\'{image}\')"></div><div class="card-body"><span class="pill">{meta}</span><h2>{project_title}</h2><p>{project_description}</p>{gallery_markup}</div></article>')
	cards = "".join(cards)
	body = hero(title, description, "OUR PROJECTS") + f'<main class="section"><div class="container"><div class="grid-3">{cards}</div></div></main>'
	route_path = ("en/" if english else "") + "projects/index.html"
	write(route_path, document(title, description, prefix, language, "projects", body, settings, products, route_path))


def build_services(products, settings, language):
	english = language == "en"
	prefix = "../../" if english else "../"
	title = "Services" if english else "บริการของเรา"
	description = "From planning through after-sales support, our team is ready to help." if english else "ให้บริการตั้งแต่การวางแผน ติดตั้ง จนถึงการดูแลหลังการขาย"
	items = [
		("free-consultation", "Free Consultation & Quotation Request", "Receive practical guidance and a quotation tailored to your project requirements.", "ปรึกษาและขอใบเสนอราคาฟรี", "รับคำแนะนำและใบเสนอราคาที่เหมาะสมกับความต้องการของโครงการของคุณ"),
		("transportation-installation-repair", "Transportation, Installation & Repair", "Transportation, installation and repair are carried out by our skilled technician team.", "ขนส่ง ติดตั้ง และซ่อมแซม", "บริการขนส่ง ติดตั้ง และซ่อมแซม โดยทีมช่างผู้ชำนาญ"),
		("warranty-after-sales", "Warranty & After-Sales Service", "We provide warranty coverage and responsive after-sales service to keep your surface performing well.", "รับประกันและบริการหลังการขาย", "รับประกันสินค้าและดูแลหลังการขาย เพื่อให้ระบบพื้นของคุณใช้งานได้อย่างมั่นใจ"),
	]
	cards = "".join(f'<article class="content-card" id="{anchor}"><span class="pill">{index + 1:02d}</span><h3>{text(en_title if english else th_title)}</h3><p>{text(en_text if english else th_text)}</p></article>' for index, (anchor, en_title, en_text, th_title, th_text) in enumerate(items))
	body = hero(title, description, "HKS SURFACES") + f'<main class="section"><div class="container"><div class="content-grid">{cards}</div></div></main>'
	route_path = ("en/" if english else "") + "services/index.html"
	write(route_path, document(title, description, prefix, language, "services", body, settings, products, route_path))


def build_certificates(certificates, products, settings, language):
	english = language == "en"
	prefix = "../../" if english else "../"
	title = certificates.get(f"title_{language}")
	description = certificates.get(f"description_{language}")
	intro = certificates.get(f"intro_{language}")
	cards = "".join(f'<article class="content-card"><h3>{text(item.get(f"title_{language}"))}</h3><p>{text(item.get(f"text_{language}"))}</p></article>' for item in certificates.get("items", []))
	body = hero(title, description, "HKS SURFACES") + f'<main class="section"><div class="container"><div class="section-head"><h2>{text(title)}</h2><p>{text(intro)}</p></div><div class="content-grid">{cards}</div></div></main>'
	route_path = ("en/" if english else "") + "certificates/index.html"
	write(route_path, document(title, description, prefix, language, "certificates", body, settings, products, route_path))


def build_blogs(blogs, products, settings, language):
	english = language == "en"
	prefix = "../../" if english else "../"
	title = "Blog & Knowledge" if english else "บทความและความรู้"
	description = "Guidance on safety and sports surface systems." if english else "ข้อมูลเกี่ยวกับพื้น EPDM พื้นสนามเด็กเล่น และพื้นสนามกีฬา"
	cards = "".join(f'<a class="card" href="{text(blog.get("path_en" if english else "path_th") or f"{blog["slug"]}/index.html")}"><div class="media" style="background-image:url(\'{asset(blog.get("image"), prefix)}\')"></div><div class="card-body"><span class="meta">{text(blog.get("date"))}</span><h2>{text(blog.get("title_en" if english else "title_th"))}</h2><p>{text(blog.get("excerpt_en" if english else "excerpt_th"))}</p></div></a>' for blog in blogs)
	body = hero(title, description, "BLOG & KNOWLEDGE") + f'<main class="section"><div class="container"><div class="grid-3">{cards}</div></div></main>'
	route_path = ("en/" if english else "") + "blog/index.html"
	write(route_path, document(title, description, prefix, language, "blog", body, settings, products, route_path))
	for blog in blogs:
		detail_prefix = "../../../" if english else "../../"
		blog_title = blog.get("title_en" if english else "title_th")
		source = blog.get("source_en" if english else "source_th")
		path = ("en/" if english else "") + f'blog/{blog["slug"]}/index.html'
		preserved_main = ""
		if source:
			source_path = ROOT / source
			if source_path.exists():
				raw_article = source_path.read_text(encoding="utf-8")
				article_start = raw_article.find("<article")
				article_tag_end = raw_article.find(">", article_start)
				article_end = raw_article.rfind("</article>")
				article = raw_article[article_tag_end + 1:article_end] if article_start >= 0 and article_tag_end > article_start and article_end > article_tag_end else ""
				article = article[:article.rfind("<footer>")] if "<footer>" in article else article
			else:
				existing_path = ROOT / path
				previous = existing_path.read_text(encoding="utf-8") if existing_path.exists() else ""
				main_start = previous.find("<main")
				main_end = previous.rfind("</main>")
				preserved_main = previous[main_start:main_end + len("</main>")] if main_start >= 0 and main_end > main_start else ""
				article = ""
		else:
			sections = blog.get("body_en" if english else "body_th", [])
			article = "".join(f"<h2>{text(section[0])}</h2><p>{text(section[1])}</p>" for section in sections if len(section) > 1)
		if blog.get("slug") == "underwater-epdm":
			article = remove_underwater_citations(article)
			preserved_main = remove_underwater_citations(preserved_main)
		if article:
			article = externalize_inline_images(article, blog["slug"], detail_prefix)
		if preserved_main:
			preserved_main = externalize_inline_images(preserved_main, blog["slug"], detail_prefix)
		image_index = 0
		def add_image_loading(match):
			nonlocal image_index
			image_index += 1
			tag = match.group(0)
			closing = "/>" if tag.endswith("/>") else ">"
			opening = tag[:-len(closing)]
			loading = ' loading="eager"' if image_index == 1 else ' loading="lazy"'
			if re.search(r"\bloading\s*=", opening, re.IGNORECASE):
				opening = re.sub(r"\sloading\s*=\s*([\"']).*?\1", loading, opening, count=1, flags=re.IGNORECASE)
			else:
				opening += loading
			if image_index == 1:
				if re.search(r"\bfetchpriority\s*=", opening, re.IGNORECASE):
					opening = re.sub(r"\sfetchpriority\s*=\s*([\"']).*?\1", ' fetchpriority="high"', opening, count=1, flags=re.IGNORECASE)
				else:
					opening += ' fetchpriority="high"'
			return opening + closing
		if article:
			article = re.sub(r"<img\b[^>]*>", add_image_loading, article, flags=re.IGNORECASE)
		if preserved_main:
			preserved_main = re.sub(r"<img\b[^>]*>", add_image_loading, preserved_main, flags=re.IGNORECASE)
		if not article and not preserved_main:
			sections = blog.get("body_en" if english else "body_th", [])
			article = "".join(f"<h2>{text(section[0])}</h2><p>{text(section[1])}</p>" for section in sections if len(section) > 1)
		if article and "<h1" not in article.lower():
			article = f"<h1>{text(blog_title)}</h1>" + article
		if preserved_main and "<h1" not in preserved_main.lower():
			main_open_end = preserved_main.find(">") + 1
			meta_end = preserved_main.find("</div>", main_open_end)
			insert_at = meta_end + len("</div>") if preserved_main.find('class="meta"', main_open_end, meta_end) >= 0 else main_open_end
			preserved_main = preserved_main[:insert_at] + f"<h1>{text(blog_title)}</h1>" + preserved_main[insert_at:]
		related_slugs = {
			"what-is-epdm-flooring": ["epdm-flooring", "epdm-granules"],
			"how-to-choose-pickleball-court-flooring": ["pickleball-court-flooring", "multi-sport-court-flooring"],
			"underwater-epdm": ["epdm-flooring-wet-area", "epdm-flooring"],
			"hks-padel-court-systems-branded": ["padel-court-flooring", "artificial-turf"],
		}.get(blog.get("slug"), [])
		product_by_slug = {product.get("slug"): product for product in products}
		language_prefix = "en/" if english else ""
		related_links = [
			f'<a href="{detail_prefix}{language_prefix}products/{text(slug)}/index.html">{text(product_by_slug[slug].get("en" if english else "th"))}</a>'
			for slug in related_slugs if slug in product_by_slug
		]
		if related_links:
			related_title = "Related HKS Surfaces systems" if english else "ระบบพื้นของ HKS Surfaces ที่เกี่ยวข้อง"
			related_markup = f'<!-- seo-related-products --><section class="article"><h2>{related_title}</h2><p>{" · ".join(related_links)}</p></section>'
			if preserved_main:
				related_pattern = re.compile(r'(?:<!-- seo-related-products -->)?<section class="article"><h2>' + re.escape(related_title) + r"</h2>.*?</section>", re.DOTALL)
				preserved_main = related_pattern.sub("", preserved_main)
				preserved_main = preserved_main.replace("</main>", related_markup + "</main>")
			else:
				article += related_markup
		body = preserved_main or f'<main class="section"><article class="article"><div class="meta">{text(blog.get("date"))}</div>{article}</article></main>'
		image_url = absolute_asset_url(blog.get("image"), settings)
		breadcrumb = breadcrumb_schema([
			("Home" if english else "หน้าแรก", "en/index.html" if english else "index.html"),
			("Blog" if english else "บทความ", "en/blog/index.html" if english else "blog/index.html"),
			(blog_title, path),
		], settings)
		article_schema = {
			"@type": "BlogPosting",
			"headline": blog_title,
			"description": blog.get("excerpt_en" if english else "excerpt_th"),
			"datePublished": blog.get("date"),
			"dateModified": blog.get("date"),
			"author": {"@type": "Organization", "name": "HKS Surfaces"},
			"publisher": {"@type": "Organization", "name": "HKS Surfaces", "logo": {"@type": "ImageObject", "url": absolute_asset_url(settings.get("logo"), settings)}},
			"mainEntityOfPage": page_url(path, settings),
		}
		if blog.get("image"):
			article_schema["image"] = image_url
		graph = {"@context": "https://schema.org", "@graph": [article_schema, breadcrumb]}
		write(path, document(blog_title, blog.get("excerpt_en" if english else "excerpt_th"), detail_prefix, language, "blog", body, settings, products, path, og_image=blog.get("image"), schema=graph, page_type="article"))


def main():
	build_admin_seed()
	homepage = read_json("homepage-data.json")
	products = read_json("products-data.json")
	projects = read_json("projects-data.json")
	blogs = read_json("blog-data.json")
	certificates = read_json("certificates-data.json")
	settings = read_json("site-config.json")
	for language in ("th", "en"):
		build_homepage(homepage, products, settings, language)
		build_contact(settings, products, language)
		build_about(products, settings, language)
		build_products(products, settings, language)
		build_services(products, settings, language)
		build_projects(projects, products, settings, language)
		build_certificates(certificates, products, settings, language)
		build_blogs(blogs, products, settings, language)
	build_sitemap(settings)
	print("Built public pages from JSON content files.")


if __name__ == "__main__":
	main()
