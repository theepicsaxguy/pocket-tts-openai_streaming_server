#!/usr/bin/env python3
"""Generate OpenAPI spec - mocks ML deps before app import."""

import os
import sys
import types


class DummyModule(types.ModuleType):
    def __init__(self, name):
        super().__init__(name)
        self._submodules = {}

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        if name not in self._submodules:
            self._submodules[name] = DummyModule(f'{self.__name__}.{name}')
        return self._submodules[name]

    def __call__(self, *a, **k):
        return lambda *a, **k: None

    def __iter__(self):
        return iter([])


# Install top-level and common submodules
for name in ['torch', 'torchaudio', 'scipy', 'soundfile', 'numpy']:
    sys.modules[name] = DummyModule(name)

for mod in ['scipy.signal', 'scipy.io', 'numpy.core', 'torch.nn', 'torch.Tensor']:
    parts = mod.split('.')
    parent = DummyModule(parts[0])
    sys.modules[mod] = parent
    for i in range(1, len(parts)):
        parent = getattr(parent, parts[i])
        full = '.'.join(parts[: i + 1])
        sys.modules[full] = parent

import inspect  # noqa: E402
import re  # noqa: E402
import textwrap  # noqa: E402

import yaml  # noqa: E402
from apispec import APISpec  # noqa: E402
from apispec.ext.marshmallow import MarshmallowPlugin  # noqa: E402
from flask import Flask  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CONVERTER_TYPE_MAP = {
    'int': {'type': 'integer'},
    'float': {'type': 'number'},
    'uuid': {'type': 'string', 'format': 'uuid'},
    'path': {'type': 'string'},
    'string': {'type': 'string'},
}


def convert_flask_path(path: str) -> tuple[str, dict[str, dict]]:
    """Convert Flask path with converters to OpenAPI format.

    Returns (openapi_path, param_type_schemas) where param_type_schemas
    maps parameter names to their OpenAPI schema dicts.
    """
    param_types: dict[str, dict] = {}

    def replace_param(match):
        raw = match.group(1)
        converter = 'string'
        name = raw
        if ':' in raw:
            converter, name = raw.split(':', 1)
        param_types[name] = CONVERTER_TYPE_MAP.get(converter, {'type': 'string'})
        return '{' + name + '}'

    openapi_path = re.sub(r'<([^>]+)>', replace_param, path)
    return openapi_path, param_types


def build_path_params(path: str, param_types: dict[str, dict]) -> list[dict]:
    """Build OpenAPI parameter objects for path parameters."""
    names = re.findall(r'\{(\w+)\}', path)
    return [
        {
            'name': n,
            'in': 'path',
            'required': True,
            'schema': param_types.get(n, {'type': 'string'}),
        }
        for n in names
    ]


def extract_request_body(view_func) -> dict | None:
    """Extract request body schema from a Flask view function's source code.

    Inspects the function source for request.json and request.files usage
    and generates the appropriate OpenAPI requestBody definition.
    """
    try:
        source = textwrap.dedent(inspect.getsource(view_func))
    except (OSError, TypeError):
        return None

    uses_files = 'request.files' in source
    uses_json = 'request.json' in source

    if not uses_json and not uses_files:
        return None

    content: dict[str, dict] = {}

    if uses_files:
        file_fields: set[str] = set()
        for m in re.finditer(r"request\.files\[['\"](\w+)['\"]\]", source):
            file_fields.add(m.group(1))
        for m in re.finditer(r"['\"](\w+)['\"]\s+in\s+request\.files", source):
            file_fields.add(m.group(1))

        schema: dict = {'type': 'object'}
        if file_fields:
            schema['properties'] = {
                f: {'type': 'string', 'format': 'binary'} for f in sorted(file_fields)
            }
        content['multipart/form-data'] = {'schema': schema}

    if uses_json:
        properties: dict[str, dict] = {}

        has_alias = bool(re.search(r'\bdata\s*=\s*request\.json', source))

        get_patterns = [r"request\.json\.get\(['\"](\w+)['\"]"]
        sub_patterns = [r"request\.json\[['\"](\w+)['\"]\]"]

        if has_alias:
            get_patterns.append(r"(?<!\w)data\.get\(['\"](\w+)['\"]")
            sub_patterns.append(r"(?<!\w)data\[['\"](\w+)['\"]\]")

        for pattern in get_patterns + sub_patterns:
            for m in re.finditer(pattern, source):
                name = m.group(1)
                if name not in properties:
                    properties[name] = _infer_field_type(name, source, has_alias)

        if has_alias:
            for m in re.finditer(r"['\"](\w+)['\"]\s+in\s+data(?:\b|[^.])", source):
                name = m.group(1)
                if name not in properties:
                    properties[name] = _infer_field_type(name, source, has_alias)

        allowed_match = re.search(r'allowed_fields\s*=\s*\[([^\]]+)\]', source)
        if allowed_match:
            for m in re.finditer(r"['\"](\w+)['\"]", allowed_match.group(1)):
                name = m.group(1)
                if name not in properties:
                    properties[name] = _infer_field_type(name, source, has_alias)

        schema = {'type': 'object'}
        if properties:
            schema['properties'] = {k: properties[k] for k in sorted(properties)}
        content['application/json'] = {'schema': schema}

    return {'content': content} if content else None


def _infer_field_type(name: str, source: str, has_alias: bool) -> dict:
    """Infer the OpenAPI type of a JSON body field from its usage context."""
    if name.endswith('_secs') or 'percent' in name:
        return {'type': 'number'}
    if name.endswith('_ids') or name == 'items':
        return {'type': 'array', 'items': {'type': 'string'}}

    patterns = [r"request\.json\.get\(['\"]" + re.escape(name) + r"['\"],\s*(.+?)\)"]
    if has_alias:
        patterns.append(r"(?<!\w)data\.get\(['\"]" + re.escape(name) + r"['\"],\s*(.+?)\)")

    for pattern in patterns:
        m = re.search(pattern, source)
        if m:
            default = m.group(1).strip()
            if default.startswith('['):
                return {'type': 'array', 'items': {'type': 'string'}}
            if default.startswith('{'):
                return {'type': 'object'}
            if default in ('True', 'False'):
                return {'type': 'boolean'}
            if re.match(r'^-?\d+$', default):
                return {'type': 'integer'}
            if re.match(r'^-?\d+\.\d+$', default):
                return {'type': 'number'}

    if any(s in name for s in ('length', 'order', 'index', 'count', 'max_chars')):
        return {'type': 'integer'}

    return {'type': 'string'}


def generate_spec() -> dict:
    from app.config import Config
    from app.logging_config import setup_logging

    setup_logging()

    app = Flask(
        __name__,
        template_folder=Config.get_template_folder(),
        static_folder=Config.get_static_folder(),
    )
    app.config['STREAM_DEFAULT'] = Config.STREAM_DEFAULT

    from app.routes import api

    app.register_blueprint(api)

    from app.studio import (
        episodes_routes,
        folders_routes,
        library_routes,
        playback_routes,
        settings_routes,
        sources_routes,
        studio_bp,
        tags_routes,
    )

    sources_routes.register_routes(studio_bp)
    episodes_routes.register_routes(studio_bp)
    folders_routes.register_routes(studio_bp)
    tags_routes.register_routes(studio_bp)
    playback_routes.register_routes(studio_bp)
    settings_routes.register_routes(studio_bp)
    library_routes.register_routes(studio_bp)
    app.register_blueprint(studio_bp)

    spec = APISpec(
        title='OpenVox API',
        version='1.0.0',
        openapi_version='3.0.3',
        plugins=[MarshmallowPlugin()],
    )

    for rule in app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue

        path, param_types = convert_flask_path(rule.rule)
        methods = [m for m in rule.methods if m not in ('HEAD', 'OPTIONS')]

        if not methods:
            continue

        operations: dict = {}
        for method in methods:
            view_func = app.view_functions.get(rule.endpoint)
            doc = (view_func.__doc__ or '').strip()
            summary = doc.split('\n')[0][:50] if doc else ''

            operation: dict = {
                'summary': summary,
                'description': doc,
                'responses': {'200': {'description': 'Success'}},
            }

            params = build_path_params(path, param_types)
            if params:
                operation['parameters'] = params

            if method in ('POST', 'PUT', 'PATCH') and view_func:
                body = extract_request_body(view_func)
                if body:
                    operation['requestBody'] = body

            operations[method.lower()] = operation

        if operations:
            spec.path(path=path, operations=operations)

    return spec.to_dict()


def main():
    output_path = sys.argv[1] if len(sys.argv) > 1 else 'openapi.yaml'
    spec = generate_spec()

    with open(output_path, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

    print(f'Generated: {output_path}')
    print(f'  - Paths: {len(spec.get("paths", {}))}')

    post_put_count = 0
    body_count = 0
    for path_ops in spec.get('paths', {}).values():
        for method in ('post', 'put', 'patch'):
            if method in path_ops:
                post_put_count += 1
                if 'requestBody' in path_ops[method]:
                    body_count += 1

    print(f'  - POST/PUT operations: {post_put_count}')
    print(f'  - With requestBody: {body_count}')


if __name__ == '__main__':
    main()
