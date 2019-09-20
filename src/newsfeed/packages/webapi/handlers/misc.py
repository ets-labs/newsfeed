"""Miscellaneous handlers."""

import copy

from aiohttp import web


async def get_status_handler(_):
    """Handle status requests."""
    return web.json_response({'status': 'OK'})


async def get_openapi_schema_handler(request):
    """Handle OpenAPI schema requests."""
    schema = copy.deepcopy(OPENAPI_SCHEMA)
    schema['servers'].append({'url': request.query.get('base_path', '/')})
    return web.json_response(schema)


OPENAPI_SCHEMA = {
    'openapi': '3.0.2',
    'info': {
        'version': '1.0.0',
        'title': 'NewsFeed Microservice',
    },
    'servers': [],
    'paths': {
        '/status/': {
            'get': {
                'summary': 'Return current microservice status',
                'operationId': 'get_status',
                'tags': [
                    'Miscellaneous',
                ],
                'responses': {
                    '200': {
                        'description': 'Information about current service status',
                    },
                },
            },
        },
        '/docs/': {
            'get': {
                'summary': 'Return microservice OpenAPI v3 documentation',
                'operationId': 'get_docs',
                'tags': [
                    'Miscellaneous',
                ],
                'responses': {
                    '200': {
                        'description': 'Service OpenAPI v3 documentation',
                    },
                },
            },
        },
    },
    'components': {
        'schemas': {
        },
    },
}
