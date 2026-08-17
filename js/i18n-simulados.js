/** CloudPath Simulados UI adapter.
 *
 * This translates the simulator chrome only. Question text, answer options,
 * explanations and domain names remain source-language content until the exam
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

    function counterHeading(selector, key, counterId) {
        const el = q(selector);
        if (!el) return;
        let counter = q(`#${counterId}`, el);
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
        text('#configCertName', 'exam.ui.configure');
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
        text('#startSimuladoBtn', 'exam.ui.startExam');
        text('#reviewErrorsBtn', 'exam.ui.reviewErrors');
        text('#createLiveRoomBtn', 'exam.ui.createLiveRoom');

        text('#examMarkBtn', 'exam.ui.markReview');
        text('#examPauseBtn', 'exam.ui.pause');
        attr('#examPauseBtn', 'title', 'exam.ui.pauseTitle');
        text('#examReportBtn', 'exam.ui.reportError');
        text('#examQuestionText', 'exam.ui.loadingQuestion');
        attr('.opt-layout-toggle', 'aria-label', 'exam.ui.optionLayout');
        attr('.olt-btn[data-sim-layout="list"]', 'title', 'exam.ui.listLayout');
        attr('.olt-btn[data-sim-layout="grid"]', 'title', 'exam.ui.gridLayout');
        text('#prevQuestionBtn', 'exam.ui.previous');
        text('#nextQuestionBtn', 'exam.ui.next');
        text('#finishExamBtn', 'exam.ui.finishExam');

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
        text('#liveControlQuestionText', 'exam.ui.loadingQuestion');
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
        if (parts.length < 2) return;
        const value = `${t('exam.ui.configure')} — ${parts.slice(1).join('—').trim()}`;
        setText(el, value);
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

    function localizeDynamic() {
        localizeConfigTitle();
        localizeLevels();

        text('#domainPreview h4', 'exam.ui.domainDistribution');
        text('#domainPreview .placeholder', 'exam.ui.noDomains');

        const resume = q('#resumeSimuladoBanner');
        if (resume && resume.style.display !== 'none') {
            setText(q('strong', resume), t('exam.ui.pausedExam'));
            text('#resumeSimuladoBtn', 'exam.ui.resume');
            text('#discardSimuladoBtn', 'exam.ui.discard');
        }

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
            const aria = answered
                ? t('exam.ui.questionAnswered', { number })
                : title;
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
            attributeFilter: ['class', 'style']
        });
    }

    global.I18n.registerAdapter(() => {
        localizeStatic();
        localizeDynamic();
        installObserver();
    });
})(window);
