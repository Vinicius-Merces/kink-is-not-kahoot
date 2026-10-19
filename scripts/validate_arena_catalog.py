"""Decode every published atlas and verify every padded frame."""
import json
import sys
from pathlib import Path
from PIL import Image

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
catalog=json.loads((root/'images/arena/v2/catalog.json').read_text())
count=0
for variant in catalog['commons']+catalog['bosses']:
    required=['idle','attack','hurt','death']
    if 'level' in variant:
        required+=['intro','enrage','idleEnraged','attackEnraged','heavy','hurtEnraged']
    assert all(s in variant['animations'] for s in required),variant['id']
    for state,spec in variant['animations'].items():
        im=Image.open(root/spec['url']).convert('RGBA');im.load()
        assert spec['duration']==(1000 if state.startswith('idle') else 500)
        for x,y,w,h in spec['frames']:
            assert x>=0 and y>=0 and x+w<=im.width and y+h<=im.height
            frame=im.crop((x,y,x+w,y+h))
            a=frame.getchannel('A')
            # The gutter must be empty: artwork can never touch a neighboring cell.
            for edge in [(0,0,w,8),(0,h-8,w,h),(0,0,8,h),(w-8,0,w,h)]:
                assert a.crop(edge).getextrema()[1]<32,(variant['id'],state,edge)
            count+=1
print(f'PASS: {count} decoded RGBA frames with safe transparent gutters')
