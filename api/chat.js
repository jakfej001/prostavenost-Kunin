export default async function handler(req, res) {
  // CORS for local dev
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) return res.status(500).json({ error: 'ANTHROPIC_API_KEY not configured' });

  try {
    const { question, context } = req.body;
    if (!question) return res.status(400).json({ error: 'Missing question' });

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        system: 'Jsi analytik stavebních rozpočtů pro RD Kunín č.p. 393. Odpovídej česky, stručně a přesně. Částky v CZK. 3 období prostavěnosti: P1=k 25.12.25, P2=k 18.3., P3=k 16.4. (omítky). Statusy: done=hotovo, partial=rozpracováno, viceprace=prostavěno>rozpočet, meneprace=záporné p2/p3, manual=ruční bez rozpočtu, zero=nezahájeno.',
        messages: [{ role: 'user', content: (context || '') + '\n\nDotaz: ' + question }],
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      return res.status(response.status).json({ error: errText });
    }

    const data = await response.json();
    const answer = data.content
      ?.filter(c => c.type === 'text')
      .map(c => c.text)
      .join('\n') || 'Žádná odpověď.';

    return res.status(200).json({ answer });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
