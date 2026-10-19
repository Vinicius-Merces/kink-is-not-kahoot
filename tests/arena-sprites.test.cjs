const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
let now = 0, sequence = 0, callbacks = new Map(), decoded = new Map();
const context = {
    performance: {now: () => now},
    requestAnimationFrame: cb => {callbacks.set(++sequence,cb);return sequence;},
    cancelAnimationFrame: id => callbacks.delete(id),
    Image: class {
        naturalWidth = 2048; naturalHeight = 8192;
        decode() {decoded.set(this.src,(decoded.get(this.src)||0)+1);return Promise.resolve();}
    },
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'../js/cloudarena-sprites.js'),'utf8'),context);
const {ArenaSprite} = context.CloudArenaSprites;
function advance(ms) {
    now += ms;
    const pending = [...callbacks.values()];callbacks.clear();pending.forEach(cb => cb(now));
}
const catalog = JSON.parse(fs.readFileSync(path.join(__dirname,'../images/arena/v2/catalog.json')));
(async () => {
    assert.equal(catalog.commons.length,20);assert.equal(catalog.bosses.length,4);
    for (let band=1; band<=4; band++) assert.equal(catalog.commons.filter(v => v.band === band).length,5);
    let actions = 0, frames = 0;
    for (const variant of [...catalog.commons,...catalog.bosses]) {
        let draws = [];
        const canvas = {width:256,height:256,isConnected:true,getContext:()=>({clearRect(){},drawImage(...args){draws.push(args);}})};
        const sprite = new ArenaSprite(variant);sprite.attach(canvas);
        await sprite.load();assert(sprite.isReady);
        for (const [state,spec] of Object.entries(variant.animations)) {
            actions++;frames+=spec.frames.length;
            assert.equal(spec.duration,state.startsWith('idle')?1000:500);
            assert(spec.frames.length === 4 || spec.frames.length === 8);
            let complete=0, seen=[];
            assert(sprite.play(state,{onFrame:i=>seen.push(i),onComplete:()=>complete++}));
            for(let i=0;i<spec.frames.length;i++) advance(spec.duration/spec.frames.length);
            assert.equal(complete,1,variant.id+'/'+state);
            assert.equal(seen[0],0);assert.equal(seen.at(-1),spec.frames.length-1);
            assert.equal(sprite._raf,null);
        }
        sprite.play('idle',{loop:true});advance(3000);assert.notEqual(sprite._raf,null);
        // New action cancels old idle: completion must not resurrect that idle.
        sprite.play('hurt');advance(500);assert.equal(sprite._raf,null);
        sprite.play('idle',{loop:true});sprite.stop();assert.equal(sprite._raf,null);
        assert(draws.every(a=>a[7]>0&&a[8]>0&&a[5]>=0&&a[6]>=0&&a[5]+a[7]<=256&&a[6]+a[8]<=256));
        canvas.isConnected=false;sprite.play('idle',{loop:true});advance(16);assert.equal(callbacks.size,0);
    }
    // A delayed image decode retains requested hurt, rather than resetting idle.
    const variant=catalog.commons[0], s=new ArenaSprite(variant);
    s.attach({width:256,height:256,isConnected:true,getContext:()=>({clearRect(){},drawImage(){}})});
    let completed=0;s.play('hurt',{onComplete:()=>completed++});await s.load();advance(500);assert.equal(completed,1);
    assert([...decoded.values()].every(n=>n===1),'images decoded once, including rerenders');
    const source=fs.readFileSync(path.join(__dirname,'../js/cloudarena.js'),'utf8');
    assert(!source.includes('enemySpriteUrl('),'no legacy URL requests');
    assert(!source.includes('id="enemySprite"'),'one visual surface only');
    assert(source.includes('previousField.dataset.encounter'),'preserve canvas across question rerenders');
    console.log(`PASS: ${actions} animations, ${frames} frames, 20 enemies, 4 bosses; cache, timing, cancellation, delayed decode and crop bounds`);
})().catch(e=>{console.error(e);process.exitCode=1;});
