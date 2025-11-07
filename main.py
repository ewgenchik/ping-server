function checkTarget(target) {
    let host = target;
    let port = 80;

    if (target.includes(':')) {
        const parts = target.split(':');
        if (parts.length === 2 && !isNaN(parts[1]) && parts[1] !== '') {
            host = parts[0];
            port = parseInt(parts[1], 10);
        } else {
            return Promise.resolve(false);
        }
    }

    // ⬇️ Замените URL на ваш Render-адрес!
    const url = `https://ping-server.onrender.com/check?host=${encodeURIComponent(host)}&port=${port}`;

    return fetch(url)
        .then(res => res.json())
        .then(data => !!data.alive)
        .catch(() => false);
}
