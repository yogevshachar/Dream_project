def parse_tasklist(raw: str):
    lines = raw.splitlines()
    entries = []

    for line in lines:
        if line.strip() == "" or "Image Name" in line or "====" in line:
            continue
        try:
            parts = line.split()
            name = parts[0]
            pid = int(parts[1])
            mem_str = parts[-2].replace(",", "").replace("K", "")
            memory_kb = float(mem_str)

            entries.append({
                "process_name": name,
                "pid": pid,
                "memory_kb": memory_kb
            })
        except:
            continue

    return entries
