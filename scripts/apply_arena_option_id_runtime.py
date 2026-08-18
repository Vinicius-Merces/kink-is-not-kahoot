#!/usr/bin/env python3
"""Switch the CloudArena server resolver from literal matchText to stable optionId.

The overlay migration guarantees IDs in the form:
    <questionId>:option:<zero-based-index>

After this patch, `matchText` remains readable metadata in breakdown JSON only.
Question wording can change without breaking metadata attachment.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server.js"

OLD_COMMENT = """// /data é bloqueado no static (gabaritos); o jogo recebe daqui apenas as
// questões QUE TÊM overlay, já resolvidas (vínculo por texto + checagem de
// gabarito feita no servidor). Uma chamada por arena; zero por batalha.
"""

NEW_COMMENT = """// /data é bloqueado no static (gabaritos); o jogo recebe daqui apenas as
// questões QUE TÊM overlay, já resolvidas por optionId estável + checagem de
// gabarito feita no servidor. matchText é apenas metadado legível.
// Uma chamada por arena; zero por batalha.
"""

OLD_RESOLVER = """                // vínculo por TEXTO + checagem cruzada de gabarito
                const resolved = q.options.map(optionText => {
                    const meta = (ov.options || []).find(o => o.matchText === optionText);
                    return meta ? { text: optionText, stage: meta.stage, reasonWrong: meta.reasonWrong || '' } : null;
                });
                const correctMeta = resolved.find(o => o && o.stage === 'correct');
                if (resolved.some(o => !o) || !correctMeta || correctMeta.text !== q.options[q.correct]) {
                    console.error(`[CloudArena] overlay desalinhado ignorado: ${q.id}`);
                    continue;
                }
"""

NEW_RESOLVER = """                // vínculo por ID estável + checagem cruzada de gabarito.
                // O texto pode evoluir ou ser localizado sem alterar a identidade.
                const resolved = q.options.map((optionText, optionIndex) => {
                    const expectedOptionId = `${q.id}:option:${optionIndex}`;
                    const meta = (ov.options || []).find(o => o.optionId === expectedOptionId);
                    return meta ? {
                        optionId: expectedOptionId,
                        text: optionText,
                        stage: meta.stage,
                        reasonWrong: meta.reasonWrong || ''
                    } : null;
                });
                const correctOptionId = `${q.id}:option:${q.correct}`;
                const correctMeta = resolved.find(o => o && o.stage === 'correct');
                if (resolved.some(o => !o) || !correctMeta || correctMeta.optionId !== correctOptionId) {
                    console.error(`[CloudArena] overlay desalinhado por optionId ignorado: ${q.id}`);
                    continue;
                }
"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one source marker, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    original = SERVER.read_text(encoding="utf-8")
    if "overlay desalinhado por optionId ignorado" in original:
        print("server.js: CloudArena optionId runtime already applied")
        return 0

    updated = original
    if OLD_COMMENT in updated:
        updated = replace_once(updated, OLD_COMMENT, NEW_COMMENT, "CloudArena route comment")
    updated = replace_once(updated, OLD_RESOLVER, NEW_RESOLVER, "CloudArena option resolver")

    SERVER.write_text(updated, encoding="utf-8")
    print("patched: server.js CloudArena now resolves overlays by stable optionId")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
