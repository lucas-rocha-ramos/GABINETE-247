export const config = {
    runtime: 'edge',
};

export default async function handler(req) {
    if (req.method !== 'POST') {
        return new Response('Método não permitido', { status: 405 });
    }

    try {
        // Recebe o formulário com o arquivo de áudio/vídeo do frontend
        const formData = await req.formData();
        const file = formData.get('file');

        if (!file) {
            return new Response(JSON.stringify({ error: 'Nenhum arquivo enviado.' }), { status: 400 });
        }

        // Monta a requisição para a API da OpenAI (Whisper)
        const openaiFormData = new FormData();
        openaiFormData.append('file', file);
        openaiFormData.append('model', 'whisper-1');
        // verbose_json é crucial para obtermos os tempos exatos (timestamps) de cada fala
        openaiFormData.append('response_format', 'verbose_json'); 

        // Envia para a OpenAI
        const openaiResponse = await fetch('https://api.openai.com/v1/audio/transcriptions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
            },
            body: openaiFormData
        });

        const data = await openaiResponse.json();

        // Retorna os dados para o nosso frontend
        return new Response(JSON.stringify(data), {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
        });

    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), { status: 500 });
    }
}
