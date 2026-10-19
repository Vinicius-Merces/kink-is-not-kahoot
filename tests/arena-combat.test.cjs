const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
let timers=[];
const ctx={console,Set,Map,Date,Math,JSON,
    localStorage:{getItem:()=>null,setItem(){}},
    document:{querySelector:()=>null,addEventListener(){}},
    window:{addEventListener(){}},
    setTimeout:(fn,ms)=>{timers.push({fn,ms});return timers.length;},clearTimeout(){},
};
vm.createContext(ctx);
let src=fs.readFileSync(path.join(__dirname,'../js/cloudarena.js'),'utf8');
src=src.replace(/\}\)\(\);\s*$/,`
    let testNext=0,testKills=0;
    renderBattle=()=>{}; heroAttack=cb=>cb(); animateEnemyHurt=()=>{};
    showToast=()=>{}; updateHpBars=()=>{}; nextRound=()=>{testNext++;battle.busy=false;};
    enemyDefeated=()=>{testKills++;};
    window.test={state,chooseJustification,chosenEnemyVariant,beginBossEnrage,bossHp,startEncounter,arenaData,
      catalog:v=>artCatalog=v,battle:v=>battle=v,getBattle:()=>battle,
      counts:()=>({next:testNext,kills:testKills})};
})();`);
vm.runInContext(src,ctx);
const t=ctx.window.test;
const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../images/arena/v2/catalog.json')));
t.catalog(catalog);
for(const certId of ['saa-c03','clf-c02','dva-c02','dea-c01']) {
    const arena=t.state.arenas[certId];
    for(const [level,total] of [[10,2],[20,2],[30,3],[40,3],[50,4],[60,4],[70,5],[80,5],[90,6],[100,6]]) {
        arena.currentLevel=level;arena.inChallenge=false;
        assert.equal(t.bossHp(certId,1),Math.floor(total/2)*4);
        assert.equal(t.bossHp(certId,2),Math.ceil(total/2)*4);
        assert.equal((t.bossHp(certId,1)+t.bossHp(certId,2))/4,total);
    }
    arena.inChallenge=true;arena.challengePosition=5;assert.equal(t.bossHp(certId),24);
    arena.challengePosition=20;assert.equal(t.bossHp(certId),32);arena.inChallenge=false;
}
for(const certId of ['saa-c03','clf-c02','dva-c02','dea-c01']) {
    for(let level=1;level<=100;level++) {
        const a=t.state.arenas[certId];a.currentLevel=level;a.pendingEncounter=null;
        t.battle({certId,boss:level%10===0});
        const v=t.chosenEnemyVariant();assert(v&&v.animations.idle);
        if(level%10===0&&level<=40) assert.equal(v.level,level);
        if(level%10!==0) {
            assert.equal(v.band,Math.min(4,Math.ceil(level/10)));
            const previous=v.id;
            t.battle({certId,boss:false});assert.notEqual(t.chosenEnemyVariant().id,previous);
        }
    }
}
const a=t.state.arenas['saa-c03'];a.currentLevel=11;a.pendingEncounter=null;
t.battle({certId:'saa-c03',boss:false,_restoredVisualId:'tecela'});
assert.equal(t.chosenEnemyVariant().id,'tecela','restored encounter keeps same art');
function flush(ms) {
    const run=timers.filter(x=>x.ms===ms);timers=timers.filter(x=>x.ms!==ms);run.forEach(x=>x.fn());
}
for(const boss of catalog.bosses) {
    a.currentLevel=boss.level;
    const before=t.counts();
    const total=2+Math.floor((boss.level/10-1)/2);
    const rounds=Math.floor(total/2),enragedRounds=Math.ceil(total/2),hp=rounds*4;
    const b={certId:'saa-c03',boss:true,bossPhase:1,round:rounds,totalRounds:rounds,
      enemyHp:1,enemyMaxHp:hp,question:{justifications:[{correct:true}]},
      _commonEnemyVariant:boss,disabledJusts:new Set()};
    t.battle(b);t.chooseJustification(0);assert.equal(b.enemyHp,0);
    flush(1300);assert.equal(b.bossPhase,2);assert.equal(b.enemyHp,enragedRounds*4);assert.equal(b.totalRounds,enragedRounds);assert.equal(b.round,1);
    assert.equal(t.counts().kills,before.kills,'phase one must not award victory');
    flush(550);assert.equal(t.counts().next,before.next+1);
    b.round=enragedRounds;b.enemyHp=1;b.busy=false;
    t.chooseJustification(0);flush(1300);assert.equal(t.counts().kills,before.kills+1);
}
// Existing level-10 saves must adopt the shorter encounter without losing form.
const q={id:'saved-boss-question',domain:'secure-architectures',justifications:[]};
t.arenaData['saa-c03']={pools:{iniciante:[q],medio:[],avancado:[]}};
for(const phase of [1,2]) {
    a.currentLevel=10;a.inChallenge=false;
    a.pendingEncounter={questionId:q.id,boss:true,enemyMaxHp:12,enemyHp:7,totalRounds:3,round:2,bossPhase:phase,visualId:'vorgrath'};
    t.startEncounter('saa-c03');const b=t.getBattle();
    assert.equal(b.totalRounds,1);assert.equal(b.round,1);assert.equal(b.enemyMaxHp,4);assert.equal(b.enemyHp,4);assert.equal(b.bossPhase,phase);
}
for(const phase of [1,2]) {
    a.currentLevel=30;
    a.pendingEncounter={questionId:q.id,boss:true,enemyMaxHp:12,enemyHp:9,totalRounds:3,round:3,bossPhase:phase,visualId:'aion'};
    t.startEncounter('saa-c03');const b=t.getBattle();const rounds=phase===2?2:1;
    assert.equal(b.totalRounds,rounds);assert.equal(b.round,rounds);assert.equal(b.enemyMaxHp,rounds*4);assert.equal(b.bossPhase,phase);
}
console.log('PASS: progressive boss HP, saved encounter migration, 400 level mappings, anti-repeat and all four two-phase boss lifecycles');
