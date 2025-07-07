import subprocess
import asyncio
import re

async def start_localtunnel(port: int) -> str:
    process = await asyncio.create_subprocess_exec(
        "lt", "--port", str(port),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    public_url = None

    while True:
        line = await process.stdout.readline()
        if not line:
            break
        decoded_line = line.decode().strip()
        print(decoded_line)

        # Example line: your url is: https://happy-raccoon-12.loca.lt
        match = re.search(r'your url is: (https://.+)', decoded_line)
        if match:
            public_url = match.group(1)
            break

    if not public_url:
        raise RuntimeError("Failed to obtain public URL from localtunnel.")

    return public_url