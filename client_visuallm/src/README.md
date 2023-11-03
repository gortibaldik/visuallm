# Bootstraping - Component Level

The user navigates the page, the page creates the list of components which are displayed in the navbar. Afterwards the default component (or the currently navigated component) is loaded.

The component sends a `GET` request to its API endpoint. From this endpoint a message similar to this one arrives:

```json
{
    'elementDescriptions': [
        {'heading': True,
        'heading_level': 2,
        'name': 'plain_text',
        'type': 'plain',
        'value': 'Interactive Generation'},
        ...
        {'address': 'button',
        'button_text': 'Send Dataset Configuration',
        'disabled': False,
        'name': 'button',
        'subelement_configs': [SubElementConfiguration(subtype='choices',
                                                        name='choices',
                                                        configuration={'choices': ['train',
                                                                                'validation'],
                                                                    'selected': 'train',
                                                                    'text': 'Select '
                                                                            'Dataset '
                                                                            'Split'},
                                                        parent_name='button'),
                                SubElementConfiguration(subtype='min_max',
                                                        name='min_max',
                                                        configuration={'max': 131437,
                                                                    'min': 0,
                                                                    'selected': 0,
                                                                    'step_size': 1.0,
                                                                    'text': 'Select '
                                                                            'Dataset '
                                                                            'Sample'},
                                                        parent_name='button')],
        'type': 'button'},
        {'address': 'barchart',
        'long_contexts': True,
        'name': 'barchart',
        'piece_infos': [PieceInfo(pieceTitle='You must be '
                                            'very fast. '
                                            'Hunting is one '
                                            'of my favorite '
                                            'hobbies.',
                                barHeights=[100.0, 100],
                                barAnnotations=['100.00%',
                                                '2.81954'],
                                barNames=['F1-Score',
                                            'Perplexity'])],
        'selectable': False,
        'type': 'softmax'},
        ...
    ],
    'result': 'success'}
```

From this message the component retrieves the names of all the elements which constitute the page. This action happens at the moment when the component is loaded, therefore it is not
possible to change the displayed elements as a response to some API call. (elements inside can be changed, their order and occurrences cannot).
