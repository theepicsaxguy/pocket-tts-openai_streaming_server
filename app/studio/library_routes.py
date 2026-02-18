"""
Studio API routes — Library, generation status, and preview endpoints.
"""

from typing import Any

from flask import jsonify, request, Response

from app.logging_config import get_logger
from app.studio.chunking import chunk_text
from app.studio.db import get_db
from app.studio.generation import get_generation_queue
from app.studio.git_ingestion import preview_git_repository
from app.studio.ingestion import ingest_url
from app.studio.normalizer import CleaningOptions, normalize_text

logger = get_logger('studio.routes.library')


def register_routes(bp) -> None:
    """Register library and misc routes on the blueprint."""

    @bp.route('/generation/status', methods=['GET'])
    def generation_status() -> Response:
        """Get generation queue status."""
        gq = get_generation_queue()

        db = get_db()
        pending_count = db.execute(
            "SELECT COUNT(*) as cnt FROM episodes WHERE status = 'pending'"
        ).fetchone()['cnt']
        generating_count = db.execute(
            "SELECT COUNT(*) as cnt FROM episodes WHERE status = 'generating'"
        ).fetchone()['cnt']
        ready_count = db.execute(
            "SELECT COUNT(*) as cnt FROM episodes WHERE status = 'ready'"
        ).fetchone()['cnt']
        error_count = db.execute(
            "SELECT COUNT(*) as cnt FROM episodes WHERE status = 'error'"
        ).fetchone()['cnt']

        return jsonify(
            {
                'current_episode_id': gq.current_episode_id,
                'queue_size': gq.queue_size,
                'db_status': {
                    'pending': pending_count,
                    'generating': generating_count,
                    'ready': ready_count,
                    'error': error_count,
                },
            }
        )

    @bp.route('/library/tree', methods=['GET'])
    def library_tree() -> Response:
        """Get the full library tree structure."""
        db = get_db()

        folders = db.execute('SELECT * FROM folders ORDER BY sort_order, name').fetchall()

        sources = db.execute(
            'SELECT id, title, source_type, original_url, folder_id, '
            'created_at, updated_at FROM sources ORDER BY created_at DESC'
        ).fetchall()

        episodes = db.execute(
            'SELECT e.id, e.source_id, e.title, e.status, e.voice_id, '
            'e.total_duration_secs, e.folder_id, e.created_at, '
            'p.percent_listened, p.last_played_at '
            'FROM episodes e '
            'LEFT JOIN playback_state p ON e.id = p.episode_id '
            'ORDER BY e.created_at DESC'
        ).fetchall()

        return jsonify(
            {
                'folders': [dict(f) for f in folders],
                'sources': [dict(s) for s in sources],
                'episodes': [dict(e) for e in episodes],
            }
        )

    @bp.route('/preview-clean', methods=['POST'])
    def preview_clean() -> Response | tuple[Response, int]:
        """Preview normalization without saving."""
        data = request.json
        if not data or not data.get('text'):
            return jsonify({'error': 'Provide text'}), 400

        options = CleaningOptions(
            remove_non_text=data.get('remove_non_text', False),
            handle_tables=data.get('handle_tables', True),
            speak_urls=data.get('speak_urls', True),
            expand_abbreviations=data.get('expand_abbreviations', True),
            code_block_rule=data.get('code_block_rule', 'skip'),
            preserve_parentheses=data.get('preserve_parentheses', True),
            preserve_structure=data.get('preserve_structure', True),
            paragraph_spacing=data.get('paragraph_spacing', 2),
            section_spacing=data.get('section_spacing', 3),
            list_item_spacing=data.get('list_item_spacing', 1),
        )

        cleaned = normalize_text(data['text'], options)
        return jsonify({'cleaned_text': cleaned})

    @bp.route('/preview-content', methods=['POST'])
    def preview_content() -> Response:
        """Preview content without importing - for URL and git repos."""
        data = request.json
        if not data:
            return jsonify({'error': 'Provide content type'}), 400

        content_type = data.get('type')
        db = get_db()
        settings = _get_cleaning_settings(db)

        options = CleaningOptions(
            remove_non_text=settings.get('clean_remove_non_text', False),
            handle_tables=settings.get('clean_handle_tables', True),
            speak_urls=settings.get('clean_speak_urls', True),
            expand_abbreviations=settings.get('clean_expand_abbreviations', True),
            code_block_rule=settings.get('code_block_rule', 'skip'),
            preserve_parentheses=settings.get('clean_preserve_parentheses', True),
            preserve_structure=settings.get('preserve_structure', True),
            paragraph_spacing=settings.get('paragraph_spacing', 2),
            section_spacing=settings.get('section_spacing', 3),
            list_item_spacing=settings.get('list_item_spacing', 1),
        )

        try:
            if content_type == 'url':
                url = data.get('url')
                if not url:
                    return jsonify({'error': 'URL is required'}), 400

                url_extraction = settings.get('url_extraction_method', 'jina')
                use_jina = url_extraction == 'jina'

                result = ingest_url(url, use_jina=use_jina, jina_fallback=False)
                cleaned = normalize_text(result['raw_text'], options)

                return jsonify(
                    {
                        'title': result['title'],
                        'raw_text': result['raw_text'][:10000],
                        'cleaned_text': cleaned[:10000],
                        'total_chars': len(result['raw_text']),
                        'source_type': 'url_import',
                    }
                )

            elif content_type == 'git':
                url = data.get('url')
                subpath = data.get('subpath')
                if not url:
                    return jsonify({'error': 'Git URL is required'}), 400

                preview = preview_git_repository(url, subpath)
                return jsonify(
                    {
                        'title': preview['suggested_title'],
                        'files': preview['files'],
                        'total_files': preview['total_files'],
                        'total_chars': preview['total_chars'],
                        'preview_text': preview['preview_text'],
                        'source_type': 'git_repository',
                    }
                )

            else:
                return jsonify({'error': 'Invalid content type'}), 400

        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception('Preview content failed')
            return jsonify({'error': str(e)}), 500

    @bp.route('/preview-chunks', methods=['POST'])
    def preview_chunks() -> Response | tuple[Response, int]:
        """Preview chunking without creating an episode."""
        data = request.json
        if not data or not data.get('text'):
            return jsonify({'error': 'Provide text'}), 400

        chunks = chunk_text(
            data['text'],
            strategy=data.get('strategy', 'paragraph'),
            max_chars=data.get('max_chars', 2000),
        )
        return jsonify({'chunks': chunks, 'count': len(chunks)})


def _get_cleaning_settings(db) -> dict[str, Any]:
    """Get user's cleaning settings from database."""
    rows = db.execute(
        "SELECT key, value FROM settings WHERE key LIKE 'clean_%' OR key = 'code_block_rule' OR key = 'url_extraction_method'"
    ).fetchall()
    return {r['key']: r['value'] for r in rows}
