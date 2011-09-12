# http://groups.google.com/group/wtforms/browse_thread/thread/caf6fcb8f678a6f0
class MultiDict(object): 
    def __init__(self, request_handler): 
        self.request_handler = request_handler 

    def __iter__(self): 
        return iter(self.request_handler.request.arguments) 

    def __len__(self): 
        return len(self.request_handler.request.arguments) 

    def __contains__(self, name): 
        # We use request.arguments because get_arguments always returns a 
        # value regardless of the existence of the key. 
        return (name in self.request_handler.request.arguments) 

    def getlist(self, name): 
        # get_arguments by default strips whitespace from the input data, 
        # so we pass strip=False to stop that in case we need to validate 
        # on whitespace. 
        return self.request_handler.get_arguments(name, strip=False) 
