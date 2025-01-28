from django.http import HttpRequest


class ClientIPFilter:
    def filter(self, record):
        request = getattr(record, "request", None)
        if isinstance(request, HttpRequest):
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            record.client_ip = (
                x_forwarded_for.split(",")[0]
                if x_forwarded_for
                else request.META.get("REMOTE_ADDR")
            )
        else:
            record.client_ip = "unknown"
        return True
