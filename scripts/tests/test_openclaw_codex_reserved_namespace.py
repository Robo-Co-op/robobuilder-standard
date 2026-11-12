from __future__ import annotations
import os,sys,json,shutil,subprocess,hashlib
from pathlib import Path
import pytest
REPO=Path(__file__).resolve().parents[2]

def snapshot(root):
    rows={}
    for p in root.rglob('*'):
        if p.is_symlink():rows[str(p.relative_to(root))]=('symlink',str(p.readlink()))
        elif p.is_file():rows[str(p.relative_to(root))]=('file',hashlib.sha256(p.read_bytes()).hexdigest())
        elif p.is_dir():rows[str(p.relative_to(root))]=('directory',)
    return rows

@pytest.mark.parametrize('replace',[False,True])
@pytest.mark.parametrize('prefix',['pro','lite'])
@pytest.mark.parametrize('existing',[False,True])
def test_Standard_cannot_claim_reserved_product_names(tmp_path,replace,prefix,existing):
    repo=tmp_path/'repo';shutil.copytree(REPO,repo,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
    source=repo/'skills/phase3/tdd/SKILL.md';source.write_text(source.read_text().replace('name: tdd\n',f'name: {prefix}-dev-loop\n',1))
    target=tmp_path/'skills'
    if existing:
        p=target/f'robobuilder-{prefix}-dev-loop/SKILL.md';p.parent.mkdir(parents=True)
        p.write_text(f'---\nname: robobuilder-{prefix}-dev-loop\nadapter: openclaw-codex\nsource_skill: skills/phase3/tdd/SKILL.md\n---\nOTHER PRODUCT SYNTHETIC BODY\n')
        (p.parent/'keep.bin').write_bytes(b'UNCHANGED\x00LOCAL\r\n')
    before=snapshot(tmp_path)
    args=[sys.executable,str(repo/'scripts/export_openclaw_codex_skills.py'),'--target',str(target)]
    if replace:args.append('--replace-existing')
    q=subprocess.run(args,capture_output=True,text=True,timeout=15,env={'PATH':'/usr/bin:/bin','HOME':str(tmp_path/'HOME'),'PYTHONDONTWRITEBYTECODE':'1'})
    assert q.returncode!=0,'Standard accepted a reserved other-product name'
    assert snapshot(tmp_path)==before
