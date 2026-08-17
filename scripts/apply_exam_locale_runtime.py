#!/usr/bin/env python3
"""Apply the locale-aware exam runtime migration deterministically.

This migration exists because the current CloudPath runtime is a large Vanilla JS /
Node codebase and the locale integration needs a few surgical changes across large
files. The script is intentionally idempotent and fails when expected source markers
change, so CI cannot silently apply a partial patch.

It patches:
- server.js: ready-bank loading, locale resolution, solo/live session locale locking
- js/simulados.js: locale propagation for catalog/start requests + explicit fallback
- js/socket-client.js: locale propagation when creating live practice-exam rooms
- js/simulado-live-host.js: live-room locale propagation + explicit fallback
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, context: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{context}: expected exactly one source marker, found {count}")
    return text.replace(old, new, 1)


def replace_after(text: str, marker: str, old: str, new: str, context: str) -> str:
    if marker not in text:
        raise RuntimeError(f"{context}: section marker not found")
    before, after = text.split(marker, 1)
    if old not in after:
        raise RuntimeError(f"{context}: source marker not found after section marker")
    after = after.replace(old, new, 1)
    return before + marker + after


def write_if_changed(path: Path, original: str, updated: str) -> bool:
    if original == updated:
        print(f"unchanged: {path.relative_to(ROOT)}")
        return False
    path.write_text(updated, encoding="utf-8")
    print(f"patched: {path.relative_to(ROOT)}")
    return True


def patch_server() -> bool:
    path = ROOT / "server.js"
    original = path.read_text(encoding="utf-8")
    if "function resolveExamPool(certId, level, requestedLocale)" in original:
        print("server.js: locale runtime already applied")
        return False

    text = original

    old_pool_block = """// Carrega as pools de perguntas (cert x nível) em memória
const examPools = new Map(); // chave: \"certId:level\" -> { certCode, certName, level, domains, questions }

function loadExamPools() {
    for (const [certId, cert] of Object.entries(CERTIFICATIONS)) {
        for (const level of cert.levels) {
            const filePath = path.join(__dirname, 'data', 'exams', certId, `${level}.json`);
            try {
                const raw = fs.readFileSync(filePath, 'utf-8');
                const pool = JSON.parse(raw);
                // Índice de tópicos (campo `topics` das questões) para prática focada
                pool.topicCounts = {};
                for (const q of pool.questions) {
                    for (const t of (q.topics || [])) {
                        pool.topicCounts[t] = (pool.topicCounts[t] || 0) + 1;
                    }
                }
                examPools.set(`${certId}:${level}`, pool);
            } catch (error) {
                console.log(`⚠️ Pool de simulado não encontrada: ${certId}/${level} (${error.message})`);
            }
        }
    }
    console.log(`📚 ${examPools.size} pools de simulado carregadas`);
}

loadExamPools();
"""

    new_pool_block = """// Carrega as pools de perguntas (cert x nível) em memória.
// PT-BR mantém a chave histórica `certId:level`; bancos EN prontos usam
// `en:certId:level`. Um banco inglês só entra no runtime quando declara
// explicitamente `_translation.status = ready`.
const examPools = new Map();

function normalizeExamLocale(locale) {
    const value = String(locale || '').trim().toLowerCase();
    return value === 'en' || value.startsWith('en-') ? 'en' : 'pt-BR';
}

function indexExamTopics(pool) {
    pool.topicCounts = {};
    for (const q of (pool.questions || [])) {
        for (const t of (q.topics || [])) {
            pool.topicCounts[t] = (pool.topicCounts[t] || 0) + 1;
        }
    }
    return pool;
}

function resolveExamPool(certId, level, requestedLocale) {
    const requested = normalizeExamLocale(requestedLocale);
    if (requested === 'en') {
        const english = examPools.get(`en:${certId}:${level}`);
        if (english && english.questions && english.questions.length) {
            return { pool: english, requestedLocale: 'en', locale: 'en', fallback: false };
        }
    }

    const canonical = examPools.get(`${certId}:${level}`) || null;
    return {
        pool: canonical,
        requestedLocale: requested,
        locale: 'pt-BR',
        fallback: requested === 'en',
    };
}

function loadExamPools() {
    for (const [certId, cert] of Object.entries(CERTIFICATIONS)) {
        for (const level of cert.levels) {
            const filePath = path.join(__dirname, 'data', 'exams', certId, `${level}.json`);
            try {
                const raw = fs.readFileSync(filePath, 'utf-8');
                const pool = indexExamTopics(JSON.parse(raw));
                examPools.set(`${certId}:${level}`, pool);
            } catch (error) {
                console.log(`⚠️ Pool de simulado não encontrada: ${certId}/${level} (${error.message})`);
            }

            const englishPath = path.join(__dirname, 'data', 'exams-en', certId, `${level}.json`);
            if (!fs.existsSync(englishPath)) continue;
            try {
                const english = indexExamTopics(JSON.parse(fs.readFileSync(englishPath, 'utf-8')));
                const meta = english._translation || {};
                if (meta.locale !== 'en' || meta.sourceLocale !== 'pt-BR' || meta.status !== 'ready') {
                    console.warn(`⚠️ Banco EN ignorado por status inválido: ${certId}/${level}`);
                    continue;
                }
                examPools.set(`en:${certId}:${level}`, english);
            } catch (error) {
                console.warn(`⚠️ Banco EN ignorado: ${certId}/${level} (${error.message})`);
            }
        }
    }
    const canonicalCount = [...examPools.keys()].filter(key => !key.startsWith('en:')).length;
    const englishCount = [...examPools.keys()].filter(key => key.startsWith('en:')).length;
    console.log(`📚 ${canonicalCount} pools PT-BR + ${englishCount} pools EN prontas carregadas`);
}

loadExamPools();
"""
    text = replace_once(text, old_pool_block, new_pool_block, "server exam-pool loader")

    cert_route_marker = "app.get('/api/simulado/certifications', (req, res) => {"
    text = replace_after(
        text,
        cert_route_marker,
        "\n    const certifications = Object.entries(CERTIFICATIONS).map(([id, cert]) => ({",
        "\n    const requestedLocale = normalizeExamLocale(req.query.locale);\n    const certifications = Object.entries(CERTIFICATIONS).map(([id, cert]) => ({",
        "server certifications locale",
    )
    text = replace_after(
        text,
        cert_route_marker,
        "            const pool = examPools.get(`${id}:${level}`);\n            return {",
        "            const resolved = resolveExamPool(id, level, requestedLocale);\n            const pool = resolved.pool;\n            return {",
        "server certifications pool resolution",
    )
    text = replace_after(
        text,
        cert_route_marker,
        "                id: level,\n                totalQuestions: pool ? pool.questions.length : 0,",
        "                id: level,\n                contentLocale: resolved.locale,\n                localeFallback: resolved.fallback,\n                totalQuestions: pool ? pool.questions.length : 0,",
        "server certifications locale metadata",
    )
    text = replace_after(
        text,
        cert_route_marker,
        "    res.json({ success: true, maxQuestions: MAX_SIMULADO_QUESTIONS, certifications });",
        "    res.json({ success: true, locale: requestedLocale, maxQuestions: MAX_SIMULADO_QUESTIONS, certifications });",
        "server certifications response",
    )

    start_marker = "app.post('/api/simulado/start', simuladoActionLimiter, async (req, res) => {"
    text = replace_after(
        text,
        start_marker,
        "    const { certId, level, numQuestions, domain } = req.body || {};",
        "    const { certId, level, numQuestions, domain, locale } = req.body || {};\n    const requestedLocale = normalizeExamLocale(locale);",
        "server start locale input",
    )
    text = replace_after(
        text,
        start_marker,
        "    const pool = examPools.get(`${certId}:${level}`);\n    if (!pool || pool.questions.length === 0) {",
        "    const resolvedPool = resolveExamPool(certId, level, requestedLocale);\n    const pool = resolvedPool.pool;\n    if (!pool || pool.questions.length === 0) {",
        "server start pool resolution",
    )
    text = replace_after(
        text,
        start_marker,
        "        certCode: pool.certCode,\n        certName: pool.certName,\n        domains: pool.domains,",
        "        certCode: pool.certCode,\n        certName: pool.certName,\n        requestedLocale,\n        locale: resolvedPool.locale,\n        localeFallback: resolvedPool.fallback,\n        domains: pool.domains,",
        "server active session locale lock",
    )
    text = replace_after(
        text,
        start_marker,
        "        certName: pool.certName,\n        level,\n        domains: pool.domains,",
        "        certName: pool.certName,\n        level,\n        requestedLocale,\n        locale: resolvedPool.locale,\n        localeFallback: resolvedPool.fallback,\n        domains: pool.domains,",
        "server start response locale metadata",
    )

    live_marker = "safeOn(socket, 'simulado:create-room', async (data, callback) => {"
    text = replace_after(
        text,
        live_marker,
        "            const { certId, level, numQuestions, creatorName, idToken } = data || {};",
        "            const { certId, level, numQuestions, creatorName, idToken, locale } = data || {};\n            const requestedLocale = normalizeExamLocale(locale);",
        "server live locale input",
    )
    text = replace_after(
        text,
        live_marker,
        "            const pool = examPools.get(`${certId}:${level}`);\n            if (!pool || pool.questions.length === 0) {",
        "            const resolvedPool = resolveExamPool(certId, level, requestedLocale);\n            const pool = resolvedPool.pool;\n            if (!pool || pool.questions.length === 0) {",
        "server live pool resolution",
    )
    text = replace_after(
        text,
        live_marker,
        "                certName: pool.certName,\n                level,\n                domains: pool.domains,",
        "                certName: pool.certName,\n                level,\n                requestedLocale,\n                locale: resolvedPool.locale,\n                localeFallback: resolvedPool.fallback,\n                domains: pool.domains,",
        "server live room locale lock",
    )
    text = replace_after(
        text,
        live_marker,
        "                certName: pool.certName,\n                level,\n                domains: pool.domains,\n                totalQuestions: questions.length",
        "                certName: pool.certName,\n                level,\n                requestedLocale,\n                locale: resolvedPool.locale,\n                localeFallback: resolvedPool.fallback,\n                domains: pool.domains,\n                totalQuestions: questions.length",
        "server live response locale metadata",
    )

    constructor_marker = "class LiveSimuladoRoom {"
    text = replace_after(
        text,
        constructor_marker,
        "        this.certName = simuladoData.certName;\n        this.level = simuladoData.level;\n        this.domains = simuladoData.domains;",
        "        this.certName = simuladoData.certName;\n        this.level = simuladoData.level;\n        this.requestedLocale = simuladoData.requestedLocale || 'pt-BR';\n        this.locale = simuladoData.locale || 'pt-BR';\n        this.localeFallback = !!simuladoData.localeFallback;\n        this.domains = simuladoData.domains;",
        "server live room constructor locale",
    )
    text = replace_after(
        text,
        constructor_marker,
        "            certName: this.certName,\n            level: this.level,\n            mode: 'live',",
        "            certName: this.certName,\n            level: this.level,\n            requestedLocale: this.requestedLocale,\n            locale: this.locale,\n            localeFallback: this.localeFallback,\n            mode: 'live',",
        "server live attempt locale metadata",
    )

    return write_if_changed(path, original, text)


def patch_simulados() -> bool:
    path = ROOT / "js" / "simulados.js"
    original = path.read_text(encoding="utf-8")
    if "function activeExamLocale()" in original:
        print("js/simulados.js: locale runtime already applied")
        return False

    text = original
    text = replace_once(
        text,
        "    const PASS_SCORE = 70;\n",
        "    const PASS_SCORE = 70;\n\n    function activeExamLocale() {\n        return (window.I18n && window.I18n.locale === 'en') ? 'en' : 'pt-BR';\n    }\n",
        "simulados locale helper",
    )
    text = replace_once(
        text,
        "            const res = await fetch('/api/simulado/certifications');",
        "            const locale = activeExamLocale();\n            const res = await fetch(`/api/simulado/certifications?locale=${encodeURIComponent(locale)}`);",
        "simulados certifications locale",
    )
    text = replace_once(
        text,
        "                    numQuestions,\n                    mode: startMode || undefined,",
        "                    numQuestions,\n                    locale: activeExamLocale(),\n                    mode: startMode || undefined,",
        "simulados start locale",
    )
    text = replace_once(
        text,
        "            currentSimulado = data;\n",
        "            currentSimulado = data;\n            if (data.localeFallback && activeExamLocale() === 'en') {\n                Utils.showToast('English questions are not available for this level yet. Portuguese content is being used for this session.', 'warning');\n            }\n",
        "simulados fallback notice",
    )
    # A locale change may refresh the selection catalog, but never swaps the bank
    # underneath an active or paused in-memory exam session.
    text = replace_once(
        text,
        "    // ============================================\n    // Carregamento de certificações\n    // ============================================\n",
        "    // ============================================\n    // Carregamento de certificações\n    // ============================================\n    document.addEventListener('cloudpath:localechange', () => {\n        if (!currentSimulado) loadCertifications();\n    });\n\n",
        "simulados locale refresh",
    )
    return write_if_changed(path, original, text)


def patch_socket_client() -> bool:
    path = ROOT / "js" / "socket-client.js"
    original = path.read_text(encoding="utf-8")
    if "createLiveSimuladoRoom(certId, level, numQuestions, creatorName, creatorId, idToken, locale, callback)" in original:
        print("js/socket-client.js: locale runtime already applied")
        return False
    text = original
    text = replace_once(
        text,
        "    createLiveSimuladoRoom(certId, level, numQuestions, creatorName, creatorId, idToken, callback) {",
        "    createLiveSimuladoRoom(certId, level, numQuestions, creatorName, creatorId, idToken, locale, callback) {",
        "socket client live locale signature",
    )
    text = replace_once(
        text,
        "        this.emit('simulado:create-room', { certId, level, numQuestions, creatorName, creatorId, idToken }, (response) => {",
        "        this.emit('simulado:create-room', { certId, level, numQuestions, creatorName, creatorId, idToken, locale }, (response) => {",
        "socket client live locale payload",
    )
    return write_if_changed(path, original, text)


def patch_live_host() -> bool:
    path = ROOT / "js" / "simulado-live-host.js"
    original = path.read_text(encoding="utf-8")
    if "function activeExamLocale()" in original:
        print("js/simulado-live-host.js: locale runtime already applied")
        return False
    text = original
    text = replace_once(
        text,
        "    const PASS_SCORE = 70;\n",
        "    const PASS_SCORE = 70;\n\n    function activeExamLocale() {\n        return (window.I18n && window.I18n.locale === 'en') ? 'en' : 'pt-BR';\n    }\n",
        "live host locale helper",
    )
    text = replace_once(
        text,
        "            socketClient.createLiveSimuladoRoom(certId, level, numQuestions, user.displayName || 'Professor', user.uid, idToken, (response) => {",
        "            socketClient.createLiveSimuladoRoom(certId, level, numQuestions, user.displayName || 'Professor', user.uid, idToken, activeExamLocale(), (response) => {",
        "live host locale propagation",
    )
    text = replace_once(
        text,
        "                session = response;\n",
        "                session = response;\n                if (response.localeFallback && activeExamLocale() === 'en') {\n                    Utils.showToast('English questions are not available for this level yet. The live room will use Portuguese content.', 'warning');\n                }\n",
        "live host fallback notice",
    )
    return write_if_changed(path, original, text)


def main() -> int:
    changed = []
    for label, func in (
        ("server.js", patch_server),
        ("js/simulados.js", patch_simulados),
        ("js/socket-client.js", patch_socket_client),
        ("js/simulado-live-host.js", patch_live_host),
    ):
        if func():
            changed.append(label)
    print("Locale runtime migration complete. Changed: " + (", ".join(changed) if changed else "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
