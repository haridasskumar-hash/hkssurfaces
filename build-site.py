"""Build the public static pages from the content files exported by admin/."""
from html import escape
import json
from pathlib import Path


ROOT = Path(__file__).parent


def read_json(name):
	with (ROOT / name).open(encoding="utf-8") as source:
		return json.load(source)


def text(value):
	return escape(str(value or ""))


def asset(path, prefix, fallback="images/sports-card.svg"):
	value = (path or fallback).lstrip("/")
	if value.startswith(("http://", "https://", "data:")):
		return value
	if not value.startswith("images/"):
		value = f"images/{value}"
	return f"{prefix}{value}"


def write(path, content):
	target = ROOT / path
	target.parent.mkdir(parents=True, exist_ok=True)
	target.write_text(content, encoding="utf-8")


def nav(prefix, language, active, settings, products):
	english = language == "en"
	labels = {
		"home": "Home" if english else "หน้าแรก",
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
		"products": f"{prefix}{base}products/index.html",
		"services": f"{prefix}{base}services/index.html",
		"projects": f"{prefix}{base}projects/index.html",
		"certificates": f"{prefix}{base}certificates/index.html",
		"blog": f"{prefix}{base}blog/index.html",
		"contact": f"{prefix}{base}index.html#contact",
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
	return f'''<div class="topbar"><div class="container"><div class="left"><a href="tel:+66877070280">{phone}</a><a href="mailto:{email}">{email}</a></div><div class="right"><a href="{language_link}">{language_label}</a></div></div></div>
<header class="mainnav"><div class="container"><a href="{links['home']}" class="logo-wrap"><img src="{asset(settings.get('logo'), prefix, 'images/hks-surfaces-logo.png')}" alt="HKS Surfaces"></a><a class="header-language" href="{language_link}" aria-label="Switch language">{language_label}</a><button class="menu" aria-label="Menu">☰</button><nav>{nav_links}{mobile_language_link}</nav><a class="quote-btn" href="{links['contact']}">{"Request a Quote" if english else "ขอใบเสนอราคา"}</a></div></header>'''


def footer(prefix, language, settings):
	contact = "Contact Us" if language == "en" else "ติดต่อเรา"
	privacy = "Privacy Policy" if language == "en" else "นโยบายความเป็นส่วนตัว"
	social_label = "Follow us" if language == "en" else "ติดตามเรา"
	return f'''<footer class="site-footer"><div class="container footer-grid"><div><img src="{asset(settings.get('logo'), prefix, 'images/hks-surfaces-logo.png')}" alt="HKS Surfaces" style="width:120px;border-radius:50%"></div><div><h3>{text(settings.get('site_name', 'HKS Surfaces'))}</h3><address>{text(settings.get('business_address'))}</address></div><div><h3>{contact}</h3><p><a href="tel:+66877070280">{text(settings.get('phone_display', '087 707 0280'))}</a><br><a href="mailto:{text(settings.get('contact_email'))}">{text(settings.get('contact_email'))}</a></p><div class="social-links" aria-label="{social_label}"><a href="#" aria-label="Facebook"><i class="bi bi-facebook"></i></a><a href="#" aria-label="YouTube"><i class="bi bi-youtube"></i></a><a href="#" aria-label="Instagram"><i class="bi bi-instagram"></i></a><a href="#" aria-label="LINE"><i class="bi bi-line"></i></a><a href="#" aria-label="X"><i class="bi bi-twitter-x"></i></a><a href="#" aria-label="Threads"><i class="bi bi-threads"></i></a></div></div></div><p class="privacy-footer-link"><a href="{prefix}{'en/' if language == 'en' else ''}privacy-policy/index.html">{privacy}</a></p></footer>'''


def document(title, description, prefix, language, active, body, settings, products):
	return f'''<!doctype html><html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{text(title)} | HKS Surfaces</title><meta name="description" content="{text(description)}"><meta name="robots" content="index,follow"><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"><link rel="stylesheet" href="{prefix}assets/styles.css"><link rel="icon" href="{prefix}images/hks-surfaces-logo.png"></head><body>{nav(prefix, language, active, settings, products)}{body}{footer(prefix, language, settings)}<script src="{prefix}assets/site.js"></script></body></html>'''


def hero(title, description, eyebrow):
	return f'<section class="page-hero"><div class="container"><div class="eyebrow">{text(eyebrow)}</div><h1>{text(title)}</h1><p>{text(description)}</p></div></section>'


def product_image(product, prefix):
	images = product.get("images") or []
	primary = next((image for image in images if image.get("primary")), images[0] if images else {})
	return asset(primary.get("file") or product.get("image"), prefix)


def product_detail_images(product, prefix, alt, language):
	images = product.get(f"images_{language}") or product.get("images") or [{"file": product.get("image")}]
	primary = next((image for image in images if image.get("primary")), images[0])
	ordered_images = [primary] + [image for image in images if image is not primary]
	return "".join(
		f'<img src="{asset(image.get("file"), prefix)}" alt="{text(alt)}">'
		for image in ordered_images
	)


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
		rows = "".join(f"<tr><th>{text(name)}</th><td>{text(value)}</td></tr>" for name, value in section.get("specifications", []))
		table = f'<table><tbody>{rows}</tbody></table>' if rows else ""
		sections.append(f'<section class="article"><h2>{text(section.get("heading"))}</h2>{paragraphs}{list_html}{subsections}{table}</section>')
	return "".join(sections)


def project_image(project, prefix):
	images = project.get("images") or []
	primary = next((image for image in images if image.get("primary")), images[0] if images else {})
	return asset(primary.get("file") or project.get("image"), prefix, "images/sports-card.svg")


def build_homepage(homepage, products, settings, language):
	english = language == "en"
	prefix = "../" if english else ""
	title = homepage.get(f"hero_title_{language}")
	subtitle = homepage.get(f"hero_subtitle_{language}")
	description = homepage.get(f"hero_text_{language}")
	product_cards = "".join(
		f'<a class="cat-card" href="{prefix}{"en/" if english else ""}products/{text(product["slug"])}/index.html"><div class="cat-img" style="background-image:url(\'{product_image(product, prefix)}\')"></div><div class="cat-body"><h3>{text(product.get("en" if english else "th"))}</h3><small>{text(product.get("cat", "SURFACES")).upper()}</small><b>→</b></div></a>'
		for product in products[:6]
	)
	gallery = "".join(f'<img src="{asset(image.get("file"), prefix)}" alt="{text(image.get("alt_en" if english else "alt_th"))}" loading="lazy">' for image in homepage.get("gallery_images", []))
	body = f'''<main><section class="hero" style="background-image:url('{asset(homepage.get('hero_image'), prefix, 'images/home/hks-surfaces-playground-pickleball-hero.png')}')"><div class="container"><div class="hero-copy"><h1>{text(title)}</h1><h2>{text(subtitle)}</h2><div class="tagline">SAFETY &amp; SPORTS SURFACE SPECIALIST</div><p>{text(description)}</p><div class="hero-actions"><a class="btn green" href="{prefix}{'en/' if english else ''}products/index.html">{"Explore Products" if english else "ดูผลิตภัณฑ์ของเรา"} →</a><a class="btn outline" href="#contact">{"Request a Quote" if english else "ขอใบเสนอราคา"} →</a></div></div><form class="quote-card" id="contact"><h3>{"Request a Quote" if english else "ขอใบเสนอราคา"}</h3><input placeholder="{"Name" if english else "ชื่อ-นามสกุล"}"><input placeholder="{"Phone" if english else "เบอร์โทรศัพท์"}"><input placeholder="Email"><textarea rows="4" placeholder="{"Project details" if english else "รายละเอียดโครงการ"}"></textarea><button class="btn green" type="button">{"Send Enquiry" if english else "ส่งข้อมูล"}</button></form></div></section><section class="category-strip"><div class="container category-grid">{product_cards}</div></section><section class="section"><div class="container"><div class="section-head"><h2>{text(homepage.get(f'gallery_title_{language}'))}</h2></div><div class="home-gallery-grid">{gallery}</div></div></section><section class="section" id="about"><div class="container"><div class="section-head"><h2>{text(homepage.get(f'about_title_{language}'))}</h2><p>{text(homepage.get(f'about_text_{language}'))}</p></div></div></section></main>'''
	write(("en/" if english else "") + "index.html", document(title, description, prefix, language, "home", body, settings, products))


def build_products(products, settings, language):
	english = language == "en"
	prefix = "../../" if english else "../"
	title = "Products & Surface Systems" if english else "ผลิตภัณฑ์และระบบพื้น"
	description = "Safety, sports, and specialty surface systems." if english else "ระบบพื้นนิรภัย พื้นสนามกีฬา และวัสดุสำหรับงานพื้น"
	cards = "".join(f'<a class="card" href="{text(product["slug"])}/index.html"><div class="media" style="background-image:url(\'{product_image(product, prefix)}\')"></div><div class="card-body"><span class="pill">{text(product.get("cat"))}</span><h2>{text(product.get("en" if english else "th"))}</h2><p>{text(product.get("den" if english else "dth"))}</p></div></a>' for product in products)
	body = hero(title, description, "PRODUCTS & SYSTEMS") + f'<main class="section"><div class="container"><div class="grid-3">{cards}</div></div></main>'
	root = ("en/" if english else "") + "products/index.html"
	write(root, document(title, description, prefix, language, "products", body, settings, products))
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
		uses_image_first_layout = is_epdm_granules or is_epdm_flooring or is_sbr_granules or is_running_track or is_pu_binder
		right_column_content = product_detail_sections(product, language, 0, 2) if is_epdm_granules else ""
		below_content = product_detail_sections(product, language, 2) if is_epdm_granules else extra_content
		layout_class = "product-layout product-layout--image-first" if uses_image_first_layout else "product-layout"
		layout_class += " product-layout--basketball" if is_basketball else ""
		image_stack_class = "product-image-stack product-image-stack--epdm-granules" if is_epdm_granules else "product-image-stack"
		image_stack_class += " product-image-stack--epdm-flooring" if is_epdm_flooring else ""
		image_stack_class += " product-image-stack--running-track" if is_running_track else ""
		contact_prefix = "en/" if english else ""
		cta_label = "Request a Quote" if english else "ขอใบเสนอราคา"
		feature_heading = "Key features" if english else "จุดเด่น"
		category = text(product.get("cat"))
		detail_images = product_detail_images(product, detail_prefix, product_title, language)
		quote_cta = "" if is_basketball else f'<a class="btn green" href="{detail_prefix}{contact_prefix}index.html#contact">{cta_label}</a>'
		intro_content = right_column_content if is_epdm_granules else f'<span class="pill">{category}</span><h2>{text(product_title)}</h2><p>{text(product_description)}</p><h3>{feature_heading}</h3><ul class="feature-list">{feature_list}</ul>{quote_cta}{right_column_content}'
		hero_content = "" if uses_image_first_layout else hero(product_title, product_description, "HKS SURFACES")
		intro_column = "" if is_epdm_flooring or is_sbr_granules or is_running_track or is_pu_binder or is_basketball else f'<div>{intro_content}</div>'
		detail = hero_content + f'<main class="section"><div class="container"><div class="{layout_class}"><div class="{image_stack_class}">{detail_images}</div>{intro_column}</div>{below_content}</div></main>'
		path = ("en/" if english else "") + f'products/{product["slug"]}/index.html'
		write(path, document(product_title, product_description, detail_prefix, language, "products", detail, settings, products))


def build_projects(projects, products, settings, language):
	english = language == "en"
	prefix = "../../" if english else "../"
	title = "Our Projects" if english else "โครงการของเรา"
	description = "Examples of HKS Surfaces installations." if english else "ผลงานระบบพื้นนิรภัย พื้น EPDM และพื้นสนามกีฬา"
	cards = []
	for project in projects:
		location = project.get("loc_en" if english else "loc_th") or ""
		meta = text(" | ".join(filter(None, [str(project.get("year") or ""), str(location)])))
		project_title = text(project.get("title_en" if english else "title_th"))
		project_description = text(project.get("desc_en" if english else "desc_th"))
		image = project_image(project, prefix)
		cards.append(f'<article class="card"><div class="media" style="background-image:url(\'{image}\')"></div><div class="card-body"><span class="pill">{meta}</span><h2>{project_title}</h2><p>{project_description}</p></div></article>')
	cards = "".join(cards)
	body = hero(title, description, "OUR PROJECTS") + f'<main class="section"><div class="container"><div class="grid-3">{cards}</div></div></main>'
	write(("en/" if english else "") + "projects/index.html", document(title, description, prefix, language, "projects", body, settings, products))


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
	write(("en/" if english else "") + "services/index.html", document(title, description, prefix, language, "services", body, settings, products))


def build_certificates(certificates, products, settings, language):
	english = language == "en"
	prefix = "../../" if english else "../"
	title = certificates.get(f"title_{language}")
	description = certificates.get(f"description_{language}")
	intro = certificates.get(f"intro_{language}")
	cards = "".join(f'<article class="content-card"><h3>{text(item.get(f"title_{language}"))}</h3><p>{text(item.get(f"text_{language}"))}</p></article>' for item in certificates.get("items", []))
	body = hero(title, description, "HKS SURFACES") + f'<main class="section"><div class="container"><div class="section-head"><h2>{text(title)}</h2><p>{text(intro)}</p></div><div class="content-grid">{cards}</div></div></main>'
	write(("en/" if english else "") + "certificates/index.html", document(title, description, prefix, language, "certificates", body, settings, products))


def build_blogs(blogs, products, settings, language):
	english = language == "en"
	prefix = "../../" if english else "../"
	title = "Blog & Knowledge" if english else "บทความและความรู้"
	description = "Guidance on safety and sports surface systems." if english else "ข้อมูลเกี่ยวกับพื้น EPDM พื้นสนามเด็กเล่น และพื้นสนามกีฬา"
	cards = "".join(f'<a class="card" href="{text(blog["slug"])}/index.html"><div class="media" style="background-image:url(\'{asset(blog.get("image"), prefix)}\')"></div><div class="card-body"><span class="meta">{text(blog.get("date"))}</span><h2>{text(blog.get("title_en" if english else "title_th"))}</h2><p>{text(blog.get("excerpt_en" if english else "excerpt_th"))}</p></div></a>' for blog in blogs)
	body = hero(title, description, "BLOG & KNOWLEDGE") + f'<main class="section"><div class="container"><div class="grid-3">{cards}</div></div></main>'
	write(("en/" if english else "") + "blog/index.html", document(title, description, prefix, language, "blog", body, settings, products))
	for blog in blogs:
		detail_prefix = "../../../" if english else "../../"
		blog_title = blog.get("title_en" if english else "title_th")
		sections = blog.get("body_en" if english else "body_th", [])
		article = "".join(f"<h2>{text(section[0])}</h2><p>{text(section[1])}</p>" for section in sections if len(section) > 1)
		body = hero(blog_title, blog.get("excerpt_en" if english else "excerpt_th"), "HKS SURFACES") + f'<main class="section"><article class="article"><div class="meta">{text(blog.get("date"))}</div><img src="{asset(blog.get("image"), detail_prefix)}" alt="{text(blog_title)}">{article}</article></main>'
		path = ("en/" if english else "") + f'blog/{blog["slug"]}/index.html'
		write(path, document(blog_title, blog.get("excerpt_en" if english else "excerpt_th"), detail_prefix, language, "blog", body, settings, products))


def main():
	homepage = read_json("homepage-data.json")
	products = read_json("products-data.json")
	projects = read_json("projects-data.json")
	blogs = read_json("blog-data.json")
	certificates = read_json("certificates-data.json")
	settings = read_json("site-config.json")
	for language in ("th", "en"):
		build_homepage(homepage, products, settings, language)
		build_products(products, settings, language)
		build_services(products, settings, language)
		build_projects(projects, products, settings, language)
		build_certificates(certificates, products, settings, language)
		build_blogs(blogs, products, settings, language)
	print("Built public pages from JSON content files.")


if __name__ == "__main__":
	main()
