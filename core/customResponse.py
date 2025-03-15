from rest_framework.response import Response


class CustomResponse(Response):
    def __init__(self, data=None, status=None, message=None, success=True):
        # Include success status in the response data
        response_data = {
            'success': success,
            'message': message,
            'data': data
        }
        super().__init__(data=response_data, status=status)
        self.message = message

    
    # def success(self):
