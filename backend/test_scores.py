import pytest

from scores import framingham_office


class TestFraminghamOfficeBased:
    def test_caso_documentado_cvrisk_homem(self):
        r = framingham_office.calcular(
            sexo="masculino", idade=55, imc=30, pas=140,
            em_tratamento_anti_hipertensivo=False, tabagismo=False, diabetes=False,
        )
        assert r.risco_10_anos * 100 == pytest.approx(16.7, abs=0.2)

    def test_mulher_tabagista_pas_elevada(self):
        r = framingham_office.calcular(
            sexo="feminino", idade=58, imc=28, pas=135,
            em_tratamento_anti_hipertensivo=False, tabagismo=True, diabetes=False,
        )
        assert r.risco_10_anos * 100 == pytest.approx(15.49, abs=0.2)

    def test_homem_sem_fatores_risco(self):
        r = framingham_office.calcular(
            sexo="masculino", idade=50, imc=27, pas=125,
            em_tratamento_anti_hipertensivo=False, tabagismo=False, diabetes=False,
        )
        assert r.risco_10_anos * 100 == pytest.approx(9.66, abs=0.2)

    def test_mulher_baixo_risco(self):
        r = framingham_office.calcular(
            sexo="feminino", idade=45, imc=22, pas=110,
            em_tratamento_anti_hipertensivo=False, tabagismo=False, diabetes=False,
        )
        assert r.risco_10_anos * 100 == pytest.approx(2.23, abs=0.2)

    def test_risco_e_limitado_entre_1_e_30_por_cento(self):
        r = framingham_office.calcular(
            sexo="masculino", idade=65, imc=32, pas=150,
            em_tratamento_anti_hipertensivo=True, tabagismo=True, diabetes=True,
        )
        assert r.risco_10_anos == pytest.approx(0.30, abs=1e-9)

    def test_sexo_invalido_levanta_erro(self):
        with pytest.raises(ValueError):
            framingham_office.calcular(
                sexo="outro", idade=50, imc=25, pas=120,
                em_tratamento_anti_hipertensivo=False, tabagismo=False, diabetes=False,
            )

    def test_contribuicoes_somam_a_diferenca_do_preditor_linear(self):
        r = framingham_office.calcular(
            sexo="masculino", idade=60, imc=33, pas=150,
            em_tratamento_anti_hipertensivo=True, tabagismo=True, diabetes=True,
        )
        soma_contribuicoes = sum(c.contribuicao for c in r.contribuicoes)
        assert soma_contribuicoes == pytest.approx(
            r.preditor_linear - r.preditor_linear_referencia, abs=1e-9
        )
