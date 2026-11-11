#!/usr/bin/env python3
"""Testes das regras puras do conferir.py.  Rodar: python3 teste_conferir.py"""
import unittest
from conferir import janelas_excluidas, dentro, cobre_rosto, julgar_janela, ler_lufs, para_saida, julgar_capa, julgar_caixa


class Regras(unittest.TestCase):
    def test_tempo_da_gravacao_vira_tempo_do_reel(self):
        # v0670: take 1,6–23,3 s; o cartão em 23,0 da gravação cai em 21,4 do Reel
        takes = [{"a": 1.6, "b": 23.3}]
        self.assertEqual(para_saida(23.0, takes), 21.4)
        self.assertEqual(janelas_excluidas([{"kind": "card", "at": 23.0, "to": "end"}], 24.7, takes),
                         [(21.4, 24.7)])
        dois = [{"a": 1.0, "b": 5.0}, {"a": 8.0, "b": 12.0}]
        self.assertEqual(para_saida(9.0, dois), 5.0)       # 4 s do 1º take + 1 s do 2º
        self.assertIsNone(para_saida(6.5, dois))           # trecho cortado

    def test_exclui_tela_dividida_e_cartao(self):
        beats = [{"type": "broll", "mode": "split", "at": 6.3, "to": 15.0},
                 {"type": "broll", "mode": "full", "at": 2, "to": 3},
                 {"type": "scene", "kind": "card", "at": 15.0, "to": "end"}]
        fora = janelas_excluidas(beats, 18.0)
        self.assertEqual(fora, [(6.3, 15.4), (15.0, 18.0)])      # +0,4 s: a volta da Brenda depois da tela dividida
        self.assertTrue(dentro(10, fora))
        self.assertFalse(dentro(2.5, fora))      # broll em tela cheia não sai da conta

    def test_tela_cheia_planejada_sai_da_conta(self):
        # P5 (24/10): prato e bifurcação aprovados no storyboard não reprovam como "sem a Brenda"
        beats = [{"type": "broll", "at": 2, "to": 3, "planejado": True}, {"type": "broll", "at": 5, "to": 6}]
        fora = janelas_excluidas(beats, 10.0)
        self.assertEqual(fora, [(2.0, 3.0)])
        self.assertFalse(dentro(5.5, fora))      # sem a marca, continua contando

    def test_legenda_abaixo_do_queixo_passa(self):
        self.assertFalse(cobre_rosto(leg_y=1218, leg_h=123, olhos=806, boca=994))

    def test_legenda_na_boca_reprova(self):
        self.assertTrue(cobre_rosto(leg_y=950, leg_h=123, olhos=806, boca=994))

    def test_legenda_acima_da_testa_passa(self):
        self.assertFalse(cobre_rosto(leg_y=300, leg_h=123, olhos=806, boca=994))

    def test_janela_boa(self):
        self.assertEqual(julgar_janela([(0.31, 0.35)] * 10, 0.30), [])

    def test_teto_demais_reprova(self):
        # olhos a 55% da altura = muito teto em cima da Brenda (o defeito de 12/10)
        self.assertEqual(julgar_janela([(0.55, 0.35)] * 10, 0.30), ["olhos a 55% (alvo 30%)"])

    def test_caixa_muda_o_alvo(self):
        self.assertEqual(julgar_janela([(0.40, 0.35)] * 10, 0.40), [])
        self.assertTrue(julgar_janela([(0.40, 0.35)] * 10, 0.30))

    def test_rosto_pequeno(self):
        self.assertEqual(julgar_janela([(0.30, 0.15)] * 10, 0.30), ["rosto pequeno (15% da largura)"])

    def test_sem_brenda(self):
        self.assertEqual(julgar_janela([None] * 6 + [(0.3, 0.3)] * 4, 0.30), ["sem a Brenda"])

    def test_janela_toda_excluida_nao_julga(self):
        self.assertEqual(julgar_janela([], 0.30), [])

    def test_capa_pronta(self):
        rosto = (500, 1180, 300, 780, 806, 994)
        self.assertEqual(julgar_capa(rosto, desvio=48.0), [])
        self.assertEqual(julgar_capa(None, desvio=48.0), ["capa (1º quadro) sem a Brenda"])
        self.assertEqual(julgar_capa(rosto, desvio=2.0), ["capa (1º quadro) em branco ou chapada"])

    def test_caixa_curta_reprova(self):
        self.assertTrue(julgar_caixa(2.95))
        self.assertEqual(julgar_caixa(3.0), [])
        self.assertEqual(julgar_caixa(0.0), [])

    def test_le_lufs_do_ffmpeg(self):
        saida = ("[Parsed_ebur128_0] Summary:\n\n  Integrated loudness:\n    I:         -14.2 LUFS\n"
                 "    Threshold: -24.4 LUFS\n\n  True peak:\n    Peak:       -1.3 dBFS\n")
        self.assertEqual(ler_lufs(saida), (-14.2, -1.3))
        self.assertEqual(ler_lufs("nada"), (None, None))


if __name__ == "__main__":
    unittest.main(verbosity=1)
