import pytest

from scores import framingham_office, prevent


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

    def test_risco_atinge_o_piso_de_1_por_cento(self):
        r = framingham_office.calcular(
            sexo="feminino", idade=30, imc=18.5, pas=90,
            em_tratamento_anti_hipertensivo=False, tabagismo=False, diabetes=False,
        )
        assert r.risco_10_anos == pytest.approx(0.01, abs=1e-9)
        assert r.risco_truncado is True

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


class TestPrevent:
    CASO_MEDIO = dict(idade=55, colesterol_total=200, hdl=50, pas=130, imc=27, egfr=90,
                       diabetes=False, tabagismo=False, anti_hipertensivo=False, estatina=False)
    CASO_ALTO_RISCO = dict(idade=65, colesterol_total=240, hdl=40, pas=150, imc=32, egfr=70,
                            diabetes=True, tabagismo=True, anti_hipertensivo=True, estatina=False)
    CASO_JOVEM_SAUDAVEL = dict(idade=35, colesterol_total=180, hdl=60, pas=115, imc=23, egfr=100,
                                diabetes=False, tabagismo=False, anti_hipertensivo=False, estatina=False)

    @pytest.mark.parametrize("sexo,risco_10_esperado,risco_30_esperado", [
        ("feminino", 3.6, 21.4),
        ("masculino", 4.7, 24.7),
    ])
    def test_perfil_medio(self, sexo, risco_10_esperado, risco_30_esperado):
        r = prevent.calcular(sexo=sexo, **self.CASO_MEDIO)
        assert r.dez_anos.risco * 100 == pytest.approx(risco_10_esperado, abs=0.2)
        assert r.trinta_anos is not None
        assert r.trinta_anos.risco * 100 == pytest.approx(risco_30_esperado, abs=0.2)

    @pytest.mark.parametrize("sexo,risco_10_esperado", [
        ("feminino", 29.8),
        ("masculino", 31.6),
    ])
    def test_perfil_alto_risco_sem_estimativa_30_anos(self, sexo, risco_10_esperado):
        r = prevent.calcular(sexo=sexo, **self.CASO_ALTO_RISCO)
        assert r.dez_anos.risco * 100 == pytest.approx(risco_10_esperado, abs=0.2)
        assert r.trinta_anos is None  # idade 65 está fora de FAIXA_30_ANOS (30-59)

    @pytest.mark.parametrize("sexo,risco_10_esperado,risco_30_esperado", [
        ("feminino", 0.4, 3.0),
        ("masculino", 0.6, 4.4),
    ])
    def test_perfil_jovem_saudavel(self, sexo, risco_10_esperado, risco_30_esperado):
        r = prevent.calcular(sexo=sexo, **self.CASO_JOVEM_SAUDAVEL)
        assert r.dez_anos.risco * 100 == pytest.approx(risco_10_esperado, abs=0.2)
        assert r.trinta_anos.risco * 100 == pytest.approx(risco_30_esperado, abs=0.2)

    @pytest.mark.parametrize("idade,tem_30_anos", [
        (29, False), (30, True), (59, True), (60, False), (79, False),
    ])
    def test_faixa_30_anos_e_o_limite_correto(self, idade, tem_30_anos):
        caso = dict(self.CASO_MEDIO)
        caso["idade"] = idade
        r = prevent.calcular(sexo="feminino", **caso)
        assert (r.trinta_anos is not None) == tem_30_anos

    def test_sexo_invalido_levanta_erro(self):
        with pytest.raises(ValueError):
            prevent.calcular(sexo="outro", **self.CASO_MEDIO)

    def test_contribuicoes_somam_a_diferenca_do_preditor_linear(self):
        r = prevent.calcular(sexo="feminino", **self.CASO_ALTO_RISCO)
        soma = sum(c.contribuicao for c in r.dez_anos.contribuicoes)
        assert soma == pytest.approx(
            r.dez_anos.preditor_linear - r.dez_anos.preditor_linear_referencia, abs=1e-9
        )
