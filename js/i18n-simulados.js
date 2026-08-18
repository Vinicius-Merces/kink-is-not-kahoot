/** CloudPath Simulados UI adapter.
 *
 * This translates the simulator chrome only. Question text, answer options,
 * explanations and domain/topic names remain content-layer data until the exam
 * banks are migrated to locale-specific datasets.
 */
(function (global) {
    'use strict';
    if (!global.I18n) return;

    const q = (selector, root = document) => root.querySelector(selector);
    const qa = (selector, root = document) => Array.from(root.querySelectorAll(selector));
    const t = (key, params) => global.I18n.t(key, params);

    function setText(el, value) {
        if (el && el.textContent !== value) el.textContent = value;
    }

    function text(selector, key, params) {
        setText(q(selector), t(key, params));
    }

    function html(selector, key) {
        const el = q(selector);
        const value = t(key);
        if (el && el.innerHTML !== value) el.innerHTML = value;
    }

    function attr(selector, name, key, params) {
        const el = q(selector);
        const value = t(key, params);
        if (el && el.getAttribute(name) !== value) el.setAttribute(name, value);
    }

    function translatedLevel(value) {
        const raw = String(value || '').trim().toLowerCase();
        if (['iniciante', 'beginner'].includes(raw)) return t('exam.beginner');
        if (['médio', 'medio', 'intermediate'].includes(raw)) return t('exam.intermediate');
        if (['avançado', 'avancado', 'advanced'].includes(raw)) return t('exam.advanced');
        return value;
    }

    function counterHeading(selector, key, counterId) {
        const el = q(selector);
        if (!el) return;
        const counter = q(`#${counterId}`, el);
        const value = counter ? counter.textContent : '0';
        const expected = `${t(key)} (${value})`;
        if (el.textContent.trim() === expected) return;
        el.innerHTML = `${t(key)} (<span id="${counterId}">${value}</span>)`;
    }

    function localizeStatic() {
        if (!q('#selectionScreen')) return;

        document.title = t('exam.metaTitle');
        text('.page-header h1', 'exam.ui.pageTitle');
        text('.page-header p', 'exam.ui.pageDescription');
        text('#simuladoModeToggle [data-mode="solo"]', 'exam.ui.soloMode');
        text('#simuladoModeToggle [data-mode="live"]', 'exam.ui.teacherMode');
        text('#certGrid .loading-spinner p', 'exam.ui.loadingCertifications');
        text('#feedbackModeToggle [data-feedback-mode="exam"]', 'exam.ui.examMode');
        text('#feedbackModeToggle [data-feedback-mode="study"]', 'exam.ui.studyMode');
        html('#feedbackModeHint', 'exam.ui.feedbackHintHtml');

        const countLabel = q('.question-count-control label');
        const max = q('#maxQuestionsLabel');
        if (countLabel && max && countLabel.dataset.i18nReady !== global.I18n.locale) {
            const currentMax = max.textContent;
            countLabel.innerHTML = `${t('exam.ui.questionCountPrefix')} <span id="maxQuestionsLabel">${currentMax}</span>)`;
            countLabel.dataset.i18nReady = global.I18n.locale;
        }
        const countValue = q('.question-count-value');
        const value = q('#numQuestionsValue');
        if (countValue && value && countValue.dataset.i18nReady !== global.I18n.locale) {
            const currentValue = value.textContent;
            countValue.innerHTML = `<span id="numQuestionsValue">${currentValue}</span> ${t('exam.ui.questions')}`;
            countValue.dataset.i18nReady = global.I18n.locale;
        }

        html('.exam-real-toggle > span', 'exam.ui.realExamHtml');
        const startBtn = q('#startSimuladoBtn');
        setText(startBtn, startBtn && startBtn.disabled ? t('exam.runtime.preparing') : t('exam.ui.startExam'));
        text('#reviewErrorsBtn', 'exam.ui.reviewErrors');
        text('#createLiveRoomBtn', 'exam.ui.createLiveRoom');

        text('#examPauseBtn', 'exam.ui.pause');
        attr('#examPauseBtn', 'title', 'exam.ui.pauseTitle');
        text('#examReportBtn', 'exam.ui.reportError');
        attr('.opt-layout-toggle', 'aria-label', 'exam.ui.optionLayout');
        attr('.olt-btn[data-sim-layout="list"]', 'title', 'exam.ui.listLayout');
        attr('.olt-btn[data-sim-layout="grid"]', 'title', 'exam.ui.gridLayout');
        text('#prevQuestionBtn', 'exam.ui.previous');
        text('#nextQuestionBtn', 'exam.ui.next');
        const finishBtn = q('#finishExamBtn');
        setText(finishBtn, finishBtn && finishBtn.disabled ? t('exam.runtime.correcting') : t('exam.ui.finishExam'));

        text('#resultScreen .form-card:nth-of-type(2) h3', 'exam.ui.domainPerformance');
        text('#topicBreakdownCard h3', 'exam.ui.topicPerformance');
        text('#topicBreakdownCard .topic-breakdown-hint', 'exam.ui.topicHint');
        text('#resultScreen .form-card:nth-of-type(4) h3', 'exam.ui.questionReview');
        text('#restartSimuladoBtn', 'exam.ui.restartExam');

        text('#liveHostScreen h2', 'exam.live.roomTitle');
        text('#copyLiveLinkBtn', 'exam.live.copyLink');
        text('#liveHostScreen .live-room-hint', 'exam.live.shareHint');
        counterHeading('#liveHostScreen .players-waiting h3', 'exam.live.studentsRoom', 'liveHostPlayerCount');
        text('#startLiveSessionBtn', 'exam.live.startVoting');
        text('#cancelLiveRoomBtn', 'exam.live.cancelRoom');

        text('#liveControlReportBtn', 'exam.ui.reportError');
        text('#liveControlResults h3', 'exam.live.classResult');
        text('#liveBackToCurrentBtn', 'exam.live.backCurrent');
        text('#liveRevoteBtn', 'exam.live.revote');
        text('#liveAdvanceBtn', 'exam.live.advance');
        text('#liveEndSessionBtn', 'exam.live.endExam');
        counterHeading('.live-control-sidebar .control-card:first-child h3', 'exam.live.students', 'liveControlPlayerCount');
        text('.live-control-sidebar .control-card:last-child h3', 'exam.live.questionsHeading');

        text('#liveResultScreen .form-card:nth-of-type(2) h3', 'exam.live.classDomainPerformance');
        text('#liveResultScreen .form-card:nth-of-type(3) h3', 'exam.ui.questionReview');
        text('#restartLiveSimuladoBtn', 'exam.live.newLiveExam');

        text('#confirmFinishTitle', 'exam.ui.finishTitle');
        text('#confirmFinishYes', 'exam.ui.finishYes');
        text('#confirmFinishNo', 'exam.ui.keepAnswering');
    }

    function localizeConfigTitle() {
        const el = q('#configCertName');
        if (!el) return;
        const parts = el.textContent.split('—');
        if (parts.length < 2) {
            setText(el, t('exam.ui.configure'));
            return;
        }
        const certName = parts.slice(1).join('—').trim();
        setText(el, `${t('exam.ui.configure')} — ${certName}`);
    }

    function localizeLevels() {
        qa('#levelSelector .level-btn').forEach(btn => {
            const levelId = btn.dataset.levelId;
            const small = q('small', btn);
            const match = small ? small.textContent.match(/\d+/) : null;
            const count = match ? match[0] : '';
            const key = levelId === 'iniciante' ? 'exam.beginner'
                : levelId === 'medio' ? 'exam.intermediate'
                    : levelId === 'avancado' ? 'exam.advanced' : null;
            if (!key) return;

            const labelNode = Array.from(btn.childNodes)
                .find(node => node.nodeType === Node.TEXT_NODE && node.textContent.trim());
            if (labelNode) {
                const desired = `\n                ${t(key)}\n                `;
                if (labelNode.nodeValue !== desired) labelNode.nodeValue = desired;
            }
            if (small && count) setText(small, `${count} ${t('exam.ui.questions')}`);
        });
    }

    function localizeCertBadge() {
        const badge = q('#examCertBadge');
        if (!badge) return;
        const match = badge.textContent.trim().match(/^(.+?)\s*•\s*(.+)$/);
        if (!match) return;
        setText(badge, `${match[1].trim()} • ${translatedLevel(match[2])}`);
    }

    function localizeResumeBanner() {
        const resume = q('#resumeSimuladoBanner');
        if (!resume || resume.style.display === 'none') return;
        setText(q('strong', resume), t('exam.ui.pausedExam'));
        text('#resumeSimuladoBtn', 'exam.ui.resume');
        text('#discardSimuladoBtn', 'exam.ui.discard');

        const small = q('small', resume);
        if (!small) return;
        if (!small.dataset.resumeCert) {
            const match = small.textContent.match(/^(.+?)\s*·\s*(.+?)\s*—\s*(\d+)\/(\d+).*?(\d+)\s*min/i);
            if (match) {
                small.dataset.resumeCert = match[1].trim();
                small.dataset.resumeLevel = match[2].trim();
                small.dataset.resumeAnswered = match[3];
                small.dataset.resumeTotal = match[4];
                small.dataset.resumeMinutes = match[5];
            }
        }
        if (small.dataset.resumeCert) {
            setText(small, t('exam.runtime.resumeDetails', {
                cert: small.dataset.resumeCert,
                level: translatedLevel(small.dataset.resumeLevel),
                answered: small.dataset.resumeAnswered,
                total: small.dataset.resumeTotal,
                minutes: small.dataset.resumeMinutes
            }));
        }
    }

    function localizeLoadError() {
        const state = q('#certGrid .empty-state');
        if (!state) return;
        setText(q('h3', state), t('exam.runtime.loadErrorTitle'));
        setText(q('p', state), t('exam.runtime.loadErrorDescription'));
    }

    function localizeResultSummary() {
        const title = q('#resultTitle');
        const circle = q('#resultScoreCircle');
        if (title && circle) {
            setText(title, circle.classList.contains('pass') ? t('exam.result.passed') : t('exam.result.keepStudying'));
        }

        const subtitle = q('#resultSubtitle');
        if (subtitle && subtitle.textContent.trim()) {
            if (!subtitle.dataset.resultCorrect) {
                const match = subtitle.textContent.match(/^(\d+)\s+(?:de|of)\s+(\d+).*?—\s*([A-Z0-9-]+)\s*\((.+?)\).*?(\d+)%/i);
                if (match) {
                    subtitle.dataset.resultCorrect = match[1];
                    subtitle.dataset.resultTotal = match[2];
                    subtitle.dataset.resultCert = match[3];
                    subtitle.dataset.resultLevel = match[4];
                    subtitle.dataset.resultPass = match[5];
                }
            }
            if (subtitle.dataset.resultCorrect) {
                setText(subtitle, t('exam.result.subtitle', {
                    correct: subtitle.dataset.resultCorrect,
                    total: subtitle.dataset.resultTotal,
                    cert: subtitle.dataset.resultCert,
                    level: translatedLevel(subtitle.dataset.resultLevel),
                    pass: subtitle.dataset.resultPass
                }));
            }
        }

        qa('#domainBreakdown .domain-result-header small').forEach(small => {
            const match = small.textContent.match(/(\d+)%/);
            if (match) setText(small, `(${t('exam.result.weight', { percent: match[1] })})`);
        });

        qa('#domainBreakdown .domain-review-links').forEach(wrap => {
            let prefix = Array.from(wrap.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
            if (!prefix) {
                prefix = document.createTextNode('');
                wrap.prepend(prefix);
            }
            const desired = `\n                        ${t('exam.result.reviewPrefix')}\n                        `;
            if (prefix.nodeValue !== desired) prefix.nodeValue = desired;
            qa('.domain-review-link', wrap).forEach(link => {
                const number = link.textContent.match(/\d+/)?.[0];
                if (number) setText(link, t('exam.result.chapter', { number }));
            });
        });

        qa('#topicBreakdown .topic-practice-link').forEach(link => setText(link, t('exam.result.practice')));

        qa('#reviewList .review-item').forEach((item, index) => {
            setText(q('.review-index', item), t('exam.result.question', { number: index + 1 }));
            setText(q('.review-status', item), item.classList.contains('correct')
                ? t('exam.result.correctStatus') : t('exam.result.incorrectStatus'));
            setText(q('.review-no-answer', item), t('exam.result.noAnswer'));
            setText(q('.review-explanation strong', item), t('exam.result.explanation'));
        });
    }

    function localizeFinishReviewSummary() {
        qa('#finishReviewSummary .finish-review-group').forEach(group => {
            const blank = qa('.finish-review-chip.blank', group);
            const flagged = qa('.finish-review-chip.flagged', group);
            const strong = q('strong', group);
            if (blank.length && strong) {
                setText(strong, t('exam.result.unansweredGroup', { count: blank.length }));
            } else if (flagged.length && strong) {
                setText(strong, t('exam.result.markedGroup', { count: flagged.length }));
            } else if (!blank.length && !flagged.length) {
                setText(group, t('exam.result.noPending'));
            }
        });
    }

    function localizeRuntimeControls() {
        const startBtn = q('#startSimuladoBtn');
        if (startBtn && startBtn.disabled) setText(startBtn, t('exam.runtime.preparing'));
        const finishBtn = q('#finishExamBtn');
        if (finishBtn && finishBtn.disabled) setText(finishBtn, t('exam.runtime.correcting'));
    }

    function localizeDynamic() {
        localizeConfigTitle();
        localizeLevels();
        localizeCertBadge();
        localizeResumeBanner();
        localizeLoadError();
        localizeRuntimeControls();
        localizeResultSummary();
        localizeFinishReviewSummary();

        text('#domainPreview h4', 'exam.ui.domainDistribution');
        text('#domainPreview .placeholder', 'exam.ui.noDomains');

        const focus = q('#domainFocusBanner .domain-focus-text');
        if (focus) {
            const strong = q('strong', focus);
            const first = Array.from(focus.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
            if (strong && first) {
                const desired = `${t('exam.ui.focusedPractice')} `;
                if (first.nodeValue !== desired) first.nodeValue = desired;
            }
        }
        attr('#clearDomainFocus', 'title', 'exam.ui.clearFocus');

        [q('#examProgressLabel'), q('#liveControlProgress')].forEach(progress => {
            if (!progress) return;
            const nums = progress.textContent.match(/\d+/g);
            if (!nums || nums.length < 2) return;
            setText(progress, t('exam.ui.questionProgress', { current: nums[0], total: nums[1] }));
        });

        qa('#examQuestionDots .exam-dot, #liveControlQuestionDots .exam-dot').forEach(dot => {
            const number = dot.dataset.index ? Number(dot.dataset.index) + 1 : Number(dot.textContent.trim());
            if (!Number.isFinite(number)) return;
            const answered = dot.classList.contains('answered');
            const title = t('exam.ui.questionNumber', { number });
            if (dot.title !== title) dot.title = title;
            const aria = answered ? t('exam.ui.questionAnswered', { number }) : title;
            if (dot.getAttribute('aria-label') !== aria) dot.setAttribute('aria-label', aria);
        });

        const mark = q('#examMarkBtn');
        if (mark && mark.style.display !== 'none') {
            setText(mark, mark.classList.contains('active') ? t('exam.ui.markedReview') : t('exam.ui.markReview'));
        }

        const multi = q('#examMultiHint');
        if (multi && multi.style.display !== 'none') {
            const nums = multi.textContent.match(/\d+/g);
            if (nums && nums.length >= 3) {
                setText(multi, t('exam.ui.multiAnswer', {
                    required: nums[0], selected: nums[1], total: nums[2]
                }));
            }
        }

        const feedbackTitle = q('#examFeedback .exam-feedback-title');
        if (feedbackTitle) {
            setText(feedbackTitle, q('#examFeedback.correct')
                ? t('exam.ui.correctAnswer') : t('exam.ui.incorrectAnswer'));
        }

        const finishMessage = q('#confirmFinishMessage');
        if (finishMessage && finishMessage.textContent.trim()) {
            const nums = finishMessage.textContent.match(/\d+/g);
            if (nums && nums.length >= 2) {
                setText(finishMessage, t('exam.ui.finishIncomplete', { answered: nums[0], total: nums[1] }));
            } else if (nums && nums.length === 1) {
                setText(finishMessage, t('exam.ui.finishComplete', { total: nums[0] }));
            }
        }
    }

    function localizeToastMessage(message) {
        const raw = String(message || '');
        const exact = new Map([
            ['Simulado descartado.', 'exam.runtime.discarded'],
            ['▶ Simulado retomado de onde você parou!', 'exam.runtime.resumed'],
            ['Faça login para iniciar um simulado', 'exam.runtime.loginRequired'],
            ['Escolha a certificação e o nível primeiro.', 'exam.runtime.chooseCertLevel'],
            ['🔁 Revisando suas questões erradas — mostre que agora você sabe!', 'exam.runtime.reviewingErrors'],
            ['⏰ Tempo esgotado! Entregando o simulado...', 'exam.runtime.timeExpired'],
            ['⏸ Simulado pausado — continue quando quiser (válido por 2h).', 'exam.runtime.paused'],
            ['Sessão expirada. Faça login novamente.', 'exam.runtime.sessionExpired'],
            ['Erro ao iniciar simulado', 'exam.runtime.startError'],
            ['Erro ao verificar resposta', 'exam.runtime.checkError'],
            ['Erro ao finalizar simulado', 'exam.runtime.finishError']
        ]);
        if (exact.has(raw)) return t(exact.get(raw));

        const multi = raw.match(/^Esta questão pede apenas (\d+) alternativas?\./);
        if (multi) return t('exam.runtime.multiLimit', { count: multi[1] });
        return message;
    }

    function installToastLocalization() {
        if (!global.Utils || typeof global.Utils.showToast !== 'function' || global.Utils.__cloudpathI18nToastWrapped) return;
        const original = global.Utils.showToast.bind(global.Utils);
        global.Utils.showToast = function (message, type, ...rest) {
            return original(localizeToastMessage(message), type, ...rest);
        };
        global.Utils.__cloudpathI18nToastWrapped = true;
    }

    let observer = null;
    let scheduled = false;
    function scheduleDynamic() {
        if (scheduled) return;
        scheduled = true;
        requestAnimationFrame(() => {
            scheduled = false;
            localizeDynamic();
        });
    }

    function installObserver() {
        const root = q('#main-content');
        if (!root || observer) return;
        observer = new MutationObserver(scheduleDynamic);
        observer.observe(root, {
            childList: true,
            subtree: true,
            characterData: true,
            attributes: true,
            attributeFilter: ['class', 'style', 'disabled']
        });
    }

    global.I18n.registerAdapter(() => {
        localizeStatic();
        localizeDynamic();
        installToastLocalization();
        installObserver();
    });
})(window);
