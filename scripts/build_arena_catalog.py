"""Pack approved artwork into padded, aspect-preserving animation atlases.

Run from the task workspace: python review/scripts/build_arena_catalog.py
Original art stays untouched. Runtime consumes explicit frame rectangles, not
guessed grid sizes. These paths document the approved sources used in this repair.
"""
import json
import sys
import os
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get('ARENA_OUTPUT', str(ROOT / 'review')))
REC = ROOT / 'art-recovery'
GEN = ROOT / 'generated_images'
SIZE = 256
catalog = {'version': 2, 'commons': [], 'bosses': []}

def recovered(name):
    paths = list(REC.rglob(name))
    assert len(paths) == 1, (name, paths)
    return paths[0]

def gen(id):
    return GEN / ('exec-' + id + '.png')

def cells(path, rows=4, indices=None):
    im = Image.open(path).convert('RGBA')
    # Find actual row valleys near expected boundaries: some approved layouts
    # have slightly uneven gutters. Never remove a fixed inset from the art.
    a = np.asarray(im)[:, :, 3]
    cuts = [0]
    for row in range(1, rows):
        expected = round(row * im.height / rows)
        radius = round(im.height / rows * .09)
        candidates = range(expected-radius, expected+radius+1)
        cuts.append(min(candidates, key=lambda y: (int((a[max(0,y-1):y+2] > 48).sum()), abs(y-expected))))
    cuts.append(im.height)
    frames = []
    for row in range(rows):
        for col in range(4):
            box = (round(col*im.width/4), cuts[row], round((col+1)*im.width/4), cuts[row+1])
            frame = im.crop(box)
            # Standardize to source-cell height, retaining aspect ratio.
            frame = frame.resize((round(frame.width * 512/frame.height), 512), Image.Resampling.LANCZOS)
            frames.append(frame)
    return [frames[i] for i in indices] if indices is not None else frames

def pack(id, animations):
    result = {}
    for action, frames in animations.items():
        path = Path('images/arena/v2') / id / (action+'.webp')
        target = OUT/path
        if target.exists() and id not in sys.argv[1:]:
            try:
                Image.open(target).load()
                result[action] = {'url': str(path), 'duration': 1000 if action.startswith('idle') else 500,
                                  'frames': [[i%4*SIZE, i//4*SIZE, SIZE, SIZE] for i in range(len(frames))]}
                continue
            except OSError:
                pass
        bounds = [f.getchannel('A').point(lambda a: 255 if a > 24 else 0).getbbox() for f in frames]
        valid = [b for b in bounds if b]
        assert valid, (id, action)
        union = (min(b[0] for b in valid), min(b[1] for b in valid), max(b[2] for b in valid), max(b[3] for b in valid))
        scale = min((SIZE-32)/(union[2]-union[0]), (SIZE-32)/(union[3]-union[1]))
        sheet = Image.new('RGBA', (SIZE*4, SIZE*((len(frames)+3)//4)))
        for i, frame in enumerate(frames):
            # One transform for the WHOLE action, including death. In particular
            # never enlarge the diminishing fragments of the last death frames.
            cut = frame.crop(union)
            cut = cut.resize((max(1,round(cut.width*scale)), max(1,round(cut.height*scale))), Image.Resampling.LANCZOS)
            px = i%4*SIZE+(SIZE-cut.width)//2
            py = i//4*SIZE+(SIZE-cut.height)//2
            sheet.alpha_composite(cut, (px,py))
        path = Path('images/arena/v2') / id / (action+'.webp')
        target = OUT/path
        target.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(target, 'WEBP', quality=86, method=2)
        # Full decode is mandatory before upload; a correct filename isn't enough.
        Image.open(target).load()
        result[action] = {'url': str(path), 'duration': 1000 if action.startswith('idle') else 500,
                          'frames': [[i%4*SIZE, i//4*SIZE, SIZE, SIZE] for i in range(len(frames))]}
    return result

def common(id, name, band, source):
    frames = cells(source)
    animations = {s: frames[i*4:i*4+4] for i,s in enumerate(['idle','attack','hurt','death'])}
    catalog['commons'].append({'id':id,'name':name,'band':band,'animations':pack(id,animations)})

old = ROOT/'review/images/arena/enemies'
common('guardduty','Sentinela GuardDuty',1,old/'secure-architectures/sentinela-fortaleza-sheet.png')
common('multi-az','Sentinela Multi-AZ',1,recovered('Sentinela Mecânico: Guarda, Ataque e Queda.png'))
common('arquimago','Arquimago das Chaves',1,recovered('Spritesheet 4x4 transparente do Arquimago das Chaves.png'))
common('permissoes','Guardião de Permissões',1,recovered('Guardião de Permissões em 16 poses.png'))
common('resiliencia','Sentinela da Resiliência',1,recovered('Sentinela da Resiliência em 16 quadros.png'))
for id,name,file in [
    ('tecela','Tecelã das Rotas','Tecelã das Rotas: 16 poses mágicas.png'),
    ('oraculo','Oráculo do DNS','Oráculo astral do DNS em movimento.png'),
    ('colosso','Colosso do Auto Scaling','Sprite sheet do Colosso do Auto Scaling.png'),
    ('espectro','Espectro do Cache','Espectro do Cache em movimento.png'),
    ('fenix','Fênix do Backup','Fênix do backup: voo, restauração e renascimento.png')]:
    common(id,name,2,recovered(file))
common('draco','Draco do Tráfego',3,gen('ffd5bcb3-7931-4fe4-b5b8-09f6551e8ba3'))
for id,name,file in [
    ('aegis','Aegis, o Draco do Firewall','networking/aegis-draco-firewall-sheet.webp'),
    ('hydra','Hydra, o Draco do Load Balancer','networking/hydra-draco-load-balancer-sheet.webp'),
    ('atlas','Atlas, o Draco do Auto Scaling','compute/atlas-draco-auto-scaling-sheet.webp'),
    ('orion','Orion, o Draco da Replicação','storage/orion-draco-replicacao-sheet.webp')]:
    common(id,name,3,old/file)
for id,name,file in [
    ('nexo','Nexo-31, o Mecha de Redes','706d7f8c-62d1-4ea3-a4b7-cb64efbca6b5'),
    ('bastiao','Bastião-AX, o Mecha de Segurança','16d1c968-7eb1-48f3-ad18-5baff90309c2'),
    ('escalador','Escalador K-9, o Mecha de Auto Scaling','660ea631-a256-4e81-8014-4e9e1c9d9527'),
    ('forja','Forja-IO, o Mecha de Processamento','b8ed1500-1baa-4050-8f4b-a49ee3aee20c'),
    ('vault','Núcleo Vault-7, o Mecha de Armazenamento','80c0b8eb-0c11-4a07-8601-e2a5fac638cc')]:
    common(id,name,4,gen(file))

def boss(id,name,level,animations):
    catalog['bosses'].append({'id':id,'name':name,'level':level,'animations':pack(id,animations)})

v = lambda file, start=0, end=8: cells(recovered(file),4,list(range(start,end)))
boss('vorgrath','Vorgrath, o Corruptor das Arquiteturas Seguras',10,{
    'idle':v('Spritesheet de Vorgrath: idle e introdução.png'),
    'intro':v('Spritesheet de Vorgrath: idle e introdução.png',8,16),
    'attack':v('Spritesheet do ataque de espada de Vorgrath.png'),
    'enrage':v('Vorgrath em corrupção e fúria.png',8,16),
    'idleEnraged':cells(recovered('Vorgrath enfurecido: oito quadros de respiração.png'),2),
    'attackEnraged':v('Spritesheet do ataque de espada de Vorgrath.png'),
    'heavy':v('Vorgrath em corrupção e fúria.png'),
    'hurt':v('Spritesheet de dano e queda de Vorgrath.png'),
    'hurtEnraged':v('Spritesheet de dano e queda de Vorgrath.png'),
    'death':v('Spritesheet de dano e queda de Vorgrath.png',8,16),
})
n = lambda file, start=0, end=8: cells(recovered(file),4,list(range(start,end)))
# Approved Nexarion hurt has FOUR frames per phase, unlike other boss actions.
boss('nexarion','Nexarion, o Dragão dos Portais Topológicos',20,{
    'idle':n('Nexarion, dragão dos portais topológicos.png'),
    'intro':n('Nexarion, dragão dos portais topológicos.png',8,16),
    'attack':n('Nexarion: sopro violeta topológico.png'),
    'enrage':n('Nexarion enfurecido: transformação e fenda em cascata.png'),
    'idleEnraged':cells(recovered('Nexarion enfurecido: spritesheet de 8 quadros.png'),2),
    'attackEnraged':n('Folha de sprites do dragão-serpente em fúria.png'),
    'heavy':n('Nexarion enfurecido: transformação e fenda em cascata.png',8,16),
    'hurt':n('Animações de dano e morte de Nexarion.png',0,4),
    'hurtEnraged':n('Animações de dano e morte de Nexarion.png',4,8),
    'death':n('Animações de dano e morte de Nexarion.png',8,16),
})
for id,name,level,sources in [
 ('aion','Aion, o Titã do Control Plane',30,{
 'intro':'a2962bf8-3393-4d79-8cab-95df5006950c','idle':'fe912263-7a0f-4600-b103-f7843d331efd',
 'attack':'bde04e65-0a2a-4d9d-bd16-6439c02d3bf2','hurt':'34023c35-bcc8-432f-bffb-eda77d4a4025',
 'enrage':'68a817b2-3d9a-402a-9aa1-a91541434f21','idleEnraged':'9843e4a6-0706-4f0c-9377-6fe51e18d887',
 'attackEnraged':'dd901d85-f729-4563-985b-d8acf9e44607','heavy':'7ba4baca-af88-4c0e-846d-b3db0271184f',
 'hurtEnraged':'61b6b04c-0657-42a8-b8ff-dd63524dbdc8','death':'45b2493d-bb2b-4ea5-8fc4-c27aa305b574'}),
 ('mnemosine','Mnemósine, a Arquivista Abissal',40,{
 'intro':'7d9bfbb9-45c9-483e-8a1a-4154d73cc7de','idle':'e5daec90-a9f7-4aa9-9f64-2c750ce43b0f',
 'attack':'163afb4e-c26a-4baf-a400-ea8bedde840d','hurt':'aabb0577-1591-440e-a7bd-2c8e52270d14',
 'enrage':'d1e8d70d-c02e-429f-8ce5-5a724b3b126c','idleEnraged':'67e49154-7885-433d-a516-6b2d1d3c9160',
 'attackEnraged':'93f83a28-8089-46c0-be7d-ae4ec640fd92','heavy':'d8479a9a-5c03-4914-bbaa-faeeeaf20de8',
 'hurtEnraged':'a66627f3-d97b-4006-b016-86c0ba0634b9','death':'d8fec670-88b7-4cd2-860d-65b4b80c54d5'})]:
    boss(id,name,level,{action:cells(gen(file),2) for action,file in sources.items()})

target=OUT/'images/arena/v2/catalog.json'
target.write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':')))
print(f'Packed {len(catalog["commons"])} enemies and {len(catalog["bosses"])} bosses')
