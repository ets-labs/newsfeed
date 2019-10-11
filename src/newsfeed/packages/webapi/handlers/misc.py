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
                            'type': 'string',
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
            'post': {
                'summary': 'Post newsfeed event',
                'operationId': 'post_newsfeed_event',
                'tags': [
                    'Events',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                ],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                'properties': {
                                    'data': {
                                        'type': 'object',
                                        'example': {
                                            'field_1': 'some_data',
                                            'field_2': 'other_data',
                                            'field_etc': 'etc_data',
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                'responses': {
                    '202': {
                        'description': 'Event has been successfully posted',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/NewsfeedEvent',
                                },
                            },
                        },
                    },
                },
            },
        },
        '/newsfeed/{newsfeed_id}/events/{event_id}/': {
            'delete': {
                'summary': 'Delete newsfeed event',
                'operationId': 'delete_newsfeed_event',
                'tags': [
                    'Events',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                    {
                        'in': 'path',
                        'name': 'event_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                    },
                ],
                'responses': {
                    '204': {
                        'description': 'Newsfeed event has been successfully deleted',
                    },
                },
            },
        },
        '/newsfeed/{newsfeed_id}/subscriptions/': {
            'get': {
                'summary': 'Return newsfeed subscriptions',
                'operationId': 'get_newsfeed_subscriptions',
                'tags': [
                    'Subscriptions',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                ],
                'responses': {
                    '200': {
                        'description': 'List of newsfeed subscriptions',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/NewsfeedSubscriptionsList',
                                },
                            },
                        },
                    },
                },
            },
            'post': {
                'summary': 'Post newsfeed subscription',
                'operationId': 'post_newsfeed_subscription',
                'tags': [
                    'Subscriptions',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                ],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                'properties': {
                                    'from_newsfeed_id': {
                                        'type': 'string',
                                        'example': '124',
                                    },
                                    'to_newsfeed_id': {
                                        'type': 'string',
                                        'example': '123',
                                    },
                                },
                            },
                        },
                    },
                },
                'responses': {
                    '201': {
                        'description': 'Subscription has been successfully created',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/NewsfeedSubscription',
                                },
                            },
                        },
                    },
                },
            },
        },
        '/newsfeed/{newsfeed_id}/subscriptions/{subscription_id}/': {
            'delete': {
                'summary': 'Delete newsfeed subscription',
                'operationId': 'delete_newsfeed_subscription',
                'tags': [
                    'Subscriptions',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                    {
                        'in': 'path',
                        'name': 'subscription_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                    },
                ],
                'responses': {
                    '204': {
                        'description': 'Newsfeed subscription has been successfully deleted',
                    },
                },
            },
        },
        '/newsfeed/{newsfeed_id}/subscribers/subscriptions/': {
            'get': {
                'summary': 'Return newsfeed subscriber subscriptions',
                'operationId': 'get_newsfeed_subscriber_subscriptions',
                'tags': [
                    'Subscriptions',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                ],
                'responses': {
                    '200': {
                        'description': 'List of newsfeed subscriber subscriptions',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/NewsfeedSubscriptionsList',
                                },
                            },
                        },
                    },
                },
            },
        },
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
            'NewsfeedSubscription': {
                'properties': {
                    'id': {
                        'type': 'string',
                        'format': 'uuid',
                    },
                },
            },
            'NewsfeedSubscriptionsList': {
                'properties': {
                    'results': {
                        'type': 'array',
                        'items': {
                            '$ref': '#/components/schemas/NewsfeedSubscription',
                        },
                    },
                },
            },
        },
    },
}
