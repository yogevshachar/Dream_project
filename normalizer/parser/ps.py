def parse_ps(raw: str):
    lines = raw.strip().splitlines()
    entries = []

    for line in lines[1:]:  # Skip header
        parts = line.split(maxsplit=10)  # Allow full command to remain uncut
        if len(parts) < 11:
            continue

        try:
            pid = int(parts[1])
            memory_kb = float(parts[5])  # RSS in KB
            command = parts[10]

            entries.append({
                "process_name": command.split("/")[-1].split()[0],  # extract base command
                "pid": pid,
                "memory_kb": memory_kb
            })
        except Exception:
            continue

    return entries
