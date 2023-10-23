class CustomRequestMixin:

    """Allows adding custom returned_response for the tests. E.g. when endpoint_callback
    or component fetch_info is called the response isn't retrieved from flask api, but from custom
    tailored response passed in the constructor.

    Warning:
    -------
        the CusomRequestMixin should be first inheritor due to MRO
    """

    def __init__(self, *, returned_response: dict, **kwargs):
        super().__init__(**kwargs)
        self.returned_response = returned_response

    def get_request_dict(self):
        return self.returned_response
