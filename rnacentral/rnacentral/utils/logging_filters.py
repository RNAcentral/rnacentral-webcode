class ClientIPFilter:
    def filter(self, record):
        # Attempt to add the client IP to the log record
        request = getattr(record, "request", None)
        if request:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            record.client_ip = (
                x_forwarded_for.split(",")[0]
                if x_forwarded_for
                else request.META.get("REMOTE_ADDR")
            )
        else:
            record.client_ip = "unknown"
        return True
