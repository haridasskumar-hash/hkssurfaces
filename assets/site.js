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
const products=[
	['safety','playground-safety-flooring','พื้นสนามเด็กเล่นนิรภัย','Playground Safety Flooring'],
	['safety','epdm-flooring','พื้น EPDM','EPDM Flooring'],
	['safety','rubber-safety-tiles','แผ่นยางนิรภัย','Rubber Safety Tiles'],
	['sports','badminton-court-flooring','พื้นสนามแบดมินตัน','Badminton Court Flooring'],
	['sports','tennis-court-flooring','พื้นสนามเทนนิส','Tennis Court Flooring'],
	['sports','basketball-court-flooring','พื้นสนามบาสเกตบอล','Basketball Court Flooring'],
	['sports','pickleball-court-flooring','พื้นสนามพิคเคิลบอล','Pickleball Court Flooring'],
	['sports','multi-sport-court-flooring','พื้นสนามกีฬาอเนกประสงค์','Multi-Sport Court Flooring'],
	['sports','running-track-flooring','พื้นลู่วิ่งสังเคราะห์','Running Track Flooring'],
	['sports','gym-flooring','พื้นฟิตเนสและยิม','Gym Flooring'],
	['materials','epdm-granules','เม็ดยาง EPDM','EPDM Granules'],
	['materials','sbr-rubber-granules','เม็ดยาง SBR','SBR Rubber Granules'],
	['materials','polyurethane-binder','กาวโพลียูรีเทน PU Binder','Polyurethane Binder']
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

document.querySelectorAll('.site-footer,.footer').forEach(footer=>{
	if(footer.querySelector('.social-links')) return;
	const contactSection=footer.querySelector('.footer-grid > div:last-child,.footer .container > div:last-child');
	if(!contactSection) return;
	const socialLinks=document.createElement('div');
	socialLinks.className='social-links';
	socialLinks.setAttribute('aria-label',isEnglish?'Follow us':'ติดตามเรา');
	socialLinks.innerHTML='<a href="#" aria-label="Facebook"><i class="bi bi-facebook"></i></a><a href="#" aria-label="YouTube"><i class="bi bi-youtube"></i></a><a href="#" aria-label="Instagram"><i class="bi bi-instagram"></i></a><a href="#" aria-label="LINE"><i class="bi bi-line"></i></a><a href="#" aria-label="X"><i class="bi bi-twitter-x"></i></a><a href="#" aria-label="Threads"><i class="bi bi-threads"></i></a>';
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