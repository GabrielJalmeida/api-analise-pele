from __future__ import annotations

import argparse
import sqlite3
import sys
import unicodedata
import re
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from database import CAMINHO_BANCO


BASE_DIR = Path(__file__).resolve().parent
BANCO = CAMINHO_BANCO
PASTA_IMAGENS = BASE_DIR / "media" / "produtos"

CATALOGO = [{'source': 'LIMPEZA/Limpeza (1).png',
  'nome': 'Equilíbrio Diário — Espuma de Limpeza',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Espuma facial leve para remover impurezas e excesso de oleosidade sem ressecar a pele.',
  'conteudo': '150 ml',
  'ativos_principais': 'Niacinamida + Pantenol',
  'preco': 39.9,
  'estoque': 25,
  'categoria': 'limpeza',
  'tipo_pele': 'mista',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'LIMPEZA/Limpeza (10).png',
  'nome': 'Brisa de Lótus — Gel de Limpeza Suave',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Gel de limpeza suave para a rotina diária, com sensação confortável e acabamento fresco.',
  'conteudo': '120 ml',
  'ativos_principais': 'Extrato de Lótus + Pantenol',
  'preco': 42.9,
  'estoque': 24,
  'categoria': 'limpeza',
  'tipo_pele': 'normal',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'LIMPEZA/Limpeza (2).png',
  'nome': 'Toque de Camomila — Água Micelar Calmante',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Água micelar calmante para limpar e remover resíduos com suavidade, sem necessidade de enxágue.',
  'conteudo': '200 ml',
  'ativos_principais': 'Camomila + Bisabolol',
  'preco': 37.9,
  'estoque': 28,
  'categoria': 'limpeza',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'LIMPEZA/Limpeza (3).png',
  'nome': 'Pureza Botânica — Gel de Limpeza Purificante',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Gel purificante para peles com tendência à oleosidade, ajudando a limpar sem sensação pesada.',
  'conteudo': '120 ml',
  'ativos_principais': 'Chá Verde + Zinco PCA',
  'preco': 44.9,
  'estoque': 22,
  'categoria': 'limpeza',
  'tipo_pele': 'oleosa',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'LIMPEZA/Limpeza (4).png',
  'nome': 'Nuvem de Algodão — Mousse de Limpeza Cremosa',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Mousse cremosa de limpeza para peles que pedem conforto e suavidade durante a higienização.',
  'conteudo': '150 ml',
  'ativos_principais': 'Algodão + Pantenol',
  'preco': 43.9,
  'estoque': 20,
  'categoria': 'limpeza',
  'tipo_pele': 'seca',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'LIMPEZA/Limpeza (5).png',
  'nome': 'Aurora Verde — Sabonete Facial em Gel',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sabonete facial em gel de textura leve para remover oleosidade e impurezas da rotina diária.',
  'conteudo': '140 ml',
  'ativos_principais': 'Chá Verde + Niacinamida',
  'preco': 38.9,
  'estoque': 26,
  'categoria': 'limpeza',
  'tipo_pele': 'oleosa',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'LIMPEZA/Limpeza (6).png',
  'nome': 'Limpeza Essencial — Óleo de Limpeza Suave',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Óleo de limpeza que dissolve resíduos e protetor solar mantendo uma sensação confortável na '
                     'pele.',
  'conteudo': '180 ml',
  'ativos_principais': 'Esqualano + Óleo de Jojoba',
  'preco': 49.9,
  'estoque': 18,
  'categoria': 'limpeza',
  'tipo_pele': 'seca',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'LIMPEZA/Limpeza (7).png',
  'nome': 'Ritual de Arroz — Gel de Limpeza Cremoso',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Gel cremoso para limpeza cotidiana com toque macio e fórmula pensada para preservar o conforto.',
  'conteudo': '120 ml',
  'ativos_principais': 'Extrato de Arroz + Glicerina',
  'preco': 41.9,
  'estoque': 21,
  'categoria': 'limpeza',
  'tipo_pele': 'normal',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'LIMPEZA/Limpeza (8).png',
  'nome': 'Frescor de Pepino — Espuma de Limpeza Refrescante',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Espuma refrescante para limpar a pele e reduzir a sensação de peso ao longo do dia.',
  'conteudo': '150 ml',
  'ativos_principais': 'Extrato de Pepino + Zinco PCA',
  'preco': 40.9,
  'estoque': 23,
  'categoria': 'limpeza',
  'tipo_pele': 'mista',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'LIMPEZA/Limpeza (9).png',
  'nome': 'Véu de Aveia — Leite de Limpeza Suave',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Leite de limpeza delicado para remover resíduos mantendo a pele macia e confortável.',
  'conteudo': '180 ml',
  'ativos_principais': 'Aveia Coloidal + Pantenol',
  'preco': 45.9,
  'estoque': 20,
  'categoria': 'limpeza',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'HIDRATANTE/Hidratante (10).png',
  'nome': 'Ceramidas Suaves — Hidratante Restaurador',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Hidratante restaurador de textura cremosa para reforçar a sensação de conforto e maciez da pele.',
  'conteudo': '50 g',
  'ativos_principais': 'Ceramidas + Pantenol',
  'preco': 59.9,
  'estoque': 19,
  'categoria': 'hidratante',
  'tipo_pele': 'seca',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'HIDRATANTE/Hidratante (2).png',
  'nome': 'Noite Serena — Creme Hidratante Noturno',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Creme noturno nutritivo para apoiar a hidratação da pele durante o período de descanso.',
  'conteudo': '50 g',
  'ativos_principais': 'Esqualano + Ceramidas',
  'preco': 64.9,
  'estoque': 18,
  'categoria': 'hidratante',
  'tipo_pele': 'seca',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'HIDRATANTE/Hidratante (3).png',
  'nome': 'Sálvia Leve — Hidratante Facial em Gel-Creme',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Gel-creme leve de rápida absorção para hidratar sem deixar sensação pesada ou excessivamente '
                     'oleosa.',
  'conteudo': '50 g',
  'ativos_principais': 'Sálvia + Niacinamida',
  'preco': 54.9,
  'estoque': 25,
  'categoria': 'hidratante',
  'tipo_pele': 'oleosa',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'HIDRATANTE/Hidratante (4).png',
  'nome': 'Aveia Dourada — Hidratante Nutritivo',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Hidratante nutritivo para peles com tendência ao ressecamento e necessidade de maior conforto.',
  'conteudo': '50 g',
  'ativos_principais': 'Aveia + Manteiga de Karité',
  'preco': 61.9,
  'estoque': 17,
  'categoria': 'hidratante',
  'tipo_pele': 'seca',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'HIDRATANTE/Hidratante (5).png',
  'nome': 'Toque de Seda — Hidratante Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Hidratante facial de acabamento macio para manter a pele equilibrada e confortável no dia a dia.',
  'conteudo': '50 g',
  'ativos_principais': 'Pantenol + Ácido Hialurônico',
  'preco': 56.9,
  'estoque': 22,
  'categoria': 'hidratante',
  'tipo_pele': 'normal',
  'pele_sensivel': False,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'HIDRATANTE/Hidratante (6).png',
  'nome': 'Brisa Mineral — Hidratante Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Hidratante facial leve com sensação fresca e fórmula versátil para diferentes momentos da '
                     'rotina.',
  'conteudo': '50 g',
  'ativos_principais': 'Água Mineral + Niacinamida',
  'preco': 57.9,
  'estoque': 21,
  'categoria': 'hidratante',
  'tipo_pele': 'mista',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'HIDRATANTE/Hidratante (7).png',
  'nome': 'Nuvem de Algodão — Hidratante Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Creme hidratante de toque confortável e fórmula delicada para uso diário em diferentes perfis de '
                     'pele.',
  'conteudo': '50 g',
  'ativos_principais': 'Algodão + Pantenol',
  'preco': 58.9,
  'estoque': 23,
  'categoria': 'hidratante',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'HIDRATANTE/Hidratante (8).png',
  'nome': 'Equilíbrio Diário — Gel-Creme Hidratante',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Gel-creme de hidratação diária com textura equilibrada para áreas que alternam oleosidade e '
                     'ressecamento.',
  'conteudo': '50 g',
  'ativos_principais': 'Niacinamida + Ácido Hialurônico',
  'preco': 55.9,
  'estoque': 24,
  'categoria': 'hidratante',
  'tipo_pele': 'mista',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'HIDRATANTE/Hidratante (9).png',
  'nome': 'Aqua Calm — Loção Hidratante',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Loção hidratante leve para acalmar a sensação de desconforto e manter a hidratação sem pesar.',
  'conteudo': '50 ml',
  'ativos_principais': 'Ácido Hialurônico + Pantenol',
  'preco': 53.9,
  'estoque': 24,
  'categoria': 'hidratante',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'HIDRATANTE/Hidratante (1).png',
  'nome': 'Conforto Essencial — Creme Hidratante',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Creme hidratante versátil para manter maciez, conforto e suporte à barreira de hidratação da '
                     'pele.',
  'conteudo': '50 g',
  'ativos_principais': 'Ácido Hialurônico + Ceramidas',
  'preco': 62.9,
  'estoque': 20,
  'categoria': 'hidratante',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'SERUM/Serum (1).png',
  'nome': 'Noite Botânica — Sérum Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum noturno de textura leve para complementar rotinas de cuidado e renovação da aparência da '
                     'pele.',
  'conteudo': '30 ml',
  'ativos_principais': 'Retinal Suave + Esqualano',
  'preco': 79.9,
  'estoque': 15,
  'categoria': 'serum',
  'tipo_pele': 'normal',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'SERUM/Serum (10).png',
  'nome': 'Brilho de Arroz — Sérum Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum iluminador para promover aparência uniforme e viçosa com textura confortável para uso '
                     'diário.',
  'conteudo': '30 ml',
  'ativos_principais': 'Fermento de Arroz + Vitaminas',
  'preco': 72.9,
  'estoque': 18,
  'categoria': 'serum',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'SERUM/Serum (2).png',
  'nome': 'Orvalho Dourado — Sérum Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum hidratante para reforçar maciez e conforto com combinação de ativos de suporte à barreira '
                     'cutânea.',
  'conteudo': '30 ml',
  'ativos_principais': 'Ceramidas + Ácido Hialurônico',
  'preco': 74.9,
  'estoque': 17,
  'categoria': 'serum',
  'tipo_pele': 'seca',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'SERUM/Serum (3).png',
  'nome': 'Aurora C — Sérum Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum antioxidante para complementar a rotina e favorecer uma aparência mais luminosa e '
                     'uniforme.',
  'conteudo': '30 ml',
  'ativos_principais': 'Vitamina C + Niacinamida',
  'preco': 76.9,
  'estoque': 20,
  'categoria': 'serum',
  'tipo_pele': 'mista',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'SERUM/Serum (4).png',
  'nome': 'Calma Verde — Sérum Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum calmante de uso diário para perfis que pedem cuidado suave e sensação de conforto.',
  'conteudo': '30 ml',
  'ativos_principais': 'Centella Asiática + Pantenol',
  'preco': 69.9,
  'estoque': 21,
  'categoria': 'serum',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'SERUM/Serum (5).png',
  'nome': 'Pérola Hialurônica — Sérum Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum hidratante concentrado para ajudar a manter aparência preenchida, macia e confortável.',
  'conteudo': '30 ml',
  'ativos_principais': 'Ácido Hialurônico',
  'preco': 67.9,
  'estoque': 22,
  'categoria': 'serum',
  'tipo_pele': 'seca',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'SERUM/Serum (6).png',
  'nome': 'Firmeza de Seda — Sérum Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum de cuidado diário voltado à aparência de firmeza e textura, com acabamento leve e sedoso.',
  'conteudo': '30 ml',
  'ativos_principais': 'Peptídeos + Colágeno Vegetal',
  'preco': 82.9,
  'estoque': 16,
  'categoria': 'serum',
  'tipo_pele': 'normal',
  'pele_sensivel': False,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'SERUM/Serum (7).png',
  'nome': 'Luz de Camomila — Sérum Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum suave para peles que pedem conforto, com ativos calmantes e textura leve para a rotina '
                     'diária.',
  'conteudo': '30 ml',
  'ativos_principais': 'Camomila + Bisabolol',
  'preco': 68.9,
  'estoque': 19,
  'categoria': 'serum',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'SERUM/Serum (8).png',
  'nome': 'Rosa Mineral — Sérum Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum leve para equilibrar hidratação e aparência da pele em uma fórmula de uso cotidiano.',
  'conteudo': '30 ml',
  'ativos_principais': 'Água Termal + Niacinamida',
  'preco': 71.9,
  'estoque': 20,
  'categoria': 'serum',
  'tipo_pele': 'mista',
  'pele_sensivel': True,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'SERUM/Serum (9).png',
  'nome': 'Chá Branco Balance — Sérum Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum balanceador para peles com tendência à oleosidade, ajudando a manter sensação leve ao '
                     'longo do dia.',
  'conteudo': '30 ml',
  'ativos_principais': 'Chá Branco + Zinco PCA',
  'preco': 73.9,
  'estoque': 18,
  'categoria': 'serum',
  'tipo_pele': 'oleosa',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'PROTETOR SOLAR/agua_de_coco_hidratacao_leve.png',
  'nome': 'Água de Coco Hidratação Leve — Protetor Solar FPS 50',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Protetor solar facial hidratante de rápida absorção para uso diário com sensação leve na pele.',
  'conteudo': '40 g',
  'ativos_principais': 'Água de Coco + Ácido Hialurônico',
  'preco': 52.9,
  'estoque': 28,
  'categoria': 'protetor_solar',
  'tipo_pele': 'seca',
  'pele_sensivel': False,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'PROTETOR SOLAR/aurora_c_antioxidante.png',
  'nome': 'Aurora C Antioxidante — Protetor Solar FPS 50',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Protetor solar facial com proposta antioxidante para proteção diária e cuidado complementar da '
                     'aparência.',
  'conteudo': '40 g',
  'ativos_principais': 'Vitamina C',
  'preco': 56.9,
  'estoque': 25,
  'categoria': 'protetor_solar',
  'tipo_pele': 'normal',
  'pele_sensivel': False,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'PROTETOR SOLAR/brisa_mineral_pele_sensivel.png',
  'nome': 'Brisa Mineral Pele Sensível — Protetor Solar FPS 50',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Protetor solar mineral sem fragrância, desenvolvido para perfis que preferem fórmulas de alta '
                     'tolerância.',
  'conteudo': '40 g',
  'ativos_principais': 'Óxido de Zinco',
  'preco': 59.9,
  'estoque': 24,
  'categoria': 'protetor_solar',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'PROTETOR SOLAR/calendula_care_pele_sensivel.png',
  'nome': 'Calêndula Care Pele Sensível — Protetor Solar FPS 50',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Protetor solar facial calmante de textura leve, pensado para peles que pedem cuidado mais '
                     'delicado.',
  'conteudo': '40 g',
  'ativos_principais': 'Extrato de Calêndula',
  'preco': 58.9,
  'estoque': 23,
  'categoria': 'protetor_solar',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'PROTETOR SOLAR/marine_repair_pos_exposicao.png',
  'nome': 'Marine Repair Pós-Exposição — Protetor Solar FPS 70',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Protetor solar facial de proteção avançada com ação hidratante para rotinas de maior exposição.',
  'conteudo': '40 g',
  'ativos_principais': 'Alantoína + Minerais Marinhos',
  'preco': 64.9,
  'estoque': 20,
  'categoria': 'protetor_solar',
  'tipo_pele': 'seca',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'PROTETOR SOLAR/matte_control_pele_oleosa.png',
  'nome': 'Matte Control Pele Oleosa — Protetor Solar FPS 70',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Protetor solar facial ultraleve com acabamento matte para peles com tendência à oleosidade.',
  'conteudo': '40 g',
  'ativos_principais': 'Zinco PCA',
  'preco': 62.9,
  'estoque': 26,
  'categoria': 'protetor_solar',
  'tipo_pele': 'oleosa',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'PROTETOR SOLAR/noite_dia_protecao_12h.png',
  'nome': 'Noite & Dia Proteção 12h — Protetor Solar FPS 60',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Protetor solar facial de longa duração para uso diário, com fórmula resistente ao suor e '
                     'confortável.',
  'conteudo': '40 g',
  'ativos_principais': 'Pantenol',
  'preco': 61.9,
  'estoque': 21,
  'categoria': 'protetor_solar',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'PROTETOR SOLAR/pepino_fresh_refrescante.png',
  'nome': 'Pepino Fresh Refrescante — Protetor Solar FPS 50',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Protetor solar facial refrescante de textura aquosa para sensação leve e confortável durante o '
                     'uso.',
  'conteudo': '40 g',
  'ativos_principais': 'Extrato de Pepino',
  'preco': 54.9,
  'estoque': 27,
  'categoria': 'protetor_solar',
  'tipo_pele': 'mista',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'PROTETOR SOLAR/perola_solar_toque_seco.png',
  'nome': 'Pérola Solar Toque Seco — Protetor Solar FPS 50',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Protetor solar facial de toque seco, invisível e não comedogênico para controle da sensação de '
                     'oleosidade.',
  'conteudo': '40 g',
  'ativos_principais': 'Niacinamida',
  'preco': 57.9,
  'estoque': 29,
  'categoria': 'protetor_solar',
  'tipo_pele': 'oleosa',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'PROTETOR SOLAR/toque_nude_efeito_blur.png',
  'nome': 'Toque Nude Efeito Blur — Protetor Solar FPS 50',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Protetor solar facial com acabamento natural e efeito blur para suavizar visualmente a aparência '
                     'dos poros.',
  'conteudo': '40 g',
  'ativos_principais': 'Niacinamida',
  'preco': 60.9,
  'estoque': 22,
  'categoria': 'protetor_solar',
  'tipo_pele': 'mista',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'OUTROS/1_clarisse_micelar_7em1.png',
  'nome': 'Clarisse Micelar 7 em 1 — Água Micelar',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Água micelar multifuncional para limpar, demaquilar, hidratar e refrescar sem necessidade de '
                     'enxágue.',
  'conteudo': '200 ml',
  'ativos_principais': 'Micelas + Glicerina',
  'preco': 34.9,
  'estoque': 30,
  'categoria': 'outros',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'OUTROS/2_exfolia_glow.png',
  'nome': 'Exfolia Glow — Esfoliante Facial Suave',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Esfoliante facial suave para renovar a aparência e remover células superficiais sem uso '
                     'agressivo.',
  'conteudo': '60 g',
  'ativos_principais': 'Partículas Naturais + Pantenol',
  'preco': 39.9,
  'estoque': 22,
  'categoria': 'outros',
  'tipo_pele': 'normal',
  'pele_sensivel': False,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'OUTROS/3_vitamina_c_boost_10.png',
  'nome': 'Vitamina C Boost 10% — Sérum Antioxidante',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum antioxidante concentrado para complementar a rotina e favorecer aparência mais luminosa.',
  'conteudo': '30 ml',
  'ativos_principais': 'Vitamina C 10%',
  'preco': 69.9,
  'estoque': 20,
  'categoria': 'outros',
  'tipo_pele': 'mista',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'OUTROS/4_mascara_verde_detox.png',
  'nome': 'Máscara Verde Detox — Argila Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Máscara facial de argila verde para rotinas de limpeza intensiva e controle da sensação de '
                     'oleosidade.',
  'conteudo': '100 g',
  'ativos_principais': 'Argila Verde + Zinco PCA',
  'preco': 44.9,
  'estoque': 18,
  'categoria': 'outros',
  'tipo_pele': 'oleosa',
  'pele_sensivel': False,
  'indicado_para_espinha': True,
  'ativo': True},
 {'source': 'OUTROS/5_tonico_calmante.png',
  'nome': 'Tônico Calmante — Camomila & Hamamélis',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Tônico facial sem álcool para refrescar e complementar a rotina de peles que pedem maior '
                     'delicadeza.',
  'conteudo': '200 ml',
  'ativos_principais': 'Camomila + Hamamélis',
  'preco': 36.9,
  'estoque': 27,
  'categoria': 'outros',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'OUTROS/6_pos_sol_refresh.png',
  'nome': 'Pós Sol Refresh — Gel Hidratante Calmante',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Gel hidratante calmante de textura leve para uso após exposição solar, com sensação refrescante.',
  'conteudo': '120 g',
  'ativos_principais': 'Aloe Vera + Pantenol',
  'preco': 47.9,
  'estoque': 19,
  'categoria': 'outros',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'OUTROS/7_olhos_revive.png',
  'nome': 'Olhos Revive — Sérum para Área dos Olhos',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Sérum leve para a área dos olhos com aplicador refrescante e proposta de cuidado para aparência '
                     'cansada.',
  'conteudo': '15 ml',
  'ativos_principais': 'Cafeína + Ácido Hialurônico',
  'preco': 58.9,
  'estoque': 16,
  'categoria': 'outros',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'OUTROS/8_fix_fresh_bruma.png',
  'nome': 'Fix & Fresh — Bruma Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Bruma facial sem álcool para hidratar, refrescar e complementar a rotina ao longo do dia.',
  'conteudo': '120 ml',
  'ativos_principais': 'Pantenol + Água Termal',
  'preco': 42.9,
  'estoque': 25,
  'categoria': 'outros',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'OUTROS/9_oleo_de_lavanda.png',
  'nome': 'Óleo de Lavanda — Óleo Facial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Óleo facial de uso noturno para proporcionar toque emoliente e sensação de conforto na rotina.',
  'conteudo': '30 ml',
  'ativos_principais': 'Óleo de Lavanda + Esqualano',
  'preco': 49.9,
  'estoque': 17,
  'categoria': 'outros',
  'tipo_pele': 'seca',
  'pele_sensivel': False,
  'indicado_para_espinha': False,
  'ativo': True},
 {'source': 'OUTROS/10_lip_care_nutri.png',
  'nome': 'Lip Care Nutri — Hidratante Labial',
  'marca': 'Lumina Skin',
  'descricao_curta': 'Hidratante labial de uso diário para nutrir e proteger os lábios contra a sensação de '
                     'ressecamento.',
  'conteudo': '4,5 g',
  'ativos_principais': 'Manteiga de Karité + Vitamina E',
  'preco': 19.9,
  'estoque': 35,
  'categoria': 'outros',
  'tipo_pele': 'todos',
  'pele_sensivel': True,
  'indicado_para_espinha': False,
  'ativo': True}]

COLUNAS_OBRIGATORIAS = {
    "id", "nome", "preco", "estoque", "tipo_pele",
    "pele_sensivel", "indicado_para_espinha", "ativo",
    "categoria", "marca", "descricao_curta", "imagem_url",
    "conteudo", "ativos_principais",
}


def slug(texto: str) -> str:
    normalizado = unicodedata.normalize("NFKD", texto)
    ascii_texto = normalizado.encode("ascii", "ignore").decode("ascii")
    ascii_texto = ascii_texto.lower()
    ascii_texto = re.sub(r"[^a-z0-9]+", "-", ascii_texto)
    return ascii_texto.strip("-")


def localizar_origem(caminho_relativo: str) -> Path:
    direto = PASTA_IMAGENS / caminho_relativo
    if direto.exists():
        return direto

    alvo = caminho_relativo.replace("\\", "/").lower()

    for arquivo in PASTA_IMAGENS.rglob("*"):
        if not arquivo.is_file():
            continue

        relativo = arquivo.relative_to(PASTA_IMAGENS).as_posix().lower()
        if relativo == alvo:
            return arquivo

    raise FileNotFoundError(
        f"Imagem não encontrada: {caminho_relativo}"
    )


def processar_imagem(origem: Path, categoria: str, nome: str) -> str:
    destino_dir = PASTA_IMAGENS / categoria
    destino_dir.mkdir(parents=True, exist_ok=True)

    destino = destino_dir / f"{slug(nome)}.webp"

    try:
        with Image.open(origem) as imagem:
            imagem.load()
            imagem = ImageOps.exif_transpose(imagem)

            if imagem.width * imagem.height > 40_000_000:
                raise ValueError(
                    f"Imagem excede 40 MP: {origem.name}"
                )

            imagem.thumbnail((1600, 1600))

            tem_alpha = (
                imagem.mode in ("RGBA", "LA")
                or (
                    imagem.mode == "P"
                    and "transparency" in imagem.info
                )
            )

            if tem_alpha:
                imagem = imagem.convert("RGBA")
            else:
                imagem = imagem.convert("RGB")

            imagem.save(
                destino,
                "WEBP",
                quality=88,
                method=6,
            )

    except (UnidentifiedImageError, OSError) as erro:
        raise ValueError(
            f"Imagem inválida: {origem}"
        ) from erro

    return (
        f"/media/produtos/{categoria}/"
        f"{destino.name}"
    )


def validar_banco(conexao: sqlite3.Connection) -> None:
    colunas = {
        linha[1]
        for linha in conexao.execute(
            "PRAGMA table_info(produtos)"
        ).fetchall()
    }

    faltando = COLUNAS_OBRIGATORIAS - colunas

    if faltando:
        raise RuntimeError(
            "Banco incompatível. Colunas ausentes: "
            + ", ".join(sorted(faltando))
        )


def validar_catalogo() -> None:
    nomes = set()

    for produto in CATALOGO:
        if produto["nome"] in nomes:
            raise ValueError(
                f"Nome duplicado no catálogo: {produto['nome']}"
            )

        nomes.add(produto["nome"])
        localizar_origem(produto["source"])

        if not (2 <= len(produto["nome"]) <= 100):
            raise ValueError(
                f"Nome inválido: {produto['nome']}"
            )

        if not (10 <= len(produto["descricao_curta"]) <= 300):
            raise ValueError(
                f"Descrição inválida: {produto['nome']}"
            )

        if not produto["conteudo"] or len(produto["conteudo"]) > 30:
            raise ValueError(
                f"Conteúdo inválido: {produto['nome']}"
            )

        if not (2 <= len(produto["ativos_principais"]) <= 200):
            raise ValueError(
                f"Ativos inválidos: {produto['nome']}"
            )

        if produto["preco"] <= 0:
            raise ValueError(
                f"Preço inválido: {produto['nome']}"
            )

        if produto["estoque"] < 0:
            raise ValueError(
                f"Estoque inválido: {produto['nome']}"
            )


def aplicar() -> tuple[int, int]:
    if not BANCO.exists():
        raise FileNotFoundError(
            f"Banco não encontrado: {BANCO}"
        )

    inseridos = 0
    atualizados = 0

    conexao = sqlite3.connect(BANCO)

    try:
        validar_banco(conexao)

        with conexao:
            for produto in CATALOGO:
                origem = localizar_origem(
                    produto["source"]
                )

                imagem_url = processar_imagem(
                    origem,
                    produto["categoria"],
                    produto["nome"],
                )

                existente = conexao.execute(
                    "SELECT id FROM produtos WHERE nome = ?",
                    (produto["nome"],),
                ).fetchone()

                valores = (
                    produto["marca"],
                    produto["descricao_curta"],
                    imagem_url,
                    produto["conteudo"],
                    produto["ativos_principais"],
                    produto["preco"],
                    produto["estoque"],
                    produto["tipo_pele"],
                    int(produto["pele_sensivel"]),
                    int(produto["indicado_para_espinha"]),
                    int(produto["ativo"]),
                    produto["categoria"],
                )

                if existente:
                    conexao.execute(
                        """
                        UPDATE produtos
                        SET
                            marca = ?,
                            descricao_curta = ?,
                            imagem_url = ?,
                            conteudo = ?,
                            ativos_principais = ?,
                            preco = ?,
                            estoque = ?,
                            tipo_pele = ?,
                            pele_sensivel = ?,
                            indicado_para_espinha = ?,
                            ativo = ?,
                            categoria = ?
                        WHERE id = ?
                        """,
                        (*valores, existente[0]),
                    )
                    atualizados += 1
                else:
                    conexao.execute(
                        """
                        INSERT INTO produtos (
                            nome,
                            marca,
                            descricao_curta,
                            imagem_url,
                            conteudo,
                            ativos_principais,
                            preco,
                            estoque,
                            tipo_pele,
                            pele_sensivel,
                            indicado_para_espinha,
                            ativo,
                            categoria
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            produto["nome"],
                            *valores,
                        ),
                    )
                    inseridos += 1

    finally:
        conexao.close()

    return inseridos, atualizados


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--aplicar",
        action="store_true",
        help="Processa as imagens e grava o catálogo no banco.",
    )
    args = parser.parse_args()

    validar_catalogo()

    if not args.aplicar:
        print("CATÁLOGO VALIDADO")
        print(f"Produtos: {len(CATALOGO)}")
        print("Imagens: OK")
        print("Banco: nenhuma alteração realizada")
        print()
        print("Para gravar: python popular_catalogo.py --aplicar")
        return 0

    inseridos, atualizados = aplicar()

    print("CATÁLOGO LUMINA CONCLUÍDO")
    print(f"Produtos do catálogo: {len(CATALOGO)}")
    print(f"Inseridos: {inseridos}")
    print(f"Atualizados: {atualizados}")
    print("Imagens WebP: OK")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        raise SystemExit(1)
