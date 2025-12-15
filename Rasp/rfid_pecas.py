#!/usr/bin/env python3
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import webbrowser
import time
import sys
import signal

print("Inicializando leitor NFC RC522...")

# Configuração GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Dicionário de IDs e suas respectivas URLs
CARTOES_CADASTRADOS = {
    584183925461: "https://borntofightf.github.io/Projeto_inova-o/index4.html",
    197057667619: "https://borntofightf.github.io/Projeto_inova-o/index5.html",
    59448255196: "https://borntofightf.github.io/Projeto_inova-o/index1.html",
    584192453749: "https://borntofightf.github.io/Projeto_inova-o/index3.html"
}

# Timeout handler
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Timeout na leitura!")

try:
    reader = SimpleMFRC522()
    print("✓ Leitor inicializado!")
    print(f"✓ {len(CARTOES_CADASTRADOS)} cartões cadastrados no sistema")
    print("=" * 50)
except Exception as e:
    print(f"✗ ERRO ao inicializar: {e}")
    print("\nVerifique:")
    print("1. SPI habilitado? → sudo raspi-config > Interface > SPI")
    print("2. Fiação correta?")
    print("   SDA → Pin 24 (GPIO8)")
    print("   SCK → Pin 23 (GPIO11)")
    print("   MOSI → Pin 19 (GPIO10)")
    print("   MISO → Pin 21 (GPIO9)")
    print("   GND → GND")
    print("   RST → Pin 22 (GPIO25)")
    print("   3.3V → 3.3V")
    print("3. Biblioteca instalada? → sudo pip3 install mfrc522")
    sys.exit(1)

try:
    contador = 0
    while True:
        try:
            contador += 1
            print(f"\n[Tentativa {contador}] Aproxime o cartão...")
            print("⏱️  Aguardando leitura (timeout: 10s)...")
            
            # Configura timeout de 10 segundos
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)
            
            try:
                id, text = reader.read()
                signal.alarm(0)  # Cancela timeout
                
                print("\n" + "=" * 50)
                print("✓ CARTÃO DETECTADO!")
                print(f"ID: {id}")
                print(f"Texto: {text.strip() if text else '(vazio)'}")
                print("=" * 50)
                
                # Verifica se o ID está cadastrado
                if id in CARTOES_CADASTRADOS:
                    url = CARTOES_CADASTRADOS[id]
                    print(f"→ ID RECONHECIDO! Abrindo página...")
                    print(f"→ URL: {url}")
                    try:
                        webbrowser.open(url)
                        print("→ Site aberto com sucesso!")
                    except Exception as web_err:
                        print(f"→ Erro ao abrir navegador: {web_err}")
                    time.sleep(3)
                else:
                    print("→ ID NÃO RECONHECIDO!")
                    print(f"→ ID recebido: {id}")
                    print(f"→ IDs cadastrados: {list(CARTOES_CADASTRADOS.keys())}")
                
                time.sleep(2)
                
            except TimeoutError:
                signal.alarm(0)
                print("\n⚠️  TIMEOUT! Nenhum cartão detectado em 10s")
                print("PROBLEMA DETECTADO:")
                print("→ O módulo RC522 não está respondendo")
                print("\nPossíveis causas:")
                print("1. SPI não habilitado no Raspberry Pi")
                print("2. Fiação incorreta ou mal conectada")
                print("3. Módulo RC522 defeituoso")
                print("4. Antena do RC522 danificada")
                print("\nTeste: Rode 'lsmod | grep spi' no terminal")
                print("Deve aparecer 'spi_bcm2835' ou similar")
                time.sleep(2)
            
        except KeyboardInterrupt:
            signal.alarm(0)
            print("\n\nEncerrando...")
            break
        except Exception as e:
            signal.alarm(0)
            print(f"\n✗ Erro: {e}")
            time.sleep(2)

finally:
    print("\nLimpando GPIO...")
    GPIO.cleanup()
    print("Finalizado.")