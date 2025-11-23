"""Analyze Emenda Pix with AI use case"""
from typing import Dict, List, Optional
from datetime import datetime
from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository
from src.application.use_cases.emenda_pix.calculate_trust_score import CalculateTrustScoreUseCase
from src.infrastructure.ai.invoice_analyzer import InvoiceAnalyzer
from src.infrastructure.external.transferegov_client import TransferegovClient


class AnalyzeEmendaPixIAUseCase:
    """Use case to analyze Emenda Pix with AI"""
    
    def __init__(self, repository: EmendaPixRepository, openai_client=None):
        self.repository = repository
        from src.infrastructure.ai.invoice_analyzer import InvoiceAnalyzer
        self.invoice_analyzer = InvoiceAnalyzer(openai_client=openai_client)
        self.transferegov_client = TransferegovClient()
    
    async def execute(self, emenda_id: str) -> EmendaPix:
        """Analyze emenda with AI and generate alerts"""
        emenda = await self.repository.find_by_id(emenda_id)
        if not emenda:
            raise ValueError(f"Emenda {emenda_id} not found")
        
        # Calcular percentual executado
        emenda.percentual_executado = emenda.calcular_percentual_executado()
        
        # Verificar se está atrasada
        if emenda.esta_atrasada():
            emenda.status_execucao = 'atrasada'
        
        # Gerar alertas
        alertas = []
        
        # Alerta de atraso
        if emenda.esta_atrasada():
            dias_atraso = (datetime.now() - emenda.data_prevista_conclusao).days
            alertas.append({
                'tipo': 'atraso',
                'severidade': 'alta',
                'mensagem': f'Emenda está {dias_atraso} dias atrasada. Prazo previsto: {emenda.data_prevista_conclusao.strftime("%d/%m/%Y")}',
                'data': datetime.now().isoformat()
            })
        
        # Alerta de baixa execução
        if emenda.percentual_executado < 10 and emenda.data_inicio:
            dias_decorridos = (datetime.now() - emenda.data_inicio).days
            if dias_decorridos > 90:
                alertas.append({
                    'tipo': 'baixa_execucao',
                    'severidade': 'media',
                    'mensagem': f'Apenas {emenda.percentual_executado:.1f}% executado após {dias_decorridos} dias',
                    'data': datetime.now().isoformat()
                })
        
        # Alerta de risco de desvio
        risco_score = self._calcular_risco_desvio(emenda)
        emenda.risco_desvio = risco_score
        
        if risco_score > 0.7:
            alertas.append({
                'tipo': 'risco_desvio',
                'severidade': 'alta',
                'mensagem': f'Alto risco de desvio detectado (score: {risco_score:.1%})',
                'data': datetime.now().isoformat()
            })
        
        # Analisar notas fiscais se disponíveis
        invoice_analyses = []
        if emenda.documentos_comprobatórios:
            for doc in emenda.documentos_comprobatórios:
                if doc.get("tipo") == "nota_fiscal" and doc.get("xml_content"):
                    try:
                        invoice_analysis = self.invoice_analyzer.analyze_invoice_xml(
                            xml_content=doc.get("xml_content"),
                            emenda_objetivo=emenda.objetivo or ""
                        )
                        if invoice_analysis.get("success"):
                            invoice_analyses.append({
                                "doc_id": doc.get("id"),
                                "analysis": invoice_analysis
                            })
                    except Exception as e:
                        logger.warning("invoice_analysis_failed", error=str(e))
        
        # Buscar Plano de Ação do Transferegov.br (Integração Vigia Pix)
        plano_acao = None
        if emenda.numero_emenda:
            try:
                codigo_emenda = f"{emenda.ano}-{emenda.numero_emenda}"
                plano_acao = await self.transferegov_client.get_plano_acao(codigo_emenda)
            except Exception as e:
                logger.warning("transferegov_fetch_failed", error=str(e), emenda_id=emenda_id)
        
        # IA de Classificação/PLN: Categorizar e extrair objeto
        categoria_gasto = None
        objeto_principal = None
        localizacao_extraida = None
        
        if emenda.objetivo or (plano_acao and plano_acao.get("descricao_programacao_orcamentaria")):
            texto_analise = emenda.objetivo or plano_acao.get("descricao_programacao_orcamentaria", "")
            if texto_analise:
                try:
                    classificacao = await self._categorizar_gasto(texto_analise)
                    categoria_gasto = classificacao.get("categoria")
                    objeto_principal = classificacao.get("objeto_principal")
                    localizacao_extraida = classificacao.get("localizacao_extraida")
                except Exception as e:
                    logger.warning("categorizacao_failed", error=str(e))
        
        # Análise de Anomalias: Comparar Portal vs Transferegov
        anomalias_cruzamento = []
        if plano_acao and emenda.valor_pago > 0:
            try:
                anomalias_cruzamento = self._analisar_anomalias_cruzamento(
                    emenda.valor_pago,
                    emenda.valor_aprovado,
                    plano_acao.get("situacao_plano_acao")
                )
                # Adicionar anomalias aos alertas
                for anomalia in anomalias_cruzamento:
                    if anomalia.get("severidade") == "alta":
                        alertas.append({
                            'tipo': anomalia.get("tipo", "anomalia_cruzamento"),
                            'severidade': 'alta',
                            'mensagem': anomalia.get("mensagem", "Inconsistência detectada entre dados financeiros e execução"),
                            'data': datetime.now().isoformat()
                        })
            except Exception as e:
                logger.warning("anomalias_analysis_failed", error=str(e))
        
        # Calcular Trust Score (Triangulação de Dados)
        trust_score_use_case = CalculateTrustScoreUseCase()
        trust_score_result = trust_score_use_case.calculate(emenda)
        
        # Análise IA
        analise_ia = {
            'transparencia_score': self._calcular_transparencia(emenda),
            'execucao_score': emenda.percentual_executado / 100,
            'risco_desvio': risco_score,
            'trust_score': trust_score_result.get('trust_score', 0.0) if trust_score_result.get('success') else 0.0,
            'trust_level': trust_score_result.get('level', 'regular') if trust_score_result.get('success') else 'regular',
            'trust_factors': trust_score_result.get('factors', {}) if trust_score_result.get('success') else {},
            'recomendacoes': self._gerar_recomendacoes(emenda),
            'invoice_analyses': invoice_analyses if invoice_analyses else None,
            'plano_acao': plano_acao,
            'categoria_gasto': categoria_gasto,
            'objeto_principal': objeto_principal,
            'localizacao_extraida': localizacao_extraida,
            'anomalias_cruzamento': anomalias_cruzamento,
            'data_analise': datetime.now().isoformat()
        }
        
        emenda.alertas = alertas
        emenda.analise_ia = analise_ia
        
        await self.repository.save(emenda)
        return emenda
    
    def _calcular_risco_desvio(self, emenda: EmendaPix) -> float:
        """Calcula score de risco de desvio (0-1)"""
        risco = 0.0
        
        # Fator 1: Diferença entre aprovado e pago
        if emenda.valor_aprovado > 0:
            diferenca = (emenda.valor_aprovado - emenda.valor_pago) / emenda.valor_aprovado
            if diferenca > 0.5:
                risco += 0.3
        
        # Fator 2: Atraso
        if emenda.esta_atrasada():
            risco += 0.3
        
        # Fator 3: Falta de transparência
        if not emenda.tem_noticias and not emenda.documentos_comprobatórios:
            risco += 0.2
        
        # Fator 4: Baixa execução com tempo decorrido
        if emenda.percentual_executado < 20 and emenda.data_inicio:
            dias = (datetime.now() - emenda.data_inicio).days
            if dias > 180:
                risco += 0.2
        
        return min(risco, 1.0)
    
    def _calcular_transparencia(self, emenda: EmendaPix) -> float:
        """Calcula score de transparência (0-1)"""
        score = 0.0
        
        if emenda.objetivo:
            score += 0.2
        if emenda.descricao_detalhada:
            score += 0.2
        if emenda.plano_trabalho:
            score += 0.2
        if emenda.tem_noticias:
            score += 0.2
        if emenda.documentos_comprobatórios:
            score += 0.2
        
        return score
    
    def _gerar_recomendacoes(self, emenda: EmendaPix) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recomendacoes = []
        
        if emenda.esta_atrasada():
            recomendacoes.append("Solicitar esclarecimentos sobre o atraso na execução")
        
        if emenda.percentual_executado < 50:
            recomendacoes.append("Acompanhar de perto a execução das metas do plano de trabalho")
        
        if not emenda.tem_noticias:
            recomendacoes.append("Buscar informações públicas sobre a execução desta emenda")
        
        if emenda.risco_desvio and emenda.risco_desvio > 0.7:
            recomendacoes.append("Encaminhar para órgãos de controle para fiscalização")
        
        return recomendacoes
    
    async def _categorizar_gasto(self, descricao: str) -> Dict:
        """
        Categoriza gasto usando PLN (Processamento de Linguagem Natural)
        
        Retorna:
        {
            "categoria": "Saúde" | "Educação" | "Infraestrutura" | ...,
            "objeto_principal": "Compra de ambulância",
            "localizacao_extraida": "Rua X, Bairro Y" (opcional)
        }
        """
        try:
            import re
            
            descricao_lower = descricao.lower()
            
            # Categorias e palavras-chave
            categorias = {
                "Saúde": ["saúde", "hospital", "posto", "ambulância", "medicamento", "equipamento médico", "unidade básica"],
                "Educação": ["educação", "escola", "creche", "material didático", "reforma escolar", "merenda"],
                "Infraestrutura": ["pavimentação", "asfalto", "ponte", "estrada", "calçada", "drenagem", "iluminação"],
                "Assistência Social": ["assistência", "cesta básica", "bolsa", "benefício", "programa social"],
                "Segurança": ["segurança", "polícia", "viaturas", "câmeras", "monitoramento"],
                "Meio Ambiente": ["meio ambiente", "saneamento", "água", "esgoto", "coleta de lixo"],
                "Cultura": ["cultura", "biblioteca", "teatro", "evento cultural", "patrimônio"],
                "Esporte": ["esporte", "quadra", "campo", "ginásio", "equipamento esportivo"]
            }
            
            # Encontrar categoria
            categoria_encontrada = "Outros"
            maior_score = 0
            
            for categoria, palavras in categorias.items():
                score = sum(1 for palavra in palavras if palavra in descricao_lower)
                if score > maior_score:
                    maior_score = score
                    categoria_encontrada = categoria
            
            # Extrair objeto principal (primeira frase ou trecho relevante)
            objeto_principal = descricao.split('.')[0].strip()
            if len(objeto_principal) > 100:
                objeto_principal = objeto_principal[:100] + "..."
            
            # Tentar extrair localização (padrões comuns)
            localizacao_extraida = None
            padroes_localizacao = [
                r"rua\s+[\w\s]+",
                r"avenida\s+[\w\s]+",
                r"bairro\s+[\w\s]+",
                r"distrito\s+[\w\s]+"
            ]
            
            for padrao in padroes_localizacao:
                match = re.search(padrao, descricao_lower, re.IGNORECASE)
                if match:
                    localizacao_extraida = match.group(0).title()
                    break
            
            # Se tiver OpenAI, usar para melhorar categorização
            if hasattr(self, 'openai_client') and self.openai_client:
                try:
                    from openai import OpenAI
                    client = self.openai_client or OpenAI()
                    
                    prompt = f"""
                    Analise a seguinte descrição de emenda parlamentar e retorne JSON:
                    {{
                        "categoria": "Saúde" | "Educação" | "Infraestrutura" | "Assistência Social" | "Segurança" | "Meio Ambiente" | "Cultura" | "Esporte" | "Outros",
                        "objeto_principal": "resumo do objeto em até 20 palavras",
                        "localizacao_extraida": "localização se mencionada ou null"
                    }}
                    
                    Descrição: {descricao}
                    """
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Você é um analisador de emendas parlamentares. Retorne apenas JSON válido."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        response_format={"type": "json_object"}
                    )
                    
                    import json
                    resultado_ia = json.loads(response.choices[0].message.content)
                    
                    if resultado_ia.get("categoria"):
                        categoria_encontrada = resultado_ia["categoria"]
                    if resultado_ia.get("objeto_principal"):
                        objeto_principal = resultado_ia["objeto_principal"]
                    if resultado_ia.get("localizacao_extraida"):
                        localizacao_extraida = resultado_ia["localizacao_extraida"]
                        
                except Exception as e:
                    logger.warning("openai_categorizacao_failed", error=str(e))
            
            return {
                "categoria": categoria_encontrada,
                "objeto_principal": objeto_principal,
                "localizacao_extraida": localizacao_extraida
            }
            
        except Exception as e:
            logger.error("categorizacao_error", error=str(e))
            return {
                "categoria": "Outros",
                "objeto_principal": descricao[:50] if descricao else "Não especificado",
                "localizacao_extraida": None
            }
    
    def _analisar_anomalias_cruzamento(
        self,
        valor_pago: float,
        valor_total: float,
        situacao_plano: Optional[str]
    ) -> List[Dict]:
        """
        Analisa anomalias comparando dados financeiros (Portal) vs execução (Transferegov)
        
        Args:
            valor_pago: Valor pago (Portal da Transparência)
            valor_total: Valor total aprovado
            situacao_plano: Situação do plano de ação (Transferegov)
        
        Returns:
            Lista de anomalias detectadas
        """
        anomalias = []
        
        if not situacao_plano:
            return anomalias
        
        situacao_lower = situacao_plano.lower()
        percentual_pago = (valor_pago / valor_total * 100) if valor_total > 0 else 0
        
        # Anomalia 1: 100% pago mas plano em análise ou cancelado
        if percentual_pago >= 99 and situacao_lower in ["em análise", "cancelado", "suspenso"]:
            anomalias.append({
                "tipo": "alto_risco_irregularidade",
                "severidade": "alta",
                "mensagem": f"⚠️ ALTO RISCO: {percentual_pago:.1f}% do valor foi pago, mas o plano de ação está '{situacao_plano}'. Possível irregularidade grave.",
                "detalhes": {
                    "valor_pago": valor_pago,
                    "percentual_pago": percentual_pago,
                    "situacao_plano": situacao_plano
                }
            })
        
        # Anomalia 2: Plano cancelado mas dinheiro pago
        if situacao_lower == "cancelado" and valor_pago > 0:
            anomalias.append({
                "tipo": "plano_cancelado_com_pagamento",
                "severidade": "alta",
                "mensagem": f"⚠️ INCONSISTÊNCIA: Plano de ação foi cancelado, mas R$ {valor_pago:,.2f} já foram pagos.",
                "detalhes": {
                    "valor_pago": valor_pago,
                    "situacao_plano": situacao_plano
                }
            })
        
        # Anomalia 3: Plano em análise mas pagamento muito alto
        if situacao_lower == "em análise" and percentual_pago > 50:
            anomalias.append({
                "tipo": "pagamento_antecipado",
                "severidade": "media",
                "mensagem": f"⚠️ ATENÇÃO: {percentual_pago:.1f}% já foi pago enquanto o plano ainda está em análise.",
                "detalhes": {
                    "valor_pago": valor_pago,
                    "percentual_pago": percentual_pago,
                    "situacao_plano": situacao_plano
                }
            })
        
        # Anomalia 4: Plano aprovado mas nenhum pagamento
        if situacao_lower == "aprovado" and valor_pago == 0:
            anomalias.append({
                "tipo": "plano_aprovado_sem_pagamento",
                "severidade": "baixa",
                "mensagem": f"ℹ️ INFO: Plano aprovado mas ainda não houve pagamento.",
                "detalhes": {
                    "situacao_plano": situacao_plano
                }
            })
        
        return anomalias

