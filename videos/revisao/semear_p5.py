#!/usr/bin/env python3
"""Acrescenta (ou substitui) o P5 · Protocolo "duas peças na mão" no projeto.json da Sala de revisão, sem mexer nos outros vídeos.
Gravação de 24/10 (croma verde, dólmã branco): IMG_5400/5401/5402 (plano aberto) e IMG_5404/5405 (mais perto, melhor).
Tempos = palavras do whisper (p5-protocolo/build/IMG_xxxx.words.json). ★ na nota = tomada que o Cleef recomenda."""
import json, subprocess
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
MINI = AQUI / "miniaturas"; MINI.mkdir(exist_ok=True)
ROT = "gravacao-2026-10-24/textos-validados.md (P5)"


def arq(n):
    return f"p5-protocolo/fonte/IMG_{n}.mp4"


def op(id_, rot, n, ini, fim, falado, aprovado, nota=""):
    dst = MINI / f"p5-{id_}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(round((ini + fim) / 2, 2)), "-i", str(RAIZ / arq(n)),
                    "-frames:v", "1", "-vf", "scale=180:-2", "-q:v", "4", str(dst)], check=True)
    return {"id": id_, "rotulo": f"{rot} · IMG_{n}", "arquivo": arq(n), "ini": ini, "fim": fim, "falado": falado,
            "aprovado": aprovado, "nota": nota, "miniatura": f"revisao/miniaturas/{dst.name}"}


A1 = "Olha essas duas peças. Essa aqui é a dentadura que a maioria das pessoas conhece, e essa outra é a prótese protocolo."
A2 = ("A dentadura fica só apoiada na gengiva, e quem segura ela é a sucção. Só que, quando a gente perde os dentes, o osso "
      "embaixo da gengiva vai diminuindo com o tempo… começa a soltar quando a pessoa fala, come ou ri.")
A3 = "Já o protocolo não depende da sucção, porque ele é parafusado em implantes que ficam dentro do osso."
A4 = "E, se for na arcada de cima, ainda tem um detalhe que pouca gente conta: ele deixa o céu da boca livre…"
A5 = "Agora, isso não quer dizer que é tudo ou nada. Entre uma e outra existe um caminho do meio, que é a sobredentadura…"
A6 = "E qual desses caminhos serve pra você, quem diz é o osso. É por isso que eu sempre começo pela tomografia…"
A7 = "Só que, seja qual for o caminho, o cuidado continua depois. No protocolo, é limpeza por baixo todo dia…"
A8 = "Então, se você quer entender qual é o seu caso, me chama no WhatsApp e me conta como está hoje…"
SEM_PECAS = "sem as peças na mão (ela segura o microfone): a imagem das peças entra em cima"

faixas = [
    {"id": "gancho", "nome": "Gancho + 1 · As duas peças", "escolha": "uma (H1 do roteiro; os outros ganchos não foram gravados)",
     "opcoes": [
         op("g-5404", "H1 · tomada 4", 5404, 1.62, 16.25, "Olha essas duas peças. Uma é a dentadura, que muita gente já conhece, "
            "e a outra é a prótese tipo protocolo. A diferença das duas é que uma é presa apenas na gengiva, que é a dentadura, "
            "e a prótese tipo protocolo é parafusada sobre implantes.", A1, "★ mais perto da câmera e a mais fluida; " + SEM_PECAS),
         op("g-5402", "H1 · tomada 3", 5402, 9.35, 23.1, "Olha só essas duas peças. Uma se chama dentadura, ela é presa apenas na "
            "gengiva do paciente. Já a outra prótese é prótese tipo protocolo, ela é parafusada sobre implantes.", A1, "plano aberto"),
         op("g-5401", "H1 · tomada 2", 5401, 36.2, 52.2, "Olha só essas duas peças. Uma se chama dentadura e a outra prótese tipo "
            "protocolo. Elas são parecidas e diferentes ao mesmo tempo. A dentadura é presa apenas na gengiva do paciente. Já a "
            "prótese tipo protocolo é parafusada, ela é fixa.", A1, "plano aberto; tem o \"parecidas e diferentes\""),
         op("g-5400", "H1 · tomada 1", 5400, 52.8, 65.9, "Olha só a diferença dessas duas próteses. Uma se chama dentadura. Ela está "
            "apenas aderida na gengiva. Já a outra, é uma prótese tipo protocolo. Ela é fixa sobre implantes, que traz mais "
            "estabilidade para o paciente.", A1, "plano aberto"),
     ]},
    {"id": "b2", "nome": "2 · A dentadura folga", "escolha": "uma",
     "opcoes": [
         op("b2-5404", "tomada 2", 5404, 22.5, 36.65, "A dentadura fica fixa apenas na gengiva, e com o tempo o paciente vai "
            "perdendo osso e gengiva naturalmente. A prótese vai folgando, trazendo desconforto, trazendo insegurança na hora de "
            "falar, na hora de sorrir.", A2, "★ curta e limpa"),
         op("b2-5404b", "tomada 2 + ajuste", 5404, 22.5, 41.65, "… na hora de sorrir. Então, ela precisa sempre de um ajuste, "
            "ou então de refazer a própria prótese.", A2, "com a frase do ajuste no fim"),
         op("b2-5402", "tomada 1", 5402, 71.1, 92.6, "A dentadura, ela é presa apenas na gengiva do paciente, fazendo a sucção. Só "
            "que com o tempo, o paciente vai perdendo osso, vai perdendo gengiva e ela vai folgando… Não sente aquela segurança "
            "com a prótese.", A2, "plano aberto; fala a sucção (como no roteiro), mais longa"),
     ]},
    {"id": "b3", "nome": "3 · O protocolo", "escolha": "uma",
     "opcoes": [
         op("b3-5404a", "tomada 1", 5404, 47.82, 56.5, "Já a prótese protocolo não. Ela é fixa, traz mais estabilidade para o "
            "paciente, ele tem mais segurança para falar, para comer, até para gargalhar.", A3, "★ termina no \"gargalhar\""),
         op("b3-5404b", "tomada 2", 5404, 61.5, 73.45, "Já a prótese tipo protocolo não. Ela é parafusada, ela fica fixa, traz "
            "mais conforto, traz mais segurança, traz mais estabilidade para o paciente.", A3,
            "fala \"parafusada\" (como o roteiro); tem uma pausa longa dentro de \"protocolo\""),
     ]},
    {"id": "b4", "nome": "4 · Céu da boca livre", "escolha": "uma ou sai (se precisar encurtar)",
     "opcoes": [
         op("b4-5404a", "tomada 1", 5404, 75.18, 89.75, "E tem uma coisinha que quase ninguém fala. A prótese tipo protocolo, "
            "principalmente quando é em cima, ela traz mais conforto. O céu da boca, ela fica livre, então o paciente consegue "
            "comer melhor, até sentir o gosto do alimento melhor.", A4, "★ inteira e fluida"),
         op("b4-5404b", "tomada 2", 5404, 91.7, 123.4, "E tem uma coisinha que quase ninguém fala. A prótese tipo protocolo "
            "superior, deixa o céu da boca livre. Traz mais conforto… (repete) …e até dá para sentir melhor o gosto dos alimentos.",
            A4, "tem uma repetição no meio: precisa de corte"),
     ]},
    {"id": "b6", "nome": "5 · Quem decide (avaliação e tomografia)", "escolha": "uma ou sai",
     "opcoes": [
         op("b6-5404", "tomada 1", 5404, 139.68, 153.0, "E aí, qual desses caminhos você deve seguir? Calma, tudo precisa passar "
            "por uma avaliação. A gente faz uma avaliação clínica, a gente solicita uma tomografia e tudo é planejado de acordo "
            "com o seu caso e sua necessidade.", A6, "★ única tomada"),
     ]},
    {"id": "b5", "nome": "6 · Virada (protocolo não é para todos)", "escolha": "uma",
     "opcoes": [
         op("b5-5405b", "tomada 3", 5405, 35.14, 58.75, "Ah, doutora, então quer dizer que todo caso a gente vai substituir a "
            "dentadura para a prótese de protocolo? Calma, não é bem assim. Cada caso é específico e bem avaliado. Tem paciente "
            "que relata que usa 20, 30 anos uma dentadura e não tem queixa, se sente confortável em usá-la. Então a gente não vai "
            "substituir. Cada caso a gente discute e acha o melhor caminho.", A5,
            "★ mais perto (\"vem pertinho\"); no lugar da sobredentadura, que não foi gravada"),
         op("b5-5405a", "tomada 2", 5405, 2.0, 21.5, "Ah, doutora, então quer dizer que a prótese de protocolo tem que substituir "
            "todas as dentaduras? Não, não é bem assim. Tem paciente que usa 20, 30 anos uma dentadura e não tem nenhum "
            "desconforto… A gente vai escolher o tratamento de acordo com a necessidade do paciente.", A5, "mais curta"),
         op("b5-5404", "tomada 1", 5404, 187.1, 198.0, "Ah, então quer dizer que a prótese tipo protocolo é o melhor e tem que ser "
            "em todos os casos? Não, tem paciente que relata que prefere usar a dentadura…", A5, "termina tropeçando"),
     ]},
    {"id": "b7", "nome": "7 · Manutenção (o depois)", "escolha": "não gravado", "opcoes": []},
    {"id": "final", "nome": "Chamada", "escolha": "uma (o anúncio fecha no botão do WhatsApp)",
     "opcoes": [
         op("f-5405d", "tomada 4", 5405, 89.62, 95.3, "Como saber qual é o melhor caso? Qual é a melhor solução? Entre em contato "
            "conosco, a gente descobre juntos.", A8, "★ fecha em \"a gente descobre juntos\""),
         op("f-5405a", "tomada 1", 5405, 70.92, 75.15, "Então, você quer saber qual é a melhor solução para você? Entre em contato "
            "conosco.", A8, "a mais curta"),
         op("f-5405c", "tomada 3", 5405, 82.24, 86.7, "Ah, doutora, e aí, qual é o meu caso? Entre em contato conosco, a gente já "
            "dá a sua avaliação.", A8, "voz do cliente na pergunta"),
     ]},
]
video = {"id": "P5", "titulo": "Protocolo: duas peças na mão", "roteiro": ROT, "fonte": "p5-protocolo/fonte/",
         "status": "13 tomadas casadas · 1 bloco sem gravação (manutenção) · sem as peças na mão; ★ = recomendação do Cleef",
         "faixas": faixas}
pj = AQUI / "projeto.json"
p = json.loads(pj.read_text())
p["videos"] = [v for v in p["videos"] if v.get("id") != "P5"] + [video]
p["atualizado"] = datetime.now().isoformat(timespec="seconds")
pj.write_text(json.dumps(p, ensure_ascii=False, indent=1))
print("ok P5:", sum(len(f["opcoes"]) for f in faixas), "opções")
