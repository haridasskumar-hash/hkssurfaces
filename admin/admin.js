
const KEY="hksSurfacesEditorV1";
let state;
const pendingProductFiles = new Map(); // key: product index -> [{id,file,url,name}]
const pendingProjectFiles = new Map(); // key: project index -> [{id,file,url,name}]
let pendingHeroFile=null;
let pendingHomeGalleryFiles=[];
try{state=JSON.parse(localStorage.getItem(KEY))||window.HKS_SEED}catch(e){state=window.HKS_SEED}
function normalizeProduct(product){
  return {...product,category:product.category??product.cat??"",title_th:product.title_th??product.th??"",title_en:product.title_en??product.en??"",short_th:product.short_th??product.dth??"",short_en:product.short_en??product.den??"",features_th:product.features_th??product.fth??[],features_en:product.features_en??product.fen??[]};
}
function normalizeProject(project){
  return {...project,category:productCategory(project),location_th:project.location_th??project.loc_th??"",location_en:project.location_en??project.loc_en??""};
}
function productCategory(project){return project.category??project.cat??""}
function normalizeBlog(blog){return {...blog,sections_th:blog.sections_th??blog.body_th??[],sections_en:blog.sections_en??blog.body_en??[]}}
state.products=(state.products||[]).map(normalizeProduct);
state.projects=(state.projects||[]).map(normalizeProject);
state.blogs=(state.blogs||[]).map(normalizeBlog);
state.certificates=state.certificates||{title_th:"ใบรับรองมาตรฐาน",title_en:"Certificates",description_th:"ข้อมูลใบรับรองและเอกสารมาตรฐานสำหรับระบบพื้น HKS Surfaces",description_en:"Quality and safety documentation for HKS Surfaces systems.",intro_th:"ติดต่อทีมงานของเราเพื่อขอเอกสารข้อมูลวัสดุ รายงานผลการทดสอบ และใบรับรองที่เกี่ยวข้องกับโครงการของคุณ",intro_en:"Please contact our team to request the applicable material data sheets, test reports and certificates for your project.",items:[{title_th:"เอกสารข้อมูลวัสดุ",title_en:"Material Documentation",text_th:"มีรายละเอียดผลิตภัณฑ์และข้อมูลวัสดุสำหรับประกอบการพิจารณาโครงการ",text_en:"Product specifications and material information available for project review."},{title_th:"ความปลอดภัยและประสิทธิภาพ",title_en:"Safety & Performance",text_th:"สามารถขอเอกสารประกอบตามความต้องการของระบบพื้นและโครงการได้",text_en:"Supporting documentation can be provided according to your system requirements."}]};
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const titles={home:"Main Page",products:"Products",projects:"Projects",certificates:"Certificates",blog:"Blog",settings:"Site Settings",preview:"Preview"};

function persist(msg="Saved in editor"){
  localStorage.setItem(KEY,JSON.stringify(state));
  const st=$("#status");st.textContent=msg;st.classList.add("ok");
  setTimeout(()=>st.classList.remove("ok"),1800);
}
function switchTab(name){
  $$(".tab").forEach(x=>x.classList.toggle("active",x.dataset.tab===name));
  $$(".panel").forEach(x=>x.classList.toggle("active",x.id==="panel-"+name));
  $("#panelTitle").textContent=titles[name]||name;
}
$$(".tab").forEach(b=>b.addEventListener("click",()=>switchTab(b.dataset.tab)));


function homeImgSrc(path,pendingId){
  if(pendingId){
    const f=pendingHomeGalleryFiles.find(x=>x.id===pendingId);
    if(f)return f.url;
  }
  if(path&&pendingHeroFile&&path===state.homepage.hero_image)return pendingHeroFile.url;
  if(!path)return "";
  if(path.startsWith("blob:")||path.startsWith("data:")||path.startsWith("http"))return path;
  if(path.startsWith("images/"))return "../"+path;
  if(path.startsWith("/images/"))return ".."+path;
  return "../"+path;
}
function renderHomeHero(){
  const box=$("#homeHeroPreview");if(!box)return;
  const src=homeImgSrc(state.homepage.hero_image);
  box.innerHTML=`<div class="image-card primary"><span class="primary-badge">Hero image</span><div class="image-preview">${src?`<img src="${safe(src)}" alt="">`:`<div class="placeholder">No hero image</div>`}</div><div class="image-meta">${safe(state.homepage.hero_image||"")}</div></div>`;
}
function renderHomeGallery(){
  const box=$("#homeGallery");if(!box)return;
  const imgs=Array.isArray(state.homepage.gallery_images)?state.homepage.gallery_images:[];
  if(!imgs.length){box.innerHTML=`<div class="placeholder">No homepage gallery images yet.</div>`;return}
  box.innerHTML=imgs.map((im,i)=>`<div class="image-card ${im.featured?"primary":""}" data-home-img="${i}">
    ${im.featured?`<span class="primary-badge">Featured</span>`:""}
    <div class="image-preview"><img src="${safe(homeImgSrc(im.file,im._pendingId))}" alt=""></div>
    <div class="image-meta">${safe(im.file||"")}</div>
    <div class="field"><label>Thai alt text</label><input data-home-alt-th="${i}" value="${safe(im.alt_th||"")}"></div>
    <div class="field"><label>English alt text</label><input data-home-alt-en="${i}" value="${safe(im.alt_en||"")}"></div>
    <div class="image-actions">
      <button type="button" class="btn small secondary" data-home-action="up" data-index="${i}">←</button>
      <button type="button" class="btn small secondary" data-home-action="down" data-index="${i}">→</button>
      <button type="button" class="btn small secondary" data-home-action="featured" data-index="${i}">${im.featured?"Featured":"Set Featured"}</button>
      <button type="button" class="btn small danger" data-home-action="remove" data-index="${i}">Remove</button>
    </div></div>`).join("");
  box.querySelectorAll("[data-home-action]").forEach(btn=>btn.addEventListener("click",()=>homeGalleryAction(+btn.dataset.index,btn.dataset.homeAction)));
}
function syncHomeAlt(){
  const imgs=state.homepage.gallery_images||[];
  $$("[data-home-alt-th]").forEach(el=>{if(imgs[+el.dataset.homeAltTh])imgs[+el.dataset.homeAltTh].alt_th=el.value.trim()});
  $$("[data-home-alt-en]").forEach(el=>{if(imgs[+el.dataset.homeAltEn])imgs[+el.dataset.homeAltEn].alt_en=el.value.trim()});
}
function homeGalleryAction(i,action){
  syncHomeAlt();const imgs=state.homepage.gallery_images||[];
  if(action==="up"&&i>0)[imgs[i-1],imgs[i]]=[imgs[i],imgs[i-1]];
  if(action==="down"&&i<imgs.length-1)[imgs[i+1],imgs[i]]=[imgs[i],imgs[i+1]];
  if(action==="featured")imgs.forEach((x,j)=>x.featured=j===i);
  if(action==="remove"){
    const removed=imgs.splice(i,1)[0];
    if(removed&&removed._pendingId){
      const f=pendingHomeGalleryFiles.find(x=>x.id===removed._pendingId);if(f)URL.revokeObjectURL(f.url);
      pendingHomeGalleryFiles=pendingHomeGalleryFiles.filter(x=>x.id!==removed._pendingId);
    }
    if(imgs.length&&!imgs.some(x=>x.featured))imgs[0].featured=true;
  }
  persist();renderHomeGallery();
}
function downloadHomeFiles(arr){
  if(!arr.length){alert("No newly uploaded images to download.");return}
  arr.forEach((x,i)=>setTimeout(()=>{const a=document.createElement("a");a.href=x.url;a.download=x.name;document.body.appendChild(a);a.click();a.remove()},i*250));
}

function homeToFields(){
  Object.keys(state.homepage).forEach(k=>{const el=$("#home_"+k);if(el && typeof state.homepage[k]!=="object")el.value=state.homepage[k]||""});
  renderHomeHero();renderHomeGallery();
}
function homeFromFields(){
  Object.keys(state.homepage).forEach(k=>{const el=$("#home_"+k);if(el && typeof state.homepage[k]!=="object")state.homepage[k]=el.value.trim()});
}
function settingsToFields(){
  ["site_name","site_url","phone_display","contact_email","business_address","logo"].forEach(k=>{const el=$("#set_"+k);if(el)el.value=state.settings[k]||""});
}
function settingsFromFields(){
  ["site_name","site_url","phone_display","contact_email","business_address","logo"].forEach(k=>{const el=$("#set_"+k);if(el)state.settings[k]=el.value.trim()});
}
function certificatesToFields(){["title_th","title_en","description_th","description_en","intro_th","intro_en"].forEach(k=>{const el=$("#cert_"+k);if(el)el.value=state.certificates[k]||""})}
function certificatesFromFields(){["title_th","title_en","description_th","description_en","intro_th","intro_en"].forEach(k=>{const el=$("#cert_"+k);if(el)state.certificates[k]=el.value.trim()})}
$$("[data-save]").forEach(b=>b.addEventListener("click",()=>{
  if(b.dataset.save==="home")homeFromFields();
  if(b.dataset.save==="settings")settingsFromFields();
  if(b.dataset.save==="certificates")certificatesFromFields();
  persist();
}));

function safe(v){return (v??"").toString().replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function editorField(label,key,val,type="input"){
  return `<div class="field"><label>${label}</label>${type==="textarea"?`<textarea data-key="${key}">${safe(val)}</textarea>`:`<input data-key="${key}" value="${safe(val)}">`}</div>`;
}
function itemShell(title,meta,idx,kind,body){
  return `<div class="item" data-kind="${kind}" data-index="${idx}">
    <div class="item-head"><div><h3>${safe(title||"(Untitled)")}</h3><div class="meta">${safe(meta||"")}</div></div>
    <div class="item-actions"><button class="btn small secondary" data-action="up">↑</button><button class="btn small secondary" data-action="down">↓</button><button class="btn small secondary" data-action="edit">Edit</button><button class="btn small danger" data-action="delete">Delete</button></div></div>
    <div class="editor">${body}<button class="btn primary small" data-action="saveitem">Save Item</button></div>
  </div>`;
}
function productBody(p, idx){
  if(!Array.isArray(p.images)) p.images = p.image ? [{file:p.image,alt_th:p.title_th||"",alt_en:p.title_en||"",primary:true}] : [];
  const gallery = renderProductImages(p, idx);
  return `<div class="grid2">
  ${editorField("Slug","slug",p.slug)}${editorField("Category","category",p.category)}
  ${editorField("Thai title","title_th",p.title_th)}${editorField("English title","title_en",p.title_en)}
  </div>${editorField("Thai short description","short_th",p.short_th,"textarea")}${editorField("English short description","short_en",p.short_en,"textarea")}
  <div class="grid2">${editorField("Primary image path","image",p.image||"")}</div>
  ${editorField("Features TH — separate with |","features_th",(p.features_th||[]).join(" | "))}
  ${editorField("Features EN — separate with |","features_en",(p.features_en||[]).join(" | "))}
  <div class="image-uploader">
    <div class="image-uploader-head">
      <div><b>Product Image Gallery</b><div class="upload-note">Upload JPG, PNG, WebP or AVIF. Multiple images are supported.</div></div>
      <input type="file" data-product-upload="${idx}" accept="image/jpeg,image/png,image/webp,image/avif" multiple>
    </div>
    <div class="image-gallery" data-product-gallery="${idx}">${gallery}</div>
    <div class="image-actions" style="margin-top:12px">
      <button type="button" class="btn small secondary" data-download-product-images="${idx}">Download Uploaded Images</button>
    </div>
  </div>`;
}
function projectBody(p, idx){
  const gallery = renderProjectImages(p, idx);
  return `<div class="grid2">${editorField("Slug","slug",p.slug)}${editorField("Category","category",p.category)}
  ${editorField("Thai title","title_th",p.title_th)}${editorField("English title","title_en",p.title_en)}
  ${editorField("Thai location","location_th",p.location_th)}${editorField("English location","location_en",p.location_en)}
  ${editorField("Project year","year",p.year)}${editorField("Primary image path","image",p.image)}</div>${editorField("Thai description","desc_th",p.desc_th,"textarea")}${editorField("English description","desc_en",p.desc_en,"textarea")}
  <div class="image-uploader">
    <div class="image-uploader-head"><div><b>Project Image Gallery</b><div class="upload-note">Upload JPG, PNG, WebP or AVIF. Multiple images are supported.</div></div><input type="file" data-project-upload="${idx}" accept="image/jpeg,image/png,image/webp,image/avif" multiple></div>
    <div class="image-gallery">${gallery}</div>
    <div class="image-actions" style="margin-top:12px"><button type="button" class="btn small secondary" data-download-project-images="${idx}">Download Uploaded Images</button></div>
  </div>`;
}
function blogBody(b){
  return `<div class="grid2">${editorField("Slug","slug",b.slug)}${editorField("Date","date",b.date)}
  ${editorField("Thai title","title_th",b.title_th)}${editorField("English title","title_en",b.title_en)}
  ${editorField("Image path","image",b.image)}</div>
  ${editorField("Thai excerpt","excerpt_th",b.excerpt_th,"textarea")}${editorField("English excerpt","excerpt_en",b.excerpt_en,"textarea")}
  ${editorField("Thai article sections — Heading :: Text, one per line","sections_th",(b.sections_th||[]).map(x=>x.join(" :: ")).join("\n"),"textarea")}
  ${editorField("English article sections — Heading :: Text, one per line","sections_en",(b.sections_en||[]).map(x=>x.join(" :: ")).join("\n"),"textarea")}`;
}
function certificateBody(item){return `<div class="grid2">${editorField("Thai title","title_th",item.title_th)}${editorField("English title","title_en",item.title_en)}</div>${editorField("Thai text","text_th",item.text_th,"textarea")}${editorField("English text","text_en",item.text_en,"textarea")}`}

function ensureImages(p){
  if(!Array.isArray(p.images)) p.images=[];
  if(p.images.length===0 && p.image){
    p.images=[{file:p.image,alt_th:p.title_th||"",alt_en:p.title_en||"",primary:true}];
  }
  if(p.images.length && !p.images.some(x=>x.primary)) p.images[0].primary=true;
  return p.images;
}
function previewSrc(img, idx){
  if(img._pendingId){
    const arr=pendingProductFiles.get(idx)||[];
    const f=arr.find(x=>x.id===img._pendingId);
    if(f) return f.url;
  }
  const path=img.file||"";
  if(!path) return "";
  if(path.startsWith("data:")||path.startsWith("blob:")||path.startsWith("http")) return path;
  if(path.startsWith("../")) return path;
  if(path.startsWith("images/")) return "../"+path;
  if(path.startsWith("/images/")) return ".."+path;
  return "../"+path;
}
function renderProductImages(p, idx){
  const imgs=ensureImages(p);
  if(!imgs.length) return `<div class="placeholder">No images yet. Use Upload Images above.</div>`;
  return imgs.map((im,i)=>{
    const src=previewSrc(im,idx);
    return `<div class="image-card ${im.primary?"primary":""}" data-img-index="${i}">
      ${im.primary?`<span class="primary-badge">Primary image</span>`:""}
      <div class="image-preview">${src?`<img src="${safe(src)}" alt="">`:`<div class="placeholder">Preview unavailable until file is selected locally.</div>`}</div>
      <div class="image-meta">${safe(im.file||"")}</div>
      <div class="field"><label>Thai alt text</label><input data-img-alt-th="${i}" value="${safe(im.alt_th||"")}"></div>
      <div class="field"><label>English alt text</label><input data-img-alt-en="${i}" value="${safe(im.alt_en||"")}"></div>
      <div class="image-actions">
        <button type="button" class="btn small secondary" data-img-action="up" data-img-index="${i}">←</button>
        <button type="button" class="btn small secondary" data-img-action="down" data-img-index="${i}">→</button>
        <button type="button" class="btn small secondary" data-img-action="primary" data-img-index="${i}">${im.primary?"Primary":"Set Primary"}</button>
        <button type="button" class="btn small danger" data-img-action="remove" data-img-index="${i}">Remove</button>
      </div>
    </div>`;
  }).join("");
}
function cleanFileName(name){
  return name.toLowerCase().replace(/\s+/g,"-").replace(/[^a-z0-9._-]/g,"").replace(/-+/g,"-");
}
function addUploadedFiles(productIdx, fileList){
  const p=state.products[productIdx];
  ensureImages(p);
  const arr=pendingProductFiles.get(productIdx)||[];
  [...fileList].forEach(file=>{
    const id="pf_"+Date.now()+"_"+Math.random().toString(36).slice(2);
    const safeName=cleanFileName(file.name)||("product-image-"+Date.now()+".jpg");
    const url=URL.createObjectURL(file);
    arr.push({id,file,url,name:safeName});
    p.images.push({
      file:"images/products/"+safeName,
      alt_th:p.title_th||"",
      alt_en:p.title_en||"",
      primary:p.images.length===0,
      _pendingId:id
    });
  });
  pendingProductFiles.set(productIdx,arr);
  if(p.images.length && !p.images.some(x=>x.primary)) p.images[0].primary=true;
  p.image=(p.images.find(x=>x.primary)||p.images[0]||{}).file||"";
  persist("Images added in editor");
  renderProducts($("#productSearch").value);
}
function saveImageAltInputs(item, productIdx){
  const p=state.products[productIdx];ensureImages(p);
  item.querySelectorAll("[data-img-alt-th]").forEach(el=>{const i=+el.dataset.imgAltTh;if(p.images[i])p.images[i].alt_th=el.value.trim()});
  item.querySelectorAll("[data-img-alt-en]").forEach(el=>{const i=+el.dataset.imgAltEn;if(p.images[i])p.images[i].alt_en=el.value.trim()});
}
function imageAction(productIdx,imgIdx,action,item){
  const p=state.products[productIdx];ensureImages(p);saveImageAltInputs(item,productIdx);
  if(action==="up" && imgIdx>0)[p.images[imgIdx-1],p.images[imgIdx]]=[p.images[imgIdx],p.images[imgIdx-1]];
  if(action==="down" && imgIdx<p.images.length-1)[p.images[imgIdx+1],p.images[imgIdx]]=[p.images[imgIdx],p.images[imgIdx+1]];
  if(action==="primary"){p.images.forEach((x,i)=>x.primary=i===imgIdx)}
  if(action==="remove"){
    const removed=p.images.splice(imgIdx,1)[0];
    if(removed&&removed._pendingId){
      const arr=pendingProductFiles.get(productIdx)||[];
      const f=arr.find(x=>x.id===removed._pendingId);if(f)URL.revokeObjectURL(f.url);
      pendingProductFiles.set(productIdx,arr.filter(x=>x.id!==removed._pendingId));
    }
    if(p.images.length&&!p.images.some(x=>x.primary))p.images[0].primary=true;
  }
  p.image=(p.images.find(x=>x.primary)||p.images[0]||{}).file||"";
  persist();renderProducts($("#productSearch").value);
}
function downloadPendingImages(productIdx){
  const arr=pendingProductFiles.get(productIdx)||[];
  if(!arr.length){alert("No newly uploaded images to download for this product.");return}
  arr.forEach((x,i)=>setTimeout(()=>{
    const a=document.createElement("a");a.href=x.url;a.download=x.name;document.body.appendChild(a);a.click();a.remove();
  },i*250));
}
function ensureProjectImages(project){
  if(!Array.isArray(project.images))project.images=[];
  if(!project.images.length&&project.image)project.images=[{file:project.image,primary:true}];
  if(project.images.length&&!project.images.some(image=>image.primary))project.images[0].primary=true;
  return project.images;
}
function projectPreviewSrc(image, projectIdx){
  if(image._pendingId){
    const pending=(pendingProjectFiles.get(projectIdx)||[]).find(file=>file.id===image._pendingId);
    if(pending)return pending.url;
  }
  return previewSrc(image,-1);
}
function renderProjectImages(project, projectIdx){
  const images=ensureProjectImages(project);
  if(!images.length)return `<div class="placeholder">No images yet. Use Upload Images above.</div>`;
  return images.map((image,imageIdx)=>{
    const src=projectPreviewSrc(image,projectIdx);
    return `<div class="image-card ${image.primary?"primary":""}">
      ${image.primary?`<span class="primary-badge">Primary image</span>`:""}
      <div class="image-preview">${src?`<img src="${safe(src)}" alt="">`:`<div class="placeholder">Preview unavailable until file is selected locally.</div>`}</div>
      <div class="image-meta">${safe(image.file||"")}</div>
      <div class="image-actions">
        <button type="button" class="btn small secondary" data-project-img-action="up" data-project-img-index="${imageIdx}">←</button>
        <button type="button" class="btn small secondary" data-project-img-action="down" data-project-img-index="${imageIdx}">→</button>
        <button type="button" class="btn small secondary" data-project-img-action="primary" data-project-img-index="${imageIdx}">${image.primary?"Primary":"Set Primary"}</button>
        <button type="button" class="btn small danger" data-project-img-action="remove" data-project-img-index="${imageIdx}">Remove</button>
      </div>
    </div>`;
  }).join("");
}
function syncProjectPrimary(project){
  ensureProjectImages(project);
  project.image=(project.images.find(image=>image.primary)||project.images[0]||{}).file||"";
}
function addUploadedProjectFiles(projectIdx, fileList){
  const project=state.projects[projectIdx], pending=pendingProjectFiles.get(projectIdx)||[];
  ensureProjectImages(project);
  [...fileList].forEach(file=>{
    const id="prf_"+Date.now()+"_"+Math.random().toString(36).slice(2);
    const name=cleanFileName(file.name)||("project-image-"+Date.now()+".jpg");
    pending.push({id,file,url:URL.createObjectURL(file),name});
    project.images.push({file:"images/projects/"+name,primary:project.images.length===0,_pendingId:id});
  });
  pendingProjectFiles.set(projectIdx,pending);syncProjectPrimary(project);
  persist("Project images added in editor");renderProjects();
}
function projectImageAction(projectIdx, imageIdx, action){
  const project=state.projects[projectIdx];ensureProjectImages(project);
  if(action==="up"&&imageIdx>0)[project.images[imageIdx-1],project.images[imageIdx]]=[project.images[imageIdx],project.images[imageIdx-1]];
  if(action==="down"&&imageIdx<project.images.length-1)[project.images[imageIdx+1],project.images[imageIdx]]=[project.images[imageIdx],project.images[imageIdx+1]];
  if(action==="primary")project.images.forEach((image,index)=>image.primary=index===imageIdx);
  if(action==="remove"){
    const removed=project.images.splice(imageIdx,1)[0];
    if(removed?._pendingId){
      const pending=pendingProjectFiles.get(projectIdx)||[], file=pending.find(entry=>entry.id===removed._pendingId);
      if(file)URL.revokeObjectURL(file.url);
      pendingProjectFiles.set(projectIdx,pending.filter(entry=>entry.id!==removed._pendingId));
    }
  }
  if(project.images.length&&!project.images.some(image=>image.primary))project.images[0].primary=true;
  syncProjectPrimary(project);persist();renderProjects();
}
function downloadPendingProjectImages(projectIdx){
  const pending=pendingProjectFiles.get(projectIdx)||[];
  if(!pending.length){alert("No newly uploaded images to download for this project.");return}
  pending.forEach((entry,index)=>setTimeout(()=>{
    const anchor=document.createElement("a");anchor.href=entry.url;anchor.download=entry.name;document.body.appendChild(anchor);anchor.click();anchor.remove();
  },index*250));
}

function renderProducts(filter=""){
  $("#productList").innerHTML=state.products.map((p,i)=>({p,i})).filter(x=>!filter||((x.p.title_th||"")+" "+(x.p.title_en||"")).toLowerCase().includes(filter.toLowerCase())).map(x=>itemShell(x.p.title_th||x.p.title_en,x.p.category,x.i,"products",productBody(x.p,x.i))).join("");
  bindItems();
}
function renderProjects(){
  $("#projectList").innerHTML=state.projects.map((p,i)=>itemShell(p.title_th||p.title_en,[p.location_th||p.category,p.year].filter(Boolean).join(" | "),i,"projects",projectBody(p,i))).join("");
  bindItems();
}
function renderBlogs(){
  $("#blogList").innerHTML=state.blogs.map((b,i)=>itemShell(b.title_th||b.title_en,b.date,i,"blogs",blogBody(b))).join("");
  bindItems();
}
function renderCertificates(){
  $("#certificateList").innerHTML=(state.certificates.items||[]).map((item,i)=>itemShell(item.title_en||item.title_th,"Certificate card",i,"certificates",certificateBody(item))).join("");
  bindItems();
}
function parseSections(v){return v.split("\n").map(x=>x.trim()).filter(Boolean).map(x=>{const q=x.split("::");return [q.shift().trim(),q.join("::").trim()]})}
function bindItems(){
  $$(".item").forEach(item=>{
    const kind=item.dataset.kind, idx=+item.dataset.index;
    item.querySelector('[data-action="edit"]').addEventListener("click",()=>item.querySelector(".editor").classList.toggle("open"));
    item.querySelector('[data-action="delete"]').addEventListener("click",()=>{if(confirm("Delete this item?")){(kind==="certificates"?state.certificates.items:state[kind]).splice(idx,1);persist();rerender(kind)}});
    item.querySelector('[data-action="up"]').addEventListener("click",()=>move(kind,idx,-1));
    item.querySelector('[data-action="down"]').addEventListener("click",()=>move(kind,idx,1));
    
    const upload=item.querySelector("[data-product-upload]");
    if(upload) upload.addEventListener("change",e=>{if(e.target.files?.length)addUploadedFiles(idx,e.target.files)});
    item.querySelectorAll("[data-img-action]").forEach(btn=>btn.addEventListener("click",()=>imageAction(idx,+btn.dataset.imgIndex,btn.dataset.imgAction,item)));
    const dl=item.querySelector("[data-download-product-images]");
    if(dl) dl.addEventListener("click",()=>downloadPendingImages(idx));
    const projectUpload=item.querySelector("[data-project-upload]");
    if(projectUpload) projectUpload.addEventListener("change",e=>{if(e.target.files?.length)addUploadedProjectFiles(idx,e.target.files)});
    item.querySelectorAll("[data-project-img-action]").forEach(btn=>btn.addEventListener("click",()=>projectImageAction(idx,+btn.dataset.projectImgIndex,btn.dataset.projectImgAction)));
    const projectDownload=item.querySelector("[data-download-project-images]");
    if(projectDownload) projectDownload.addEventListener("click",()=>downloadPendingProjectImages(idx));

    item.querySelector('[data-action="saveitem"]').addEventListener("click",()=>{
      const obj=(kind==="certificates"?state.certificates.items:state[kind])[idx];
      if(kind==="products") saveImageAltInputs(item,idx);
      item.querySelectorAll("[data-key]").forEach(el=>{
        const k=el.dataset.key;let v=el.value.trim();
        if(k==="features_th"||k==="features_en")v=v.split("|").map(x=>x.trim()).filter(Boolean);
        if(k==="sections_th"||k==="sections_en")v=parseSections(v);
        obj[k]=v;
      });
      if(kind==="products"){ensureImages(obj);obj.image=(obj.images.find(x=>x.primary)||obj.images[0]||{}).file||obj.image||"";}
      if(kind==="projects")syncProjectPrimary(obj);
      persist();rerender(kind);
    });
  });
}
function move(kind,idx,delta){
  const collection=kind==="certificates"?state.certificates.items:state[kind];const j=idx+delta;if(j<0||j>=collection.length)return;
  [collection[idx],collection[j]]=[collection[j],collection[idx]];if(kind==="products"){const product=collection[j];ensureImages(product);product.image=(product.images.find(x=>x.primary)||product.images[0]||{}).file||product.image||"";}
      persist();rerender(kind);
}
function rerender(kind){if(kind==="products")renderProducts($("#productSearch").value);if(kind==="projects")renderProjects();if(kind==="blogs")renderBlogs();if(kind==="certificates")renderCertificates()}
$("#productSearch").addEventListener("input",e=>renderProducts(e.target.value));
$("#addProduct").addEventListener("click",()=>{state.products.push({slug:"new-product",category:"sports",title_th:"สินค้าใหม่",title_en:"New Product",short_th:"",short_en:"",features_th:[],features_en:[],applications_th:"",applications_en:"",image:"",images:[]});persist();renderProducts()});
$("#addProject").addEventListener("click",()=>{state.projects.push({slug:"new-project",category:"project",title_th:"โครงการใหม่",title_en:"New Project",location_th:"ประเทศไทย",location_en:"Thailand",year:"",desc_th:"",desc_en:"",image:"",images:[]});persist();renderProjects()});
$("#addBlog").addEventListener("click",()=>{state.blogs.push({slug:"new-blog-post",date:new Date().toISOString().slice(0,10),title_th:"บทความใหม่",title_en:"New Blog Post",excerpt_th:"",excerpt_en:"",image:"images/your-blog.webp",sections_th:[],sections_en:[]});persist();renderBlogs()});
$("#addCertificate").addEventListener("click",()=>{state.certificates.items.push({title_th:"ใบรับรองใหม่",title_en:"New Certificate",text_th:"",text_en:""});persist();renderCertificates()});

function download(name,data){
  const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});
  const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),500);
}
function exportProducts(){return state.products.map(({category,title_th,title_en,short_th,short_en,features_th,features_en,...product})=>({...product,cat:category,th:title_th,en:title_en,dth:short_th,den:short_en,fth:features_th,fen:features_en}))}
function exportProjects(){return state.projects.map(({location_th,location_en,...project})=>({...project,loc_th:location_th,loc_en:location_en}))}
function exportBlogs(){return state.blogs.map(({sections_th,sections_en,...blog})=>({...blog,body_th:sections_th,body_en:sections_en}))}
$("#backupBtn").addEventListener("click",()=>download("hks-surfaces-content-backup.json",state));
$("#exportBtn").addEventListener("click",()=>{
  const active=$(".tab.active")?.dataset.tab||"home";
  if(active==="home"){homeFromFields();download("homepage-data.json",state.homepage)}
  if(active==="products")download("products-data.json",exportProducts());
  if(active==="projects")download("projects-data.json",exportProjects());
  if(active==="certificates"){certificatesFromFields();download("certificates-data.json",state.certificates)}
  if(active==="blog")download("blog-data.json",exportBlogs());
  if(active==="settings"){settingsFromFields();download("site-config.json",state.settings)}
  persist("Exported current section");
});
$("#previewBtn").addEventListener("click",()=>{homeFromFields();$("#pvTitle").textContent=state.homepage.hero_title_th;$("#pvSubtitle").textContent=state.homepage.hero_subtitle_th;$("#pvText").textContent=state.homepage.hero_text_th;$("#pvAboutTitle").textContent=state.homepage.about_title_th;$("#pvAboutText").textContent=state.homepage.about_text_th;switchTab("preview")});


$("#homeHeroUpload")?.addEventListener("change",e=>{
  const file=e.target.files?.[0];if(!file)return;
  if(pendingHeroFile)URL.revokeObjectURL(pendingHeroFile.url);
  const name=cleanFileName(file.name)||("hero-"+Date.now()+".jpg");
  pendingHeroFile={file,url:URL.createObjectURL(file),name};
  state.homepage.hero_image="images/home/"+name;
  $("#home_hero_image").value=state.homepage.hero_image;
  persist("Hero image added");renderHomeHero();
});
$("#downloadHeroImage")?.addEventListener("click",()=>{
  if(!pendingHeroFile){alert("No newly uploaded hero image to download.");return}
  const a=document.createElement("a");a.href=pendingHeroFile.url;a.download=pendingHeroFile.name;document.body.appendChild(a);a.click();a.remove();
});
$("#homeGalleryUpload")?.addEventListener("change",e=>{
  const files=[...(e.target.files||[])];if(!files.length)return;
  state.homepage.gallery_images=Array.isArray(state.homepage.gallery_images)?state.homepage.gallery_images:[];
  files.forEach(file=>{
    const id="hg_"+Date.now()+"_"+Math.random().toString(36).slice(2);
    const name=cleanFileName(file.name)||("home-gallery-"+Date.now()+".jpg");
    const obj={id,file,url:URL.createObjectURL(file),name};pendingHomeGalleryFiles.push(obj);
    state.homepage.gallery_images.push({file:"images/home/"+name,alt_th:"",alt_en:"",featured:state.homepage.gallery_images.length===0,_pendingId:id});
  });
  if(state.homepage.gallery_images.length&&!state.homepage.gallery_images.some(x=>x.featured))state.homepage.gallery_images[0].featured=true;
  persist("Homepage gallery images added");renderHomeGallery();
});
$("#downloadHomeGalleryImages")?.addEventListener("click",()=>downloadHomeFiles(pendingHomeGalleryFiles));

homeToFields();settingsToFields();certificatesToFields();renderProducts();renderProjects();renderCertificates();renderBlogs();
