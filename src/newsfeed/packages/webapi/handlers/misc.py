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
        '/newsfeed/{newsfeed_id}/events/': {
            'get': {
                'summary': 'Return newsfeed events',
                'operationId': 'get_newsfeed_events',
                'tags': [
                    'Events',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'integer',
                        },
                    },
                ],
                'responses': {
                    '200': {
                        'description': 'List of newsfeed events',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/NewsfeedEventsList',
                                },
                            },
                        },
                    },
                },
            },
        },

        # '/sign-offs/{signoff_id}/': {
        #     'get': {
        #         'summary': 'Return specified sign-off details',
        #         'operationId': 'get_signoff',
        #         'tags': [
        #             'Sign-offs',
        #         ],
        #         'parameters': [
        #             {
        #                 'in': 'path',
        #                 'name': 'signoff_id',
        #                 'required': True,
        #                 'schema': {
        #                     'type': 'integer',
        #                 },
        #             },
        #         ],
        #         'responses': {
        #             '200': {
        #                 'description': 'Sign-off details',
        #                 'content': {
        #                     'application/json': {
        #                         'schema': {
        #                             '$ref': '#/components/schemas/Signoff',
        #                         },
        #                     },
        #                 },
        #             },
        #         },
        #     },
        #     'put': {
        #         'summary': 'Update specified sign-off',
        #         'operationId': 'update_signoff',
        #         'tags': [
        #             'Sign-offs',
        #         ],
        #         'parameters': [
        #             {
        #                 'in': 'path',
        #                 'name': 'signoff_id',
        #                 'required': True,
        #                 'schema': {
        #                     'type': 'integer',
        #                 },
        #             },
        #         ],
        #         'requestBody': {
        #             'required': True,
        #             'content': {
        #                 'application/json': {
        #                     'schema': {
        #                         'properties': {
        #                             'name': {
        #                                 'type': 'string',
        #                                 'example': 'golang-developer-roadmap',
        #                             },
        #                             'contribution_type': {
        #                                 'type': 'string',
        #                                 'example': 'medium',
        #                             },
        #                             'repository': {
        #                                 'type': 'integer',
        #                                 'example': 123,
        #                             },
        #                             'approver': {
        #                                 'type': 'string',
        #                                 'example': 'agreen',
        #                             },
        #                         },
        #                     },
        #                 },
        #             },
        #         },
        #         'responses': {
        #             '200': {
        #                 'description': 'Sign-off has been successfully updated',
        #                 'content': {
        #                     'application/json': {
        #                         'schema': {
        #                             '$ref': '#/components/schemas/Signoff',
        #                         },
        #                     },
        #                 },
        #             },
        #         },
        #     },
        #     'delete': {
        #         'summary': 'Delete specified sign-off',
        #         'operationId': 'delete_signoff',
        #         'tags': [
        #             'Sign-offs',
        #         ],
        #         'parameters': [
        #             {
        #                 'in': 'path',
        #                 'name': 'signoff_id',
        #                 'required': True,
        #                 'schema': {
        #                     'type': 'integer',
        #                 },
        #             },
        #         ],
        #         'responses': {
        #             '204': {
        #                 'description': 'Sign-off has been successfully deleted',
        #             },
        #         },
        #     },
        # },
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
            'NewsfeedEvent': {
                'properties': {
                    'id': {
                        'type': 'string',
                        'format': 'uuid',
                    },
                },
            },
            'NewsfeedEventsList': {
                'properties': {
                    'results': {
                        'type': 'array',
                        'items': {
                            '$ref': '#/components/schemas/NewsfeedEvent',
                        },
                    },
                },
            },
        },
    },
}
