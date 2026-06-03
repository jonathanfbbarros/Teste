# Jogo de Ímpar ou Par com Flask, Python e OpenCV

Este projeto é uma aplicação web simples para jogar **Ímpar ou Par** contra o computador.

A tela web captura uma imagem da webcam e envia para o backend Flask. O backend usa **OpenCV** para tentar identificar a quantidade de dedos levantados. Caso a leitura da câmera não seja confiável, o jogo usa o número manual selecionado na tela.

## Estrutura do projeto

```text
impar_par_opencv_flask/
├── app.py
├── game_logic.py
├── opencv_utils.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Como executar

### 1. Criar ambiente virtual

No Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

No macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Rodar o servidor Flask

```bash
python app.py
```

Depois acesse:

```text
http://127.0.0.1:5000
```

## Como jogar

1. Escolha **Par** ou **Ímpar**.
2. Selecione um número manual entre 0 e 5 como apoio.
3. Ative a câmera.
4. Mostre a mão para a câmera.
5. Clique em **Capturar e jogar**.

O computador sorteia um número entre 0 e 5. A soma das duas jogadas define se o resultado é par ou ímpar.

## Observação sobre o OpenCV

A detecção de dedos usa uma técnica simples baseada em:

- segmentação de pele em HSV;
- identificação do maior contorno;
- cálculo de `convexityDefects` para estimar os espaços entre os dedos.

Ela funciona melhor com:

- boa iluminação;
- fundo limpo;
- mão próxima e centralizada;
- pouca variação de objetos com cor semelhante à pele.

Para uma versão mais robusta, recomenda-se integrar **MediaPipe Hands** ou treinar um modelo específico de visão computacional.
