import cv2
import mediapipe as mp

mp_maos = mp.solutions.hands
mp_desenho = mp.solutions.drawing_utils



def contar_dedos(pontos_mao, lado_mao):
    dedos = 0

    # Indicador, médio, anelar e mínimo
    pontas = [8, 12, 16, 20]
    bases = [6, 10, 14, 18]

    for ponta, base in zip(pontas, bases):
        if pontos_mao.landmark[ponta].y < pontos_mao.landmark[base].y:
            dedos += 1

    # Polegar
    if lado_mao == "Right":
        if pontos_mao.landmark[4].x < pontos_mao.landmark[3].x:
            dedos += 1
    else:
        if pontos_mao.landmark[4].x > pontos_mao.landmark[3].x:
            dedos += 1

    return dedos


camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("Erro: não foi possível acessar a câmera.")
    exit()

with mp_maos.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as maos:

    while True:
        sucesso, frame = camera.read()

        if not sucesso:
            print("Erro ao capturar imagem da câmera.")
            break

        frame = cv2.flip(frame, 1)

        imagem_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagem_rgb.flags.writeable = False

        resultado = maos.process(imagem_rgb)

        imagem_rgb.flags.writeable = True

        texto = "Nenhuma mao detectada"

        if resultado.multi_hand_landmarks and resultado.multi_handedness:
            pontos_mao = resultado.multi_hand_landmarks[0]
            lado_mao = resultado.multi_handedness[0].classification[0].label

            quantidade = contar_dedos(pontos_mao, lado_mao)

            mp_desenho.draw_landmarks(
                frame,
                pontos_mao,
                mp_maos.HAND_CONNECTIONS
            )

            texto = f"Dedos levantados: {quantidade}"

        cv2.putText(
            frame,
            texto,
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow("Contador de Dedos", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

camera.release()
cv2.destroyAllWindows()