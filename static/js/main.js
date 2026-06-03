const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startCameraBtn = document.getElementById('startCameraBtn');
const captureBtn = document.getElementById('captureBtn');
const manualPlayBtn = document.getElementById('manualPlayBtn');
const cameraStatus = document.getElementById('cameraStatus');
const manualNumber = document.getElementById('manualNumber');
const result = document.getElementById('result');
const debugImage = document.getElementById('debugImage');

let stream = null;

function getChoice() {
  return document.querySelector('input[name="choice"]:checked').value;
}

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 960, height: 600, facingMode: 'user' },
      audio: false
    });
    video.srcObject = stream;
    cameraStatus.textContent = 'Câmera ativada. Centralize sua mão e clique em Capturar e jogar.';
  } catch (error) {
    cameraStatus.textContent = 'Não foi possível ativar a câmera. Você ainda pode jogar manualmente.';
    console.error(error);
  }
}

function captureFrame() {
  if (!stream) return null;

  const width = video.videoWidth || 960;
  const height = video.videoHeight || 600;
  canvas.width = width;
  canvas.height = height;

  const ctx = canvas.getContext('2d');
  ctx.translate(width, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0, width, height);

  return canvas.toDataURL('image/jpeg', 0.9);
}

async function playGame(useCamera) {
  result.className = 'result-box empty';
  result.innerHTML = '<h3>Processando...</h3><p>Enviando jogada para o backend Flask.</p>';

  const image = useCamera ? captureFrame() : null;

  try {
    const response = await fetch('/play', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        choice: getChoice(),
        manualNumber: manualNumber.value,
        image
      })
    });

    const data = await response.json();

    if (!response.ok) throw new Error(data.error || 'Erro ao jogar.');

    const won = data.winner === 'usuario';
    const sourceLabel = data.source === 'opencv'
      ? `OpenCV detectou ${data.userNumber} dedo(s) com confiança ${data.confidence}.`
      : `Número manual utilizado: ${data.userNumber}.`;

    result.className = `result-box ${won ? 'win' : 'lose'}`;
    result.innerHTML = `
      <h3>${won ? 'Você venceu! 🔥' : 'Computador venceu 😅'}</h3>
      <p><strong>Sua escolha:</strong> ${data.choice === 'par' ? 'Par' : 'Ímpar'}</p>
      <p><strong>Sua jogada:</strong> ${data.userNumber} | <strong>Computador:</strong> ${data.computerNumber}</p>
      <p><strong>Total:</strong> ${data.total} (${data.parity === 'par' ? 'Par' : 'Ímpar'})</p>
      <p><strong>Origem da jogada:</strong> ${sourceLabel}</p>
      <p>${data.opencvMessage}</p>
    `;

    if (data.debugImage) {
      debugImage.src = data.debugImage;
      debugImage.classList.remove('hidden');
    }
  } catch (error) {
    result.className = 'result-box lose';
    result.innerHTML = `<h3>Ops!</h3><p>${error.message}</p>`;
  }
}

startCameraBtn.addEventListener('click', startCamera);
captureBtn.addEventListener('click', () => playGame(true));
manualPlayBtn.addEventListener('click', () => playGame(false));

if (navigator.mediaDevices?.getUserMedia) startCamera();
else cameraStatus.textContent = 'Seu navegador não liberou acesso à câmera. Use o modo manual.';
