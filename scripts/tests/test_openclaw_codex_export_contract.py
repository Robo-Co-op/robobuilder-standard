from __future__ import annotations
import os,sys,json,hashlib,shutil,subprocess
from pathlib import Path
import pytest
REPO=Path(__file__).resolve().parents[2]

def run_export(repo,target,replace):
    args=[sys.executable,str(repo/'scripts/export_openclaw_codex_skills.py'),'--target',str(target)]
    if replace:args.append('--replace-existing')
    return subprocess.run(args,capture_output=True,text=True,timeout=15,env={'PATH':'/usr/bin:/bin','HOME':str(target.parent/'synthetic-home'),'PYTHONDONTWRITEBYTECODE':'1'})

def tree(root):
    out={}
    if not root.exists():return out
    for current,dirs,files in os.walk(root,followlinks=False):
        for name in dirs[:]+files:
            p=Path(current)/name;key=str(p.relative_to(root))
            if p.is_symlink():out[key]=('link',os.readlink(p));dirs.remove(name) if name in dirs else None
            elif p.is_dir():out[key]=('directory',)
            else:out[key]=('file',hashlib.sha256(p.read_bytes()).hexdigest())
    return out

def owned_marker(name,source):
    return f'---\nname: {name}\ndescription: synthetic\nsource_skill: {source}\nadapter: openclaw-codex\n---\nsynthetic-only\n'

@pytest.mark.parametrize('replace',[False,True])
def test_other_product_and_local_complete_trees_preserved(tmp_path,replace):
    target=tmp_path/'skills';keep=[]
    for suffix in ['pro-dev-loop','lite-build','local']:
        p=target/('robobuilder-'+suffix);p.mkdir(parents=True)
        body=owned_marker(p.name,'skills/phaseX/'+suffix+'/SKILL.md') if suffix!='local' else 'local authored text\n'
        (p/'SKILL.md').write_text(body);(p/'nested').mkdir();(p/'nested/keep.bin').write_bytes(b'\x00SYNTHETIC\r\n');(p/'empty').mkdir();keep.append((p,tree(p)))
    q=run_export(REPO,target,replace);assert q.returncode==0,q.stderr
    for p,before in keep:assert tree(p)==before

@pytest.mark.parametrize('replace',[False,True])
@pytest.mark.parametrize('kind',['malformed','other-product','array','directory'])
def test_unmanaged_manifest_refuses_without_any_change(tmp_path,replace,kind):
    target=tmp_path/'skills';assert run_export(REPO,target,True).returncode==0
    p=target/'manifest.json';p.unlink()
    if kind=='directory':p.mkdir();(p/'keep.txt').write_text('synthetic local manifest folder')
    elif kind=='malformed':p.write_text('{')
    elif kind=='array':p.write_text('[]')
    else:p.write_text(json.dumps({'name':'another-product','source':'https://example.invalid/local','shared':'_robobuilder_shared'}))
    before=tree(tmp_path);q=run_export(REPO,target,replace);assert q.returncode!=0;assert tree(tmp_path)==before

@pytest.mark.parametrize('replace',[False,True])
def test_unmanaged_shared_refuses_without_any_change(tmp_path,replace):
    target=tmp_path/'skills';shared=target/'_robobuilder_shared';shared.mkdir(parents=True);(shared/'keep.bin').write_bytes(b'LOCAL\r\n')
    before=tree(tmp_path);q=run_export(REPO,target,replace);assert q.returncode!=0;assert tree(tmp_path)==before

@pytest.mark.parametrize('replace',[False,True])
def test_legitimate_source_category_move_refresh(tmp_path,replace):
    repo=tmp_path/'repo';shutil.copytree(REPO,repo,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'));target=tmp_path/'skills'
    assert run_export(repo,target,True).returncode==0
    old=repo/'skills/phase3/tdd';new=repo/'skills/phase4/tdd';assert not new.exists();old.rename(new)
    before=tree(target);q=run_export(repo,target,replace)
    if q.returncode:assert tree(target)==before
    assert q.returncode==0,'legitimate generated output refused after category move; existing tree preserved: '+q.stderr[-500:]
    assert 'source_skill: skills/phase4/tdd/SKILL.md' in (target/'robobuilder-tdd/SKILL.md').read_text()

@pytest.mark.parametrize('replace',[False,True])
def test_legitimate_frontmatter_alias_refresh(tmp_path,replace):
    repo=tmp_path/'repo';shutil.copytree(REPO,repo,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'));target=tmp_path/'skills'
    source=repo/'skills/phase3/tdd/SKILL.md';text=source.read_text();assert 'name: tdd\n' in text;source.write_text(text.replace('name: tdd\n','name: alias-tdd\n',1))
    assert run_export(repo,target,True).returncode==0
    generated=target/'robobuilder-alias-tdd/SKILL.md';expected=generated.read_bytes();generated.write_bytes(expected+b'\nold generated body\n')
    before=tree(target);q=run_export(repo,target,replace)
    if q.returncode:assert tree(target)==before
    assert q.returncode==0,'exporter refuses its own accepted alias output: '+q.stderr[-500:]
    assert generated.read_bytes()==expected

@pytest.mark.parametrize('replace',[False,True])
def test_marked_stale_standard_cleanup_is_mode_specific(tmp_path,replace):
    target=tmp_path/'skills';assert run_export(REPO,target,True).returncode==0
    stale=target/'robobuilder-retired';stale.mkdir();(stale/'SKILL.md').write_text(owned_marker(stale.name,'skills/phase9/retired/SKILL.md'))
    q=run_export(REPO,target,replace);assert q.returncode==0,q.stderr;assert stale.exists() is (not replace)

@pytest.mark.parametrize('replace',[False,True])
def test_empty_local_collision_preserves_even_empty_directories(tmp_path,replace):
    target=tmp_path/'skills';(target/'robobuilder-tdd/empty-local-subdir').mkdir(parents=True);(tmp_path/'outside-empty').mkdir()
    before=tree(tmp_path);q=run_export(REPO,target,replace);assert q.returncode!=0;assert tree(tmp_path)==before

@pytest.mark.parametrize('replace',[False,True])
def test_wrong_existing_source_marker_still_refuses(tmp_path,replace):
    target=tmp_path/'skills';assert run_export(REPO,target,True).returncode==0
    p=target/'robobuilder-tdd/SKILL.md';p.write_text(p.read_text().replace('source_skill: skills/phase3/tdd/SKILL.md','source_skill: skills/phase0/setup/SKILL.md'))
    before=tree(tmp_path);q=run_export(REPO,target,replace);assert q.returncode!=0;assert tree(tmp_path)==before
