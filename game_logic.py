from __future__ import annotations


def validar_numero(value) -> int:
    """Valida número da jogada entre 0 e 5."""
    try:
        numero = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Informe um número inteiro entre 0 e 5.") from exc

    if numero < 0 or numero > 5:
        raise ValueError("O número precisa estar entre 0 e 5.")
    return numero


def decidir_vencedor(escolha_usuario: str, numero_usuario: int, numero_computador: int) -> dict[str, str | int]:
    """Regra central do jogo de Ímpar ou Par."""
    total = numero_usuario + numero_computador
    parity = "par" if total % 2 == 0 else "impar"
    winner = "usuario" if parity == escolha_usuario else "computador"

    return {
        "total": total,
        "parity": parity,
        "winner": winner,
    }
