if(!document.querySelector('link[href*="bootstrap-icons"]')){
	const iconStylesheet=document.createElement('link');
	iconStylesheet.rel='stylesheet';
	iconStylesheet.href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css';
	document.head.append(iconStylesheet);
}

document.querySelector('.menu')?.addEventListener('click',()=>document.querySelector('nav')?.classList.toggle('open'));

const siteNavigation=document.querySelector('nav');
const scriptUrl=document.currentScript?.src||'';
const isEnglish=/(?:^|\/)en(?:\/|$)/.test(location.pathname);
const siteRoot=scriptUrl.replace(/assets\/site\.js(?:\?.*)?$/,'');
const siteRootPath=new URL(siteRoot,location.href).pathname;
const pagePath=location.pathname.startsWith(siteRootPath)?location.pathname.slice(siteRootPath.length).replace(/^\/+/, ''):'';
const languagePagePath=pagePath.replace(/^en\//,'')||'index.html';
const languageTarget=`${siteRoot}${isEnglish?'':'en/'}${languagePagePath}${location.hash}`;
document.querySelectorAll('.topbar .right a,.mobile-language,.header-language').forEach(link=>link.href=languageTarget);
const products=[
	['safety','playground-safety-flooring','พื้นสนามเด็กเล่นนิรภัย','Playground Safety Flooring'],
	['safety','epdm-flooring','พื้น EPDM','EPDM Flooring'],
	['safety','epdm-flooring-wet-area','พื้น EPDM สำหรับสวนน้ำ','EPDM Flooring for Wet Areas'],
	['safety','rubber-safety-tiles','แผ่นยางนิรภัย','Rubber Safety Tiles'],
	['sports','badminton-court-flooring','พื้นสนามแบดมินตัน','Badminton Court Flooring'],
	['sports','tennis-court-flooring','พื้นสนามเทนนิส','Tennis Court Flooring'],
	['sports','basketball-court-flooring','พื้นสนามบาสเกตบอล','Basketball Court Flooring'],
	['sports','pickleball-court-flooring','พื้นสนามพิคเคิลบอล','Pickleball Court Flooring'],
	['sports','padel-court-flooring','โซลูชันพื้นสนามพาเดล','Padel Court Flooring Solutions'],
	['sports','multi-sport-court-flooring','พื้นสนามกีฬาอเนกประสงค์','Multi-Sport Court Flooring'],
	['sports','running-track-flooring','พื้นลู่วิ่งสังเคราะห์','Running Track Flooring'],
	['sports','gym-flooring','พื้นฟิตเนสและยิม','Gym Flooring'],
	['materials','epdm-granules','เม็ดยาง EPDM','EPDM Granules'],
	['materials','sbr-rubber-granules','เม็ดยาง SBR','SBR Rubber Granules'],
	['materials','polyurethane-binder','กาวโพลียูรีเทน PU Binder','Polyurethane Binder'],
	['materials','epoxy-flooring','พื้นอีพ็อกซี่','Epoxy Flooring']
	,['materials','artificial-turf','หญ้าเทียม','Artificial Turf']
];

if(siteNavigation&&!siteNavigation.querySelector('.nav-dropdown')){
	const productLinks=[...siteNavigation.querySelectorAll('a[href*="products/index.html"]')];
	const productLink=productLinks.shift();
	if(productLink){
		const labels=isEnglish?{safety:'Safety Flooring',sports:'Sports Flooring',materials:'Materials'}:{safety:'พื้นนิรภัย',sports:'พื้นสนามกีฬา',materials:'วัสดุสำหรับระบบพื้น'};
		const dropdown=document.createElement('div');
		dropdown.className='nav-dropdown';
		const productBase=`${siteRoot}${isEnglish?'en/':''}products/`;
		dropdown.innerHTML=`<button class="nav-dropdown-toggle" type="button" aria-expanded="false">${isEnglish?'Products':'ผลิตภัณฑ์'}<span aria-hidden="true">⌄</span></button><div class="product-menu"><a class="product-menu-all" href="${productBase}index.html">${isEnglish?'All Products':'ดูผลิตภัณฑ์ทั้งหมด'}</a><div class="product-menu-groups">${Object.keys(labels).map(category=>`<section class="product-menu-group"><h3>${labels[category]}</h3>${products.filter(product=>product[0]===category).map(product=>`<a href="${productBase}${product[1]}/index.html">${product[isEnglish?3:2]}</a>`).join('')}</section>`).join('')}</div></div>`;
		productLink.replaceWith(dropdown);
		productLinks.forEach(link=>link.remove());
	}
}

document.querySelectorAll('.nav-dropdown-toggle').forEach(toggle=>{
	toggle.addEventListener('click',()=>{
		const dropdown=toggle.closest('.nav-dropdown');
		const isOpen=dropdown?.classList.toggle('open');
		toggle.setAttribute('aria-expanded',String(isOpen));
	});
});

document.addEventListener('click',event=>{
	if(!event.target.closest('.nav-dropdown')){
		document.querySelectorAll('.nav-dropdown.open').forEach(dropdown=>{
		dropdown.classList.remove('open');
		dropdown.querySelector('.nav-dropdown-toggle')?.setAttribute('aria-expanded','false');
		});
	}
});

const projectImageTriggers=document.querySelectorAll('.project-image-trigger');
if(projectImageTriggers.length){
	const lightbox=document.createElement('div');
	lightbox.className='lightbox';
	lightbox.setAttribute('role','dialog');
	lightbox.setAttribute('aria-modal','true');
	lightbox.setAttribute('aria-label',isEnglish?'Enlarged project image':'ภาพโครงการขนาดใหญ่');
	lightbox.innerHTML='<button class="lightbox-close" type="button" aria-label="Close">&times;</button><button class="lightbox-prev" type="button" aria-label="Previous image">&#8249;</button><img class="lightbox-image" alt=""><button class="lightbox-next" type="button" aria-label="Next image">&#8250;</button>';
	document.body.append(lightbox);
	const lightboxImage=lightbox.querySelector('.lightbox-image');
	const previousButton=lightbox.querySelector('.lightbox-prev');
	const nextButton=lightbox.querySelector('.lightbox-next');
	let activeTriggers=[];
	let activeIndex=0;
	const closeLightbox=()=>{lightbox.classList.remove('open');document.body.classList.remove('lightbox-open');lightboxImage.removeAttribute('src')};
	const showImage=index=>{
		activeIndex=(index+activeTriggers.length)%activeTriggers.length;
		const trigger=activeTriggers[activeIndex];
		lightboxImage.src=trigger.dataset.lightboxSrc;
		lightboxImage.alt=trigger.getAttribute('alt')||trigger.getAttribute('aria-label')||'';
		previousButton.hidden=activeTriggers.length<2;
		nextButton.hidden=activeTriggers.length<2;
	};
	const openLightbox=trigger=>{
		const group=trigger.dataset.lightboxGroup;
		activeTriggers=[...projectImageTriggers].filter(item=>item.dataset.lightboxGroup===group);
		activeIndex=Math.max(0,activeTriggers.indexOf(trigger));
		showImage(activeIndex);
		lightbox.classList.add('open');
		document.body.classList.add('lightbox-open');
		lightbox.querySelector('.lightbox-close').focus();
	};
	projectImageTriggers.forEach(trigger=>{
		trigger.addEventListener('click',()=>openLightbox(trigger));
		trigger.addEventListener('keydown',event=>{
			if(event.key==='Enter'||event.key===' '){event.preventDefault();openLightbox(trigger)}
		});
	});
	lightbox.querySelector('.lightbox-close').addEventListener('click',closeLightbox);
	previousButton.addEventListener('click',()=>showImage(activeIndex-1));
	nextButton.addEventListener('click',()=>showImage(activeIndex+1));
	lightbox.addEventListener('click',event=>{if(event.target===lightbox)closeLightbox()});
	document.addEventListener('keydown',event=>{
		if(!lightbox.classList.contains('open'))return;
		if(event.key==='Escape')closeLightbox();
		if(event.key==='ArrowLeft')showImage(activeIndex-1);
		if(event.key==='ArrowRight')showImage(activeIndex+1);
	});
	lightbox.addEventListener('wheel',event=>{if(Math.abs(event.deltaY)>Math.abs(event.deltaX))showImage(activeIndex+(event.deltaY>0?1:-1))},{passive:true});
}

document.querySelectorAll('.site-footer,.footer').forEach(footer=>{
	if(footer.querySelector('.social-links')) return;
	const contactSection=footer.querySelector('.footer-grid > div:last-child,.footer .container > div:last-child');
	if(!contactSection) return;
	const socialLinks=document.createElement('div');
	socialLinks.className='social-links';
	socialLinks.setAttribute('aria-label',isEnglish?'Follow us':'ติดตามเรา');
	socialLinks.innerHTML='<a href="#" aria-label="Facebook"><i class="bi bi-facebook"></i></a><a href="#" aria-label="YouTube"><i class="bi bi-youtube"></i></a><a href="#" aria-label="Instagram"><i class="bi bi-instagram"></i></a><a href="https://line.me/ti/p/Rn_AsnrLLf" target="_blank" rel="noopener noreferrer" aria-label="LINE"><i class="bi bi-line"></i></a><a href="#" aria-label="X"><i class="bi bi-twitter-x"></i></a><a href="#" aria-label="Threads"><i class="bi bi-threads"></i></a>';
	contactSection.append(socialLinks);
});

if(siteNavigation&&!siteNavigation.querySelector('a[href*="certificates/"]')){
	const certificateUrl=scriptUrl.replace(/assets\/site\.js(?:\?.*)?$/,isEnglish?'en/certificates/index.html':'certificates/index.html');
	const certificateLink=document.createElement('a');
	certificateLink.href=certificateUrl;
	certificateLink.textContent=isEnglish?'Certificate':'ใบรับรองมาตรฐาน';
	const blogLink=[...siteNavigation.querySelectorAll('a')].find(link=>/blog\/index\.html/.test(link.getAttribute('href')||''));
	siteNavigation.insertBefore(certificateLink,blogLink||null);
}

if(siteNavigation&&!siteNavigation.querySelector('.service-menu')){
	const servicesUrl=scriptUrl.replace(/assets\/site\.js(?:\?.*)?$/,isEnglish?'en/services/index.html':'services/index.html');
	const servicesDropdown=document.createElement('div');
	servicesDropdown.className='nav-dropdown service-dropdown';
	servicesDropdown.innerHTML=`<button class="nav-dropdown-toggle" type="button" aria-expanded="false">${isEnglish?'Services':'บริการ'}<span aria-hidden="true">⌄</span></button><div class="product-menu service-menu"><a href="${servicesUrl}#free-consultation">${isEnglish?'Free Consultation & Quotation Request':'ปรึกษาและขอใบเสนอราคาฟรี'}</a><a href="${servicesUrl}#transportation-installation-repair">${isEnglish?'Transportation, Installation & Repair':'ขนส่ง ติดตั้ง และซ่อมแซม'}</a><a href="${servicesUrl}#warranty-after-sales">${isEnglish?'Warranty & After-Sales Service':'รับประกันและบริการหลังการขาย'}</a></div>`;
	const projectsLink=[...siteNavigation.querySelectorAll('a')].find(link=>/projects\/index\.html/.test(link.getAttribute('href')||''));
	siteNavigation.insertBefore(servicesDropdown,projectsLink||null);
	servicesDropdown.querySelector('.nav-dropdown-toggle')?.addEventListener('click',()=>{
		const isOpen=servicesDropdown.classList.toggle('open');
		servicesDropdown.querySelector('.nav-dropdown-toggle')?.setAttribute('aria-expanded',String(isOpen));
	});
}