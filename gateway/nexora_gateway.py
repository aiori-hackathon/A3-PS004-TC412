import re
import socket
import subprocess

HOST = "172.20.10.2"
PORT = 5050

ALLOWED_DOMAINS = {
    "secure.nexora.test",
    "sensor.nexora.test",
}


def check_dnssec(domain):
    if domain not in ALLOWED_DOMAINS:
        return "ERROR: Domain not allowed"

    try:
        result = subprocess.run(
            [
                "wsl", "dig",
                "@127.0.0.1",
                domain, "A", "+dnssec",
                "+time=5", "+tries=1",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        output = result.stdout

        status_match = re.search(
            r"status:\s+([A-Z]+)", output
        )
        flags_match = re.search(
            r"flags:\s*([^;]+);", output
        )

        status = (
            status_match.group(1)
            if status_match else "UNKNOWN"
        )

        flags = (
            set(flags_match.group(1).split())
            if flags_match else set()
        )

        ip_match = re.search(
            rf"(?im)^{re.escape(domain)}\.?\s+"
            r"\d+\s+IN\s+A\s+"
            r"(\d{1,3}(?:\.\d{1,3}){3})\s*$",
            output,
        )

        ip_address = (
            ip_match.group(1)
            if ip_match else "NONE"
        )

        if status == "NOERROR" and "ad" in flags:
            return f"SECURE|{domain}|{ip_address}"

        if status == "SERVFAIL":
            return f"VALIDATION_FAILED_OR_SERVFAIL|{domain}"

        if status == "NOERROR":
            return f"NO_AD_FLAG|{domain}|{ip_address}"

        return f"DNS_ERROR|{status}|{domain}"

    except subprocess.TimeoutExpired:
        return "ERROR: DNS query timed out"

    except OSError as error:
        return f"ERROR: Could not run WSL DNS query: {error}"


def main():
    with socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    ) as server:
        server.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )
        server.bind((HOST, PORT))
        server.listen(5)

        print("NEXORA gateway is running!")
        print(f"Listening on {HOST}:{PORT}")

        while True:
            connection, address = server.accept()

            with connection:
                print("Client connected:", address)

                try:
                    domain = connection.recv(256).decode().strip()
                    print("Requested domain:", domain)

                    response = check_dnssec(domain)
                    connection.sendall(
                        (response + "\n").encode()
                    )

                    print("Gateway response:", response)

                except (ConnectionError, UnicodeDecodeError) as error:
                    print("Client communication error:", error)


if __name__ == "__main__":
    main()