class SwaggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Short-circuit for swagger fake view
        if getattr(request, "swagger_fake_view", False):
            return self.get_response(request)

        # Normal processing
        response = self.get_response(request)
        return response
