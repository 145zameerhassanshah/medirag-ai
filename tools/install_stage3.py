"""Safe non-destructive Stage 3 install. Run from project root: python path/to/install_stage3.py --apply"""
import argparse
from pathlib import Path
import shutil
import sys
from datetime import datetime

FILES = [
 'backend/app/main.py',
 'backend/app/db/ai_models.py',
 'backend/app/core/bot_policy.py',
 'backend/app/prompts/__init__.py',
 'backend/app/prompts/platform_rules.py',
 'backend/app/prompts/role_templates.py',
 'backend/app/prompts/builder.py',
 'backend/app/services/chat_service.py',
 'backend/app/services/intent_router.py',
 'backend/app/services/catalogue_lookup.py',
 'backend/app/services/usage_service.py',
 'backend/app/rag/providers.py',
 'backend/app/rag/retrieval.py',
 'backend/app/rag/citation_validator.py',
 'backend/app/api/routes/assistant_settings.py',
 'backend/tests/test_response_engine.py',
 'frontend/src/app/assistant-settings/page.tsx',
]

def main():
    parser=argparse.ArgumentParser(description='Install Stage 3 into existing MediRAG project safely')
    parser.add_argument('--project',type=Path,default=Path.cwd(),help='Existing medirag_fullstack folder')
    parser.add_argument('--apply',action='store_true',help='Write files; default is dry run')
    args=parser.parse_args()
    dest=args.project.resolve()
    source=Path(__file__).resolve().parent.parent
    if not (dest/'backend/app/services/chat_service.py').is_file() or not (dest/'frontend/package.json').is_file():
        raise SystemExit('ERROR: Stage 1 modular backend and existing frontend required. No files changed.')
    if dest==source:
        raise SystemExit('ERROR: Install into your existing project, not the extracted package.')
    for rel in FILES:
        if not (source/rel).is_file():
            raise SystemExit(f'ERROR: Package missing {rel}; no files changed.')
    changes=[(rel,'REPLACE' if (dest/rel).exists() else 'NEW') for rel in FILES]
    for rel, action in changes:print(f'{action:7} {rel}')
    if not args.apply:
        print('\nDRY RUN ONLY. Review the list, then add --apply to install.')
        return
    # Backups stored outside the repo, avoiding accidental git commits of old code.
    backup=Path.home()/'MediRAG-Stage3-Backups'/datetime.now().strftime('%Y%m%d-%H%M%S')
    for rel,action in changes:
        if action=='REPLACE':
            (backup/rel).parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(dest/rel,backup/rel)
    # Keep the original upload/db files untouched; copy only listed source paths.
    for rel,_ in changes:
        (dest/rel).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source/rel,dest/rel)
    print('\nInstalled successfully. Existing .env, SQLite, Chroma and frontend /live untouched.')
    print('Previous source file backups:',backup)
    print('Next: cd backend && python -m pytest tests/test_response_engine.py -q')

if __name__=='__main__': main()
