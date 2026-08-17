#!/usr/bin/env python3
"""Add /en route support, path-aware locale selection, hreflang and EN metadata."""
from __future__ import annotations
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SERVER=ROOT/'server.js'; I18N=ROOT/'js'/'i18n.js'
PUBLIC=['index.html','trilha.html','trilha-dea.html','trilha-dva.html','trilha-saa.html','simulados.html','cloudarena.html']

SERVER_MARKER='// CLOUDPATH_INDEXABLE_EN_ROUTES'
SERVER_BLOCK=r'''// CLOUDPATH_INDEXABLE_EN_ROUTES
const EN_PAGE_METADATA = {
    'index.html': ['CloudPath | AWS Certification Study Platform', 'Study for AWS certifications with guided learning paths, practice exams, progress tracking and CloudArena challenges.'],
    'trilha.html': ['CloudPath | AWS Cloud Practitioner Study Path', 'Study AWS Cloud Practitioner concepts through a structured CloudPath learning path.'],
    'trilha-dea.html': ['CloudPath | AWS Data Engineer Associate Study Path', 'Study for AWS Certified Data Engineer - Associate with structured CloudPath learning content.'],
    'trilha-dva.html': ['CloudPath | AWS Developer Associate Study Path', 'Study for AWS Certified Developer - Associate with structured CloudPath learning content.'],
    'trilha-saa.html': ['CloudPath | AWS Solutions Architect Associate Study Path', 'Study for AWS Certified Solutions Architect - Associate with structured CloudPath learning content.'],
    'simulados.html': ['CloudPath | AWS Practice Exams', 'Practice AWS certification questions in Exam Mode or Study Mode with progress and review.'],
    'cloudarena.html': ['CloudPath | CloudArena AWS Challenge', 'Challenge your AWS knowledge in CloudArena with interactive certification battles.'],
};

function escapeHtmlAttribute(value) {
    return String(value).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function renderEnglishHtml(fileName, req) {
    const filePath = path.join(__dirname, fileName);
    let html = fs.readFileSync(filePath, 'utf8');
    const ptPath = fileName === 'index.html' ? '/' : `/${fileName}`;
    const enPath = fileName === 'index.html' ? '/en/' : `/en/${fileName}`;
    const origin = `${req.protocol}://${req.get('host')}`;
    const canonical = `${origin}${enPath}`;
    const ptUrl = `${origin}${ptPath}`;
    const enUrl = canonical;
    const metadata = EN_PAGE_METADATA[fileName];

    html = html.replace(/<html\b([^>]*?)\blang=["'][^"']*["']([^>]*)>/i, '<html$1lang="en"$2>');
    if (metadata) {
        html = html.replace(/<title>[\s\S]*?<\/title>/i, `<title>${metadata[0]}</title>`);
        const description = `<meta name="description" content="${escapeHtmlAttribute(metadata[1])}">`;
        if (/<meta\b[^>]*\bname=["']description["'][^>]*>/i.test(html)) {
            html = html.replace(/<meta\b[^>]*\bname=["']description["'][^>]*>/i, description);
        } else {
            html = html.replace('</head>', `    ${description}\n</head>`);
        }
    }

    const canonicalTag = `<link rel="canonical" href="${escapeHtmlAttribute(canonical)}">`;
    if (/<link\b[^>]*\brel=["']canonical["'][^>]*>/i.test(html)) {
        html = html.replace(/<link\b[^>]*\brel=["']canonical["'][^>]*>/i, canonicalTag);
    } else {
        html = html.replace('</head>', `    ${canonicalTag}\n</head>`);
    }
    html = html.replace(/\s*<link\b[^>]*data-cloudpath-hreflang[^>]*>/gi, '');
    const alternates = [
        `<link data-cloudpath-hreflang rel="alternate" hreflang="pt-BR" href="${escapeHtmlAttribute(ptUrl)}">`,
        `<link data-cloudpath-hreflang rel="alternate" hreflang="en" href="${escapeHtmlAttribute(enUrl)}">`,
        `<link data-cloudpath-hreflang rel="alternate" hreflang="x-default" href="${escapeHtmlAttribute(ptUrl)}">`,
    ].join('\n    ');
    html = html.replace('</head>', `    ${alternates}\n</head>`);
    return html;
}

app.use((req, res, next) => {
    if (!['GET', 'HEAD'].includes(req.method) || !(req.path === '/en' || req.path.startsWith('/en/'))) {
        return next();
    }
    let localizedPath = req.path.slice(3) || '/';
    if (!localizedPath.startsWith('/')) localizedPath = `/${localizedPath}`;
    const fileName = localizedPath === '/' ? 'index.html' : localizedPath.replace(/^\/+/, '');
    if (!fileName.includes('/') && fileName.endsWith('.html')) {
        const filePath = path.join(__dirname, fileName);
        if (fs.existsSync(filePath)) {
            res.type('html').send(renderEnglishHtml(fileName, req));
            return;
        }
    }
    if (localizedPath === '/') {
        res.type('html').send(renderEnglishHtml('index.html', req));
        return;
    }
    const queryIndex = req.url.indexOf('?');
    const query = queryIndex >= 0 ? req.url.slice(queryIndex) : '';
    req.url = localizedPath + query;
    next();
});

'''

I18N_MARKER='// CLOUDPATH_ROUTE_LOCALE_SYNC'
I18N_BLOCK=r'''// CLOUDPATH_ROUTE_LOCALE_SYNC
    const cloudPathRouteIsEnglish = location.pathname === '/en' || location.pathname.startsWith('/en/');
    let cloudPathInjectedLangParam = false;
    if (cloudPathRouteIsEnglish) {
        const routeUrl = new URL(location.href);
        if (!routeUrl.searchParams.has('lang')) {
            routeUrl.searchParams.set('lang', 'en');
            history.replaceState(history.state, '', routeUrl);
            cloudPathInjectedLangParam = true;
        }
    }

    function cloudPathSyncLocaleRouteLinks() {
        const selected = String(window.I18n?.locale || document.documentElement.lang || 'pt-BR').toLowerCase().startsWith('en') ? 'en' : 'pt-BR';
        const wantsEnglish = selected === 'en';
        for (const anchor of document.querySelectorAll('a[href]')) {
            const raw = anchor.getAttribute('href');
            if (!raw || raw.startsWith('#') || raw.startsWith('mailto:') || raw.startsWith('tel:') || raw.startsWith('javascript:')) continue;
            let url;
            try { url = new URL(raw, location.href); } catch { continue; }
            if (url.origin !== location.origin) continue;
            let pathname = url.pathname;
            const eligible = pathname === '/' || pathname === '/en/' || pathname.endsWith('.html');
            if (!eligible) continue;
            if (wantsEnglish && !(pathname === '/en' || pathname.startsWith('/en/'))) {
                pathname = pathname === '/' ? '/en/' : `/en${pathname}`;
            } else if (!wantsEnglish && (pathname === '/en' || pathname.startsWith('/en/'))) {
                pathname = pathname.slice(3) || '/';
                if (!pathname.startsWith('/')) pathname = `/${pathname}`;
            }
            anchor.setAttribute('href', `${pathname}${url.search}${url.hash}`);
        }
    }

    document.addEventListener('cloudpath:i18nready', () => {
        if (cloudPathInjectedLangParam) {
            const cleanUrl = new URL(location.href);
            cleanUrl.searchParams.delete('lang');
            history.replaceState(history.state, '', cleanUrl);
            cloudPathInjectedLangParam = false;
        }
        cloudPathSyncLocaleRouteLinks();
    });
    document.addEventListener('cloudpath:localechange', () => {
        const selected = String(window.I18n?.locale || 'pt-BR').toLowerCase().startsWith('en') ? 'en' : 'pt-BR';
        let pathname = location.pathname;
        if (selected === 'en' && !(pathname === '/en' || pathname.startsWith('/en/'))) {
            pathname = pathname === '/' ? '/en/' : `/en${pathname}`;
        } else if (selected !== 'en' && (pathname === '/en' || pathname.startsWith('/en/'))) {
            pathname = pathname.slice(3) || '/';
            if (!pathname.startsWith('/')) pathname = `/${pathname}`;
        }
        if (pathname !== location.pathname) history.replaceState(history.state, '', `${pathname}${location.search}${location.hash}`);
        cloudPathSyncLocaleRouteLinks();
    });

'''

def patch_server():
    text=SERVER.read_text(encoding='utf-8')
    if SERVER_MARKER in text: return False
    marker='app.use(express.static(path.join(__dirname)));'
    if text.count(marker)!=1: raise RuntimeError(f'server static marker expected once, found {text.count(marker)}')
    SERVER.write_text(text.replace(marker,SERVER_BLOCK+marker,1),encoding='utf-8'); return True

def patch_i18n():
    text=I18N.read_text(encoding='utf-8')
    if I18N_MARKER in text: return False
    marker="    'use strict';\n"
    if text.count(marker)!=1:
        marker="'use strict';\n"
        if text.count(marker)!=1: raise RuntimeError('i18n use-strict marker not found uniquely')
    I18N.write_text(text.replace(marker,marker+I18N_BLOCK,1),encoding='utf-8'); return True

def inject_hreflang():
    changed=0
    for name in PUBLIC:
        path=ROOT/name
        if not path.exists(): continue
        text=path.read_text(encoding='utf-8')
        if 'data-cloudpath-hreflang' in text: continue
        pt='/' if name=='index.html' else f'/{name}'; en='/en/' if name=='index.html' else f'/en/{name}'
        tags=(f'    <link data-cloudpath-hreflang rel="alternate" hreflang="pt-BR" href="{pt}">\n'
              f'    <link data-cloudpath-hreflang rel="alternate" hreflang="en" href="{en}">\n'
              f'    <link data-cloudpath-hreflang rel="alternate" hreflang="x-default" href="{pt}">\n')
        if text.count('</head>')!=1: raise RuntimeError(f'{name}: expected one </head>')
        path.write_text(text.replace('</head>',tags+'</head>',1),encoding='utf-8'); changed+=1
    return changed

def patch_sitemap():
    path=ROOT/'sitemap.xml'
    if not path.exists(): return False
    text=path.read_text(encoding='utf-8')
    if '<!-- cloudpath-en-routes -->' in text: return False
    urls=re.findall(r'<loc>(https?://[^<]+)</loc>',text)
    if not urls: return False
    origin=re.match(r'(https?://[^/]+)',urls[0]).group(1)
    entries=[]
    for name in PUBLIC:
        en='/en/' if name=='index.html' else f'/en/{name}'
        absolute=origin+en
        if absolute not in urls: entries.append(f'  <url><loc>{absolute}</loc></url>')
    if not entries: return False
    marker='</urlset>'
    text=text.replace(marker,'  <!-- cloudpath-en-routes -->\n'+'\n'.join(entries)+'\n'+marker,1)
    path.write_text(text,encoding='utf-8'); return True

def main():
    print('server', 'patched' if patch_server() else 'current')
    print('i18n', 'patched' if patch_i18n() else 'current')
    print('hreflang pages patched:',inject_hreflang())
    print('sitemap', 'patched' if patch_sitemap() else 'current/absent')
    return 0
if __name__=='__main__': raise SystemExit(main())
